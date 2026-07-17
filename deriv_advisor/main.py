from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from .config import load_config
from .service import generate_advice_report


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


async def run_once(verbose: bool = False) -> int:
    _configure_logging(verbose)
    config = load_config()
    report = await generate_advice_report(config)
    print(report.to_text(compact=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Suggest Deriv trades from market ticks, news, and recent account activity."
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("cli", help="Run one-shot CLI suggestions (default)")
    sub.add_parser("telegram", help="Run the Telegram bot for phone access")
    args = parser.parse_args(argv)

    if args.command == "telegram":
        from .telegram_bot import main as telegram_main

        telegram_argv = ["-v"] if args.verbose else []
        return telegram_main(telegram_argv)

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
