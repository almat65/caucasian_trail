# Quick Start Guide

## 5-Minute Setup

### 1. Get GitHub Token
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "Trail Bot"
4. Check: ✅ **repo** (full control)
5. Generate and **COPY THE TOKEN**

### 2. Get Telegram Token
1. Open Telegram → Search: `@BotFather`
2. Send: `/newbot`
3. Follow prompts
4. **COPY THE TOKEN**

### 3. Setup Bot
```bash
cd telegram_bot

# Create virtual environment (keeps packages isolated)
python -m venv venv

# Activate it
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install packages
pip install -r requirements.txt

# Setup config
cp .env.example .env
# Edit .env and paste your tokens

# Test and run
python test_setup.py  # Verify setup
python position_updater.py  # Start bot!
```

### 4. Use Bot
1. Open your bot in Telegram
2. Send: `/start`
3. Answer questions
4. Done! GitHub updates automatically

## What Happens?
```
You → Telegram Bot → GitHub API → GitHub repo updated → GitHub Pages deploys → Map updated
```

All automatic! No manual git commands needed.

## Tips
- Keep bot running while hiking (needs internet)
- Or run on a VPS/cloud server for 24/7 availability
- Bot handles ALL git operations for you
- You just send messages to update the map!
