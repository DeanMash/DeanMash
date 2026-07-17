from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import Config, load_config
from .service import generate_advice_report

logger = logging.getLogger(__name__)
STATIC_DIR = Path(__file__).resolve().parent / "static"


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


def create_app(config: Config | None = None) -> FastAPI:
    config = config or load_config()
    app = FastAPI(title="Deriv Trade Advisor", docs_url=None, redoc_url=None)
    app.state.config = config

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
            "mode": "suggestions_only",
            "auth_required": bool(config.dashboard_token),
            "symbols": config.symbols,
            "min_confidence": config.min_confidence,
        }

    @app.get("/api/suggestions")
    async def suggestions(
        request: Request,
        token: str | None = Query(default=None),
        x_dashboard_token: str | None = Header(default=None),
    ) -> dict:
        _check_dashboard_access(
            request.app.state.config,
            header_token=x_dashboard_token,
            query_token=token,
        )
        try:
            report = await generate_advice_report(request.app.state.config)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Dashboard suggestion request failed")
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return report.to_dict()

    return app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Web dashboard for Deriv trade suggestions.")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--host", default=None, help="Override DASHBOARD_HOST")
    parser.add_argument("--port", type=int, default=None, help="Override DASHBOARD_PORT")
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)

    try:
        config = load_config()
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    host = args.host or config.dashboard_host
    port = args.port or config.dashboard_port
    app = create_app(config)

    print("Deriv Trade Advisor dashboard (suggestions only)")
    print(f"Open on this machine: http://127.0.0.1:{port}")
    print(f"On your phone (same Wi‑Fi): http://<this-computer-ip>:{port}")
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
