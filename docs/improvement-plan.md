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
| 点击实现 | `adb shell input tap` | 无障碍 GestureDescription（优先）→ Shell 回退 |
| UI 树获取 | `adb shell uiautomator dump`（慢，~1-3s） | AccessibilityService 直接遍历（毫秒级） |
| 截图 | `adb exec-out screencap` | 系统服务直接截图 |
| 文本输入 | ADB Keyboard 广播 | 无障碍 SET_TEXT → 自研 IME → 剪贴板粘贴 |
| 图像识别 | PaddleOCR（文字识别） | PaddleOCR + OpenCV 图像匹配 |
| AI 集成 | AI 在外部通过 MCP 协议调用 | 内置 Agent 循环（截图→AI 决策→执行→循环） |
| 系统控制 | 仅基础操作 | WiFi/蓝牙/NFC/音量/亮度/暗色模式等 |
| 触发机制 | 无 | 定时/通知/短信/来电/位置/蓝牙等 15+ 种触发器 |

---

## 三、改进计划

### P0 - 高优先级（性能和稳定性提升）

#### 3.1 优化 UI 元素获取速度

**现状**：使用 `adb shell uiautomator dump` 获取 UI 层次结构，每次耗时 1-3 秒，且偶尔失败。

**改进方案**：

- **方案 A：在手机端部署轻量 Agent（推荐）**
  - 开发一个极简 Android App/Service，利用 AccessibilityService 实时获取 UI 树
  - 通过 HTTP/WebSocket 暴露接口，PhoneMCP 通过网络直接拉取
  - 优势：毫秒级响应，UI 树信息更完整（含 focused/enabled 等状态）
  - 参考：vFlow 的 `AccessibilityService.kt` + `ServiceStateBus`

- **方案 B：并行化 uiautomator dump**
  - 保持现有 ADB 方式，但优化为异步执行
  - 在截图的同时并行 dump UI 树，减少总等待时间
  - 缓存上一次的 UI 树，在 dump 失败时使用缓存

**评估**：方案 A 效果最好但需要额外安装 App；方案 B 改动最小但提升有限。建议先做 B，长期做 A。

#### 3.2 增强截图可靠性和速度

**现状**：使用 `adb exec-out screencap -p`，偶尔会因 ADB 连接不稳定导致截图失败或截断。

**改进方案**：
- 增加截图重试机制（失败自动重试 2 次）
- 支持截图压缩（JPEG 格式 + 质量参数），减少传输数据量
- 参考 vFlow 的 `captureScreenEx()` 支持 format/quality/maxWidth/maxHeight 参数
- 添加截图缓存机制，短时间内重复请求直接返回缓存

#### 3.3 改进文本输入方案

**现状**：ASCII 文本用 `adb shell input text`，非 ASCII 用 ADB Keyboard 广播。依赖用户手动安装和激活 ADB Keyboard。

**改进方案**：
- 增加剪贴板粘贴方案作为回退：`adb shell am broadcast` 设置剪贴板 → `adb shell input keyevent 279`（粘贴）
- 优化特殊字符转义处理（目前空格、引号等特殊字符处理不够健壮）
- 参考 vFlow 的三级回退策略：无障碍 SET_TEXT → IME → 剪贴板粘贴

---

### P1 - 中优先级（功能增强）

#### 3.4 增加 OpenCV 图像匹配能力

**现状**：仅支持 OCR 文字识别定位元素。

**改进方案**：
- 新增 `find_image` 工具，支持模板匹配
- 用户可提供参考图片，在截图中定位目标元素位置
- 适用场景：图标点击、验证码识别、游戏操作等纯图形化界面
- 依赖：opencv-python（可选依赖，不强制安装）
- 参考：vFlow 的 `FindImageModule` + `OpenCVImageMatcher`

#### 3.5 增加更多系统控制工具

**现状**：仅支持基础的点击/滑动/按键/启动应用。

**建议新增工具**：

```
# 设备信息
get_device_info      - 获取设备型号、系统版本、屏幕分辨率、电量等
get_battery_info     - 获取电池状态和电量百分比

# 系统控制
set_screen_brightness - 设置屏幕亮度
toggle_wifi          - 开关 WiFi
toggle_bluetooth     - 开关蓝牙
set_volume           - 设置音量
wake_screen          - 唤醒屏幕
lock_screen          - 锁屏

# 文件操作
push_file            - 推送文件到手机
pull_file            - 从手机拉取文件
list_files           - 列出目录内容

# 剪贴板
get_clipboard        - 获取剪贴板内容
set_clipboard        - 设置剪贴板内容
```

