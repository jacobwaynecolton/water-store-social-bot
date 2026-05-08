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
    Generate an illustration-style image with DALL-E 3.
    We use illustration rather than photo-realism because AI-generated product
    details (lids, valves, labels) look wrong in realistic renders but fine in art styles.
    Saves locally before the DALL-E URL expires (~1 hour).
    """
    # Wrap the prompt in illustration framing so DALL-E doesn't try to be photorealistic
    illustration_prompt = (
        f"A clean watercolour illustration: {prompt}. "
        "Soft watercolour style, loose brushwork, warm tones, no text, no logos. "
        "Looks like editorial illustration, not a photograph or 3D render."
    )

    response = client.images.generate(
        model="dall-e-3",
        prompt=illustration_prompt,
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
