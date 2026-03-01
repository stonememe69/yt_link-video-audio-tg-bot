#!/usr/bin/env python3
"""
Telegram Bot for downloading YouTube videos and audio
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import asyncio
from pathlib import Path

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Download directory
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

class YouTubeDownloader:
    """Handles YouTube video/audio downloads"""
    
    @staticmethod
    def get_video_info(url: str) -> dict:
        """Get video information without downloading"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            # Anti-bot bypass options
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
            }
    
    @staticmethod
    async def download_video(url: str, output_path: str) -> str:
        """Download video in best quality"""
        ydl_opts = {
            'format': 'best[ext=mp4][height<=720]/best[ext=mp4]/best',
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': False,
            # Anti-bot bypass options
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        loop = asyncio.get_event_loop()
        
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        
        await loop.run_in_executor(None, download)
        return output_path
    
    @staticmethod
    async def download_audio(url: str, output_path: str) -> str:
        """Download audio only in MP3 format"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': False,
            # Anti-bot bypass options
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        loop = asyncio.get_event_loop()
        
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        
        await loop.run_in_executor(None, download)
        # yt-dlp adds .mp3 extension
        return output_path.replace('.%(ext)s', '.mp3')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = (
        "🎥 *YouTube Downloader Bot* 🎵\n\n"
        "Welcome! I can help you download YouTube videos and audio.\n\n"
        "*Commands:*\n"
        "• `/video <URL>` - Download video\n"
        "• `/audio <URL>` - Download audio (MP3)\n"
        "• `/info <URL>` - Get video information\n"
        "• `/help` - Show this help message\n\n"
        "*Or simply send me a YouTube URL!*\n\n"
        "Example: `/video https://youtube.com/watch?v=...`"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await start(update, context)


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get video information"""
    if not context.args:
        await update.message.reply_text("Please provide a YouTube URL.\nExample: `/info https://youtube.com/watch?v=...`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    
    await update.message.reply_text("🔍 Fetching video information...")
    
    try:
        info = YouTubeDownloader.get_video_info(url)
        
        duration_mins = info['duration'] // 60
        duration_secs = info['duration'] % 60
        
        info_message = (
            f"📹 *Video Information*\n\n"
            f"*Title:* {info['title']}\n"
            f"*Uploader:* {info['uploader']}\n"
            f"*Duration:* {duration_mins}:{duration_secs:02d}\n"
            f"*Views:* {info['view_count']:,}\n\n"
            f"Use `/video {url}` to download video\n"
            f"Use `/audio {url}` to download audio"
        )
        
        await update.message.reply_text(info_message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download video"""
    if not context.args:
        await update.message.reply_text("Please provide a YouTube URL.\nExample: `/video https://youtube.com/watch?v=...`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    
    status_message = await update.message.reply_text("⏬ Starting video download...")
    
    try:
        # Get video info first
        info = YouTubeDownloader.get_video_info(url)
        await status_message.edit_text(f"⏬ Downloading: *{info['title']}*", parse_mode='Markdown')
        
        # Generate output filename
        safe_title = "".join(c for c in info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        output_path = str(DOWNLOAD_DIR / f"{safe_title[:50]}.%(ext)s")
        
        # Download video
        downloaded_file = await YouTubeDownloader.download_video(url, output_path)
        
        await status_message.edit_text("📤 Uploading video to Telegram...")
        
        # Find the actual downloaded file
        possible_extensions = ['.mp4', '.mkv', '.webm']
        actual_file = None
        for ext in possible_extensions:
            test_file = output_path.replace('.%(ext)s', ext)
            if os.path.exists(test_file):
                actual_file = test_file
                break
        
        if actual_file and os.path.exists(actual_file):
            file_size = os.path.getsize(actual_file)
            
            # Telegram has a 50MB limit for bots
            if file_size > 50 * 1024 * 1024:
                await status_message.edit_text("❌ Video is too large (>50MB) to send via Telegram bot.")
                os.remove(actual_file)
                return
            
            # Send video
            with open(actual_file, 'rb') as video_file:
                await update.message.reply_video(
                    video=video_file,
                    caption=f"🎥 {info['title']}",
                    supports_streaming=True
                )
            
            await status_message.edit_text("✅ Video downloaded and sent successfully!")
            
            # Clean up
            os.remove(actual_file)
        else:
            await status_message.edit_text("❌ Error: Downloaded file not found.")
        
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        await status_message.edit_text(f"❌ Error: {str(e)}")


async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download audio"""
    if not context.args:
        await update.message.reply_text("Please provide a YouTube URL.\nExample: `/audio https://youtube.com/watch?v=...`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    
    status_message = await update.message.reply_text("🎵 Starting audio download...")
    
    try:
        # Get video info first
        info = YouTubeDownloader.get_video_info(url)
        await status_message.edit_text(f"🎵 Downloading: *{info['title']}*", parse_mode='Markdown')
        
        # Generate output filename
        safe_title = "".join(c for c in info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        output_path = str(DOWNLOAD_DIR / f"{safe_title[:50]}.%(ext)s")
        
        # Download audio
        downloaded_file = await YouTubeDownloader.download_audio(url, output_path)
        
        await status_message.edit_text("📤 Uploading audio to Telegram...")
        
        if os.path.exists(downloaded_file):
            file_size = os.path.getsize(downloaded_file)
            
            # Telegram has a 50MB limit for bots
            if file_size > 50 * 1024 * 1024:
                await status_message.edit_text("❌ Audio is too large (>50MB) to send via Telegram bot.")
                os.remove(downloaded_file)
                return
            
            # Send audio
            with open(downloaded_file, 'rb') as audio_file:
                await update.message.reply_audio(
                    audio=audio_file,
                    caption=f"🎵 {info['title']}",
                    title=info['title'],
                    performer=info['uploader']
                )
            
            await status_message.edit_text("✅ Audio downloaded and sent successfully!")
            
            # Clean up
            os.remove(downloaded_file)
        else:
            await status_message.edit_text("❌ Error: Downloaded file not found.")
        
    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        await status_message.edit_text(f"❌ Error: {str(e)}")


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle URLs sent directly without command"""
    text = update.message.text
    
    # Check if it's a YouTube URL
    if 'youtube.com' in text or 'youtu.be' in text:
        # Ask user what they want to download
        keyboard_message = (
            "What would you like to download?\n\n"
            "Use:\n"
            f"• `/video {text}` for video\n"
            f"• `/audio {text}` for audio\n"
            f"• `/info {text}` for information"
        )
        await update.message.reply_text(keyboard_message, parse_mode='Markdown')
    else:
        await update.message.reply_text("Please send a valid YouTube URL.")


def main() -> None:
    """Start the bot."""
    # Get token from environment variable
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        print("\nTo set your token:")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return
    
    # Create the Application
    application = Application.builder().token(TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("video", video_command))
    application.add_handler(CommandHandler("audio", audio_command))
    
    # Register message handler for URLs
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    # Start the Bot
    print("🤖 Bot is starting...")
    print("✅ Bot is running! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
