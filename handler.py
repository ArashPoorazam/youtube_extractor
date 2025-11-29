from main import logger
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CallbackContext


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! Send me a YouTube link to extract its audio.")


async def url_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(
        f"I received your message: '{text}'"
    )


async def buttons(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("Option 1"), KeyboardButton("Option2")],
        [KeyboardButton("Go Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(text="Choose", reply_markup=reply_markup)


async def go_back(update: Update, context: CallbackContext):
    await update.message.reply_text("Went back")



async def handle_messages(update: Update, context: CallbackContext):
    text = update.message.text

    match text:
        case "Go Back":
            await go_back(update, context)
        case _:
            await url_handler(update, context)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling an update:", exc_info=context.error)