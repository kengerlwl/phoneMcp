"""
PhoneMCP CLI — Execute phone actions via JSON commands from the command line.

Usage:
    phone-mcp run '{"action":"screenshot"}'
    phone-mcp run '[{"action":"tap","x":500,"y":800},{"action":"wait","seconds":1}]'

This module enables Skill-based usage where AI agents invoke phone-mcp
as a CLI tool (via run_terminal_cmd) instead of connecting to an MCP server.
"""

import base64
import io
import json
import os
import sys
import tempfile
import time
import uuid

from phone_mcp.adb.adb_binary import init_adb

# ---------------------------------------------------------------------------
# Global UI element cache (persisted across batch commands within one invocation)
# ---------------------------------------------------------------------------
_ui_elements_cache: dict = {"elements": [], "timestamp": 0, "mode": "xml"}


# ---------------------------------------------------------------------------
# Action Handlers
# ---------------------------------------------------------------------------

def _handle_list_devices(params: dict) -> dict:
    from phone_mcp.adb import list_devices as adb_list_devices
    devices = adb_list_devices()
    device_list = []
    for d in devices:
        device_list.append({
            "device_id": d.device_id,
            "status": d.status,
            "connection_type": d.connection_type.value,
            "model": d.model,
        })
    return {"status": "success", "devices": device_list, "count": len(device_list)}


def _handle_connect_device(params: dict) -> dict:
    from phone_mcp.adb import ADBConnection
    address = params.get("address", "")
    timeout = params.get("timeout", 10)
    if not address:
        return {"status": "error", "error": "Missing required parameter: address"}
    conn = ADBConnection()
    success, message = conn.connect(address, timeout)
    return {"status": "success" if success else "error", "message": message, "address": address}


def _handle_disconnect_device(params: dict) -> dict:
    from phone_mcp.adb import ADBConnection
    address = params.get("address")
    conn = ADBConnection()
    success, message = conn.disconnect(address)
    return {"status": "success" if success else "error", "message": message}


def _handle_screenshot(params: dict) -> dict:
    from phone_mcp.adb import get_screenshot as adb_get_screenshot
    from PIL import Image as PILImage

    device_id = params.get("device_id")
    save_path = params.get("path")

    screenshot = adb_get_screenshot(device_id)
    image_bytes = base64.b64decode(screenshot.base64_data)

    img = PILImage.open(io.BytesIO(image_bytes))

    # Convert RGBA to RGB
    if img.mode == "RGBA":
        rgb_img = PILImage.new("RGB", img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[3])
        img = rgb_img
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # Compress
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=60, optimize=True)
    img_bytes = output.getvalue()

    # Save to file
    if not save_path:
        save_path = os.path.join(
            tempfile.gettempdir(), f"phone-mcp-screenshot-{uuid.uuid4().hex[:8]}.jpg"
        )

    with open(save_path, "wb") as f:
        f.write(img_bytes)

    return {
        "status": "success",
        "path": save_path,
        "width": img.size[0],
        "height": img.size[1],
        "size_bytes": len(img_bytes),
    }


def _handle_get_ui_elements(params: dict) -> dict:
    from phone_mcp.adb import get_ui_elements as adb_get_ui_elements, format_elements_for_llm

    global _ui_elements_cache

    device_id = params.get("device_id")
    clickable_only = params.get("clickable_only", False)
    mode = params.get("mode", "xml")

    elements = adb_get_ui_elements(device_id, clickable_only, mode=mode)

    _ui_elements_cache = {
        "elements": elements,
        "timestamp": time.time(),
        "mode": mode,
    }

    element_list = []
    for elem in elements:
        element_list.append({
            "index": elem.index,
            "text": elem.text,
            "content_desc": elem.content_desc,
            "resource_id": elem.resource_id.split("/")[-1] if "/" in elem.resource_id else elem.resource_id,
            "class": elem.class_name.split(".")[-1] if elem.class_name else "",
            "center": elem.center,
            "bounds": elem.bounds,
            "clickable": elem.clickable,
        })

    formatted = format_elements_for_llm(elements)

    return {
        "status": "success",
        "mode": mode,
        "elements": element_list,
        "count": len(element_list),
        "formatted": formatted,
        "hint": "Use tap_element with index or text to click an element",
    }


