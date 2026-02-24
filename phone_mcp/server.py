"""
Phone MCP Server - Android automation tools via MCP protocol.

This module exposes Android device control capabilities as MCP tools,
allowing AI agents to interact with Android devices through ADB.

Usage:
    python -m phone_mcp

Or import and run:
    from phone_mcp import server
    server.run(host="0.0.0.0", port=8009)
"""

import base64
import io
import time
from typing import Any, Dict, Optional

from PIL import Image as PILImage
from fastmcp import FastMCP
from fastmcp.utilities.types import Image as MCPImage

from phone_mcp.adb import (
    ADBConnection,
    list_devices as adb_list_devices,
    get_screenshot as adb_get_screenshot,
    tap as adb_tap,
    double_tap as adb_double_tap,
    long_press as adb_long_press,
    swipe as adb_swipe,
    back as adb_back,
    home as adb_home,
    launch_app as adb_launch_app,
    get_current_app as adb_get_current_app,
    type_text as adb_type_text,
    clear_text as adb_clear_text,
    detect_and_set_adb_keyboard,
    get_ui_elements as adb_get_ui_elements,
    find_element_by_text as adb_find_element_by_text,
    find_element_by_resource_id as adb_find_element_by_resource_id,
    find_element_by_index as adb_find_element_by_index,
    format_elements_for_llm,
)

# Global cache for UI elements
_ui_elements_cache: dict = {"elements": [], "timestamp": 0, "mode": "xml"}

# Create MCP Server instance
mcp = FastMCP("PhoneMCP")


# ============================================================================
# Device Management Tools
# ============================================================================


