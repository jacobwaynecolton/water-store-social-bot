import os
import json
import base64
import random
import logging
import anthropic

logger = logging.getLogger(__name__)

APPROVED_PHOTOS_DIR = "./data/approved_photos"
MANIFEST_PATH = "./data/approved_photos/manifest.json"
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

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

_client = None


def _get_client():
    global _client
    if _client is None:
        from backend.config import ANTHROPIC_API_KEY
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def analyze_and_tag_photos():
    """
    Scans data/approved_photos/ for any images not yet in the manifest and
    uses Claude vision to generate a description and theme tags for each one.
    Safe to call repeatedly — already-analyzed images are skipped.
    """
    os.makedirs(APPROVED_PHOTOS_DIR, exist_ok=True)
    manifest = _load_manifest()

    new_files = [
        f for f in os.listdir(APPROVED_PHOTOS_DIR)
        if os.path.splitext(f)[1].lower() in VALID_EXTENSIONS
        and f not in manifest
    ]

    if not new_files:
        logger.info("Photo analysis: no new photos to tag")
        return manifest

    logger.info(f"Analyzing {len(new_files)} new photo(s) with Claude vision...")

    for filename in new_files:
        path = os.path.join(APPROVED_PHOTOS_DIR, filename)
        try:
            tags = _analyze_image(path)
            manifest[filename] = {
                "path": path,
                "description": tags["description"],
                "keywords": tags["keywords"],
                "themes": tags["themes"],
            }
            logger.info(f"Tagged {filename}: {tags['description'][:60]}")
        except Exception as e:
            logger.warning(f"Could not analyze {filename}: {e}")

    _save_manifest(manifest)
    return manifest


def _analyze_image(path: str) -> dict:
    """Ask Claude to describe the image and suggest which themes it suits."""
    ext = os.path.splitext(path)[1].lower()
    media_type_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".webp": "image/webp",
    }
    media_type = media_type_map.get(ext, "image/jpeg")

    with open(path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    themes_list = "\n".join(f"- {t}" for t in CONTENT_THEMES)

    response = _get_client().messages.create(
        model="claude-haiku-4-5-20251001",  # cheap and fast for image analysis
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": image_data},
                },
                {
                    "type": "text",
                    "text": f"""Briefly describe what's in this image, then list keywords and the best matching themes.

Available themes:
{themes_list}

Reply in exactly this format:
DESCRIPTION: <one sentence>
KEYWORDS: <comma-separated list of 6-10 keywords>
THEMES: <comma-separated list of 1-3 best matching themes from the list above>""",
                },
            ],
        }],
    )

    text = response.content[0].text.strip()
    result = {"description": "", "keywords": [], "themes": []}

    for line in text.split("\n"):
        if line.startswith("DESCRIPTION:"):
            result["description"] = line[len("DESCRIPTION:"):].strip()
        elif line.startswith("KEYWORDS:"):
            result["keywords"] = [k.strip() for k in line[len("KEYWORDS:"):].split(",")]
        elif line.startswith("THEMES:"):
            result["themes"] = [t.strip() for t in line[len("THEMES:"):].split(",")]

    return result


def get_approved_photo_for_theme(theme: str) -> tuple[str, str] | None:
    """
    Find an approved photo for the given theme using AI-generated descriptions.
    Scores each photo by how many of its tags mention the theme or its keywords.
    Falls back to a random photo if nothing scores.

    Returns (url_path, local_path) or None if the folder is empty.
    """
    manifest = _load_manifest()

    photos = [
        (filename, meta) for filename, meta in manifest.items()
        if os.path.exists(meta["path"])
    ]

    if not photos:
        return None

    # Score by: direct theme match in themes list, or keyword overlap with theme string
    theme_words = set(theme.lower().replace("(", "").replace(")", "").split())

    scored = []
    for filename, meta in photos:
        score = 0
        # Strong signal: Claude explicitly matched this theme
        if any(theme.lower() in t.lower() or t.lower() in theme.lower() for t in meta.get("themes", [])):
            score += 10
        # Weaker signal: keywords from the description overlap with theme words
        for kw in meta.get("keywords", []):
            if any(word in kw.lower() for word in theme_words):
                score += 1
        scored.append((score, filename, meta["path"]))

    scored.sort(reverse=True)
    top_score = scored[0][0]

    candidates = [(fn, p) for s, fn, p in scored if s == top_score]
    chosen_filename, chosen_path = random.choice(candidates)
    return f"/approved-photos/{chosen_filename}", chosen_path


def _load_manifest() -> dict:
    if not os.path.exists(MANIFEST_PATH):
        return {}
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def _save_manifest(manifest: dict):
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