def _handle_tap_element(params: dict) -> dict:
    from phone_mcp.adb import (
        get_ui_elements as adb_get_ui_elements,
        find_element_by_text as adb_find_element_by_text,
        find_element_by_resource_id as adb_find_element_by_resource_id,
        find_element_by_index as adb_find_element_by_index,
        tap as adb_tap,
    )

    global _ui_elements_cache

    index = params.get("index")
    text = params.get("text")
    resource_id = params.get("resource_id")
    device_id = params.get("device_id")
    delay = params.get("delay", 1.0)
    refresh = params.get("refresh", False)

    if index is None and text is None and resource_id is None:
        return {"status": "error", "error": "Must provide at least one of: index, text, or resource_id"}

    cache_age = time.time() - _ui_elements_cache.get("timestamp", 0)
    elements = _ui_elements_cache.get("elements", [])
    cached_mode = _ui_elements_cache.get("mode", "xml")

    if refresh or cache_age > 30 or not elements:
        elements = adb_get_ui_elements(device_id, clickable_only=False, mode=cached_mode)
        _ui_elements_cache = {"elements": elements, "timestamp": time.time(), "mode": cached_mode}

    element = None
    search_method = ""

    if index is not None:
        element = adb_find_element_by_index(elements, index)
        search_method = f"index={index}"
    elif text is not None:
        element = adb_find_element_by_text(elements, text, exact_match=False)
        search_method = f"text='{text}'"
    elif resource_id is not None:
        element = adb_find_element_by_resource_id(elements, resource_id, partial_match=True)
        search_method = f"resource_id='{resource_id}'"

    # Retry with fresh elements if not found
    if element is None and not refresh:
        elements = adb_get_ui_elements(device_id, clickable_only=False, mode=cached_mode)
        _ui_elements_cache = {"elements": elements, "timestamp": time.time(), "mode": cached_mode}

        if index is not None:
            element = adb_find_element_by_index(elements, index)
        elif text is not None:
            element = adb_find_element_by_text(elements, text, exact_match=False)
        elif resource_id is not None:
            element = adb_find_element_by_resource_id(elements, resource_id, partial_match=True)

    if element is None:
        return {
            "status": "error",
            "error": f"Element not found with {search_method}. Try get_ui_elements first.",
            "available_count": len(elements),
        }

    x, y = element.center
    adb_tap(x, y, device_id, delay)

    # Invalidate cache after tap
    _ui_elements_cache = {"elements": [], "timestamp": 0, "mode": "xml"}

    return {
        "status": "success",
        "action": "tap_element",
        "element": {
            "index": element.index,
            "text": element.text,
            "content_desc": element.content_desc,
            "resource_id": element.resource_id,
        },
        "coordinates": {"x": x, "y": y},
        "search_method": search_method,
    }


def _handle_tap(params: dict) -> dict:
    from phone_mcp.adb import tap as adb_tap

    x = params.get("x")
    y = params.get("y")
    device_id = params.get("device_id")
    delay = params.get("delay", 1.0)

    if x is None or y is None:
        return {"status": "error", "error": "Missing required parameters: x, y"}

    adb_tap(x, y, device_id, delay)
    return {"status": "success", "action": "tap", "x": x, "y": y}


def _handle_double_tap(params: dict) -> dict:
    from phone_mcp.adb import double_tap as adb_double_tap

    x = params.get("x")
    y = params.get("y")
    device_id = params.get("device_id")
    delay = params.get("delay")

    if x is None or y is None:
        return {"status": "error", "error": "Missing required parameters: x, y"}

    adb_double_tap(x, y, device_id, delay)
    return {"status": "success", "action": "double_tap", "x": x, "y": y}


