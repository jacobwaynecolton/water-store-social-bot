import os
import requests
from datetime import datetime
import openai
from backend.config import OPENAI_API_KEY, IMAGE_SAVE_DIR

client = openai.OpenAI(api_key=OPENAI_API_KEY)


def generate_image(prompt: str) -> tuple[str, str]:
    """
    Generates a 1024x1024 image with DALL-E 3 and saves it locally.

    Returns (dalle_url, local_path).
    We save locally right away because DALL-E URLs expire after ~1 hour —
    but we still return the URL because Instagram's API requires a public URL
    at publish time, and we post immediately after generating.
    """
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url

    # Download and persist the image before the URL goes stale
    os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)
    filename = f"post_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
    local_path = os.path.join(IMAGE_SAVE_DIR, filename)

    img_bytes = requests.get(image_url, timeout=30).content
    with open(local_path, "wb") as f:
        f.write(img_bytes)

    return image_url, local_path
