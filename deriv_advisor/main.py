from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import datetime, timezone

from .analyzer import analyze_news, analyze_ticks
from .config import load_config
from .deriv_client import DerivClient
from .news_client import fetch_news
from .suggester import build_suggestions


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_divider(title: str = "") -> None:
    line = "=" * 64
    if title:
        print(f"\n{line}\n{title}\n{line}")
    else:
        print(line)


async def run_once(verbose: bool = False) -> int:
    _configure_logging(verbose)
    config = load_config()

    _print_divider("Deriv Trade Advisor — SUGGESTIONS ONLY")
    print("This tool never places trades. Review every idea yourself.")
    print(f"Generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")

    news_items = fetch_news(config.news_api_key, max_items=20)
    news_sentiment = analyze_news(news_items)

    async with DerivClient(config.ws_url, config.api_token) as client:
        if client.account is None:
            raise RuntimeError("Deriv account was not authorized")
        account = client.account
        trades = await client.get_recent_trades(limit=30)

        technicals = []
        for symbol in config.symbols:
            try:
                series = await client.get_ticks_history(symbol, config.tick_count)
                technicals.append(analyze_ticks(series))
                print(f"Fetched {len(series.prices)} ticks for {symbol}")
            except Exception as exc:  # noqa: BLE001
                logging.error("Failed to analyze %s: %s", symbol, exc)

    suggestions = build_suggestions(
        technicals=technicals,
        news=news_sentiment,
        trades=trades,
        min_confidence=config.min_confidence,
    )

    _print_divider("Account")
    print(f"Login ID : {account.loginid}")
    print(f"Type     : {'DEMO' if account.is_virtual else 'REAL'}")
    print(f"Balance  : {account.balance:.2f} {account.currency}")

    _print_divider("News snapshot")
    print(news_sentiment.summary)
    print(f"Headlines analyzed: {news_sentiment.headline_count}")
    for title in news_sentiment.sample_titles:
        print(f"  • {title}")

    _print_divider(f"Suggestions (min confidence {config.min_confidence:g})")
    if not suggestions:
        print("No suggestions met the confidence threshold right now.")
        print("Try lowering MIN_CONFIDENCE or waiting for a clearer market move.")
        return 0

    for idx, suggestion in enumerate(suggestions, start=1):
        print(
            f"\n#{idx} {suggestion.symbol} → {suggestion.direction} "
            f"| confidence {suggestion.confidence:.1f}% "
            f"| last {suggestion.last_price}"
        )
        for reason in suggestion.reasons:
            print(f"   - {reason}")

    _print_divider("Disclaimer")
    print(
        "Signals are heuristic and can be wrong. Past ticks/news do not guarantee "
        "future results. Use a demo account while evaluating this tool."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Suggest Deriv trades from market ticks, news, and recent account activity."
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args(argv)

    try:
        return asyncio.run(run_once(verbose=args.verbose))
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
