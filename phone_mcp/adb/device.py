"""Device control utilities for Android automation."""

import subprocess
import time

from phone_mcp.config.apps import APP_PACKAGES
from phone_mcp.config.timing import TIMING_CONFIG


def get_current_app(device_id: str | None = None) -> str:
    """
    Get the currently focused app name.

    Args:
        device_id: Optional ADB device ID for multi-device setups.

    Returns:
        The app name if recognized, otherwise "System Home".
    """
    adb_prefix = _get_adb_prefix(device_id)

    result = subprocess.run(
        adb_prefix + ["shell", "dumpsys", "window"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    output = result.stdout
    if not output:
        raise ValueError("No output from dumpsys window")

    for line in output.split("\n"):
        if "mCurrentFocus" in line or "mFocusedApp" in line:
            for app_name, package in APP_PACKAGES.items():
                if package in line:
                    return app_name

    return "System Home"


def tap(
    x: int, y: int, device_id: str | None = None, delay: float | None = None
) -> None:
    """Tap at the specified coordinates."""
    if delay is None:
        delay = TIMING_CONFIG.device.default_tap_delay

    adb_prefix = _get_adb_prefix(device_id)

    subprocess.run(
        adb_prefix + ["shell", "input", "tap", str(x), str(y)], capture_output=True
    )
    time.sleep(delay)


def double_tap(
    x: int, y: int, device_id: str | None = None, delay: float | None = None
) -> None:
    """Double tap at the specified coordinates."""
    if delay is None:
        delay = TIMING_CONFIG.device.default_double_tap_delay

    adb_prefix = _get_adb_prefix(device_id)

    subprocess.run(
        adb_prefix + ["shell", "input", "tap", str(x), str(y)], capture_output=True
    )
    time.sleep(TIMING_CONFIG.device.double_tap_interval)
    subprocess.run(
        adb_prefix + ["shell", "input", "tap", str(x), str(y)], capture_output=True
    )
    time.sleep(delay)


def long_press(
    x: int,
    y: int,
    duration_ms: int = 3000,
    device_id: str | None = None,
    delay: float | None = None,
) -> None:
    """Long press at the specified coordinates."""
    if delay is None:
        delay = TIMING_CONFIG.device.default_long_press_delay

    adb_prefix = _get_adb_prefix(device_id)

    subprocess.run(
        adb_prefix
        + ["shell", "input", "swipe", str(x), str(y), str(x), str(y), str(duration_ms)],
        capture_output=True,
    )
    time.sleep(delay)


def swipe(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int | None = None,
    device_id: str | None = None,
    delay: float | None = None,
) -> None:
    """Swipe from start to end coordinates."""
    if delay is None:
        delay = TIMING_CONFIG.device.default_swipe_delay

    adb_prefix = _get_adb_prefix(device_id)

    if duration_ms is None:
        dist_sq = (start_x - end_x) ** 2 + (start_y - end_y) ** 2
        duration_ms = int(dist_sq / 1000)
        duration_ms = max(1000, min(duration_ms, 2000))

    subprocess.run(
        adb_prefix
        + [
            "shell",
            "input",
            "swipe",
            str(start_x),
            str(start_y),
            str(end_x),
            str(end_y),
            str(duration_ms),
        ],
        capture_output=True,
    )
    time.sleep(delay)


def back(device_id: str | None = None, delay: float | None = None) -> None:
    """Press the back button."""
    if delay is None:
        delay = TIMING_CONFIG.device.default_back_delay

    adb_prefix = _get_adb_prefix(device_id)

    subprocess.run(
        adb_prefix + ["shell", "input", "keyevent", "4"], capture_output=True
    )
    time.sleep(delay)


def home(device_id: str | None = None, delay: float | None = None) -> None:
    """Press the home button."""
    if delay is None:
        delay = TIMING_CONFIG.device.default_home_delay

    adb_prefix = _get_adb_prefix(device_id)

    subprocess.run(
        adb_prefix + ["shell", "input", "keyevent", "KEYCODE_HOME"], capture_output=True
    )
    time.sleep(delay)


def launch_app(
    app_name: str, device_id: str | None = None, delay: float | None = None
) -> bool:
    """
    Launch an app by name.

    Uses am start with the launcher activity to reliably start apps.
    Falls back to monkey command if am start fails.
    """
    if delay is None:
        delay = TIMING_CONFIG.device.default_launch_delay

    if app_name not in APP_PACKAGES:
        return False

    adb_prefix = _get_adb_prefix(device_id)
    package = APP_PACKAGES[app_name]

    # 方法1：使用 am start 启动应用的启动器活动（更可靠）
    # 先获取应用的 launcher activity
    result = subprocess.run(
        adb_prefix + [
            "shell",
            "cmd", "package", "resolve-activity",
            "--brief",
            "-c", "android.intent.category.LAUNCHER",
            package,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    activity = None
    if result.returncode == 0 and result.stdout.strip():
        # 解析输出，格式通常是 "priority=0 preferredOrder=0 match=0x108000 specificIndex=-1 isDefault=true\ncom.package.name/.ActivityName"
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if '/' in line and not line.startswith('priority'):
                activity = line.strip()
                break

    if activity:
        # 使用 am start 启动具体的 activity
        result = subprocess.run(
            adb_prefix + [
                "shell",
                "am", "start",
                "-n", activity,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode == 0 and "Error" not in result.stdout:
            time.sleep(delay)
            return True

    # 方法2：使用 am start 通过 intent 启动（备选方案）
    result = subprocess.run(
        adb_prefix + [
            "shell",
            "am", "start",
            "-a", "android.intent.action.MAIN",
            "-c", "android.intent.category.LAUNCHER",
            "-n", f"{package}/.MainActivity",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    # 检查是否成功
    if result.returncode == 0 and "Error" not in result.stdout:
        time.sleep(delay)
        return True

    # 方法3：使用 monkey 命令作为最后的备选方案
    subprocess.run(
        adb_prefix + [
            "shell",
            "monkey",
            "-p", package,
            "-c", "android.intent.category.LAUNCHER",
            "1",
        ],
        capture_output=True,
    )
    time.sleep(delay)
    return True


def launch_app_by_package(
    package: str, device_id: str | None = None, delay: float | None = None
) -> bool:
    """
    Launch an app by package name.

    Args:
        package: The package name (e.g., "com.tencent.mm")
        device_id: Optional ADB device ID
        delay: Delay after launching

    Returns:
        True if launch succeeded, False otherwise
    """
    if delay is None:
        delay = TIMING_CONFIG.device.default_launch_delay

    adb_prefix = _get_adb_prefix(device_id)

    # 方法1：获取并启动 launcher activity
    result = subprocess.run(
        adb_prefix + [
            "shell",
            "cmd", "package", "resolve-activity",
            "--brief",
            "-c", "android.intent.category.LAUNCHER",
            package,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    activity = None
    if result.returncode == 0 and result.stdout.strip():
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if '/' in line and not line.startswith('priority'):
                activity = line.strip()
                break

    if activity:
        result = subprocess.run(
            adb_prefix + ["shell", "am", "start", "-n", activity],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode == 0 and "Error" not in result.stdout:
            time.sleep(delay)
            return True

    # 方法2：使用 monkey 命令
    result = subprocess.run(
        adb_prefix + [
            "shell", "monkey",
            "-p", package,
            "-c", "android.intent.category.LAUNCHER",
            "1",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    time.sleep(delay)
    return "No activities found" not in result.stdout


def search_installed_apps(keyword: str, device_id: str | None = None) -> list[str]:
    """
    Search for installed apps matching a keyword.

    Args:
        keyword: Search keyword (matches package name)
        device_id: Optional ADB device ID

    Returns:
        List of matching package names
    """
    adb_prefix = _get_adb_prefix(device_id)

    result = subprocess.run(
        adb_prefix + ["shell", "pm", "list", "packages"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if result.returncode != 0:
        return []

    packages = []
    keyword_lower = keyword.lower()
    for line in result.stdout.strip().split('\n'):
        if line.startswith('package:'):
            pkg = line[8:]  # Remove "package:" prefix
            if keyword_lower in pkg.lower():
                packages.append(pkg)

    return packages


# 常用按键映射
KEY_MAP = {
    "enter": "66",
    "tab": "61",
    "delete": "67",
    "backspace": "67",
    "space": "62",
    "escape": "111",
    "esc": "111",
    "volume_up": "24",
    "volume_down": "25",
    "volume_mute": "164",
    "power": "26",
    "camera": "27",
    "menu": "82",
    "search": "84",
    "media_play_pause": "85",
    "media_stop": "86",
    "media_next": "87",
    "media_previous": "88",
    "media_rewind": "89",
    "media_fast_forward": "90",
    "mute": "91",
    "page_up": "92",
    "page_down": "93",
    "dpad_up": "19",
    "dpad_down": "20",
    "dpad_left": "21",
    "dpad_right": "22",
    "dpad_center": "23",
}


def press_key(key: str, device_id: str | None = None, delay: float = 0.5) -> None:
    """
    Send a key event to the device.

    Args:
        key: Key name (e.g., "enter", "volume_up") or keycode number
        device_id: Optional ADB device ID
        delay: Delay after pressing the key
    """
    adb_prefix = _get_adb_prefix(device_id)

    # 转换按键名称为键码
    key_lower = key.lower().strip()
    keycode = KEY_MAP.get(key_lower, key)

    # 如果不是数字，尝试添加 KEYCODE_ 前缀
    if not keycode.isdigit():
        keycode = f"KEYCODE_{keycode.upper()}"

    subprocess.run(
        adb_prefix + ["shell", "input", "keyevent", keycode],
        capture_output=True,
    )
    time.sleep(delay)


def _get_adb_prefix(device_id: str | None) -> list:
    """Get ADB command prefix with optional device specifier."""
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]

