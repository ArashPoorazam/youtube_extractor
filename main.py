import os
import logging
import requests
from telegram import Update
from telegram.error import NetworkError
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    configure()
    API_KEY = os.getenv("API_KEY")
    TELEGRAM_PROXY = os.getenv("TELEGRAM_PROXY")

    if not API_KEY:
        logger.error("API_KEY not found. Ensure you have a .env file with API_KEY=<YOUR_BOT_TOKEN>")
        return

    # --- Initialize bot application ---
    app = Application.builder().token(API_KEY).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, url_handler))
    
    app.add_error_handler(error_handler)

    # Polling...
    try:
        logger.info("Bot starts polling...")
        app.run_polling(poll_interval=3)
    except NetworkError as e:
        logger.error(f"Network Error during polling: {e}")
        logger.error("This often means the proxy connection failed during the main application bootstrap.")
    except Exception as e:
        logger.error(f"General Error: {e}")


def configure():
    load_dotenv()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /start command. Replying to user.")
    await update.message.reply_text("Hello! Send me a YouTube link to extract its audio.")

async def url_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    logger.info(f"Received text: {text}")
    await update.message.reply_text(
        f"I received your message: '{text}'"
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling an update:", exc_info=context.error)


if __name__ == "__main__":
    main()