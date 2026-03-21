---
name: phone-mcp
description: "Android phone automation via CLI. Use when the user needs to control their Android phone, including tapping buttons, typing text, launching apps, taking screenshots, swiping, or any phone operation task. Trigger words: 操作手机、控制手机、手机截图、打开App、发消息、phone、android、手机自动化。"
---

# Android Phone Automation with PhoneMCP

Control Android devices via ADB through a single CLI executable. No MCP server needed.

> **Prerequisites**: Android device connected via USB or WiFi with USB debugging enabled.

## Platform-Specific Binary Path

The `phone-mcp` binary is located in the same directory as this SKILL.md file:

```bash
# macOS / Linux
<SKILL_DIR>/phone-mcp run '{"action":"list_devices"}'

# Windows (CMD)
<SKILL_DIR>\phone-mcp.exe run "{\"action\":\"list_devices\"}"

# Windows (PowerShell)
$json = '{\"action\":\"list_devices\"}'; & "<SKILL_DIR>\phone-mcp.exe" run $json
```

> Replace `<SKILL_DIR>` with the actual directory path where this skill is installed (e.g., `~/.catpaw/skills/phone-mcp` or `~/.claude/skills/phone-mcp`).

## Core Workflow

Every phone automation follows this pattern:

1. **Get UI Elements**: `{"action":"get_ui_elements"}` — get all interactive elements on screen
2. **Interact**: Use element index or text to tap, type, etc.
3. **Re-get UI Elements**: After any screen change, get fresh elements

```bash
# Step 1: See what's on screen
<SKILL_DIR>/phone-mcp run '{"action":"get_ui_elements"}'
# Output includes formatted element list with index, text, bounds, clickable status

# Step 2: Tap an element by text
<SKILL_DIR>/phone-mcp run '{"action":"tap_element","text":"微信"}'

# Step 3: After screen changes, get fresh elements
<SKILL_DIR>/phone-mcp run '{"action":"get_ui_elements"}'
```

## Batch Execution

Pass a JSON array to run multiple commands sequentially. **Stops on first failure.**

```bash
<SKILL_DIR>/phone-mcp run '[{"action":"launch_app","name":"微信"},{"action":"wait","seconds":2},{"action":"get_ui_elements"}]'
```

**When to batch**: `launch_app + wait + get_ui_elements`, `tap + wait`, `type_text + key` — any sequence where you don't need intermediate output.

**When NOT to batch**: `get_ui_elements` (you need the output to decide next action), `screenshot` (you need to see the image).

## Essential Commands

