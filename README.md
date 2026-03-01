# YouTube Telegram Bot 🎥🎵

A Telegram bot that downloads YouTube videos and audio files directly through Telegram.

## Features

- 🎥 **Download Videos** - Download YouTube videos in best quality (MP4)
- 🎵 **Download Audio** - Extract and download audio as MP3 (192kbps)
- ℹ️ **Video Information** - Get details about videos before downloading
- 📊 **Progress Updates** - Real-time status updates during download
- 🧹 **Auto Cleanup** - Automatically removes files after sending

## Prerequisites

Before running the bot, you need:

1. **Python 3.8+** installed
2. **FFmpeg** installed (required for audio conversion)
3. **A Telegram Bot Token** from [@BotFather](https://t.me/botfather)

### Installing FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## Setup Instructions

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the prompts:
   - Choose a name for your bot (e.g., "My YouTube Downloader")
   - Choose a username (must end in 'bot', e.g., "my_yt_downloader_bot")
4. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or install manually:
pip install python-telegram-bot==21.0.1 yt-dlp==2024.3.10
```

### 3. Set Your Bot Token

**Linux/macOS:**
```bash
export TELEGRAM_BOT_TOKEN='your_bot_token_here'
```

**Windows (Command Prompt):**
```cmd
set TELEGRAM_BOT_TOKEN=your_bot_token_here
```

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN='your_bot_token_here'
```

### 4. Run the Bot

```bash
python youtube_bot.py
```

You should see:
```
🤖 Bot is starting...
✅ Bot is running! Press Ctrl+C to stop.
```

## Usage

### Commands

Open your bot in Telegram and use these commands:

- `/start` - Welcome message and instructions
- `/help` - Show help message
- `/info <URL>` - Get video information
  - Example: `/info https://youtube.com/watch?v=dQw4w9WgXcQ`
- `/video <URL>` - Download video
  - Example: `/video https://youtube.com/watch?v=dQw4w9WgXcQ`
- `/audio <URL>` - Download audio as MP3
  - Example: `/audio https://youtube.com/watch?v=dQw4w9WgXcQ`

### Quick Usage

You can also just send a YouTube URL directly, and the bot will respond with options!

### Example Workflow

1. Send a YouTube URL to the bot:
   ```
   https://youtube.com/watch?v=dQw4w9WgXcQ
   ```

2. Bot suggests commands:
   ```
   What would you like to download?
   
   Use:
   • /video https://... for video
   • /audio https://... for audio
   • /info https://... for information
   ```

3. Choose what you want:
   ```
   /audio https://youtube.com/watch?v=dQw4w9WgXcQ
   ```

4. Bot downloads and sends the file!

## Limitations

- **File Size**: Telegram bots can only send files up to 50MB
- **Download Speed**: Depends on your internet connection and YouTube's servers
- **Format**: Videos are downloaded as MP4, audio as MP3

## Troubleshooting

### "Error: TELEGRAM_BOT_TOKEN environment variable not set"
Make sure you've set the token as shown in step 3 above.

### "Error downloading video"
- Check if the YouTube URL is valid
- Some videos may be age-restricted or geo-blocked
- Try a different video to test

### "Video is too large (>50MB)"
The video exceeds Telegram's 50MB limit. Try:
- Using `/audio` instead to download just the audio
- Finding a shorter/lower quality version

### FFmpeg not found
Make sure FFmpeg is installed and available in your system PATH.

## Project Structure

```
youtube-telegram-bot/
├── youtube_bot.py      # Main bot script
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── downloads/         # Temporary download directory (auto-created)
```

## Advanced Configuration

### Running as a Service (Linux)

Create a systemd service file `/etc/systemd/system/youtube-bot.service`:

```ini
[Unit]
Description=YouTube Telegram Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/bot
Environment="TELEGRAM_BOT_TOKEN=your_token_here"
ExecStart=/usr/bin/python3 /path/to/bot/youtube_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable youtube-bot
sudo systemctl start youtube-bot
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY youtube_bot.py .

CMD ["python", "youtube_bot.py"]
```

Build and run:
```bash
docker build -t youtube-bot .
docker run -e TELEGRAM_BOT_TOKEN='your_token' youtube-bot
```

## Security Notes

- Never share your bot token publicly
- Don't commit the token to version control
- Consider using environment variables or config files (not tracked by git)
- The bot downloads videos temporarily and deletes them after sending

## Contributing

Feel free to fork and improve! Some ideas:
- Add playlist support
- Support for more video platforms
- Quality selection options
- Download progress bars
- User preferences and favorites

## License

MIT License - feel free to use and modify!

## Credits

Built with:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)

## Support

If you encounter any issues:
1. Check the Troubleshooting section above
2. Make sure all dependencies are installed
3. Verify your bot token is correct
4. Check the console output for error messages

---

Made with ❤️ for easy YouTube downloads on Telegram!
