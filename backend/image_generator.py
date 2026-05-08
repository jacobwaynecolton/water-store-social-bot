import os
import logging
import requests
from datetime import datetime
import openai
from backend.config import OPENAI_API_KEY, IMAGE_SAVE_DIR

logger = logging.getLogger(__name__)
from backend.image_scraper import get_approved_photo_for_theme

client = openai.OpenAI(api_key=OPENAI_API_KEY)


def get_image_for_post(theme: str, dalle_prompt: str) -> tuple[str, str]:
    """
    Hybrid image picker:
      1. Check data/approved_photos/ for a real photo matching the theme.
      2. Fall back to a DALL-E 3 watercolour illustration.

    To use real photos: drop .jpg/.png files into data/approved_photos/.
    Name them descriptively (e.g. hot_tub_showroom.jpg) for better matching.

    Returns (public_url, local_path).
    public_url is passed to the Meta API — for approved photos this is the
    /approved-photos/ endpoint; for DALL-E it's the temporary CDN URL.
    """
    approved = get_approved_photo_for_theme(theme)
    if approved:
        url_path, local_path = approved
        logger.info(f"Using approved photo: {local_path}")
        return url_path, local_path

    return _generate_illustration(dalle_prompt)


def _generate_illustration(prompt: str) -> tuple[str, str]:
    """
    Generate a styled image with DALL-E 3.
    Claude embeds a STYLE: prefix in the prompt to pick between watercolour and infographic.
    Saves locally before the DALL-E URL expires (~1 hour).
    """
    if prompt.startswith("STYLE:INFOGRAPHIC"):
        subject = prompt[len("STYLE:INFOGRAPHIC"):].strip()
        dalle_prompt = (
            f"A clean social media infographic illustration: {subject}. "
            "Flat design style, bold geometric shapes, limited palette of 2-3 colours, "
            "icon-style graphics, modern and clean like a Canva template. "
            "No text, no labels, no logos."
        )
    else:
        # Default to watercolour — strip STYLE:WATERCOLOUR prefix if present
        subject = prompt.replace("STYLE:WATERCOLOUR", "").strip()
        dalle_prompt = (
            f"A watercolour illustration: {subject}. "
            "Soft watercolour style, loose brushwork, warm tones, no text, no logos. "
            "Editorial illustration feel, not a photograph or 3D render."
        )

    illustration_prompt = dalle_prompt

    response = client.images.generate(
        model="dall-e-3",
        prompt=dalle_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url

    os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)
    filename = f"post_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
    local_path = os.path.join(IMAGE_SAVE_DIR, filename)

    img_bytes = requests.get(image_url, timeout=30).content
    with open(local_path, "wb") as f:
        f.write(img_bytes)

    return image_url, local_path
