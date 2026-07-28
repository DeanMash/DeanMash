from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import Config, load_config
from .demo_data import build_demo_report, demo_config
from .instagram_client import extract_instagram_urls
from .markets import DEFAULT_SYMBOLS, INDEX_DISPLAY_NAMES, normalize_symbols
from .service import generate_advice_report

logger = logging.getLogger(__name__)
STATIC_DIR = Path(__file__).resolve().parent / "static"


class SuggestionRequest(BaseModel):
    instagram_urls: list[str] = Field(default_factory=list)
    instagram_text: str = ""
    symbols: list[str] = Field(default_factory=list)
    symbols_text: str = ""


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _check_dashboard_access(
    config: Config,
    *,
    header_token: str | None,
    query_token: str | None,
) -> None:
    if not config.dashboard_token:
        return
    provided = header_token or query_token
    if provided != config.dashboard_token:
        raise HTTPException(status_code=401, detail="Invalid or missing dashboard token")


def _collect_instagram_urls(
    *,
    urls: list[str] | None = None,
    text: str = "",
    query_csv: str | None = None,
) -> list[str]:
    collected: list[str] = []
    for url in urls or []:
        collected.extend(extract_instagram_urls(url))
    if text:
        collected.extend(extract_instagram_urls(text))
    if query_csv:
        collected.extend(extract_instagram_urls(query_csv.replace(",", " ")))

    deduped: list[str] = []
    seen: set[str] = set()
    for url in collected:
        key = url.rstrip("/").lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(url)
    return deduped


async def _build_report(request: Request, urls: list[str], symbols: list[str] | None = None):
    if request.app.state.demo_mode:
        return build_demo_report(instagram_urls=urls, symbols=symbols)
    return await generate_advice_report(
        request.app.state.config,
        instagram_urls=urls,
        symbols=symbols,
    )


def create_app(config: Config | None = None, *, demo_mode: bool = False) -> FastAPI:
    if demo_mode:
        config = config or demo_config()
    else:
        config = config or load_config()

    app = FastAPI(title="Deriv Trade Advisor", docs_url=None, redoc_url=None)
    app.state.config = config
    app.state.demo_mode = demo_mode

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    async def index() -> FileResponse:
        index_path = STATIC_DIR / "index.html"
        if not index_path.exists():
            raise HTTPException(status_code=404, detail="Dashboard UI missing")
        return FileResponse(index_path)

    @app.get("/api/health")
    async def health() -> dict:
        return {
            "ok": True,
            "mode": "demo" if demo_mode else "suggestions_only",
            "auth_required": bool(config.dashboard_token),
            "symbols": config.symbols,
            "min_confidence": config.min_confidence,
            "instagram_enabled": True,
            "available_indices": [
                {"symbol": symbol, "display_name": name}
                for symbol, name in INDEX_DISPLAY_NAMES.items()
            ],
            "default_symbols": DEFAULT_SYMBOLS,
        }

    @app.get("/api/suggestions")
    async def suggestions_get(
        request: Request,
        token: str | None = Query(default=None),
        instagram: str | None = Query(default=None),
        symbols: str | None = Query(default=None),
        x_dashboard_token: str | None = Header(default=None),
    ) -> dict:
        _check_dashboard_access(
            request.app.state.config,
            header_token=x_dashboard_token,
            query_token=token,
        )
        urls = _collect_instagram_urls(query_csv=instagram)
        watchlist = normalize_symbols(symbols) if symbols else None
        try:
            report = await _build_report(request, urls, symbols=watchlist)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Dashboard suggestion request failed")
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return report.to_dict()

    @app.post("/api/suggestions")
    async def suggestions_post(
        request: Request,
        body: SuggestionRequest,
        token: str | None = Query(default=None),
        x_dashboard_token: str | None = Header(default=None),
    ) -> dict:
        _check_dashboard_access(
            request.app.state.config,
            header_token=x_dashboard_token,
            query_token=token,
        )
        urls = _collect_instagram_urls(urls=body.instagram_urls, text=body.instagram_text)
        watchlist = normalize_symbols(body.symbols or body.symbols_text)
        try:
            report = await _build_report(
                request,
                urls,
                symbols=watchlist or None,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Dashboard suggestion request failed")
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return report.to_dict()

    return app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Web dashboard for Deriv trade suggestions.")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--demo", action="store_true", help="Run with sample data (no Deriv token)")
    parser.add_argument("--host", default=None, help="Override DASHBOARD_HOST")
    parser.add_argument("--port", type=int, default=None, help="Override DASHBOARD_PORT")
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)

    if args.demo:
        config = demo_config()
        app = create_app(config, demo_mode=True)
        host = args.host or config.dashboard_host
        port = args.port or config.dashboard_port
        print("Deriv Trade Advisor — DEMO MODE (sample data, no live Deriv calls)")
        print(f"Open: http://127.0.0.1:{port}")
        print("Click Get suggestions to see sample CALL/PUT ideas.")
        uvicorn.run(app, host=host, port=port, log_level="debug" if args.verbose else "info")
        return 0

    try:
        config = load_config()
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        print("Tip: run a sample UI with: python -m deriv_advisor web --demo", file=sys.stderr)
        return 1

    host = args.host or config.dashboard_host
    port = args.port or config.dashboard_port
    app = create_app(config)

    print("Deriv Trade Advisor dashboard (suggestions only)")
    print(f"Open on this machine: http://127.0.0.1:{port}")
    print(f"On your phone (same Wi‑Fi): http://<this-computer-ip>:{port}")
    print("Paste Instagram post/reel links in the dashboard before Get suggestions.")
    if config.dashboard_token:
        print("DASHBOARD_TOKEN is set — include it in the UI access field or ?token=")
    else:
        print(
            "Warning: DASHBOARD_TOKEN is empty. Anyone on your network who can "
            "reach this port can request suggestions."
        )

    uvicorn.run(app, host=host, port=port, log_level="debug" if args.verbose else "info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
