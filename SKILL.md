---
name: phone-mcp
description: "Android phone automation via CLI. Use when the user needs to control their Android phone, including tapping buttons, typing text, launching apps, taking screenshots, swiping, or any phone operation task. Trigger words: 操作手机、控制手机、手机截图、打开App、发消息、phone、android、手机自动化。"
---

# Android Phone Automation with PhoneMCP

Control Android devices via ADB through a single CLI executable. No MCP server needed.

> **Prerequisites**: Android device connected via USB or WiFi with USB debugging enabled.

## Binary Path

The `phone-mcp` binary is in the **same directory as this SKILL.md file**. Determine the absolute path of this SKILL.md's parent directory and use it as the binary path. For example, if this file is at `~/.catpaw/skills/phone-mcp/SKILL.md`, then the binary is `~/.catpaw/skills/phone-mcp/phone-mcp`.

On Windows, the binary is `phone-mcp.exe` in the same directory.

## Step 0: Always Check Device First

Before any phone operation, verify a device is connected:

```bash
<BIN> run '{"action":"list_devices"}'
```

If `"count": 0`, tell the user to connect their Android phone via USB and enable USB debugging. **Do not proceed without a connected device.**

## Core Workflow

Every phone automation follows this loop:

1. **Observe**: `get_ui_elements` to see what's on screen (structured text data)
2. **Act**: `tap_element`, `type_text`, `swipe`, etc.
3. **Re-observe**: After any action that changes the screen, call `get_ui_elements` again

```bash
# 1. Observe — see what's on screen
<BIN> run '{"action":"get_ui_elements"}'
# Output: list of elements with index, text, bounds, clickable status

# 2. Act — tap an element by its text
<BIN> run '{"action":"tap_element","text":"微信"}'

# 3. Re-observe — screen changed, get fresh elements
<BIN> run '{"action":"get_ui_elements"}'
```

### When to use `screenshot` vs `get_ui_elements`

| Situation | Use |
|-----------|-----|
| Need to decide what to tap/interact with | `get_ui_elements` (structured, reliable) |
| Need to see the visual layout / verify result | `screenshot` (returns image file path) |
| `get_ui_elements` returns very few elements | `screenshot` + `get_ui_elements` with `"mode":"ocr"` |
| User asks "show me the screen" | `screenshot` |

**Prefer `get_ui_elements` for decision-making.** Use `screenshot` for visual verification or when you need spatial context.

## Batch Execution

Pass a JSON array for sequential commands. **Stops on first failure.**

```bash
<BIN> run '[{"action":"launch_app","name":"微信"},{"action":"wait","seconds":2},{"action":"get_ui_elements"}]'
```

**Batch** when you don't need intermediate output: `launch_app + wait`, `tap + wait`, `type_text + key`.
**Don't batch** `get_ui_elements` or `screenshot` — you need their output to decide the next step.

## Command Reference

### Device Management

```bash
<BIN> run '{"action":"list_devices"}'
<BIN> run '{"action":"connect","address":"192.168.1.100:5555"}'
<BIN> run '{"action":"disconnect"}'
```

### Observe Screen

```bash
# Structured element list (preferred for interaction)
<BIN> run '{"action":"get_ui_elements"}'
<BIN> run '{"action":"get_ui_elements","clickable_only":true}'
<BIN> run '{"action":"get_ui_elements","mode":"ocr"}'     # For WebView/games/Flutter

# Visual screenshot (saved to file, returns path)
<BIN> run '{"action":"screenshot"}'
<BIN> run '{"action":"screenshot","path":"/tmp/my-screenshot.jpg"}'
```

### Interact with Elements (⭐ Preferred)

```bash
<BIN> run '{"action":"tap_element","index":5}'              # By index from get_ui_elements
<BIN> run '{"action":"tap_element","text":"发送"}'           # By visible text (fuzzy match)
<BIN> run '{"action":"tap_element","resource_id":"send_btn"}' # By resource ID
```

### Coordinate-Based Actions

```bash
<BIN> run '{"action":"tap","x":540,"y":1200}'
<BIN> run '{"action":"double_tap","x":540,"y":1200}'
<BIN> run '{"action":"swipe","start_x":540,"start_y":1800,"end_x":540,"end_y":600}'  # Scroll down
<BIN> run '{"action":"swipe","start_x":540,"start_y":600,"end_x":540,"end_y":1800}'  # Scroll up
```

### Text Input

```bash
<BIN> run '{"action":"type_text","text":"Hello 你好"}'            # Type (clears input first by default)
<BIN> run '{"action":"type_text","text":"追加文本","clear_first":false}'  # Append without clearing
<BIN> run '{"action":"clear_text"}'
```

### System Keys

```bash
<BIN> run '{"action":"back"}'
<BIN> run '{"action":"home"}'
<BIN> run '{"action":"key","key":"enter"}'
<BIN> run '{"action":"key","key":"volume_up"}'
```

Key names: `enter`, `delete`, `tab`, `space`, `volume_up`, `volume_down`, `power`, `camera`, `media_play_pause`, `media_next`, `media_previous`, `dpad_up`, `dpad_down`, `dpad_left`, `dpad_right`.

### App Control

```bash
<BIN> run '{"action":"launch_app","name":"微信"}'            # By common name
<BIN> run '{"action":"launch_app","package":"com.tencent.mm"}'  # By package name
<BIN> run '{"action":"current_app"}'
<BIN> run '{"action":"search_apps","keyword":"tencent"}'     # Find package names
```

### Wait

```bash
<BIN> run '{"action":"wait","seconds":2}'
```

## UI Element Detection Modes

| Mode | Best For |
|------|----------|
| `"xml"` (default) | Native Android apps — fast and structured |
| `"ocr"` | WebView, games, Flutter, or when xml returns too few elements |
| `"auto"` | Auto: tries xml first, falls back to ocr |

## Multi-Device

All commands accept optional `"device_id"` parameter:

```bash
<BIN> run '{"action":"list_devices"}'
# → {"devices":[{"device_id":"R5CR1234","model":"SM-S9080"},...]}

<BIN> run '{"action":"screenshot","device_id":"R5CR1234"}'
```

## Error Handling

All responses are JSON with `"status": "success"` or `"status": "error"`.

| Error | Solution |
|-------|----------|
| Element not found | Run `get_ui_elements` to refresh, verify text/index |
| No devices | Check USB, run `list_devices` |
| Few elements detected | Switch to `"mode":"ocr"` |
| Screenshot failed | Device may be on secure screen, retry |

## Key Rules

1. **Always `get_ui_elements` before interacting** — never guess coordinates or element names.
2. **Always re-observe after screen changes** — tap, swipe, navigation all invalidate previous elements.
3. **Prefer `tap_element` over `tap`** — text/index-based tapping is more reliable than coordinates.
4. **Add `wait` after launching apps** — apps need 1-3 seconds to load.
5. **Don't hardcode UI flows** — different phones have different UI. Always read `get_ui_elements` output and adapt.

