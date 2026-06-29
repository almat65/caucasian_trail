"""
GitHub API operations for the Caucasian Trail Telegram Bot
"""

import json
import base64
import requests
from config import GITHUB_TOKEN, GITHUB_REPO, FILE_PATH


def fetch_geojson_from_github():
    """Fetch current geojson file from GitHub"""
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    content = response.json()
    # Content is base64 encoded
    file_content = base64.b64decode(content['content']).decode('utf-8')

    return json.loads(file_content), content['sha']  # Return both content and SHA for updating


def update_geojson_on_github(geojson_data, sha, commit_message=None, current_position_data=None):
    """Update geojson file on GitHub with optional custom commit message"""
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Encode content
    content = json.dumps(geojson_data, ensure_ascii=False, indent=2)
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

    # Prepare commit
    if commit_message is None:
        day = current_position_data.get("day", "?") if current_position_data else "?"
        commit_message = f'Bot: Add Day {day} position'

    data = {
        'message': commit_message,
        'content': encoded_content,
        'sha': sha,
        'branch': 'master'
    }

    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()


async def upload_photo_to_github(photo_bytes, filename, commit_message='Bot: Upload photo'):
    """Upload a photo file to GitHub assets/photos/ folder"""
    file_path = f'assets/photos/{filename}'
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Encode photo as base64
    encoded_content = base64.b64encode(photo_bytes).decode('utf-8')

    # Check if file already exists (to get SHA if updating)
    check_response = requests.get(url, headers=headers)
    sha = None
    if check_response.status_code == 200:
        sha = check_response.json()['sha']

    # Prepare commit
    data = {
        'message': commit_message,
        'content': encoded_content,
        'branch': 'master'
    }

    if sha:
        data['sha'] = sha  # Update existing file

    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()