这些大部分可通过 ADB 命令实现，无需额外依赖。

#### 3.6 增加多设备并行控制

**现状**：虽然支持 `list_devices` 和 `connect_device`，但一次只能操作一台设备。

**改进方案**：
- 所有工具增加可选的 `device_id` 参数
- 支持同时连接多台设备并行操作
- 适用场景：多设备批量测试、多账号操作

#### 3.7 增加 REST API 模式

**现状**：仅支持 MCP 协议（SSE/STDIO），只有 MCP 客户端能使用。

**改进方案**：
- 增加 HTTP REST API 传输模式
- 提供标准的 RESTful 接口（GET /screenshot、POST /tap 等）
- 让非 MCP 客户端（浏览器、curl、Python 脚本等）也能调用
- 参考：vFlow 的 `ApiServer.kt`（NanoHTTPD + Token 认证）

---

### P2 - 低优先级（锦上添花）

#### 3.8 增加操作录制与回放

**现状**：无录制功能。

**改进方案**：
- 新增 `start_recording` / `stop_recording` 工具
- 记录一段时间内所有 AI 的操作序列（点击坐标、滑动路径、文本输入等）
- 支持 `replay_recording` 回放录制的操作
- 参考：vFlow 的 `CoreTouchReplayModule` + `TouchEventRecord`

#### 3.9 增加元素等待机制

**现状**：只有简单的 `wait` 工具（固定等待）。

**改进方案**：
- 新增 `wait_for_element` 工具：等待指定文本/元素出现
- 新增 `wait_for_element_disappear` 工具：等待指定元素消失
- 支持超时设置
- 参考：vFlow 的 `AgentTools.waitForElementToDisappear()`

#### 3.10 增加通知监听能力

**改进方案**：
- 新增 `get_notifications` 工具，获取当前通知栏内容
- 适用场景：等待验证码短信、监控消息推送等
- 实现：`adb shell dumpsys notification` 解析

#### 3.11 增加 WebSocket 实时推送

**现状**：AI 需要主动轮询截图和 UI 状态。

**改进方案**：
- 增加 WebSocket 通道，实时推送屏幕变化事件
- 当检测到页面跳转、弹窗出现等事件时主动通知 AI
- 减少不必要的截图轮询，提升响应速度

---

## 四、实施优先级排序

```
阶段一（近期）：
  ├── 3.2 截图可靠性优化（1-2 天）
  ├── 3.3 文本输入增强（1-2 天）
  └── 3.5 系统控制工具扩展（2-3 天）

阶段二（中期）：
  ├── 3.1-B UI 获取并行优化（1-2 天）
  ├── 3.4 OpenCV 图像匹配（3-5 天）
  ├── 3.6 多设备并行控制（2-3 天）
  └── 3.9 元素等待机制（1-2 天）

阶段三（长期）：
  ├── 3.1-A 端侧 Agent App 开发（2-3 周）
  ├── 3.7 REST API 模式（3-5 天）
  ├── 3.8 操作录制回放（3-5 天）
  ├── 3.10 通知监听（1-2 天）
  └── 3.11 WebSocket 推送（3-5 天）
```

---

## 五、保持的优势（不应改变的）

在改进过程中，PhoneMCP 的以下核心优势应当保持：

1. **极致轻量** — 不引入不必要的重依赖，保持安装简单（`pip install` 即用）
2. **MCP 协议原生支持** — 这是区别于所有竞品的核心优势
3. **无需 Root/越狱** — 仅依赖标准 ADB，门槛最低
4. **跨平台** — Python 可在 macOS/Windows/Linux 上运行
5. **AI-First 设计** — 所有工具的参数和返回值都针对 AI 理解进行了优化

---

## 六、参考资料

- vFlow 项目：https://github.com/ChaoMixian/vFlow
- MCP 协议规范：https://modelcontextprotocol.io
- Android AccessibilityService：https://developer.android.com/reference/android/accessibilityservice/AccessibilityService
- OpenCV Template Matching：https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html

