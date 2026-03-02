# PhoneMCP 改进计划

> 基于 vFlow（https://github.com/ChaoMixian/vFlow）的对比分析，梳理 PhoneMCP 的改进方向。

## 一、背景

PhoneMCP 是一个轻量级的 MCP 工具服务器，通过 ADB 让 AI 客户端（Claude、Cursor 等）远程控制 Android 手机。核心优势在于**极其轻量**（~500 行核心代码）和**与 AI 生态无缝衔接**（MCP 协议）。

通过分析 vFlow 这款 Android 端侧自动化平台（400+ Kotlin 文件，100+ 自动化模块），我们识别了以下可以借鉴的改进方向。

---

## 二、现状对比总结

| 维度 | PhoneMCP 现状 | vFlow 参考 |
|------|-------------|-----------|
| 运行环境 | PC 端 Python，通过 ADB 远程控制 | 手机端 Kotlin 原生 App |
| 点击实现 | `adb shell input tap` | 无障碍 GestureDescription → Shell 回退 |
| UI 树获取 | `adb shell uiautomator dump`（慢，1-3s） | AccessibilityService 直接遍历（毫秒级） |
| 截图 | `adb exec-out screencap` | 系统服务直接截图 |
| 文本输入 | ADB Keyboard 广播 | 无障碍 SET_TEXT → 自研 IME → 剪贴板粘贴 |
| 图像识别 | PaddleOCR（文字识别） | PaddleOCR + OpenCV 图像匹配 |
| 系统控制 | 仅基础操作 | WiFi/蓝牙/NFC/音量/亮度/暗色模式等 |
| 触发机制 | 无 | 定时/通知/短信/来电/位置等 15+ 种触发器 |

---

## 三、改进计划

### P0 - 高优先级（性能和稳定性）

#### 3.1 优化 UI 元素获取速度

**现状**：`adb shell uiautomator dump` 每次耗时 1-3 秒，偶尔失败。

**方案 A - 端侧 Agent App（推荐，长期）**：

- 开发极简 Android Service，利用 AccessibilityService 实时获取 UI 树
- 通过 HTTP 暴露接口，PhoneMCP 通过网络直接拉取
- 毫秒级响应，UI 信息更完整（含 focused/enabled 等状态）

**方案 B - 并行化优化（短期）**：

- 截图与 dump UI 树并行执行，减少总等待时间
- 缓存上一次 UI 树，dump 失败时使用缓存

#### 3.2 增强截图可靠性

**现状**：`adb exec-out screencap -p` 偶尔失败或截断。

**改进**：

- 增加截图重试机制（失败自动重试 2 次）
- 支持截图压缩（JPEG + 质量参数），减少传输数据量
- 支持 format/quality/maxWidth/maxHeight 参数
- 短时间内重复请求直接返回缓存

#### 3.3 改进文本输入

**现状**：依赖用户手动安装 ADB Keyboard。

**改进**：

- 增加剪贴板粘贴回退方案
- 优化特殊字符转义（空格、引号等）
- 参考 vFlow 三级回退：无障碍 SET_TEXT → IME → 剪贴板粘贴

---

### P1 - 中优先级（功能增强）

#### 3.4 OpenCV 图像匹配

- 新增 `find_image` 工具，支持模板匹配
- 适用：图标点击、验证码、游戏等纯图形化界面
- 依赖：opencv-python（可选）

#### 3.5 系统控制工具扩展

新增工具：

| 工具 | 功能 |
|------|------|
| `get_device_info` | 设备型号、系统版本、分辨率、电量 |
| `toggle_wifi` | 开关 WiFi |
| `toggle_bluetooth` | 开关蓝牙 |
| `set_volume` | 设置音量 |
| `wake_screen` / `lock_screen` | 唤醒/锁屏 |
| `push_file` / `pull_file` | 文件传输 |
| `get_clipboard` / `set_clipboard` | 剪贴板操作 |
| `get_notifications` | 获取通知栏内容 |

大部分可通过 ADB 命令实现，无需额外依赖。

#### 3.6 多设备并行控制

- 所有工具增加可选 `device_id` 参数
- 支持同时连接多台设备并行操作

#### 3.7 元素等待机制

- 新增 `wait_for_element` — 等待指定文本/元素出现
- 新增 `wait_for_element_disappear` — 等待元素消失
- 支持超时设置

---

### P2 - 低优先级（锦上添花）

#### 3.8 REST API 模式

- 增加 HTTP REST API 传输模式
- 让非 MCP 客户端也能调用（浏览器、curl、脚本等）

#### 3.9 操作录制与回放

- `start_recording` / `stop_recording` / `replay_recording`
- 记录操作序列，支持回放

#### 3.10 WebSocket 实时推送

- 实时推送屏幕变化事件
- 减少截图轮询，提升响应速度

---

## 四、实施路线

**阶段一（近期，1-2 周）**：

- 3.2 截图可靠性优化
- 3.3 文本输入增强
- 3.5 系统控制工具扩展

**阶段二（中期，3-4 周）**：

- 3.1-B UI 获取并行优化
- 3.4 OpenCV 图像匹配
- 3.6 多设备并行控制
- 3.7 元素等待机制

**阶段三（长期，1-2 月）**：

- 3.1-A 端侧 Agent App
- 3.8 REST API 模式
- 3.9 操作录制回放
- 3.10 WebSocket 推送

---

## 五、保持的核心优势

改进过程中应始终保持：

1. **极致轻量** — 不引入不必要的重依赖，`pip install` 即用
2. **MCP 协议原生** — 区别于所有竞品的核心优势
3. **无需 Root** — 仅依赖标准 ADB，门槛最低
4. **跨平台** — macOS/Windows/Linux 通用
5. **AI-First** — 工具参数和返回值针对 AI 理解优化

---

## 六、参考资料

- vFlow: https://github.com/ChaoMixian/vFlow
- MCP 协议: https://modelcontextprotocol.io
- Android AccessibilityService: https://developer.android.com/reference/android/accessibilityservice/AccessibilityService
- OpenCV Template Matching: https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html

