import random
import anthropic
from backend.config import (
    ANTHROPIC_API_KEY,
    BUSINESS_NAME,
    BUSINESS_DESCRIPTION,
    BUSINESS_WEBSITE,
    CONTENT_THEMES,
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def pick_theme() -> str:
    return random.choice(CONTENT_THEMES)


def generate_post_content(theme: str) -> dict:
    """
    Asks Claude to write a full post for the given theme.
    Returns a dict with keys: facebook, instagram, hashtags, image_prompt.
    """
    prompt = f"""You are the social media manager for {BUSINESS_NAME} ({BUSINESS_WEBSITE}).

About us: {BUSINESS_DESCRIPTION}

Today's content theme: {theme}

Write a social media post with these four parts:

1. Facebook caption — conversational, 2-3 sentences, no hashtags (FB algorithm doesn't like them)
2. Instagram caption — punchy opening line, 3-5 sentences, ends with a call to action
3. Instagram hashtags — 10-15 relevant tags
4. Image prompt for DALL-E 3 — describe a clean, realistic photo that fits this post.
   Style: bright, modern, professional product/lifestyle photography. No text in the image.

Use exactly this format, each on its own line:
FACEBOOK: <caption>
INSTAGRAM: <caption>
HASHTAGS: <hashtags>
IMAGE_PROMPT: <prompt>"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()

    # Parse the structured response into a dict
    result = {}
    current_key = None
    for line in text.split("\n"):
        for prefix, key in [
            ("FACEBOOK:", "facebook"),
            ("INSTAGRAM:", "instagram"),
            ("HASHTAGS:", "hashtags"),
            ("IMAGE_PROMPT:", "image_prompt"),
        ]:
            if line.startswith(prefix):
                current_key = key
                result[key] = line[len(prefix):].strip()
                break
        else:
            # continuation of the previous field
            if current_key and line.strip():
                result[current_key] += " " + line.strip()

    # Append hashtags to the Instagram caption
    if "hashtags" in result:
        result["instagram"] = result.get("instagram", "") + "\n\n" + result["hashtags"]

    return result


def generate_comment_reply(comment_text: str, commenter_name: str) -> str:
    """Generate a short, on-brand reply to a comment. Keeps it human and friendly."""
    prompt = f"""You are the social media manager for {BUSINESS_NAME}, a water specialty store in Ontario.
Reply to this comment in a friendly, helpful tone. Keep it to 1-2 sentences max.
Don't be salesy. If it's a complaint, acknowledge it and offer to help offline (DM or phone).

Commenter: {commenter_name}
Comment: {comment_text}

Reply:"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text.strip()
