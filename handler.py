import re
from main import logger
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CallbackContext

# Imported files
from youtube_extraction import *


### Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! Send me a YouTube link to extract its audio.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def creator_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


### Buttons
async def link_buttons(update: Update, context: CallbackContext, link: str):
    keyboard = [
        [KeyboardButton("🎥 Video"), KeyboardButton("🔊 Audio")],
        [KeyboardButton("🈯 Subtitle")],
        [KeyboardButton("Go Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(text=f"{link}", reply_markup=reply_markup)
    await update.message.reply_text(text="what can I do for you?", reply_markup=reply_markup)


# Video
async def video_q_buttons(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("🎥 144 P"), KeyboardButton("🎥 360 P")],
        [KeyboardButton("🎥 720 P"), KeyboardButton("🎥 1080 P")],
        [KeyboardButton("Go Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(text="Choose", reply_markup=reply_markup)


async def send_video_144(update: Update, context: CallbackContext, video: YoutubeVideo):
    await update.message.reply_text("⏳ Please Wait...")
    path = await video.download_video_144()
    await update.message.delete()

    if path:
        await update.message.reply_video(path)
        await update.message.reply_text("Video sent!")
    else:
        await update.message.reply_text("Video Not Found!")


async def send_video_360(update: Update, context: CallbackContext, video: YoutubeVideo):
    await update.message.reply_text("⏳ Please Wait...")
    path = await video.download_video_360()
    await update.message.delete()

    if path:
        await update.message.reply_video(path)
        await update.message.reply_text("Video sent!")
    else:
        await update.message.reply_text("Video Not Found!")



async def send_video_720(update: Update, context: CallbackContext, video: YoutubeVideo):
    await update.message.reply_text("⏳ Please Wait...")
    path = await video.download_video_720()
    await update.message.delete()

    if path:
        await update.message.reply_video(path)
        await update.message.reply_text("Video sent!")
    else:
        await update.message.reply_text("Video Not Found!")


async def send_video_1080(update: Update, context: CallbackContext, video: YoutubeVideo):
    await update.message.reply_text("⏳ Please Wait...")
    path = await video.download_video_1080()
    await update.message.delete()

    if path:
        await update.message.reply_video(path)
        await update.message.reply_text("Video sent!")
    else:
        await update.message.reply_text("Video Not Found!")


# Subtitle
async def sub_choose(update: Update, context: CallbackContext, video: YoutubeVideo):
    await update.message.reply_text("⏳ Please Wait...")
    en, ru = await video.check_subs()
    await update.message.delete()

    if en and ru:
        keyboard = [
            [KeyboardButton("🇺🇸 English"), KeyboardButton("🇷🇺 Russia")],
            [KeyboardButton("Go Back")]
        ]
    elif en:
        keyboard = [
            [KeyboardButton("🇺🇸 English")],
            [KeyboardButton("Go Back")]
        ]
    elif ru:
        keyboard = [
            [KeyboardButton("🇷🇺 Russia")],
            [KeyboardButton("Go Back")]
        ]
    else:
        await update.message.reply_text("No Subtitle Found...")

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(text="Choose", reply_markup=reply_markup)


async def text_en(update: Update, context: CallbackContext, video: YoutubeVideo):
    caption = video.get_en_subtitles()
    if caption:
        await update.message.reply_text(caption)
    else:
        await update.message.reply_text("No English subtitle found.")


async def text_ru(update: Update, context: CallbackContext, video: YoutubeVideo):
    caption = video.get_ru_subtitles()
    if caption:
        await update.message.reply_text(caption)
    else:
        await update.message.reply_text("No Russian subtitle found.")


async def sub_output_buttons(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("📘 Text"), KeyboardButton("📕 PDF")],
        [KeyboardButton("📗 Word"), KeyboardButton("📙 Online")],
        [KeyboardButton("Go Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(text="Choose", reply_markup=reply_markup)


# Audio
async def send_audio(update: Update, context: CallbackContext, video: YoutubeVideo):
    await update.message.reply_text("⏳ Please Wait...")
    path = await video.download_audio()
    await update.message.delete()
    if path:
        await update.message.reply_audio(path)
        await update.message.reply_text("Audio Sent!")
    else:
        await update.message.reply_text("Audio Not Found!")


async def go_back(update: Update, context: CallbackContext, link: str):
    await update.message.reply_text("Went back")
    keyboard = [
        [KeyboardButton("🎥 Video"), KeyboardButton("🔊 Audio")],
        [KeyboardButton("🈯 Subtitle")],
        [KeyboardButton("Go Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(text=f"{link}", reply_markup=reply_markup)
    await update.message.reply_text(text="what can I do for you?", reply_markup=reply_markup)


### Messages
async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(
        f"Aurora is comming soon...\nrecived: {text}"
    )


async def handle_messages(update: Update, context: CallbackContext):
    text = update.message.text

    if text.startswith("https://youtu.be/") or text.startswith("https://youtube.com/"):
        youtube_video = YoutubeVideo(text)
        await link_buttons(update, context, text)

    match text:
        case "Go Back":
            await go_back(update, context, text)
        case "🈯 Subtitle":
            await sub_choose(update, context)
        case "🎥 Video":
            await video_q_buttons(update, context)
        case "🔊 Audio":
            await send_audio(update, context, youtube_video)
        case "🎥 144 P":
            await send_video_144(update, context, youtube_video)
        case "🎥 360 P":
            await send_video_360(update, context, youtube_video)
        case "🎥 720 P":
            await send_video_720(update, context, youtube_video)
        case "🎥 1080 P":
            await send_video_1080(update, context, youtube_video)
        case "🇺🇸 English":
            await text_en(update, context, youtube_video)
        case "🇷🇺 Russia":
            await text_ru(update, context, youtube_video)
        # case "📘 Text":
        #     await go_back(update, context, youtube_video)
        # case "📕 PDF":
        #     await go_back(update, context, youtube_video)
        # case "📗 Word":
        #     await go_back(update, context, youtube_video)
        # case "📙 Online":
        #     await go_back(update, context, youtube_video)
        case _:
            await chat_handler(update, context)


# Errors
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling an update:", exc_info=context.error)