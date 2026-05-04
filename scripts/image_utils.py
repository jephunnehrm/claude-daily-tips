import os
import time
import requests
import urllib.parse
from typing import Optional


DEFAULT_IMAGE_PATH = "assets/images/placeholder.jpg"
MAX_RETRIES = 5
INITIAL_BACKOFF = 2  # seconds


def download_and_save_image(
    prompt: str,
    prefix: str,
    date_str: str,
    slug: str,
    timeout: int = 60
) -> str:
    """
    Download image from Pollination AI and save locally.
    Retries up to MAX_RETRIES times on failure with exponential backoff.
    Returns local path if successful, or placeholder path if all retries fail.

    Args:
        prompt: Image generation prompt
        prefix: Filename prefix (e.g., 'dotnet', 'java', '')
        date_str: Date string (YYYY-MM-DD)
        slug: URL-safe slug from title
        timeout: Request timeout in seconds

    Returns:
        Local image path (relative) suitable for markdown, or placeholder on failure
    """
    os.makedirs("assets/images", exist_ok=True)

    image_prompt_clean = prompt.strip().rstrip(".,;")
    pollinations_url = (
        f"https://image.pollinations.ai/prompt/{urllib.parse.quote(image_prompt_clean)}"
        f"?width=800&height=400&nologo=true&model=flux"
    )

    print("🖼️ Downloading image from Pollination AI...")

    for attempt in range(MAX_RETRIES):
        try:
            img_response = requests.get(pollinations_url, timeout=timeout)

            if img_response.status_code != 200:
                raise Exception(
                    f"HTTP {img_response.status_code}: {img_response.reason}"
                )

            content_type = img_response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                raise Exception(
                    f"Invalid content type: {content_type} (expected image/*)"
                )

            # Build local filename
            if prefix:
                img_filename = f"assets/images/{prefix}-{date_str}-{slug}.jpg"
            else:
                img_filename = f"assets/images/{date_str}-{slug}.jpg"

            # Save to disk
            with open(img_filename, "wb") as f:
                f.write(img_response.content)

            image_url = f"/claude-daily-tips/{img_filename}"
            print(f"✅ Image saved locally: {img_filename}")
            return image_url

        except (requests.RequestException, Exception) as e:
            if attempt < MAX_RETRIES - 1:
                backoff = INITIAL_BACKOFF * (2 ** attempt)
                print(f"⚠️ Download failed (attempt {attempt + 1}/{MAX_RETRIES}): {type(e).__name__}")
                print(f"   Retrying in {backoff}s...")
                time.sleep(backoff)
            else:
                print(f"❌ Image download failed after {MAX_RETRIES} attempts: {e}")
                print(f"   Using placeholder image — will retry next run")
                return DEFAULT_IMAGE_PATH
