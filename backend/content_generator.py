import random
import anthropic
from backend.config import (
    ANTHROPIC_API_KEY,
    BUSINESS_NAME,
    BUSINESS_DESCRIPTION,
    BUSINESS_WEBSITE,
    CONTENT_THEMES,
    THEME_LOOKBACK,
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def pick_theme(recent_themes: list[str] = []) -> str:
    """
    Pick a content theme, avoiding the last THEME_LOOKBACK themes so we don't
    run two similar posts back to back.
    """
    available = [t for t in CONTENT_THEMES if t not in recent_themes]
    # Fallback if every theme has been used recently (shouldn't happen in normal use)
    if not available:
        available = CONTENT_THEMES
    return random.choice(available)


def generate_post_content(theme: str) -> dict:
    """
    Asks Claude to write a full post for the given theme.
    Returns a dict with keys: facebook, instagram, hashtags, image_prompt.
    """
    prompt = f"""You are the social media manager for {BUSINESS_NAME} ({BUSINESS_WEBSITE}).

About us: {BUSINESS_DESCRIPTION}

Today's content theme: {theme}

Write a social media post with these four parts:

1. Facebook caption — conversational, 2-3 sentences, no hashtags
2. Instagram caption — punchy opening line, 3-5 sentences, ends with a call to action
3. Instagram hashtags — 10-15 relevant tags
4. Image prompt for DALL-E 3 — write a prompt that will produce something that looks like
   a real photograph, NOT a graphic or illustration.

   Rules for the image prompt:
   - Start with "A photograph of" or "A photo of"
   - Describe a realistic, specific scene (a person, a product in a real setting, a backyard, a kitchen)
   - Include lighting details: "soft natural window light", "golden hour", "overcast Ontario sky"
   - Include a camera feel: "shallow depth of field", "shot on 50mm lens", "candid moment"
   - Subjects should look like they belong in Owen Sound, Ontario — real Canadian homes, backyards, kitchens
   - No text, logos, or overlays in the image
   - No glowing effects, perfect gradients, or anything that looks rendered or CGI

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
            if current_key and line.strip():
                result[current_key] += " " + line.strip()

    if "hashtags" in result:
        result["instagram"] = result.get("instagram", "") + "\n\n" + result["hashtags"]

    return result


def generate_comment_reply(comment_text: str, commenter_name: str) -> str:
    """Generate a short, on-brand reply to a comment. Keeps it human and friendly."""
    prompt = f"""You are the social media manager for {BUSINESS_NAME} in Owen Sound, Ontario.
Reply to this comment in a friendly, helpful tone. 1-2 sentences max.
Don't be salesy. If it's a complaint, acknowledge it and offer to help offline (DM or call 519-371-8500).

Commenter: {commenter_name}
Comment: {comment_text}

Reply:"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text.strip()
