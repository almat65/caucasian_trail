"""
Data models for the Caucasian Trail Telegram Bot
"""


class PositionData:
    """Store position data during conversation"""
    def __init__(self):
        self.data = {}
        self.update_id = None
        self.uploaded_photos = []  # Track uploaded photo filenames
        self.photo_count = 0  # Counter for naming photos

    def reset(self):
        self.data = {}
        self.update_id = None
        self.uploaded_photos = []
        self.photo_count = 0


# Global storage for current position being added
current_position = PositionData()