```bash
# --- Device Management ---
<SKILL_DIR>/phone-mcp run '{"action":"list_devices"}'
<SKILL_DIR>/phone-mcp run '{"action":"connect","address":"192.168.1.100:5555"}'
<SKILL_DIR>/phone-mcp run '{"action":"disconnect"}'

# --- Screenshot ---
<SKILL_DIR>/phone-mcp run '{"action":"screenshot"}'
# Returns: {"status":"success","path":"/tmp/phone-mcp-screenshot-xxxx.jpg","width":1080,"height":2400}
# Use the returned path to view the image

<SKILL_DIR>/phone-mcp run '{"action":"screenshot","path":"/tmp/my-screenshot.jpg"}'
# Save to specific path

# --- UI Elements (⭐ Recommended interaction method) ---
<SKILL_DIR>/phone-mcp run '{"action":"get_ui_elements"}'
<SKILL_DIR>/phone-mcp run '{"action":"get_ui_elements","clickable_only":true}'
<SKILL_DIR>/phone-mcp run '{"action":"get_ui_elements","mode":"ocr"}'

# --- Tap Element (⭐ Recommended, more reliable than coordinates) ---
<SKILL_DIR>/phone-mcp run '{"action":"tap_element","index":5}'
<SKILL_DIR>/phone-mcp run '{"action":"tap_element","text":"发送"}'
<SKILL_DIR>/phone-mcp run '{"action":"tap_element","resource_id":"send_button"}'

# --- Coordinate Tap ---
<SKILL_DIR>/phone-mcp run '{"action":"tap","x":540,"y":1200}'
<SKILL_DIR>/phone-mcp run '{"action":"double_tap","x":540,"y":1200}'

# --- Swipe ---
<SKILL_DIR>/phone-mcp run '{"action":"swipe","start_x":540,"start_y":1800,"end_x":540,"end_y":600}'

# --- Text Input ---
<SKILL_DIR>/phone-mcp run '{"action":"type_text","text":"Hello 你好"}'
<SKILL_DIR>/phone-mcp run '{"action":"type_text","text":"新文本","clear_first":true}'
<SKILL_DIR>/phone-mcp run '{"action":"clear_text"}'

# --- System Keys ---
<SKILL_DIR>/phone-mcp run '{"action":"back"}'
<SKILL_DIR>/phone-mcp run '{"action":"home"}'
<SKILL_DIR>/phone-mcp run '{"action":"key","key":"enter"}'
<SKILL_DIR>/phone-mcp run '{"action":"key","key":"volume_up"}'

# --- App Control ---
<SKILL_DIR>/phone-mcp run '{"action":"launch_app","name":"微信"}'
<SKILL_DIR>/phone-mcp run '{"action":"launch_app","package":"com.tencent.mm"}'
<SKILL_DIR>/phone-mcp run '{"action":"current_app"}'
<SKILL_DIR>/phone-mcp run '{"action":"search_apps","keyword":"tencent"}'

# --- Wait ---
<SKILL_DIR>/phone-mcp run '{"action":"wait","seconds":2}'
```

## Common Patterns

### Open App and Navigate

```bash
# Launch WeChat
<SKILL_DIR>/phone-mcp run '{"action":"launch_app","name":"微信"}'
<SKILL_DIR>/phone-mcp run '{"action":"wait","seconds":2}'
<SKILL_DIR>/phone-mcp run '{"action":"get_ui_elements"}'
# Read the element list, find the target, then tap
<SKILL_DIR>/phone-mcp run '{"action":"tap_element","text":"通讯录"}'
```

### Send a Message

```bash
# 1. Launch app and wait
<SKILL_DIR>/phone-mcp run '[{"action":"launch_app","name":"微信"},{"action":"wait","seconds":2}]'

# 2. Get elements and find search
<SKILL_DIR>/phone-mcp run '{"action":"get_ui_elements"}'
<SKILL_DIR>/phone-mcp run '{"action":"tap_element","text":"搜索"}'
<SKILL_DIR>/phone-mcp run '{"action":"wait","seconds":1}'

# 3. Type contact name and select
<SKILL_DIR>/phone-mcp run '{"action":"type_text","text":"张三"}'
<SKILL_DIR>/phone-mcp run '{"action":"wait","seconds":1}'
<SKILL_DIR>/phone-mcp run '{"action":"get_ui_elements"}'
<SKILL_DIR>/phone-mcp run '{"action":"tap_element","text":"张三"}'
<SKILL_DIR>/phone-mcp run '{"action":"wait","seconds":1}'

# 4. Type message and send
<SKILL_DIR>/phone-mcp run '{"action":"get_ui_elements"}'
# Find the input box and type
<SKILL_DIR>/phone-mcp run '{"action":"tap_element","resource_id":"edittext"}'
<SKILL_DIR>/phone-mcp run '{"action":"type_text","text":"你好，明天见！"}'
<SKILL_DIR>/phone-mcp run '{"action":"tap_element","text":"发送"}'
```

### Search in an App

```bash
<SKILL_DIR>/phone-mcp run '[{"action":"launch_app","name":"淘宝"},{"action":"wait","seconds":3}]'
<SKILL_DIR>/phone-mcp run '{"action":"get_ui_elements"}'
<SKILL_DIR>/phone-mcp run '{"action":"tap_element","text":"搜索"}'
<SKILL_DIR>/phone-mcp run '{"action":"type_text","text":"iPhone 手机壳"}'
<SKILL_DIR>/phone-mcp run '{"action":"key","key":"enter"}'
```

