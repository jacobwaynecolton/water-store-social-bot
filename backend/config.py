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
POST_TIMES = os.getenv("POST_TIMES", "09:00,13:00,18:00").split(",")
COMMENT_CHECK_INTERVAL = int(os.getenv("COMMENT_CHECK_INTERVAL", "30"))

# --- Business context ---
BUSINESS_NAME = "The Water Store Owen Sound"
BUSINESS_WEBSITE = "waterstoreos.ca"
BUSINESS_DESCRIPTION = """
The Water Store Owen Sound is an independently owned store at 1555 16th Street East,
Owen Sound, Ontario. In business for 23 years (est. 2003), named Business of the Year
in 2024, and part of The Water Stores Group (16 Ontario locations).

Products and services:
- Reverse osmosis and alkaline drinking water systems
- 8 self-serve U-Fill refill stations (purified RO and alkaline water)
- Water softeners, UV purifiers, air purifiers
- Free water testing and quality analysis
- Hot tubs, swim spas, and saunas
- BBQ grills and pellet smokers (Traeger, Louisiana, Pitboss)
- Hot tub delivery, servicing, and winterization
- Financing available through Financeit

Brand voice: friendly, knowledgeable, no pressure. Community-focused.
Tagline: "Water treatment, hot tub, and BBQ experts for 23 years!"
Hours: 9am–5pm daily. Phone: 519-371-8500.
"""

# How many recent themes to look back when avoiding repeats.
# With 9 themes and 3 posts/day, this ensures a theme isn't reused within ~3 posts.
# Look back this many posts when avoiding theme repeats. 6 posts = ~2 days at 3/day,
# enough that even thematically adjacent topics (e.g. hot tubs + saunas) don't run close together.
THEME_LOOKBACK = 6

# Content themes — covers the full range of what the store sells
CONTENT_THEMES = [
    "drinking water systems (RO or alkaline)",
    "U-Fill refill station",
    "water softeners or water quality problem (staining, odor, hard water)",
    "hot tubs or swim spas",
    "BBQ grills or pellet smokers",
    "saunas",
    "health and hydration tip",
    "free water testing offer",
    "seasonal promotion or local Owen Sound community",
]

DATABASE_URL = "sqlite:///./data/bot.db"
IMAGE_SAVE_DIR = "./data/images"

DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
