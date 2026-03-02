"""Input utilities for Android device text input using native ADB commands."""

import os
import subprocess
import tempfile
import time
from pathlib import Path

from phone_mcp.adb.adb_binary import get_adb_path

# Track whether clip helper dex has been pushed to device
_clip_helper_cache: dict[str, bool] = {}


def type_text(text: str, device_id: str | None = None) -> None:
    """
    Type text into the currently focused input field.

    For ASCII text, uses `adb shell input text` (native).
    For non-ASCII text (Chinese, emoji, etc.), uses clipboard paste
    (zero APK dependency, works on all Android versions).

    Args:
        text: The text to type.
        device_id: Optional ADB device ID for multi-device setups.
    """
    if not text:
        return

    adb_prefix = _get_adb_prefix(device_id)

    if all(ord(c) < 128 for c in text):
        escaped = _escape_for_input_text(text)
        subprocess.run(
            adb_prefix + ["shell", "input", "text", escaped],
            capture_output=True,
            text=True,
        )
    else:
        _type_non_ascii(text, device_id)


def _type_non_ascii(text: str, device_id: str | None = None) -> None:
    """Type non-ASCII text via clipboard + inject Ctrl+V."""
    adb_prefix = _get_adb_prefix(device_id)
    remote_text_path = "/data/local/tmp/.phone_mcp_clip_text"

    _ensure_clip_helper_on_device(device_id)

    # Write text to temp file on device (avoid shell encoding issues)
    proc = subprocess.run(
        adb_prefix + ["shell", "cat", ">", remote_text_path],
        input=text,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Failed to write temp file: {proc.stderr}")

    # Run helper to set clipboard and inject Ctrl+V
    _run_clip_helper("paste", device_id)

    # Cleanup
    subprocess.run(
        adb_prefix + ["shell", "rm", "-f", remote_text_path],
        capture_output=True,
        text=True,
    )


def _run_clip_helper(action: str, device_id: str | None = None) -> None:
    """Run clip helper on device with specified action."""
    adb_prefix = _get_adb_prefix(device_id)
    result = subprocess.run(
        adb_prefix + [
            "shell",
            "CLASSPATH=/data/local/tmp/.phone_mcp_clip_helper.dex",
            "app_process", "/system/bin", "ClipHelper", action
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if "OK" not in result.stdout:
        raise RuntimeError(
            f"ClipHelper failed (action={action}): {result.stderr.strip() or result.stdout}"
        )


def _ensure_clip_helper_on_device(device_id: str | None = None) -> None:
    """Ensure clip helper dex exists on device."""
    device_key = device_id or "default"
    if _clip_helper_cache.get(device_key):
        return

    adb_prefix = _get_adb_prefix(device_id)
    remote_path = "/data/local/tmp/.phone_mcp_clip_helper.dex"

    # Check if already exists on device
    result = subprocess.run(
        adb_prefix + ["shell", "test", "-f", remote_path, "&&", "echo", "EXISTS"],
        capture_output=True,
        text=True,
    )
    if "EXISTS" in result.stdout:
        _clip_helper_cache[device_key] = True
        return

    # Get pre-built dex and push to device
    local_dex = _get_clip_helper_dex_path()
    push_result = subprocess.run(
        adb_prefix + ["push", local_dex, remote_path],
        capture_output=True,
        text=True,
    )
    if push_result.returncode != 0:
        raise RuntimeError(f"Failed to push clip helper: {push_result.stderr}")

    _clip_helper_cache[device_key] = True


def _get_clip_helper_dex_path() -> str:
    """Get path to clip helper dex file (extract from embedded base64 if needed)."""
    from phone_mcp.adb._clip_helper_dex import get_dex_bytes

    with tempfile.NamedTemporaryFile(suffix=".dex", delete=False) as f:
        f.write(get_dex_bytes())
        return f.name


def clear_text(device_id: str | None = None) -> None:
    """
    Clear text in the currently focused input field.

    Uses Ctrl+A (select all) then DEL (delete).
    Works on all Android versions via helper injection.
    """
    adb_prefix = _get_adb_prefix(device_id)

    # Move cursor to end
    subprocess.run(
        adb_prefix + ["shell", "input", "keyevent", "KEYCODE_MOVE_END"],
        capture_output=True,
        text=True,
    )
    time.sleep(0.1)

    # Try native keycombination first (Android 12+)
    result = subprocess.run(
        adb_prefix + ["shell", "input", "keycombination", "113", "29"],
        capture_output=True,
        text=True,
    )

    if "Unknown command" in result.stderr or result.returncode != 0:
        # Fallback to helper injection (Android 10 and below)
        try:
            _ensure_clip_helper_on_device(device_id)
            _run_clip_helper("ctrla", device_id)
        except RuntimeError:
            pass  # If helper fails, text may still be partially selected

    time.sleep(0.1)

    # Delete selected text
    subprocess.run(
        adb_prefix + ["shell", "input", "keyevent", "KEYCODE_DEL"],
        capture_output=True,
        text=True,
    )


def _escape_for_input_text(text: str) -> str:
    """Escape special characters for adb shell input text."""
    result = text.replace(" ", "%s")
    special_chars = "&<>'\"(){}|;\\`$!~"
    for char in special_chars:
        result = result.replace(char, f"\\{char}")
    return result


def _get_adb_prefix(device_id: str | None) -> list:
    """Get ADB command prefix with optional device specifier."""
    adb = get_adb_path()
    if device_id:
        return [adb, "-s", device_id]
    return [adb]
