import re
from io import BytesIO
from PIL import Image

def is_valid_svg(content: str) -> bool:
    if not content:
        return False
    # Simple validation: checks if it has an opening and closing <svg> tag
    content = content.strip().lower()
    return "<svg" in content and "</svg>" in content

def extract_viewbox(content: str) -> str:
    if not content:
        return "0 0 24 24"
    match = re.search(r'viewBox=["\']([^"\']+)["\']', content, re.IGNORECASE)
    if match:
        return match.group(1)
    return "0 0 24 24"

def convert_image_to_webp(image_bytes: bytes, quality: int = 80) -> bytes:
    try:
        image = Image.open(BytesIO(image_bytes))
        output = BytesIO()
        # Convert to RGB if it's RGBA but we want to save without alpha issues, or keep RGBA for webp
        # WebP supports alpha channel, so we can keep it as is.
        image.save(output, format="WEBP", quality=quality)
        return output.getvalue()
    except Exception as e:
        raise ValueError(f"Invalid image format: {e}")
