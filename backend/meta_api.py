import requests
from backend.config import (
    META_API_BASE,
    META_ACCESS_TOKEN,
    FACEBOOK_PAGE_ID,
    INSTAGRAM_ACCOUNT_ID,
)


def _post(endpoint: str, data: dict) -> dict:
    """POST to the Meta Graph API."""
    url = f"{META_API_BASE}/{endpoint}"
    data["access_token"] = META_ACCESS_TOKEN
    resp = requests.post(url, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _get(endpoint: str, params: dict = {}) -> dict:
    """GET from the Meta Graph API."""
    url = f"{META_API_BASE}/{endpoint}"
    params = {**params, "access_token": META_ACCESS_TOKEN}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


# --- Posting ---

def post_to_facebook(caption: str, image_url: str) -> str:
    """
    Posts a photo to the Facebook page.
    The /photos endpoint accepts a public image URL and caption in one call.
    Returns the resulting post ID.
    """
    result = _post(f"{FACEBOOK_PAGE_ID}/photos", {
        "url": image_url,
        "caption": caption,
        "published": "true",
    })
    # the response shape differs slightly depending on whether it returns post_id or id
    return result.get("post_id") or result.get("id")


def post_to_instagram(caption: str, image_url: str) -> str:
    """
    Instagram publishing via the Graph API is a two-step process:
      1. Create a media container (image + caption staged but not live)
      2. Call media_publish to make it go live

    The image_url must be publicly accessible — DALL-E URLs work here
    as long as we call this shortly after generating the image.
    Returns the published media ID.
    """
    # Step 1: stage the media
    container = _post(f"{INSTAGRAM_ACCOUNT_ID}/media", {
        "image_url": image_url,
        "caption": caption,
    })

    # Step 2: publish it
    result = _post(f"{INSTAGRAM_ACCOUNT_ID}/media_publish", {
        "creation_id": container["id"],
    })
    return result["id"]


# --- Comment fetching ---

def get_facebook_comments(post_id: str) -> list[dict]:
    try:
        result = _get(f"{post_id}/comments", {
            "fields": "id,from,message,created_time",
            "filter": "stream",
        })
        return result.get("data", [])
    except Exception:
        return []


def get_instagram_comments(media_id: str) -> list[dict]:
    try:
        result = _get(f"{media_id}/comments", {
            "fields": "id,username,text,timestamp",
        })
        return result.get("data", [])
    except Exception:
        return []


# --- Replying ---

def reply_to_facebook_comment(comment_id: str, reply: str) -> bool:
    try:
        _post(f"{comment_id}/comments", {"message": reply})
        return True
    except Exception:
        return False


def reply_to_instagram_comment(comment_id: str, reply: str) -> bool:
    try:
        _post(f"{comment_id}/replies", {"message": reply})
        return True
    except Exception:
        return False
