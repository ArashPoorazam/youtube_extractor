import os # Required for file cleanup
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CallbackContext

# Import the class for video operations
from youtube_extraction import YoutubeVideo


# Fix for Circular Dependency: Define a logger locally
logger = logging.getLogger(__name__)


# --- Utility to download and send files with guaranteed cleanup ---
async def send_and_clean_file(update: Update, context: CallbackContext, download_func, file_type: str):
    """Handles download, sending, and required file cleanup."""
    
    # 1. Retrieve the link from user_data
    link = context.user_data.get('video_link')
    if not link:
        await update.message.reply_text("❌ Error: Please send a YouTube link first!")
        return

    # 2. Initialize video object and download
    try:
        video = YoutubeVideo(link)
        await update.message.reply_text(f"⏳ Please Wait... Downloading {file_type}...")
        
        # Call the specific download method (now synchronous, as pytube methods are)
        path = download_func(video)
        
        if path:
            if file_type == "Audio":
                await update.message.reply_audio(path)
            elif file_type.startswith("Video"):
                await update.message.reply_video(path)
            
            await update.message.reply_text(f"{file_type} sent successfully!")
        else:
            await update.message.reply_text(f"{file_type} Not Found for this video!")

    except Exception as e:
        logger.error(f"Error during {file_type} processing: {e}", exc_info=True)
        await update.message.reply_text(f"An error occurred while processing the {file_type}. Please try a different video.")

    finally:
        # 3. CRITICAL FIX: Ensure file deletion (Resource Leak Fix)
        if 'path' in locals() and path and os.path.exists(path):
            try:
                os.remove(path)
                logger.info(f"Cleaned up file: {path}")
            except OSError as e:
                logger.error(f"Error deleting file {path}: {e}")

# --- Utility for link buttons, used in multiple places ---
async def link_buttons(update: Update, context: CallbackContext, link: str):
    keyboard = [
        [KeyboardButton("🎥 Video"), KeyboardButton("🔊 Audio")],
        [KeyboardButton("🈯 Subtitle")],
        [KeyboardButton("Go Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(text=f"Selected video: {link}", reply_markup=reply_markup)
    await update.message.reply_text(text="What can I do for you?", reply_markup=reply_markup)


# --- Command Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear user data on start just in case
    context.user_data.clear()
    logger.info(f"User {update.effective_user.id} started the bot. user_data cleared.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! Send me a YouTube link to extract its audio, video, or subtitles.")

# Placeholder commands
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a YouTube link and use the buttons to download content.")

async def creator_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This bot was created by an enthusiastic developer!")


# --- Button Handlers (Simplified and integrated with cleanup utility) ---

async def video_q_buttons(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("🎥 144 P"), KeyboardButton("🎥 360 P")],
        [KeyboardButton("🎥 720 P"), KeyboardButton("🎥 1080 P")],
        [KeyboardButton("Go Back")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(text="Choose a video quality:", reply_markup=reply_markup)


async def sub_choose(update: Update, context: CallbackContext):
    link = context.user_data.get('video_link')
    if not link:
        await update.message.reply_text("❌ Error: Please send a YouTube link first!")
        return

    try:
        video = YoutubeVideo(link)
        logger.info(f"Checking subtitles for video: {link}")
        await update.message.reply_text("⏳ Checking for subtitles...")
        
        # Check subs (synchronous call)
        en, ru = video.check_subs()
        
        keyboard = []
        if en:
            keyboard.append(KeyboardButton("🇺🇸 English"))
        if ru:
            keyboard.append(KeyboardButton("🇷🇺 Russia"))

        if not keyboard:
            await update.message.reply_text("No English or Russian Subtitle Found for this video.")
            return

        # Add the 'Go Back' button row
        keyboard_rows = [keyboard, [KeyboardButton("Go Back")]]
        reply_markup = ReplyKeyboardMarkup(keyboard_rows, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(text="Choose subtitle language:", reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error checking subtitles: {e}")
        await update.message.reply_text("An error occurred while checking for subtitles.")


async def text_en(update: Update, context: CallbackContext):
    link = context.user_data.get('video_link')
    if not link:
        await update.message.reply_text("❌ Error: Please send a YouTube link first!")
        return

    try:
        video = YoutubeVideo(link)
        caption = video.get_en_subtitles()
        if caption:
            await update.message.reply_text(caption)
        else:
            await update.message.reply_text("No English subtitle found.")
    except Exception as e:
        logger.error(f"Error getting English subtitles: {e}")
        await update.message.reply_text("An error occurred while fetching subtitles.")

async def text_ru(update: Update, context: CallbackContext):
    link = context.user_data.get('video_link')
    if not link:
        await update.message.reply_text("❌ Error: Please send a YouTube link first!")
        return
        
    try:
        video = YoutubeVideo(link)
        caption = video.get_ru_subtitles()
        if caption:
            await update.message.reply_text(caption)
        else:
            await update.message.reply_text("No Russian subtitle found.")
    except Exception as e:
        logger.error(f"Error getting Russian subtitles: {e}")
        await update.message.reply_text("An error occurred while fetching subtitles.")

async def go_back(update: Update, context: CallbackContext):
    # FIX: Retrieve the correct link from user_data
    link = context.user_data.get('video_link', "No video selected.") 
    
    await update.message.reply_text("Went back")
    await link_buttons(update, context, link)


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
    
    # 1. New Link Received (Store State)
    if text.startswith("https://youtu.be/") or text.startswith("https://youtube.com/"):
        # CRITICAL FIX 2: Store the link in user_data
        context.user_data['video_link'] = text 
        logger.info(f"New video link stored in user_data: {text}")
        await link_buttons(update, context, text)
        return

    # 2. Button Press Received (Use State)
    # The 'video' object is now retrieved/created inside the helper functions, 
    # fixing the UnboundLocalError.
    match text:
        case "Go Back":
            await go_back(update, context) # Link retrieved from user_data inside go_back
        case "🈯 Subtitle":
            await sub_choose(update, context)
        case "🎥 Video":
            await video_q_buttons(update, context)
        case "🔊 Audio":
            # Use the generalized function with the specific download method
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
        # Assuming all subtitle output buttons return to the main menu for now
        case "📘 Text" | "📕 PDF" | "📗 Word" | "📙 Online":
             await go_back(update, context)
        case _:
            link = context.user_data.get('video_link')
            logger.warning(f"Unmatched text received: '{text}'. Current link in user_data: {link}")
            await chat_handler(update, context)


# Errors
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling an update:", exc_info=context.error)