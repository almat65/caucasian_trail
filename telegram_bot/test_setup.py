#!/usr/bin/env python3
"""
Test script to verify GitHub and Telegram tokens work
Run this before starting the bot to check your setup
"""

import os
import sys

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded .env file")
except ImportError:
    print("⚠ python-dotenv not installed, using environment variables only")

# Check tokens
github_token = os.environ.get('GITHUB_TOKEN')
telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')

print("\n=== Checking Configuration ===\n")

errors = []

# Check GitHub token
if not github_token:
    print("❌ GITHUB_TOKEN not set")
    errors.append("GITHUB_TOKEN missing")
elif len(github_token) < 20:
    print("❌ GITHUB_TOKEN looks invalid (too short)")
    errors.append("GITHUB_TOKEN invalid")
else:
    print(f"✓ GITHUB_TOKEN found ({github_token[:8]}...)")

# Check Telegram token
if not telegram_token:
    print("❌ TELEGRAM_BOT_TOKEN not set")
    errors.append("TELEGRAM_BOT_TOKEN missing")
elif ':' not in telegram_token:
    print("❌ TELEGRAM_BOT_TOKEN looks invalid (should contain ':')")
    errors.append("TELEGRAM_BOT_TOKEN invalid")
else:
    print(f"✓ TELEGRAM_BOT_TOKEN found ({telegram_token.split(':')[0]}:...)")

# Test GitHub API connection
if github_token and len(github_token) >= 20:
    print("\n=== Testing GitHub API ===\n")
    try:
        import requests
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get('https://api.github.com/user', headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ GitHub API working! Authenticated as: {user_data['login']}")

            # Check repo access
            repo_response = requests.get(
                'https://api.github.com/repos/almat65/caucasian_trail',
                headers=headers
            )
            if repo_response.status_code == 200:
                print("✓ Repository access confirmed")
            else:
                print(f"⚠ Cannot access repository (status {repo_response.status_code})")
                errors.append("No repository access")
        else:
            print(f"❌ GitHub API error: {response.status_code}")
            print(f"   Response: {response.json()}")
            errors.append("GitHub API authentication failed")
    except Exception as e:
        print(f"❌ Error testing GitHub API: {e}")
        errors.append(f"GitHub test failed: {e}")

# Test Telegram Bot API
if telegram_token and ':' in telegram_token:
    print("\n=== Testing Telegram Bot API ===\n")
    try:
        import requests
        response = requests.get(f'https://api.telegram.org/bot{telegram_token}/getMe')

        if response.status_code == 200:
            bot_data = response.json()
            if bot_data['ok']:
                print(f"✓ Telegram Bot API working!")
                print(f"  Bot name: {bot_data['result']['first_name']}")
                print(f"  Bot username: @{bot_data['result']['username']}")
            else:
                print(f"❌ Telegram API returned error: {bot_data}")
                errors.append("Telegram API error")
        else:
            print(f"❌ Telegram API error: {response.status_code}")
            errors.append("Telegram authentication failed")
    except Exception as e:
        print(f"❌ Error testing Telegram API: {e}")
        errors.append(f"Telegram test failed: {e}")

# Summary
print("\n=== Summary ===\n")
if errors:
    print(f"❌ Found {len(errors)} error(s):")
    for error in errors:
        print(f"   - {error}")
    print("\nPlease fix these issues before running the bot.")
    sys.exit(1)
else:
    print("✅ All checks passed! You're ready to run the bot.")
    print("\nRun: python position_updater.py")
    sys.exit(0)
