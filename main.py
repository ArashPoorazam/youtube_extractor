import os
import logging
from telegram.error import NetworkError
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Import Files
from handler import start_command, help_command, creator_command, handle_messages, error_handler, export_users
from database import init_db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    init_db()
    configure()
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        logger.error("API_KEY not found. Ensure you have a .env file with API_KEY=<YOUR_BOT_TOKEN>")
        return

    # --- Initialize bot application ---
    app = Application.builder().token(API_KEY).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("creator", creator_command))
    app.add_handler(CommandHandler("export", export_users))
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