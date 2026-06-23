# Caucasian Trail Telegram Bot

Telegram bot to automatically update position data on the trail map.

## Setup

### 1. Create GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name: "Caucasian Trail Bot"
4. Select scopes: **repo** (full control of private repositories)
5. Click "Generate token"
6. **COPY THE TOKEN** - you won't see it again!

### 2. Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Follow instructions to name your bot
4. **COPY THE TOKEN** BotFather gives you

### 3. Install Dependencies

```bash
cd telegram_bot
pip install -r requirements.txt
```

### 4. Set Environment Variables

**Recommended: Use .env file**

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your tokens:
   ```
   GITHUB_TOKEN=ghp_your_actual_token_here
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

**Alternative: Set in terminal session**

**Windows (PowerShell):**
```powershell
$env:GITHUB_TOKEN="your_github_token_here"
$env:TELEGRAM_BOT_TOKEN="your_telegram_token_here"
```

**Linux/Mac:**
```bash
export GITHUB_TOKEN="your_github_token_here"
export TELEGRAM_BOT_TOKEN="your_telegram_token_here"
```

### 5. Run the Bot

**First, test your setup:**
```bash
python test_setup.py
```

This will verify your tokens are working correctly.

**If all tests pass, start the bot:**
```bash
python position_updater.py
```

The bot will start and wait for messages!

## Usage

1. Open Telegram and find your bot
2. Send `/start`
3. Answer the questions:
   - Day number (e.g., 9)
   - Date (YYYY-MM-DD format, e.g., 2026-06-18)
   - Location name (e.g., Харбук)
   - Distance in km (e.g., 8.5)
   - Elevation gain in m (e.g., 550)
   - Accommodation type (tent/glamping/guesthouse/hotel)
   - Location (send via Telegram's location feature or enter lat/long manually)
   - YouTube URL (or 'skip')
   - Notes (or 'skip')
   - Photo filenames (or 'skip')

4. Bot will update GitHub automatically!
5. Map updates in ~1 minute via GitHub Pages

## Commands

- `/start` - Begin adding a new position
- `/cancel` - Cancel current operation

## Hosting Options

### Option 1: Run on Your Computer
Just keep the script running while hiking (need internet)

### Option 2: VPS/Cloud Server
- DigitalOcean Droplet ($5/month)
- AWS EC2 free tier
- Google Cloud free tier
- Heroku

### Option 3: Raspberry Pi
Run at home 24/7

## Security Notes

- **NEVER commit tokens to git!**
- Keep tokens in environment variables only
- Consider using `.env` file (add to `.gitignore`)
- Tokens give full access to your repo - keep them secret!

## Troubleshooting

**Bot doesn't respond:**
- Check if script is running
- Verify tokens are set correctly
- Check internet connection

**GitHub update fails:**
- Verify GitHub token has `repo` permissions
- Check if repository name is correct
- Ensure you have write access to the repo

**Invalid date/coordinates:**
- Use exact formats requested
- Date: YYYY-MM-DD
- Coordinates: decimal degrees (e.g., 42.0665056)
