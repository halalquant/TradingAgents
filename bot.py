import logging
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from io import BytesIO
from tradingagents.domain.model import AnalysisStatus

from service import enqueue_analysis, get_status
from tradingagents.config import get_config
from tradingagents.config import settings
from datetime import datetime

# --------------------------------------------------
# Config
# --------------------------------------------------
config = get_config()

BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Helpers
# --------------------------------------------------
async def send_text_as_file(
    bot: Bot,
    chat_id: int,
    content: str,
    filename: str,
    caption: str | None = None,
):
    """
    Send text content as a file to Telegram without saving to disk.
    The file is created in memory only.
    """

    if not content:
        content = "No content"
    
    if isinstance(content, str):
        data = content.encode("utf-8")
    else:
        data = content  # already bytes

    buffer = BytesIO(data)
    buffer.name = filename

    await bot.send_document(
        chat_id=chat_id,
        document=buffer,
        caption=caption,
    )

def is_user_whitelisted(user_id: int) -> bool:
    if not settings.WHITELIST_ENABLED:
        return True
    return user_id in settings.WHITELISTED_USER_IDS

def is_coin_available(symbol: str) -> bool:
    if not settings.AVAILABLE_COINS:
        return True
    return symbol.upper() in settings.AVAILABLE_COINS

# --------------------------------------------------
# Commands
# --------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to TradingAgents Bot\n\n"
        "Commands:\n"
        "/analyze BTC/USDT – start analysis\n"
        "/report BTC/USDT – check analysis status"
    )

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_whitelisted(user_id):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /analyze BTC/USDT")
        return

    symbol = context.args[0].upper()
    if not is_coin_available(symbol):
        await update.message.reply_text(f"❌ The symbol {symbol} is not available for analysis.")
        return

    response = enqueue_analysis(user_id=user_id, symbol=symbol, date=datetime.now().strftime("%Y-%m-%d"))
    logger.info(f"Analyze response for user {user_id}, symbol {symbol}: {response}")

    if response.status == "error":
        await update.message.reply_text(f"❌ Error: {response.message}")
        return

    await update.message.reply_text(
        f"{response.message}\n\n"
        f"• Symbol: {symbol}\n"
        f"• Job ID: `{response.job_id}`\n"
        "Use /report to check status.",
        parse_mode="Markdown",
    )


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_whitelisted(user_id):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /report job-id")
        return

    job_id = context.args[0]

    response = get_status(user_id, job_id)
    logger.info(f"Report response for user {user_id}, job {job_id}: {response}")

    if not response:
        await update.message.reply_text("❌ Job not found. or error occurred.")
        return

    if response.status in (AnalysisStatus.PENDING, AnalysisStatus.RUNNING):
        await update.message.reply_text(
            f"⏳ Status: {response.status.value}\n"
            "Please check again later."
        )
        return

    if response.status == AnalysisStatus.DONE:
        await send_text_as_file(
            bot=context.bot,
            chat_id=update.effective_chat.id,
            content=response.result,
            filename=f"analysis_{job_id}.md",
            caption="📊 Analysis completed. Full report attached.",
        )
        return

    if response.status == AnalysisStatus.FAILED:
        await update.message.reply_text(
            f"❌ Analysis failed:\n{response.message}"
        )


# --------------------------------------------------
# App
# --------------------------------------------------
def main():
    logger.info("INFO: Starting Telegram bot... {}".format(BOT_TOKEN))
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("report", report))

    logger.info("🚀 Telegram bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
