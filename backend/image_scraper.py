import os
import random
import logging

logger = logging.getLogger(__name__)

APPROVED_PHOTOS_DIR = "./data/approved_photos"

# Maps each theme to keywords — filenames containing these words get matched first.
# Just name your photos something like "hot_tub_deck.jpg" or "bbq_traeger.jpg".
THEME_KEYWORDS = {
    "drinking water systems (RO or alkaline)": [
        "water", "ro", "reverse", "osmosis", "alkaline", "filter", "drinking", "purif", "tap",
    ],
    "U-Fill refill station": [
        "refill", "ufill", "fill", "station", "jug", "bottle",
    ],
    "water softeners or water quality problem (staining, odor, hard water)": [
        "soft", "treatment", "quality", "hard", "iron", "filter", "well",
    ],
    "hot tubs or swim spas": [
        "hot", "tub", "spa", "swim", "jacuzzi", "pool",
    ],
    "BBQ grills or pellet smokers": [
        "bbq", "grill", "smoker", "pellet", "traeger", "pitboss", "cook",
    ],
    "saunas": [
        "sauna", "steam", "cedar", "infrared",
    ],
    "health and hydration tip": [
        "water", "glass", "drink", "health", "hydrat",
    ],
    "free water testing offer": [
        "test", "water", "quality",
    ],
    "seasonal promotion or local Owen Sound community": [
        "owen", "sound", "store", "local", "community", "promo", "season",
    ],
}

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def get_approved_photo_for_theme(theme: str) -> tuple[str, str] | None:
    """
    Look in data/approved_photos/ for a photo that matches the theme.
    Matches by checking if any theme keyword appears in the filename.
    Falls back to a random photo from the folder if nothing matches.

    Returns (url_path, local_path) where url_path is the /approved-photos/{filename}
    endpoint the dashboard/Meta can use, or None if the folder is empty.

    To add photos: drop .jpg/.png files into data/approved_photos/.
    Name them descriptively (e.g. hot_tub_showroom.jpg) for better theme matching.
    """
    os.makedirs(APPROVED_PHOTOS_DIR, exist_ok=True)

    all_photos = [
        f for f in os.listdir(APPROVED_PHOTOS_DIR)
        if os.path.splitext(f)[1].lower() in VALID_EXTENSIONS
    ]

    if not all_photos:
        return None

    theme_kws = THEME_KEYWORDS.get(theme, [])
    matched = [
        f for f in all_photos
        if any(kw in f.lower() for kw in theme_kws)
    ]

    chosen = random.choice(matched) if matched else random.choice(all_photos)
    local_path = os.path.join(APPROVED_PHOTOS_DIR, chosen)

    # The URL path served by FastAPI's /approved-photos static mount
    url_path = f"/approved-photos/{chosen}"
    return url_path, local_path
