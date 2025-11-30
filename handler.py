import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CallbackContext

# Import Files
from youtube_extraction import YoutubeVideo

logger = logging.getLogger(__name__)


# Download and send files with guaranteed cleanup
async def send_and_clean_file(update: Update, context: CallbackContext, download_func, file_type: str):
    """Handles download, sending, and required file cleanup."""
    
    # 1. Retrieve the link from user_data
    link = context.user_data.get('video_link')
    if not link:
        await update.message.reply_text("❌ لطفا اول لینک ویدیو را بفرستید.")
        return

    # 2. Initialize video object and download
    try:
        video = YoutubeVideo(link)
        await update.message.reply_text(f"⏳ لطفا منتظر بمانید، در حال دانلود... {file_type}...")
        
        # Call the specific download method
        path = download_func(video)
        
        if path:
            if file_type == "Audio":
                await update.message.reply_audio(path)
            elif file_type.startswith("Video"):
                await update.message.reply_video(path)
            
            await update.message.reply_text(f"{file_type} با موفقت ارسال شد!")
        else:
            await update.message.reply_text(f"{file_type} برای این ویدیو پیدا نشد...")

    except Exception as e:
        logger.error(f"Error during {file_type} processing: {e}", exc_info=True)
        await update.message.reply_text(f"خطایی هنگام پردازش رخ داد، دوباره تلاش کنید. {file_type}")

    # 3. Ensure file deletion 
    finally:
        if 'path' in locals() and path and os.path.exists(path):
            try:
                os.remove(path)
                logger.info(f"Cleaned up file: {path}")
            except OSError as e:
                logger.error(f"Error deleting file {path}: {e}")


### commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    logger.info(f"User {update.effective_user.id} started the bot. user_data cleared.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! Send me a YouTube link to extract its audio, video, or subtitles.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a YouTube link and use the buttons to download content.")

async def creator_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This bot was created by an enthusiastic developer!")


### buttons
async def link_buttons(update: Update, context: CallbackContext, link: str):
    link = context.user_data.get('video_link')
    if not link:
        await update.message.reply_text("❌ لطفا اول لینک ویدیو را بفرستید.")
        return
    
    video = YoutubeVideo(link)

    keyboard = [
        [KeyboardButton("🎥 Video"), KeyboardButton("🔊 Audio")],
        [KeyboardButton("🈯 Subtitle")],
        [KeyboardButton("Go Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(text=f"{video.title}\n\nلینک: {link}", reply_markup=reply_markup)
    await update.message.reply_text(text="چه کاری میتونم براتون انجان بدم؟ 😁", reply_markup=reply_markup)


async def video_q_buttons(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("🎥 144 P"), KeyboardButton("🎥 360 P")],
        [KeyboardButton("🎥 720 P"), KeyboardButton("🎥 1080 P")],
        [KeyboardButton("Go Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(text="با چه کیفیتی میخواید دانلود کنید؟", reply_markup=reply_markup)


# subtitle
async def sub_choose(update: Update, context: CallbackContext):
    link = context.user_data.get('video_link')
    if not link:
        await update.message.reply_text("❌ لطفا اول لینک ویدیو را بفرستید.")
        return

    keyboard = [
        [KeyboardButton("🇺🇸 English"), KeyboardButton("🇷🇺 Russia")],
        [KeyboardButton("Go Back")]
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(text="زیر نویس به چه زبانی باشد؟", reply_markup=reply_markup)


async def text_en(update: Update, context: CallbackContext):
    link = context.user_data.get('video_link')
    if not link:
        await update.message.reply_text("❌ لطفا اول لینک ویدیو را بفرستید.")
        return

    try:
        video = YoutubeVideo(link)
        caption = video.get_en_subtitles()
        if caption:
            await update.message.reply_text(caption)
        else:
            await update.message.reply_text("زیر نویسی برای این زبان یافت نشد.")
    except Exception as e:
        logger.error(f"Error getting English subtitles: {e}")
        await update.message.reply_text("خطایی هنگام پردازش رخ داد دوباره تلاش کنید.")

async def text_ru(update: Update, context: CallbackContext):
    link = context.user_data.get('video_link')
    if not link:
        await update.message.reply_text("❌ لطفا اول لینک ویدیو را بفرستید.")
        return
        
    try:
        video = YoutubeVideo(link)
        caption = video.get_ru_subtitles()
        if caption:
            await update.message.reply_text(caption)
        else:
            await update.message.reply_text("زیر نویسی برای این زبان یافت نشد.")
    except Exception as e:
        logger.error(f"Error getting Russian subtitles: {e}")
        await update.message.reply_text("خطایی هنگام پردازش رخ داد دوباره تلاش کنید.")


# Go back
async def go_back(update: Update, context: CallbackContext): 
    await update.message.reply_text("🏡 بازگشت.", reply_markup=ReplyKeyboardRemove())


### chats
async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    logger.debug(f"Handling unrecognised text: {text}")
    await update.message.reply_text(
        f"Aurora is coming soon...\nReceived: {text}"
    )


# --- Main Message Handler ---
async def handle_messages(update: Update, context: CallbackContext):
    text = update.message.text
    logger.debug(f"Received message: {text}")
    
    if text.startswith("https://youtu.be/") or text.startswith("https://youtube.com/"):
        # Store the link in user_data
        context.user_data['video_link'] = text 
        logger.info(f"New video link stored in user_data: {text}")
        await link_buttons(update, context, text)
        return

    match text:
        case "Go Back":
            await go_back(update, context) 
        case "🈯 Subtitle":
            await sub_choose(update, context)
        case "🎥 Video":
            await video_q_buttons(update, context)
        case "🔊 Audio":
            await send_and_clean_file(update, context, YoutubeVideo.download_audio, "Audio")
        case "🎥 144 P":
            await send_and_clean_file(update, context, YoutubeVideo.download_video_144, "Video 144p")
        case "🎥 360 P":
            await send_and_clean_file(update, context, YoutubeVideo.download_video_360, "Video 360p")
        case "🎥 720 P":
            await send_and_clean_file(update, context, YoutubeVideo.download_video_720, "Video 720p")
        case "🎥 1080 P":
            await send_and_clean_file(update, context, YoutubeVideo.download_video_1080, "Video 1080p")
        case "🇺🇸 English":
            await text_en(update, context)
        case "🇷🇺 Russia":
            await text_ru(update, context)
        case _:
            await chat_handler(update, context)


# Errors
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling an update:", exc_info=context.error)