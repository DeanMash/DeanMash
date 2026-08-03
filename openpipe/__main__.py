"""CLI entry: python -m openpipe"""

from __future__ import annotations

import argparse
import logging

import uvicorn

from . import config
from .engine import OutreachEngine
from .store import Store
from .web import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenPipe outbound email system")
    parser.add_argument(
        "command",
        nargs="?",
        default="web",
        choices=["web", "seed", "discover", "plan", "run"],
        help="web (default) | seed | discover | plan | run",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--host", default=config.HOST)
    parser.add_argument("--port", type=int, default=config.PORT)
    parser.add_argument("--limit", type=int, default=8, help="Prospects to discover")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    )

    store = Store()
    engine = OutreachEngine(store)

    if args.command == "seed":
        biz = store.seed_demo(force=True)
        engine.plan_business(biz.id)
        print(f"Seeded demo business: {biz.name} ({biz.id})")
        return

    if args.command == "discover":
        biz = store.seed_demo()
        result = engine.discover_and_plan(biz.id, limit=args.limit)
        print(result)
        return

    if args.command == "plan":
        biz = store.seed_demo()
        result = engine.plan_business(biz.id)
        print(result)
        return

    if args.command == "run":
        biz = store.seed_demo()
        engine.plan_business(biz.id)
        result = engine.run_due(biz.id)
        print(result)
        return

    app = create_app(store)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
