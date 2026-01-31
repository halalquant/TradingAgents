import logging
import markdown2
from weasyprint import HTML
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from io import BytesIO
from tradingagents.domain.model import AnalysisStatus

from service import enqueue_analysis, get_status, execute_trader_proposal
from tradingagents.config import get_config
from tradingagents.config import settings
from datetime import datetime, timezone
import json

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

def generate_pdf_bytes(data: dict) -> bytes:
    """
    Converts analysis data dict to PDF bytes using logic from json2pdf.py
    """
    special_keys = ["investment_debate_state", "risk_debate_state"]
    html_pages = []

    for title, content in data.items():
        page_html = f"<h1>{title}</h1>\n"

        # Special handling for specific keys
        if title in special_keys and isinstance(content, dict):
            for sub_key, sub_value in content.items():
                page_html += f"<h2>{sub_key}</h2>\n"
                if isinstance(sub_value, str):
                    page_html += markdown2.markdown(sub_value)
                else:
                    page_html += f"<pre>{json.dumps(sub_value, indent=2)}</pre>\n"
        else:
            # General handling
            if isinstance(content, str):
                page_html += markdown2.markdown(content)
            else:
                page_html += f"<pre>{json.dumps(content, indent=2)}</pre>\n"

        # Wrap page HTML with CSS
        html_page = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                h1 {{ page-break-before: always; font-size: 24pt; }}
                h2 {{ font-size: 18pt; margin-top: 20px; }}
                body {{ font-family: Arial, sans-serif; margin: 50px; }}
                pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; white-space: pre-wrap; }}
            </style>
        </head>
        <body>
            {page_html}
        </body>
        </html>
        """
        html_pages.append(html_page)

    full_html = "\n".join(html_pages)
    
    # Use weasyprint to generate PDF from HTML
    pdf_bytes = HTML(string=full_html).write_pdf()
    return pdf_bytes

# --------------------------------------------------
# Commands
# --------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to TradingAgents Bot\n\n"
        "Commands:\n"
        "/analyze BTC/USDT – start analysis\n"
        "/report job_id – check analysis status\n"
        "/execute job_id – execute trader proposal"
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

    response = enqueue_analysis(user_id=user_id, symbol=symbol, date=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"))
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
    logger.info(f"Report response for user {user_id}, job {job_id}")

    if not response or response.status == AnalysisStatus.NOT_FOUND:
        await update.message.reply_text("❌ Job not found. or error occurred.")
        return

    if response.status in (AnalysisStatus.PENDING, AnalysisStatus.RUNNING):
        await update.message.reply_text(
            f"⏳ Status: {response.status.value}\n"
            "Please check again later."
        )
        return

    if response.status == AnalysisStatus.DONE:
        # Parse the result
        result_data = response.result
        if isinstance(result_data, str):
            result_data = json.loads(result_data)

        # Extract trader proposal
        trader_proposal_json = None
        try:
            trader_proposal = result_data.get("trader_proposal", {})
            if trader_proposal:
                trader_proposal_json = json.dumps(trader_proposal, indent=2)
        except Exception:
            pass
        
        # Send proposal text in chat
        if trader_proposal_json:
            await update.message.reply_text(
                f"📊 *Analysis Completed*\n\n"
                f"*Trader Proposal:*\n"
                f"```json\n{trader_proposal_json}\n```",
                parse_mode="Markdown"
            )
        
        # Generate and Send PDF
        try:
            await update.message.reply_text("⏳ Generating PDF report...")
            pdf_bytes = generate_pdf_bytes(result_data)
            
            # Create a BytesIO object for the file
            pdf_file = BytesIO(pdf_bytes)
            pdf_file.name = f"analysis_{job_id}.pdf"

            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=pdf_file,
                caption="📊 Full analysis report attached.",
            )
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            await update.message.reply_text("❌ Failed to generate PDF report. Sending JSON instead.")
            
            # Fallback to JSON if PDF generation fails
            await send_text_as_file(
                bot=context.bot,
                chat_id=update.effective_chat.id,
                content=response.result,
                filename=f"analysis_{job_id}.json",
                caption="📊 Full analysis report (JSON fallback).",
            )
        return

    if response.status == AnalysisStatus.FAILED:
        await update.message.reply_text(
            f"❌ Analysis failed:\n{response.message}"
        )

async def execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_whitelisted(user_id):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /execute job_id")
        return

    job_id = context.args[0]

    await update.message.reply_text("⏳ Executing trader proposal...")

    response = execute_trader_proposal(user_id, job_id)
    logger.info(f"Execute response for user {user_id}, job {job_id}: {response}")

    if not response.get("success"):
        error_msg = response.get("error", "Unknown error")
        await update.message.reply_text(f"❌ Execution failed:\n{error_msg}")
        return

    # Format execution results
    total = response.get("total_proposals", 0)
    executed = response.get("executed", 0)
    failed = response.get("failed", 0)
    
    results_summary = (
        f"✅ *Execution Completed*\n\n"
        f"Total Proposals: {total}\n"
        f"Successfully Executed: {executed}\n"
        f"Failed: {failed}\n\n"
    )

    if response.get("results"):
        results_json = json.dumps(response["results"], indent=2)
        results_summary += f"*Results:*\n```json\n{results_json[:1000]}\n```\n"

    if response.get("errors"):
        errors_json = json.dumps(response["errors"], indent=2)
        results_summary += f"\n⚠️ *Errors:*\n```json\n{errors_json[:500]}\n```"

    await update.message.reply_text(results_summary, parse_mode="Markdown")


# --------------------------------------------------
# App
# --------------------------------------------------
def main():
    logger.info("INFO: Starting Telegram bot... {}".format(BOT_TOKEN))
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("execute", execute))

    logger.info("🚀 Telegram bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
