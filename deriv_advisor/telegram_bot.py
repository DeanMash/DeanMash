from __future__ import annotations

import argparse
import logging
import sys
import time

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .config import load_config
from .instagram_client import extract_instagram_urls
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


def _alert_recipients(allowed: set[int]) -> list[int]:
    return sorted(allowed)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    allowed: set[int] = context.application.bot_data["allowed_chat_ids"]
    config = context.application.bot_data["config"]
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
        "/suggest <instagram link> — include Instagram caption tone\n"
        "/alerts — show alert settings\n"
        "/alerts on|off — enable/disable scheduled alerts\n"
        "/chatid — show this chat id\n"
        "/help — show help\n\n"
        f"Scheduled alerts: {'ON' if context.application.bot_data.get('alerts_enabled', config.alert_enabled) else 'OFF'} "
        f"every {config.alert_interval_minutes}m at ≥{config.alert_min_confidence:g}% confidence.\n"
        "You can also paste an Instagram post/reel link.\n"
        "No trades are placed automatically."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None or update.message is None:
        return
    await update.message.reply_text(f"Your chat id: {update.effective_chat.id}")


async def alerts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    allowed: set[int] = context.application.bot_data["allowed_chat_ids"]
    config = context.application.bot_data["config"]
    chat = update.effective_chat
    if chat is None or update.message is None:
        return
    if not _is_allowed(chat.id, allowed):
        await update.message.reply_text(
            f"Access denied for chat_id {chat.id}. "
            "Add this id to TELEGRAM_ALLOWED_CHAT_IDS in your .env."
        )
        return

    arg = (context.args[0].lower() if context.args else "").strip()
    if arg in {"on", "enable", "true", "1"}:
        context.application.bot_data["alerts_enabled"] = True
        await update.message.reply_text("Scheduled high-confidence alerts enabled.")
        return
    if arg in {"off", "disable", "false", "0"}:
        context.application.bot_data["alerts_enabled"] = False
        await update.message.reply_text("Scheduled alerts disabled.")
        return

    enabled = context.application.bot_data.get("alerts_enabled", config.alert_enabled)
    recipients = _alert_recipients(allowed)
    await update.message.reply_text(
        "Alert settings:\n"
        f"• Enabled: {enabled}\n"
        f"• Interval: every {config.alert_interval_minutes} minutes\n"
        f"• Min confidence: {config.alert_min_confidence:g}%\n"
        f"• Cooldown per idea: {config.alert_cooldown_minutes} minutes\n"
        f"• Recipients: {recipients or 'none (set TELEGRAM_ALLOWED_CHAT_IDS)'}\n\n"
        "Use /alerts on or /alerts off"
    )


async def _run_suggest(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    instagram_urls: list[str],
) -> None:
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

    if instagram_urls:
        await update.message.reply_text(
            f"Analyzing Deriv markets + news + {len(instagram_urls)} Instagram link(s)…"
        )
    else:
        await update.message.reply_text("Analyzing Deriv markets + news…")

    try:
        config = context.application.bot_data["config"]
        report = await generate_advice_report(config, instagram_urls=instagram_urls)
        text = report.to_text(compact=True)
        if len(text) > 3900:
            text = text[:3900] + "\n…(truncated)"
        await update.message.reply_text(text)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Suggestion request failed")
        await update.message.reply_text(f"Failed to generate suggestions: {exc}")


async def suggest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = " ".join(context.args) if context.args else ""
    if update.message and update.message.text:
        raw = f"{raw} {update.message.text}"
    urls = extract_instagram_urls(raw)
    await _run_suggest(update, context, instagram_urls=urls)


async def instagram_link_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or not update.message.text:
        return
    urls = extract_instagram_urls(update.message.text)
    if not urls:
        return
    await _run_suggest(update, context, instagram_urls=urls)


