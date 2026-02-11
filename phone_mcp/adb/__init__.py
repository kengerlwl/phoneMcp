"""ADB utilities for Android device interaction."""

from phone_mcp.adb.connection import (
    ADBConnection,
    ConnectionType,
    DeviceInfo,
    list_devices,
    quick_connect,
)
from phone_mcp.adb.device import (
    back,
    double_tap,
    get_current_app,
    home,
    launch_app,
    long_press,
    swipe,
    tap,
)
from phone_mcp.adb.input import (
    clear_text,
    detect_and_set_adb_keyboard,
    restore_keyboard,
    type_text,
)
from phone_mcp.adb.screenshot import Screenshot, get_screenshot
from phone_mcp.adb.ui_hierarchy import (
    UIElement,
    find_element_by_index,
    find_element_by_resource_id,
    find_element_by_text,
    format_elements_for_llm,
    get_ui_elements,
    get_ui_hierarchy_xml,
)

__all__ = [
    # Connection
    "ADBConnection",
    "ConnectionType",
    "DeviceInfo",
    "list_devices",
    "quick_connect",
    # Device control
    "tap",
    "double_tap",
    "long_press",
    "swipe",
    "back",
    "home",
    "launch_app",
    "get_current_app",
    # Input
    "type_text",
    "clear_text",
    "detect_and_set_adb_keyboard",
    "restore_keyboard",
    # Screenshot
    "Screenshot",
    "get_screenshot",
    # UI Hierarchy
    "UIElement",
    "get_ui_elements",
    "get_ui_hierarchy_xml",
    "find_element_by_text",
    "find_element_by_resource_id",
    "find_element_by_index",
    "format_elements_for_llm",
]