def _handle_swipe(params: dict) -> dict:
    from phone_mcp.adb import swipe as adb_swipe

    start_x = params.get("start_x")
    start_y = params.get("start_y")
    end_x = params.get("end_x")
    end_y = params.get("end_y")
    duration_ms = params.get("duration_ms")
    device_id = params.get("device_id")
    delay = params.get("delay", 1.0)

    if any(v is None for v in [start_x, start_y, end_x, end_y]):
        return {"status": "error", "error": "Missing required parameters: start_x, start_y, end_x, end_y"}

    adb_swipe(start_x, start_y, end_x, end_y, duration_ms, device_id, delay)
    return {
        "status": "success",
        "action": "swipe",
        "start": {"x": start_x, "y": start_y},
        "end": {"x": end_x, "y": end_y},
    }


def _handle_type_text(params: dict) -> dict:
    from phone_mcp.adb import type_text as adb_type_text, clear_text as adb_clear_text

    text = params.get("text", "")
    device_id = params.get("device_id")
    clear_first = params.get("clear_first", True)

    if not text:
        return {"status": "error", "error": "Missing required parameter: text"}

    if clear_first:
        adb_clear_text(device_id)
    adb_type_text(text, device_id)

    return {"status": "success", "action": "type_text", "text": text, "cleared": clear_first}


def _handle_clear_text(params: dict) -> dict:
    from phone_mcp.adb import clear_text as adb_clear_text

    device_id = params.get("device_id")
    adb_clear_text(device_id)
    return {"status": "success", "action": "clear_text"}


def _handle_press_back(params: dict) -> dict:
    from phone_mcp.adb import back as adb_back

    device_id = params.get("device_id")
    delay = params.get("delay", 1.0)
    adb_back(device_id, delay)
    return {"status": "success", "action": "back"}


def _handle_press_home(params: dict) -> dict:
    from phone_mcp.adb import home as adb_home

    device_id = params.get("device_id")
    delay = params.get("delay", 1.0)
    adb_home(device_id, delay)
    return {"status": "success", "action": "home"}


def _handle_press_key(params: dict) -> dict:
    from phone_mcp.adb.device import press_key as adb_press_key

    key = params.get("key", "")
    device_id = params.get("device_id")
    delay = params.get("delay", 0.5)

    if not key:
        return {"status": "error", "error": "Missing required parameter: key"}

    adb_press_key(key, device_id, delay)
    return {"status": "success", "action": "press_key", "key": key}


def _handle_launch_app(params: dict) -> dict:
    from phone_mcp.adb import launch_app as adb_launch_app
    from phone_mcp.adb.device import launch_app_by_package

    app_name = params.get("app_name") or params.get("name")
    package_name = params.get("package_name") or params.get("package")
    device_id = params.get("device_id")
    delay = params.get("delay", 1.0)

    if not app_name and not package_name:
        return {"status": "error", "error": "Must provide app_name or package_name"}

    if package_name:
        success = launch_app_by_package(package_name, device_id, delay)
        if success:
            return {"status": "success", "action": "launch_app", "package_name": package_name}
        else:
            return {"status": "error", "error": f"Failed to launch: {package_name}"}

    success = adb_launch_app(app_name, device_id, delay)
    if success:
        return {"status": "success", "action": "launch_app", "app_name": app_name}
    else:
        return {"status": "error", "error": f"App not found: {app_name}. Use search_apps to find package name."}


def _handle_get_current_app(params: dict) -> dict:
    from phone_mcp.adb import get_current_app as adb_get_current_app

    device_id = params.get("device_id")
    app_name = adb_get_current_app(device_id)
    return {"status": "success", "app_name": app_name}


def _handle_search_apps(params: dict) -> dict:
    from phone_mcp.adb.device import search_installed_apps

    keyword = params.get("keyword", "")
    device_id = params.get("device_id")

    if not keyword:
        return {"status": "error", "error": "Missing required parameter: keyword"}

    apps = search_installed_apps(keyword, device_id)
    return {"status": "success", "apps": apps, "count": len(apps)}


def _handle_wait(params: dict) -> dict:
    seconds = params.get("seconds", 1.0)
    time.sleep(seconds)
    return {"status": "success", "action": "wait", "seconds": seconds}


