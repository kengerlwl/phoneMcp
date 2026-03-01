"""Input utilities for Android device text input using native ADB commands."""

import base64
import subprocess
import time


def type_text(text: str, device_id: str | None = None) -> None:
    """
    Type text into the currently focused input field.

    For ASCII text, uses `adb shell input text` (native, no extra app needed).
    For non-ASCII text (e.g. Chinese), uses ADB Keyboard's ADB_INPUT_B64 broadcast.

    Args:
        text: The text to type.
        device_id: Optional ADB device ID for multi-device setups.
    """
    if not text:
        return

    adb_prefix = _get_adb_prefix(device_id)

    # Check if text is pure ASCII
    if all(ord(c) < 128 for c in text):
        # Escape special shell characters for `input text`
        escaped = _escape_for_input_text(text)
        subprocess.run(
            adb_prefix + ["shell", "input", "text", escaped],
            capture_output=True,
            text=True,
        )
    else:
        # Non-ASCII (Chinese, emoji, etc.): use ADB Keyboard broadcast
        encoded_text = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        subprocess.run(
            adb_prefix
            + [
                "shell",
                "am",
                "broadcast",
                "-a",
                "ADB_INPUT_B64",
                "--es",
                "msg",
                encoded_text,
            ],
            capture_output=True,
            text=True,
        )


def clear_text(device_id: str | None = None) -> None:
    """
    Clear text in the currently focused input field using native ADB commands.

    Uses Ctrl+A (select all) then DEL (delete) to clear the field.
    """
    adb_prefix = _get_adb_prefix(device_id)

    # Move cursor to end first
    subprocess.run(
        adb_prefix + ["shell", "input", "keyevent", "--longpress", "KEYCODE_MOVE_END"],
        capture_output=True,
        text=True,
    )
    time.sleep(0.1)

    # Ctrl+A to select all text
    subprocess.run(
        adb_prefix + ["shell", "input", "keycombination", "113", "29"],  # CTRL + A
        capture_output=True,
        text=True,
    )
    time.sleep(0.1)

    # Delete selected text
    subprocess.run(
        adb_prefix + ["shell", "input", "keyevent", "KEYCODE_DEL"],
        capture_output=True,
        text=True,
    )


def _escape_for_input_text(text: str) -> str:
    """
    Escape special characters for `adb shell input text`.

    The `input text` command interprets certain characters specially.
    Spaces must be replaced with %s, and shell metacharacters must be escaped.
    """
    # Replace space with %s (adb input text convention)
    result = text.replace(" ", "%s")
    # Escape shell special characters
    special_chars = "&<>'\"(){}|;\\`$!~"
    for char in special_chars:
        result = result.replace(char, f"\\{char}")
    return result


def _get_adb_prefix(device_id: str | None) -> list:
    """Get ADB command prefix with optional device specifier."""
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]

