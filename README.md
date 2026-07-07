[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/kengerlwl-phonemcp-badge.png)](https://mseep.ai/app/kengerlwl-phonemcp)

# 📱 PhoneMCP — Let AI Control Your Phone

<p align="center">
  <strong>让 AI 助手直接操控你的 Android 手机 —— 支持 Skill 和 MCP 两种接入方式</strong>
</p>

<p align="center">
  <a href="https://github.com/kengerlwl/phoneMcp/releases"><img src="https://img.shields.io/github/v/release/kengerlwl/phoneMcp?style=flat-square" alt="Release"></a>
  <a href="https://github.com/kengerlwl/phoneMcp/blob/main/LICENSE"><img src="https://img.shields.io/github/license/kengerlwl/phoneMcp?style=flat-square" alt="License"></a>
  <a href="https://github.com/kengerlwl/phoneMcp/stargazers"><img src="https://img.shields.io/github/stars/kengerlwl/phoneMcp?style=flat-square" alt="Stars"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square" alt="Python"></a>
</p>

<p align="center">
  <a href="https://www.bilibili.com/video/BV1vgcizLEaw/">📺 完整演示视频</a> ·
  <a href="https://b23.tv/tIW7mVP">🎬 快速上手教程</a>
</p>

---

## 🎬 演示

> 用自然语言让 AI 帮你操作手机 —— 打开 App、发消息、搜索商品，一句话搞定。

[![演示视频](https://i2.hdslb.com/bfs/archive/7f854a8e4160da37e191cf3700c63cc5448bdb71.jpg)](https://www.bilibili.com/video/BV1vgcizLEaw/)

▶️ [点击观看完整演示视频](https://www.bilibili.com/video/BV1vgcizLEaw/) | [31 秒快速上手](https://b23.tv/tIW7mVP)

---

## 💡 这是什么？

PhoneMCP 是一个 **AI 手机操控工具**，通过 ADB 让 AI 助手能够**直接看到你的手机屏幕、点击按钮、输入文字、打开 App** —— 就像一个真正的助手在帮你操作手机。

提供**两种接入方式**，适配不同的 AI 客户端生态：

| 方式 | 适合场景 | 是否需要配置 |
|------|---------|-------------|
| **⭐ Skill 模式（推荐）** | CatPaw、Claude Code 等支持 Skill 的客户端 | **零配置**，下载解压即用 |
| **MCP 模式** | Claude Desktop、Cursor 等 MCP 客户端 | 需要配置 MCP 服务器地址 |

## 🏗️ 工作原理

```
┌─────────────────────────────────────────────────────────┐
│                      你的电脑                            │
│                                                         │
│  ┌──────────────┐              ┌──────────────────┐    │
│  │  AI 助手      │  Skill/CLI  │   PhoneMCP       │    │
│  │              │ ──────────► │                  │    │
│  │ · CatPaw    │   或 MCP     │  截图 / 点击      │    │
│  │ · Claude    │              │  输入 / 滑动      │    │
│  │ · Cursor    │              │  启动App / ...    │    │
│  │ · ...       │              │                  │    │
│  └──────────────┘              └────────┬─────────┘    │
│                                         │ ADB          │
└─────────────────────────────────────────┼───────────────┘
                                          │
                                   USB / WiFi
                                          │
                                ┌─────────▼─────────┐
                                │   Android 手机     │
                                │                   │
                                │  📱 屏幕截图       │
                                │  👆 触控操作       │
                                │  ⌨️ 文本输入       │
                                │  📦 应用管理       │
                                └───────────────────┘
```

## ✨ 功能特性

- 📸 **截图** — 获取手机实时屏幕截图
- 👆 **触控** — 点击、双击、滑动
- ⌨️ **输入** — 输入文本（完美支持中文），清除文本
- 🏠 **按键** — 返回、主页、音量、电源等系统按键
- 📱 **应用** — 启动应用、搜索已安装应用、获取当前应用
- 🎯 **UI 元素识别** — 智能获取屏幕 UI 元素列表，通过索引/文本精准点击（推荐）
- 🔍 **OCR 模式** — 针对 WebView / 游戏 / Flutter 等场景，支持 OCR 文字识别
- 📡 **多设备** — 支持 USB 和 WiFi 连接，可同时管理多台设备

## 🚀 快速开始

### 前置要求

1. Android 手机通过 USB 连接电脑（或通过 WiFi 连接）
2. 手机开启 **USB 调试**（见下方教程）

> 💡 使用可执行文件时**无需安装 ADB**，已内嵌。

<details>
<summary>📱 <strong>手机端开启 USB 调试教程（点击展开）</strong></summary>

#### 第一步：开启开发者选项

1. 打开手机 **设置**
2. 进入 **关于手机**（部分手机在「设置 > 系统 > 关于手机」）
3. 连续点击 **版本号** 7 次，直到出现「您已进入开发者模式」的提示

> 💡 不同品牌的路径可能略有差异：
> - **小米/红米**：设置 → 我的设备 → 全部参数与信息 → 连续点击「MIUI 版本」
> - **华为/荣耀**：设置 → 关于手机 → 连续点击「版本号」
> - **OPPO/realme**：设置 → 关于手机 → 连续点击「版本号」
> - **vivo/iQOO**：设置 → 关于手机 → 连续点击「软件版本号」
> - **三星**：设置 → 关于手机 → 软件信息 → 连续点击「编译编号」
> - **一加**：设置 → 关于本机 → 连续点击「版本号」

#### 第二步：开启 USB 调试

1. 返回 **设置** 主页
2. 进入 **系统** → **开发者选项**（部分手机直接在设置列表底部）
3. 打开 **USB 调试** 开关
4. 如果有 **USB 安装** 和 **USB 调试（安全设置）**，也一并打开

#### 第三步：连接电脑并授权

1. 用 USB 数据线连接手机和电脑
2. 手机上会弹出「**允许 USB 调试吗？**」的对话框
3. 勾选「**始终允许使用这台计算机进行调试**」
4. 点击 **确定/允许**

> ⚠️ **注意事项**：
> - 请使用支持数据传输的 USB 线（非纯充电线）
> - 如果没有弹出授权对话框，尝试拔插 USB 或在终端运行 `adb devices` 触发
> - 部分手机需要在 USB 连接方式中选择「**文件传输 (MTP)**」模式

</details>

---

## ⭐ 方式一：Skill 模式（推荐，零配置）

**最简单的方式**：下载 Skill 压缩包，解压到 AI 客户端的 Skill 目录，即刻可用。

### 1. 下载

从 [Releases 页面](https://github.com/kengerlwl/phoneMcp/releases) 下载对应平台的 **Skill 压缩包**：

| 平台 | 下载文件 |
|------|---------|
| 🍎 macOS (Apple Silicon) | `phone-mcp-skill-macos-arm64.zip` |
| 🐧 Linux | `phone-mcp-skill-linux-amd64.zip` |
| 🪟 Windows | `phone-mcp-skill-windows-amd64.zip` |

### 2. 解压到 Skill 目录

```bash
# CatPaw
unzip phone-mcp-skill-macos-arm64.zip -d ~/.catpaw/skills/phone-mcp/

# Claude Code
unzip phone-mcp-skill-macos-arm64.zip -d ~/.claude/skills/phone-mcp/
```

解压后的目录结构：

```
phone-mcp/
├── SKILL.md      # AI 操作指南（AI 自动读取）
└── phone-mcp     # 可执行文件（内嵌 ADB）
```

### 3. 开始使用

连接手机后，直接对 AI 说：

- *"帮我打开微信，给张三发一条消息说'明天见'"*
- *"截个屏看看手机现在的界面"*
- *"打开淘宝搜索 iPhone 手机壳"*

AI 会自动读取 SKILL.md，通过 CLI 调用可执行文件来操控你的手机。**无需任何额外配置。**

### CLI 用法

Skill 模式下 AI 会自动调用这些命令，你也可以手动使用：

```bash
# 检测连接的设备
./phone-mcp run '{"action":"list_devices"}'

# 截图
./phone-mcp run '{"action":"screenshot"}'

# 获取屏幕元素
./phone-mcp run '{"action":"get_ui_elements"}'

# 点击元素
./phone-mcp run '{"action":"tap_element","text":"微信"}'

# 输入文本
./phone-mcp run '{"action":"type_text","text":"你好"}'

# 批量执行
./phone-mcp run '[{"action":"launch_app","name":"微信"},{"action":"wait","seconds":2},{"action":"get_ui_elements"}]'
```

---

## 🔧 方式二：MCP 服务器模式

适用于 Claude Desktop、Cursor 等支持 MCP 协议的客户端。需要先启动服务器，再在客户端中配置连接。

### 下载

从 [Releases 页面](https://github.com/kengerlwl/phoneMcp/releases) 下载独立可执行文件：

| 平台 | 文件 |
|------|------|
| 🐧 Linux | `phone-mcp-linux-amd64` |
| 🪟 Windows | `phone-mcp-windows-amd64.exe` |
| 🍎 macOS (Apple Silicon) | `phone-mcp-macos-arm64` |

### SSE 模式（默认，推荐）

```bash
# 启动服务器
./phone-mcp-macos-arm64 serve
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
      "args": ["serve", "--transport", "stdio"]
    }
  }
}
```

### 从源码运行

```bash
git clone https://github.com/kengerlwl/phoneMcp.git
cd phoneMcp
pip install -r requirements.txt
python main.py serve
```

### 命令行参数

```
phone-mcp serve [选项]

选项：
  -t, --transport TYPE   传输模式: sse 或 stdio（默认: sse）
  -H, --host HOST        监听地址（默认: 0.0.0.0）
  -p, --port PORT        监听端口（默认: 8009）
  --path PATH            MCP 路径（默认: /Phone）
  --guide                显示详细使用指南
```

---

## 🛠️ 支持的操作

| 操作 | CLI action | MCP Tool | 说明 |
|------|-----------|----------|------|
| 列出设备 | `list_devices` | `list_devices` | 列出已连接的 Android 设备 |
| 连接设备 | `connect` | `connect_device` | 连接远程设备（WiFi/TCP） |
| 断开设备 | `disconnect` | `disconnect_device` | 断开设备连接 |
| 截图 | `screenshot` | `get_screenshot` | 获取屏幕截图 |
| 获取元素 | `get_ui_elements` | `get_ui_elements` | 获取 UI 元素列表 ⭐ |
| 点击元素 | `tap_element` | `tap_element` | 通过索引/文本/ID 点击 ⭐ |
| 坐标点击 | `tap` | — | 点击指定坐标 |
| 双击 | `double_tap` | — | 双击指定坐标 |
| 滑动 | `swipe` | `swipe` | 滑动屏幕 |
| 输入文本 | `type_text` | `type_text` | 输入文本（支持中文） |
| 清除文本 | `clear_text` | `clear_text` | 清除输入框文本 |
| 返回键 | `back` | `press_back` | 按返回键 |
| 主页键 | `home` | `press_home` | 按主页键 |
| 按键 | `key` | `press_key` | 发送任意按键事件 |
| 启动应用 | `launch_app` | `launch_app` | 通过名称或包名启动应用 |
| 当前应用 | `current_app` | `get_current_app` | 获取当前前台应用 |
| 搜索应用 | `search_apps` | `search_apps` | 搜索已安装应用 |
| 等待 | `wait` | `wait` | 等待指定时间 |

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