# ---------------------------------------------------------------------------
# Action Router
# ---------------------------------------------------------------------------

ACTION_MAP = {
    "list_devices": _handle_list_devices,
    "connect_device": _handle_connect_device,
    "connect": _handle_connect_device,
    "disconnect_device": _handle_disconnect_device,
    "disconnect": _handle_disconnect_device,
    "screenshot": _handle_screenshot,
    "get_screenshot": _handle_screenshot,
    "get_ui_elements": _handle_get_ui_elements,
    "ui_elements": _handle_get_ui_elements,
    "tap_element": _handle_tap_element,
    "tap": _handle_tap,
    "double_tap": _handle_double_tap,
    "swipe": _handle_swipe,
    "type_text": _handle_type_text,
    "type": _handle_type_text,
    "clear_text": _handle_clear_text,
    "clear": _handle_clear_text,
    "press_back": _handle_press_back,
    "back": _handle_press_back,
    "press_home": _handle_press_home,
    "home": _handle_press_home,
    "press_key": _handle_press_key,
    "key": _handle_press_key,
    "launch_app": _handle_launch_app,
    "launch": _handle_launch_app,
    "get_current_app": _handle_get_current_app,
    "current_app": _handle_get_current_app,
    "search_apps": _handle_search_apps,
    "search": _handle_search_apps,
    "wait": _handle_wait,
}


def execute_action(command: dict) -> dict:
    """Execute a single action command and return JSON-serializable result."""
    action = command.get("action", "")
    if not action:
        return {"status": "error", "error": "Missing 'action' field"}

    handler = ACTION_MAP.get(action)
    if not handler:
        available = sorted(set(ACTION_MAP.keys()))
        return {
            "status": "error",
            "error": f"Unknown action: '{action}'",
            "available_actions": available,
        }

    try:
        return handler(command)
    except Exception as e:
        return {"status": "error", "error": str(e), "action": action}


def execute_commands(raw_json: str) -> str:
    """
    Parse JSON input (single object or array), execute commands,
    and return JSON string output.
    """
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as e:
        return json.dumps({"status": "error", "error": f"Invalid JSON: {e}"}, ensure_ascii=False)

    if isinstance(parsed, dict):
        result = execute_action(parsed)
        return json.dumps(result, ensure_ascii=False)

    if isinstance(parsed, list):
        results = []
        for i, cmd in enumerate(parsed):
            if not isinstance(cmd, dict):
                results.append({"status": "error", "error": f"Command #{i} is not a JSON object"})
                break
            result = execute_action(cmd)
            results.append(result)
            # Stop on first failure
            if result.get("status") == "error":
                break
        return json.dumps(results, ensure_ascii=False)

    return json.dumps({"status": "error", "error": "Input must be a JSON object or array"}, ensure_ascii=False)


def cli_main(args: list[str] | None = None):
    """
    CLI entry point.

    Usage:
        phone-mcp run '{"action":"screenshot"}'
        phone-mcp run '[{"action":"tap","x":100,"y":200},{"action":"wait","seconds":1}]'
        echo '{"action":"list_devices"}' | phone-mcp run -
    """
    if args is None:
        args = sys.argv[1:]

    if not args:
        print(json.dumps({"status": "error", "error": "No JSON command provided. Usage: phone-mcp run '{\"action\":\"screenshot\"}'"}, ensure_ascii=False))
        sys.exit(1)

    raw_json = args[0]

    # Support reading from stdin with "-"
    if raw_json == "-":
        raw_json = sys.stdin.read().strip()

    if not raw_json:
        print(json.dumps({"status": "error", "error": "Empty command"}, ensure_ascii=False))
        sys.exit(1)

    # Initialize ADB
    try:
        init_adb()
    except FileNotFoundError as e:
        print(json.dumps({"status": "error", "error": f"ADB not found: {e}"}, ensure_ascii=False))
        sys.exit(1)

    output = execute_commands(raw_json)
    print(output)

