import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Meta Graph API ---
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
META_API_VERSION = "v21.0"
META_API_BASE = f"https://graph.facebook.com/{META_API_VERSION}"

# --- Scheduler ---
# Times the bot posts each day in HH:MM 24h format, comma-separated
POST_TIMES = os.getenv("POST_TIMES", "09:00,13:00,18:00").split(",")
# How often to poll for new comments (minutes)
COMMENT_CHECK_INTERVAL = int(os.getenv("COMMENT_CHECK_INTERVAL", "30"))

# --- Business context passed to Claude ---
BUSINESS_NAME = "Water Store OS"
BUSINESS_WEBSITE = "waterstoreos.ca"
BUSINESS_DESCRIPTION = """
We're a water specialty store in Ontario. We sell water filtration systems,
reverse osmosis systems, water softeners, UV purifiers, and offer home water
delivery services. Our customers care about clean, healthy water for their families.
"""

# Content themes Claude rotates through to keep the feed varied
CONTENT_THEMES = [
    "product spotlight",
    "health and hydration tip",
    "water quality education",
    "seasonal promotion",
    "customer lifestyle",
    "behind the scenes",
    "FAQ or common water misconception",
]

DATABASE_URL = "sqlite:///./data/bot.db"
IMAGE_SAVE_DIR = "./data/images"

# When True, content is generated and saved locally but nothing is posted to Meta.
# Useful for testing the AI pipeline without touching real social accounts.
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
