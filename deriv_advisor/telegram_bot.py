from __future__ import annotations

import argparse
import logging
import sys

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from .config import load_config
from .service import generate_advice_report

logger = logging.getLogger(__name__)


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _is_allowed(chat_id: int, allowed: set[int]) -> bool:
    return not allowed or chat_id in allowed


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    allowed: set[int] = context.application.bot_data["allowed_chat_ids"]
    chat = update.effective_chat
    if chat is None or update.message is None:
        return
    if not _is_allowed(chat.id, allowed):
        await update.message.reply_text(
            f"Access denied for chat_id {chat.id}. "
            "Add this id to TELEGRAM_ALLOWED_CHAT_IDS in your .env."
        )
        return

    await update.message.reply_text(
        "Deriv Trade Advisor bot (suggestions only).\n\n"
        "Commands:\n"
        "/suggest — analyze markets and send trade ideas\n"
        "/chatid — show this chat id\n"
        "/help — show help\n\n"
        "No trades are placed automatically."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None or update.message is None:
        return
    await update.message.reply_text(f"Your chat id: {update.effective_chat.id}")


async def suggest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    allowed: set[int] = context.application.bot_data["allowed_chat_ids"]
    chat = update.effective_chat
    if chat is None or update.message is None:
        return
    if not _is_allowed(chat.id, allowed):
        await update.message.reply_text(
            f"Access denied for chat_id {chat.id}. "
            "Add this id to TELEGRAM_ALLOWED_CHAT_IDS in your .env."
        )
        return

    await update.message.reply_text("Analyzing Deriv markets + news… this can take ~10–30s.")
    try:
        config = context.application.bot_data["config"]
        report = await generate_advice_report(config)
        text = report.to_text(compact=True)
        # Telegram hard limit is 4096 chars.
        if len(text) > 3900:
            text = text[:3900] + "\n…(truncated)"
        await update.message.reply_text(text)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Suggestion request failed")
        await update.message.reply_text(f"Failed to generate suggestions: {exc}")


def build_app(token: str, allowed_chat_ids: set[int]):
    config = load_config()
    app = Application.builder().token(token).build()
    app.bot_data["config"] = config
    app.bot_data["allowed_chat_ids"] = allowed_chat_ids

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("chatid", chatid))
    app.add_handler(CommandHandler(["suggest", "ideas"], suggest))
    return app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Telegram bot for Deriv trade suggestions.")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)

    try:
        config = load_config()
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not config.telegram_bot_token:
        print(
            "Error: TELEGRAM_BOT_TOKEN is missing. "
            "Create a bot with @BotFather and add the token to .env.",
            file=sys.stderr,
        )
        return 1

    app = build_app(config.telegram_bot_token, config.telegram_allowed_chat_ids)
    print("Telegram bot running. Open Telegram and send /suggest to your bot.")
    if config.telegram_allowed_chat_ids:
        print(f"Allowed chat ids: {sorted(config.telegram_allowed_chat_ids)}")
    else:
        print(
            "Warning: TELEGRAM_ALLOWED_CHAT_IDS is empty — any Telegram user who "
            "finds the bot can request suggestions. Send /chatid then lock it down."
        )
    app.run_polling(allowed_updates=Update.ALL_TYPES)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
