"""OCR-based UI element detection for Android screens.

When uiautomator XML dump fails (e.g. WebView, games, Flutter apps),
this module provides OCR-based fallback to detect text elements on screen.

Uses PaddleOCR for text detection and recognition, returning results
in the same UIElement format for seamless integration.
"""

import io
import subprocess
from typing import List

from PIL import Image, ImageDraw, ImageFont

from phone_mcp.adb.ui_hierarchy import UIElement


def _get_adb_prefix(device_id: str | None) -> list:
    """Get ADB command prefix with optional device specifier."""
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]


def _capture_screenshot_bytes(device_id: str | None = None, timeout: int = 10) -> bytes:
    """Capture a screenshot and return raw PNG bytes (without saving to file)."""
    adb_prefix = _get_adb_prefix(device_id)

    result = subprocess.run(
        adb_prefix + ["exec-out", "screencap", "-p"],
        capture_output=True,
        timeout=timeout,
    )

    if result.returncode != 0 or not result.stdout:
        raise RuntimeError("Failed to capture screenshot for OCR")

    return result.stdout


# Cached PaddleOCR instance (initialization is expensive, ~2-5s).
_ocr_instance = None


def _get_ocr_instance():
    """Get or create a cached PaddleOCR instance."""
    global _ocr_instance
    if _ocr_instance is not None:
        return _ocr_instance

    import os
    os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

    try:
        from paddleocr import PaddleOCR
    except ImportError:
        raise ImportError(
            "PaddleOCR is required for OCR mode. "
            "Install it with: pip install paddleocr paddlepaddle"
        )

    _ocr_instance = PaddleOCR(
        use_textline_orientation=True,
        lang="ch",
    )
    return _ocr_instance


def ocr_get_ui_elements(
    device_id: str | None = None,
    screenshot_bytes: bytes | None = None,
    timeout: int = 10,
) -> List[UIElement]:
    """
    Use OCR to detect text elements on the screen.

    Args:
        device_id: Optional ADB device ID.
        screenshot_bytes: Optional pre-captured screenshot bytes.
            If not provided, will capture a new screenshot.
        timeout: Timeout for screenshot capture.

    Returns:
        List of UIElement objects detected via OCR.
    """
    ocr = _get_ocr_instance()

    # Capture screenshot if not provided
    if screenshot_bytes is None:
        screenshot_bytes = _capture_screenshot_bytes(device_id, timeout)

    img = Image.open(io.BytesIO(screenshot_bytes))

    # Run OCR on the image
    import numpy as np
    img_array = np.array(img)
    results = ocr.predict(img_array)

    elements: List[UIElement] = []

    if not results:
        return elements

    result = results[0]
    rec_texts = result.get("rec_texts", [])
    rec_scores = result.get("rec_scores", [])
    dt_polys = result.get("dt_polys", [])

    index = 0
    for i, text in enumerate(rec_texts):
        # Skip low confidence results
        confidence = rec_scores[i] if i < len(rec_scores) else 0
        if confidence < 0.5:
            continue

        # Skip empty text
        if not text or not text.strip():
            continue

        # Get bounding polygon and convert to rect (left, top, right, bottom)
        if i >= len(dt_polys):
            continue
        poly = dt_polys[i]  # shape (4, 2) ndarray: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
        xs = [int(p[0]) for p in poly]
        ys = [int(p[1]) for p in poly]
        left = min(xs)
        top = min(ys)
        right = max(xs)
        bottom = max(ys)

        # Skip zero-size elements
        if right <= left or bottom <= top:
            continue

        element = UIElement(
            index=index,
            text=text.strip(),
            content_desc="",
            resource_id="",
            class_name="ocr_text",
            bounds=(left, top, right, bottom),
            clickable=True,  # OCR elements are assumed clickable
            enabled=True,
            focused=False,
            selected=False,
        )
        elements.append(element)
        index += 1

    return elements


def draw_annotated_screenshot(
    screenshot_bytes: bytes,
    elements: List[UIElement],
) -> bytes:
    """
    Draw index annotations on the screenshot for each detected element.

    Args:
        screenshot_bytes: Raw PNG screenshot bytes.
        elements: List of UIElement to annotate.

    Returns:
        Annotated screenshot as JPEG bytes.
    """
    img = Image.open(io.BytesIO(screenshot_bytes))

    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    draw = ImageDraw.Draw(img)

    # Try to use a reasonable font size based on image dimensions
    font_size = max(16, min(img.width, img.height) // 50)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

    for elem in elements:
        left, top, right, bottom = elem.bounds

        # Draw bounding box
        draw.rectangle([left, top, right, bottom], outline="red", width=2)

        # Draw index label background
        label = str(elem.index)
        bbox = draw.textbbox((0, 0), label, font=font)
        label_w = bbox[2] - bbox[0] + 6
        label_h = bbox[3] - bbox[1] + 4

        # Position label at top-left of the element
        label_x = max(0, left - 1)
        label_y = max(0, top - label_h - 1)

        draw.rectangle(
            [label_x, label_y, label_x + label_w, label_y + label_h],
            fill="red",
        )
        draw.text(
            (label_x + 3, label_y + 2),
            label,
            fill="white",
            font=font,
        )

    # Compress as JPEG
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=70, optimize=True)
    return output.getvalue()