@mcp.tool()
def list_devices() -> Dict[str, Any]:
    """
    列出所有已连接的 Android 设备。
    List all connected Android devices.
    """
    try:
        devices = adb_list_devices()
        device_list = []
        for device in devices:
            device_list.append({
                "device_id": device.device_id,
                "status": device.status,
                "connection_type": device.connection_type.value,
                "model": device.model
            })

        return {
            "status": "success",
            "devices": device_list,
            "count": len(device_list)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def connect_device(address: str, timeout: int = 10) -> Dict[str, Any]:
    """
    连接到远程 Android 设备（通过 WiFi/TCP）。
    Connect to a remote Android device via WiFi/TCP.

    Args:
        address: 设备地址，格式为 "IP:端口" (如 "192.168.1.100:5555")
        timeout: 连接超时时间（秒），默认 10 秒
    """
    try:
        conn = ADBConnection()
        success, message = conn.connect(address, timeout)

        return {
            "status": "success" if success else "error",
            "message": message,
            "address": address
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def disconnect_device(address: Optional[str] = None) -> Dict[str, Any]:
    """
    断开与远程设备的连接。
    Disconnect from a remote device.

    Args:
        address: 要断开的设备地址。如果为空，则断开所有远程设备。
    """
    try:
        conn = ADBConnection()
        success, message = conn.disconnect(address)

        return {
            "status": "success" if success else "error",
            "message": message
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================================
# Screenshot Tools
# ============================================================================


@mcp.tool()
def get_screenshot(
    device_id: Optional[str] = None,
    annotated: bool = False,
) -> MCPImage:
    """
    获取设备屏幕截图。
    Get device screenshot.

    左上角是（0, 0），x轴是往右递增，y轴是往下递增。

    Args:
        device_id: 设备 ID
        annotated: 是否在截图上标注 UI 元素索引。
            设为 True 时，会先获取 UI 元素列表（使用缓存中的 mode），
            然后在截图上用红色方框和数字索引标注每个元素。
            标注后的截图可以配合 tap_element(index=N) 精准点击。
    """
    screenshot = adb_get_screenshot(device_id)

    image_bytes = base64.b64decode(screenshot.base64_data)

    if annotated:
        # Use cached elements if fresh, otherwise fetch new ones
        global _ui_elements_cache
        cache_age = time.time() - _ui_elements_cache.get("timestamp", 0)
        elements = _ui_elements_cache.get("elements", [])
        cached_mode = _ui_elements_cache.get("mode", "xml")

        if cache_age > 30 or not elements:
            elements = adb_get_ui_elements(device_id, clickable_only=False, mode=cached_mode)
            _ui_elements_cache = {
                "elements": elements,
                "timestamp": time.time(),
                "mode": cached_mode,
            }

        from phone_mcp.adb.ocr import draw_annotated_screenshot
        img_bytes = draw_annotated_screenshot(image_bytes, elements)
        return MCPImage(data=img_bytes, format="jpeg")

    img = PILImage.open(io.BytesIO(image_bytes))

    # Convert RGBA to RGB (JPEG doesn't support transparency)
    if img.mode == 'RGBA':
        rgb_img = PILImage.new('RGB', img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[3])
        img = rgb_img
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Compress image
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=60, optimize=True)
    img_bytes = output.getvalue()

    return MCPImage(data=img_bytes, format="jpeg")


# ============================================================================
# Touch Control Tools
# ============================================================================


@mcp.tool()
def tap(x: int, y: int, device_id: Optional[str] = None, delay: float = 1.0) -> Dict[str, Any]:
    """
    在屏幕指定坐标点击。
    Tap at the specified coordinates on the screen.
    """
    try:
        adb_tap(x, y, device_id, delay)
        return {"status": "success", "action": "tap", "x": x, "y": y}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def double_tap(x: int, y: int, device_id: Optional[str] = None, delay: float = 1.0) -> Dict[str, Any]:
    """
    在屏幕指定坐标双击。
    Double tap at the specified coordinates on the screen.
    """
    try:
        adb_double_tap(x, y, device_id, delay)
        return {"status": "success", "action": "double_tap", "x": x, "y": y}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def long_press(
    x: int,
    y: int,
    duration_ms: int = 3000,
    device_id: Optional[str] = None,
    delay: float = 1.0
) -> Dict[str, Any]:
    """
    在屏幕指定坐标长按。
    Long press at the specified coordinates on the screen.
    """
    try:
        adb_long_press(x, y, duration_ms, device_id, delay)
        return {
            "status": "success",
            "action": "long_press",
            "x": x,
            "y": y,
            "duration_ms": duration_ms
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def swipe(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: Optional[int] = None,
    device_id: Optional[str] = None,
    delay: float = 1.0
) -> Dict[str, Any]:
    """
    在屏幕上滑动。
    Swipe from start to end coordinates on the screen.
    """
    try:
        adb_swipe(start_x, start_y, end_x, end_y, duration_ms, device_id, delay)
        return {
            "status": "success",
            "action": "swipe",
            "start": {"x": start_x, "y": start_y},
            "end": {"x": end_x, "y": end_y},
            "duration_ms": duration_ms
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================================
# Input Tools
# ============================================================================


@mcp.tool()
def type_text(
    text: str,
    device_id: Optional[str] = None,
    clear_first: bool = True
) -> Dict[str, Any]:
    """
    在当前聚焦的输入框中输入文本。
    Type text into the currently focused input field.

    Args:
        text: 要输入的文本
        device_id: 设备 ID
        clear_first: 是否先清空输入框（默认 True）

    注意：需要设备已安装 ADB Keyboard。
    """
    try:
        detect_and_set_adb_keyboard(device_id)
        if clear_first:
            adb_clear_text(device_id)
        adb_type_text(text, device_id)

        return {"status": "success", "action": "type_text", "text": text, "cleared": clear_first}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def clear_text(device_id: Optional[str] = None) -> Dict[str, Any]:
    """
    清除当前聚焦输入框中的文本。
    Clear text in the currently focused input field.
    """
    try:
        adb_clear_text(device_id)
        return {"status": "success", "action": "clear_text"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================================
# System Button Tools
# ============================================================================


@mcp.tool()
def press_back(device_id: Optional[str] = None, delay: float = 1.0) -> Dict[str, Any]:
    """
    按下返回键。
    Press the back button.
    """
    try:
        adb_back(device_id, delay)
        return {"status": "success", "action": "back"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def press_home(device_id: Optional[str] = None, delay: float = 1.0) -> Dict[str, Any]:
    """
    按下主页键，返回桌面。
    Press the home button to return to the home screen.
    """
    try:
        adb_home(device_id, delay)
        return {"status": "success", "action": "home"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def press_key(key: str, device_id: Optional[str] = None, delay: float = 0.5) -> Dict[str, Any]:
    """
    发送按键事件。
    Send a key event to the device.

    Args:
        key: 按键名称或键码。常用按键:
            - enter: 回车键
            - tab: Tab键
            - delete: 删除键
            - volume_up: 音量+
            - volume_down: 音量-
            - power: 电源键
            - camera: 相机键
            - menu: 菜单键
            - search: 搜索键
            - media_play_pause: 播放/暂停
            - media_next: 下一曲
            - media_previous: 上一曲
            - 或任意 KEYCODE_* 键码 (如 66 代表 Enter)
        device_id: 设备 ID
        delay: 按键后的延迟（秒）
    """
    try:
        from phone_mcp.adb.device import press_key as adb_press_key
        adb_press_key(key, device_id, delay)
        return {"status": "success", "action": "press_key", "key": key}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================================
# App Control Tools
# ============================================================================


@mcp.tool()
def launch_app(
    app_name: Optional[str] = None,
    package_name: Optional[str] = None,
    device_id: Optional[str] = None,
    delay: float = 1.0
) -> Dict[str, Any]:
    """
    启动指定应用。
    Launch an app by name or package name.

    Args:
        app_name: 应用名称（如"微信"、"Chrome"），支持常见应用
        package_name: 应用包名（如"com.tencent.mm"），支持任意应用
        device_id: 设备 ID
        delay: 启动后的等待时间（秒）

    提示：可以用 search_apps 搜索应用包名
    """
    try:
        if not app_name and not package_name:
            return {
                "status": "error",
                "error": "Must provide either app_name or package_name"
            }

        # 优先使用包名
        if package_name:
            from phone_mcp.adb.device import launch_app_by_package
            success = launch_app_by_package(package_name, device_id, delay)
            if success:
                return {"status": "success", "action": "launch_app", "package_name": package_name}
            else:
                return {"status": "error", "error": f"Failed to launch app: {package_name}"}

        # 使用应用名称
        success = adb_launch_app(app_name, device_id, delay)
        if success:
            return {"status": "success", "action": "launch_app", "app_name": app_name}
        else:
            return {
                "status": "error",
                "error": f"App not found: {app_name}. Use search_apps to find the package name."
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def get_current_app(device_id: Optional[str] = None) -> Dict[str, Any]:
    """
    获取当前前台应用名称。
    Get the name of the currently focused app.
    """
    try:
        app_name = adb_get_current_app(device_id)
        return {"status": "success", "app_name": app_name}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def search_apps(keyword: str, device_id: Optional[str] = None) -> Dict[str, Any]:
    """
    搜索设备上已安装的应用。
    Search for installed apps on the device.

    Args:
        keyword: 搜索关键词（包名或应用名的一部分）

    Returns:
        匹配的应用包名列表
    """
    try:
        from phone_mcp.adb.device import search_installed_apps
        apps = search_installed_apps(keyword, device_id)
        return {
            "status": "success",
            "apps": apps,
            "count": len(apps),
            "hint": "Use launch_app(package_name='...') to launch an app by package name"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================================
# UI Element Tools (Recommended for precise interaction)
# ============================================================================


@mcp.tool()
def get_ui_elements(
    device_id: Optional[str] = None,
    clickable_only: bool = False,
    mode: str = "xml",
) -> Dict[str, Any]:
    """
    获取当前屏幕上的所有 UI 元素列表。
    Get all UI elements on the current screen.

    这是推荐的交互方式：先获取元素列表，然后使用 tap_element 通过索引或文本点击。
    比直接使用坐标点击更准确可靠。

    Args:
        device_id: 设备 ID
        clickable_only: 是否只返回可点击元素（仅 xml 模式有效）
        mode: 元素检测模式，可选值：
            - "xml": 默认模式，使用 uiautomator XML dump，速度快、信息丰富（推荐优先使用）
            - "ocr": OCR 模式，通过截图文字识别检测元素，适用于 WebView、游戏、Flutter 等
              uiautomator 无法获取元素的场景
            - "auto": 自动模式，先尝试 xml，如果失败或返回元素过少则自动切换到 ocr

    提示：
        - 大多数原生 App 使用默认的 "xml" 模式即可
        - 如果发现返回的元素很少或不准确，切换到 "ocr" 或 "auto" 模式
        - OCR 模式需要安装 paddleocr：pip install paddleocr paddlepaddle
    """
    global _ui_elements_cache

    try:
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
            "hint": "Use tap_element(index=N) or tap_element(text='...') to click an element"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def tap_element(
    index: Optional[int] = None,
    text: Optional[str] = None,
    resource_id: Optional[str] = None,
    device_id: Optional[str] = None,
    delay: float = 1.0,
    refresh: bool = False,
) -> Dict[str, Any]:
    """
    通过元素索引、文本或资源ID点击 UI 元素。
    Tap a UI element by index, text, or resource ID.

    这是推荐的点击方式，比直接使用坐标更准确。
    优先使用 index（最快），其次是 text（模糊匹配），最后是 resource_id。
    """
    global _ui_elements_cache

    try:
        cache_age = time.time() - _ui_elements_cache.get("timestamp", 0)
        elements = _ui_elements_cache.get("elements", [])
        cached_mode = _ui_elements_cache.get("mode", "xml")

        if refresh or cache_age > 30 or not elements:
            elements = adb_get_ui_elements(device_id, clickable_only=False, mode=cached_mode)
            _ui_elements_cache = {
                "elements": elements,
                "timestamp": time.time(),
                "mode": cached_mode,
            }

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
        else:
            return {
                "status": "error",
                "error": "Must provide at least one of: index, text, or resource_id"
            }

        if element is None:
            if not refresh:
                elements = adb_get_ui_elements(device_id, clickable_only=False, mode=cached_mode)
                _ui_elements_cache = {
                    "elements": elements,
                    "timestamp": time.time(),
                    "mode": cached_mode,
                }

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
                    "available_count": len(elements)
                }

        x, y = element.center
        adb_tap(x, y, device_id, delay)

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
            "search_method": search_method
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================================
# Utility Tools
# ============================================================================


@mcp.tool()
def wait(seconds: float = 1.0) -> Dict[str, Any]:
    """
    等待指定时间。
    Wait for a specified duration.
    """
    try:
        time.sleep(seconds)
        return {"status": "success", "action": "wait", "seconds": seconds}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================================
# Server Run Function
# ============================================================================


def run(transport: str = "sse", host: str = "0.0.0.0", port: int = 8009, path: str = "/Phone"):
    """Run the MCP server."""
    print("=" * 60)
    print("🚀 Phone MCP Server")
    print("=" * 60)
    print(f"📡 Transport: {transport}")
    print(f"🌐 Host: {host}")
    print(f"🔌 Port: {port}")
    print("=" * 60)
    print("\n📱 Available Tools:")
    print("  - list_devices          列出已连接设备")
    print("  - connect_device        连接远程设备")
    print("  - disconnect_device     断开设备连接")
    print("  - get_screenshot        获取屏幕截图")
    print("  - get_ui_elements       获取UI元素列表 ⭐推荐")
    print("  - tap_element           通过元素点击 ⭐推荐")
    print("  - tap                   坐标点击屏幕")
    print("  - double_tap            双击屏幕")
    print("  - long_press            长按屏幕")
    print("  - swipe                 滑动屏幕")
    print("  - type_text             输入文本")
    print("  - clear_text            清除文本")
    print("  - press_back            按返回键")
    print("  - press_home            按主页键")
    print("  - press_key             发送按键事件")
    print("  - launch_app            启动应用")
    print("  - get_current_app       获取当前应用")
    print("  - search_apps           搜索已安装应用")
    print("  - wait                  等待")
    print("=" * 60)
    print("\n🎯 Starting server...\n")

    mcp.run(transport=transport, host=host, port=port, path=path)


if __name__ == "__main__":
    run()

