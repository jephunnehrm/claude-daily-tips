import os
import requests
import urllib.parse
from typing import Optional


DEFAULT_IMAGE_PATH = "assets/images/placeholder.jpg"


def download_and_save_image(
    prompt: str,
    prefix: str,
    date_str: str,
    slug: str,
    timeout: int = 60
) -> str:
    """
    Download image from Pollination AI and save locally.
    Returns local path if successful, raises exception if it fails.

    Args:
        prompt: Image generation prompt
        prefix: Filename prefix (e.g., 'dotnet', 'java', '')
        date_str: Date string (YYYY-MM-DD)
        slug: URL-safe slug from title
        timeout: Request timeout in seconds

    Returns:
        Local image path (relative) suitable for markdown

    Raises:
        Exception: If image download fails
    """
    os.makedirs("assets/images", exist_ok=True)

    image_prompt_clean = prompt.strip().rstrip(".,;")
    pollinations_url = (
        f"https://image.pollinations.ai/prompt/{urllib.parse.quote(image_prompt_clean)}"
        f"?width=800&height=400&nologo=true&model=flux"
    )

    print("🖼️ Downloading image from Pollination AI...")
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

    except requests.RequestException as e:
        raise Exception(f"Request failed: {e}")
    except Exception as e:
        raise Exception(f"Image download failed: {e}")