def _should_send_alert(
    context: ContextTypes.DEFAULT_TYPE,
    *,
    symbol: str,
    direction: str,
    cooldown_minutes: int,
) -> bool:
    key = f"{symbol}:{direction}"
    last_sent: dict[str, float] = context.application.bot_data.setdefault("alert_last_sent", {})
    now = time.time()
    previous = last_sent.get(key, 0.0)
    if now - previous < cooldown_minutes * 60:
        return False
    last_sent[key] = now
    return True


async def high_confidence_alert_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    config = context.application.bot_data["config"]
    enabled = context.application.bot_data.get("alerts_enabled", config.alert_enabled)
    if not enabled:
        return

    recipients = _alert_recipients(context.application.bot_data["allowed_chat_ids"])
    if not recipients:
        logger.warning("Alert job skipped: TELEGRAM_ALLOWED_CHAT_IDS is empty")
        return

    try:
        report = await generate_advice_report(config)
    except Exception:  # noqa: BLE001
        logger.exception("Scheduled alert analysis failed")
        return

    high = [
        s
        for s in report.suggestions
        if s.confidence >= config.alert_min_confidence
        and _should_send_alert(
            context,
            symbol=s.symbol,
            direction=s.direction,
            cooldown_minutes=config.alert_cooldown_minutes,
        )
    ]
    if not high:
        logger.info(
            "Alert job: no new ideas at ≥%s%% (cache_hit=%s)",
            config.alert_min_confidence,
            report.cache_hit,
        )
        return

    lines = [
        "High-confidence Deriv ideas (suggestions only)",
        f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
    ]
    for idx, suggestion in enumerate(high, start=1):
        lines.append(
            f"#{idx} {suggestion.symbol} → {suggestion.direction} "
            f"| {suggestion.confidence:.1f}% | last {suggestion.last_price}"
        )
        for reason in suggestion.reasons[:2]:
            lines.append(f"   - {reason}")
    lines.append("")
    lines.append("Not financial advice. Review before trading.")
    text = "\n".join(lines)
    if len(text) > 3900:
        text = text[:3900] + "\n…(truncated)"

    for chat_id in recipients:
        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to send alert to chat_id=%s", chat_id)


def build_app(token: str, allowed_chat_ids: set[int]):
    config = load_config()
    app = Application.builder().token(token).build()
    app.bot_data["config"] = config
    app.bot_data["allowed_chat_ids"] = allowed_chat_ids
    app.bot_data["alerts_enabled"] = config.alert_enabled
    app.bot_data["alert_last_sent"] = {}

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("chatid", chatid))
    app.add_handler(CommandHandler("alerts", alerts_cmd))
    app.add_handler(CommandHandler(["suggest", "ideas"], suggest))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, instagram_link_message)
    )

    if app.job_queue is None:
        logger.warning(
            "JobQueue unavailable. Install python-telegram-bot[job-queue] for scheduled alerts."
        )
    else:
        app.job_queue.run_repeating(
            high_confidence_alert_job,
            interval=config.alert_interval_minutes * 60,
            first=20,
            name="high-confidence-alerts",
        )
        logger.info(
            "Scheduled alerts every %s minutes at ≥%s%% confidence",
            config.alert_interval_minutes,
            config.alert_min_confidence,
        )
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
    print("Telegram bot running. Open Telegram and send /suggest or paste an Instagram link.")
    print(
        f"Scheduled alerts: {'ON' if config.alert_enabled else 'OFF'} "
        f"every {config.alert_interval_minutes}m ≥{config.alert_min_confidence:g}%"
    )
    if config.telegram_allowed_chat_ids:
        print(f"Allowed chat ids: {sorted(config.telegram_allowed_chat_ids)}")
    else:
        print(
            "Warning: TELEGRAM_ALLOWED_CHAT_IDS is empty — scheduled alerts cannot notify anyone, "
            "and any Telegram user who finds the bot can request suggestions."
        )
    app.run_polling(allowed_updates=Update.ALL_TYPES)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
