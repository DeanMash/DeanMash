from __future__ import annotations

import argparse
import logging

import uvicorn


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="closeloop", description="CloseLoop contractor follow-ups")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command")

    web = sub.add_parser("web", help="Run the web dashboard")
    web.add_argument("--host", default="0.0.0.0")
    web.add_argument("--port", type=int, default=8000)

    run = sub.add_parser("run-followups", help="Process due SMS/email follow-ups once")
    run.add_argument("--date", default="", help="YYYY-MM-DD override (default: today)")

    sub.add_parser("seed", help="Seed demo contractor data")

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if args.command in (None, "web"):
        host = getattr(args, "host", "0.0.0.0")
        port = getattr(args, "port", 8000)
        uvicorn.run("closeloop.web:app", host=host, port=port, reload=False)
        return 0

    from datetime import date

    from closeloop.config import get_settings
    from closeloop.db import SessionLocal, init_db
    from closeloop.seed import seed_demo
    from closeloop.service import process_due_follow_ups

    init_db()
    if args.command == "seed":
        with SessionLocal() as db:
            biz = seed_demo(db)
            print(f"Seeded business #{biz.id}: {biz.name}")
        return 0

    if args.command == "run-followups":
        on_day = date.fromisoformat(args.date) if args.date else date.today()
        with SessionLocal() as db:
            if get_settings().seed_demo:
                seed_demo(db)
            stats = process_due_follow_ups(db, on_day=on_day)
            print(stats)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())