### Scroll and Browse

```bash
# Scroll down to see more content
<SKILL_DIR>/phone-mcp run '{"action":"swipe","start_x":540,"start_y":1800,"end_x":540,"end_y":600}'
<SKILL_DIR>/phone-mcp run '{"action":"get_ui_elements"}'

# Scroll up
<SKILL_DIR>/phone-mcp run '{"action":"swipe","start_x":540,"start_y":600,"end_x":540,"end_y":1800}'
```

### Take Screenshot and Analyze

```bash
# Take a screenshot
<SKILL_DIR>/phone-mcp run '{"action":"screenshot"}'
# Response: {"status":"success","path":"/tmp/phone-mcp-screenshot-abc123.jpg",...}
# Then read the image file at the returned path to see what's on screen
```

## UI Element Detection Modes

| Mode | When to Use |
|------|------------|
| `"xml"` (default) | Native Android apps — fast and accurate |
| `"ocr"` | WebView, games, Flutter, or any app where xml returns few elements |
| `"auto"` | Auto-detect: tries xml first, falls back to ocr if too few elements |

```bash
# Default XML mode (recommended for most apps)
<SKILL_DIR>/phone-mcp run '{"action":"get_ui_elements"}'

# OCR mode (for web views, games, etc.)
<SKILL_DIR>/phone-mcp run '{"action":"get_ui_elements","mode":"ocr"}'

# Auto mode
<SKILL_DIR>/phone-mcp run '{"action":"get_ui_elements","mode":"auto"}'
```

## Key Name Reference

For `{"action":"key","key":"<name>"}`:

| Key Name | Description |
|----------|-------------|
| `enter` | Enter/Confirm |
| `back` | Back (same as `{"action":"back"}`) |
| `delete` | Delete/Backspace |
| `tab` | Tab |
| `space` | Space |
| `volume_up` / `volume_down` | Volume |
| `power` | Power button |
| `camera` | Camera |
| `media_play_pause` / `media_next` / `media_previous` | Media controls |
| `dpad_up` / `dpad_down` / `dpad_left` / `dpad_right` | D-pad navigation |

## Multi-Device Support

All commands support an optional `device_id` parameter for multi-device setups:

```bash
# List all devices first
<SKILL_DIR>/phone-mcp run '{"action":"list_devices"}'
# Response: {"devices":[{"device_id":"R5CR1234","status":"device","model":"SM-S9080"},...]}

# Target a specific device
<SKILL_DIR>/phone-mcp run '{"action":"screenshot","device_id":"R5CR1234"}'
<SKILL_DIR>/phone-mcp run '{"action":"tap_element","text":"微信","device_id":"R5CR1234"}'
```

## Stdin Support

Pipe JSON commands via stdin using `-`:

```bash
echo '{"action":"list_devices"}' | <SKILL_DIR>/phone-mcp run -
cat commands.json | <SKILL_DIR>/phone-mcp run -
```

## Error Handling

All commands return JSON with a `status` field:

```json
{"status": "success", ...}
{"status": "error", "error": "Element not found with text='xxx'"}
```

Common errors and solutions:

- **Element not found** → Run `get_ui_elements` first to refresh, check if the text/index is correct
- **No devices found** → Check USB connection, run `list_devices` to verify
- **Screenshot failed** → Device may be on a secure screen (e.g., banking app), try again
- **get_ui_elements returns few elements** → Switch to `"mode":"ocr"` for WebView/game/Flutter apps

## Tips

- **Always use `get_ui_elements` + `tap_element`** instead of coordinate tapping — it's more reliable across different devices and screen sizes.
- **Batch non-interactive commands** to reduce round-trips (e.g., `launch_app + wait`).
- **Re-get UI elements** after every screen transition (tap, swipe, navigation).
- **Use OCR mode** when the default XML mode doesn't detect enough elements.
- **Add `wait` commands** after launching apps or navigating (apps need time to load).
- Screenshots are saved as JPEG files. The returned `path` can be used to view the image.

