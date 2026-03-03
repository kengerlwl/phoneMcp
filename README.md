# 📱 PhoneMCP — Let AI Control Your Phone

<p align="center">
  <strong>通过 MCP 协议让 AI 助手直接操控你的 Android 手机</strong>
</p>

<p align="center">
  <a href="https://github.com/kengerlwl/phoneMcp/releases"><img src="https://img.shields.io/github/v/release/kengerlwl/phoneMcp?style=flat-square" alt="Release"></a>
  <a href="https://github.com/kengerlwl/phoneMcp/blob/main/LICENSE"><img src="https://img.shields.io/github/license/kengerlwl/phoneMcp?style=flat-square" alt="License"></a>
  <a href="https://github.com/kengerlwl/phoneMcp/stargazers"><img src="https://img.shields.io/github/stars/kengerlwl/phoneMcp?style=flat-square" alt="Stars"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square" alt="Python"></a>
</p>

---

PhoneMCP 是一个基于 [MCP（Model Context Protocol）](https://modelcontextprotocol.io/) 的 Android 设备控制服务器。它通过 ADB 将 Android 手机的操作能力暴露为标准 MCP 工具，让 Claude、Cursor、CatPaw 等 AI 助手可以**直接看到你的手机屏幕、点击按钮、输入文字、打开 App** —— 就像一个真正的 AI 助手在帮你操作手机。

## ✨ 功能特性

- 📸 **截图** — 获取手机实时屏幕截图，支持 UI 元素标注
- 👆 **触控** — 点击、双击、滑动
- ⌨️ **输入** — 输入文本（完美支持中文），清除文本
- 🏠 **按键** — 返回、主页、音量、电源等系统按键
- 📱 **应用** — 启动应用、搜索已安装应用、获取当前应用
- 🎯 **UI 元素识别** — 智能获取屏幕 UI 元素列表，通过索引/文本精准点击（推荐）
- 🔍 **OCR 模式** — 针对 WebView / 游戏 / Flutter 等场景，支持 OCR 文字识别
- 📡 **多设备** — 支持 USB 和 WiFi 连接，可同时管理多台设备

## 🚀 快速开始

### 前置要求

1. 安装 [ADB](https://developer.android.com/tools/adb) 并添加到 PATH
2. Android 手机通过 USB 连接电脑（或通过 WiFi 连接）
3. 手机开启 **USB 调试**（开发者选项中）

### 方式一：下载可执行文件（推荐，开箱即用）

从 [Releases 页面](https://github.com/kengerlwl/phoneMcp/releases) 下载对应平台的文件：

| 平台 | 文件 |
|------|------|
| 🐧 Linux | `phone-mcp-linux-amd64` |
| 🪟 Windows | `phone-mcp-windows-amd64.exe` |
| 🍎 macOS (Apple Silicon) | `phone-mcp-macos-arm64` |

下载后直接运行：

```bash
# macOS / Linux
chmod +x phone-mcp-macos-arm64
./phone-mcp-macos-arm64

# Windows
phone-mcp-windows-amd64.exe
```

### 方式二：pip 安装

```bash
pip install -r requirements.txt
```

然后运行：

```bash
python -m phone_mcp
# 或
phone-mcp
```

### 方式三：从源码运行

```bash
git clone https://github.com/kengerlwl/phoneMcp.git
cd phoneMcp
pip install -r requirements.txt
python main.py
```

## 🔧 配置 AI 助手

PhoneMCP 启动后，你需要在 AI 客户端（Claude Desktop / Cursor / CatPaw 等）中添加 MCP 服务器配置。

### SSE 模式（默认，推荐）

启动服务：

```bash
./phone-mcp-macos-arm64
# 默认监听 http://0.0.0.0:8009
```

在 MCP 客户端配置中添加：

```json
{
  "mcpServers": {
    "phone-mcp": {
      "url": "http://localhost:8009/Phone/sse"
    }
  }
}
```

### STDIO 模式

适用于 Claude Desktop 等直接调用可执行文件的场景：

```json
{
  "mcpServers": {
    "phone-mcp": {
      "command": "/path/to/phone-mcp-macos-arm64",
      "args": ["--transport", "stdio"]
    }
  }
}
```

## 📖 命令行参数

```
phone-mcp [选项]

选项：
  -t, --transport TYPE   传输模式: sse 或 stdio（默认: sse）
  -H, --host HOST        监听地址（默认: 0.0.0.0）
  -p, --port PORT        监听端口（默认: 8009）
  --path PATH            MCP 路径（默认: /Phone）
  --guide                显示详细使用指南
```

## 🛠️ 提供的 MCP 工具

| 工具 | 说明 |
|------|------|
| `list_devices` | 列出已连接设备 |
| `connect_device` | 连接远程设备（WiFi/TCP） |
| `disconnect_device` | 断开设备连接 |
| `get_screenshot` | 获取屏幕截图（支持 UI 标注） |
| `get_ui_elements` | 获取 UI 元素列表 ⭐ |
| `tap_element` | 通过索引/文本/ID 点击元素 ⭐ |
| `tap` | 坐标点击 |
| `double_tap` | 双击 |
| `swipe` | 滑动 |
| `type_text` | 输入文本（支持中文） |
| `clear_text` | 清除文本 |
| `press_back` | 返回键 |
| `press_home` | 主页键 |
| `press_key` | 发送任意按键 |
| `launch_app` | 启动应用 |
| `get_current_app` | 获取当前应用 |
| `search_apps` | 搜索已安装应用 |
| `wait` | 等待 |

> 💡 **推荐工作流**：先调用 `get_ui_elements` 获取屏幕元素，再用 `tap_element` 精准点击，比直接使用坐标更可靠。

## 💬 使用示例

连接好手机后，你可以在 AI 助手中直接用自然语言操作手机：

- *"帮我打开微信，给张三发一条消息说'明天见'"*
- *"截个屏看看手机现在的界面"*
- *"打开设置，把 WiFi 关掉"*
- *"打开淘宝搜索 iPhone 手机壳"*
- *"帮我看看手机上装了哪些应用"*

AI 助手会自动调用 PhoneMCP 的工具来完成这些操作。

## ⭐ 支持项目

如果 PhoneMCP 对你有帮助，请给个 **Star** ⭐ 支持一下！

[![Star History Chart](https://api.star-history.com/svg?repos=kengerlwl/phoneMcp&type=Date)](https://star-history.com/#kengerlwl/phoneMcp&Date)

## 📄 License

[MIT](LICENSE)

