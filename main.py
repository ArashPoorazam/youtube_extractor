import os
import logging
from telegram.error import NetworkError
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Imported files
from handler import *


# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    configure()
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        logger.error("API_KEY not found. Ensure you have a .env file with API_KEY=<YOUR_BOT_TOKEN>")
        return

    # --- Initialize bot application ---
    app = Application.builder().token(API_KEY).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    app.add_error_handler(error_handler)

    # Polling...
    try:
        logger.info("Bot starts polling...")
        app.run_polling(poll_interval=3)
    except NetworkError as e:
        logger.error(f"Network Error during polling: {e}")
    except Exception as e:
        logger.error(f"General Error: {e}")


def configure():
    load_dotenv()


if __name__ == "__main__":
    main()