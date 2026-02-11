#!/usr/bin/env python3
"""
PhoneMCP - Android 设备控制 MCP Server

使用方法:
    phone-mcp                           # 默认启动 (SSE, 0.0.0.0:8009)
    phone-mcp --port 8080               # 指定端口
    phone-mcp --transport stdio         # 使用 stdio 传输
"""

import argparse
import sys

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                      PhoneMCP v1.0                           ║
║        Android Device Control via MCP Protocol               ║
╚══════════════════════════════════════════════════════════════╝
"""

USAGE_GUIDE = """
================== 使用指南 ==================

【功能说明】
  本工具将 Android 设备控制能力通过 MCP 协议暴露，
  使 AI 助手可以远程控制你的 Android 设备。

【提供的 MCP Tools】
  - list_devices        : 列出已连接设备
  - connect_device      : 连接远程设备
  - get_screenshot      : 获取屏幕截图
  - get_ui_elements     : 获取UI元素列表 ⭐推荐
  - tap_element         : 通过元素点击 ⭐推荐
  - tap                 : 坐标点击
  - swipe               : 滑动屏幕
  - type_text           : 输入文本
  - press_back/home     : 按键操作
  - launch_app          : 启动应用

【配置 AI 助手】
  在 Claude Desktop 或其他 MCP 客户端配置:

  SSE 模式:
  {
    "mcpServers": {
      "phone-mcp": {
        "url": "http://localhost:8009/Phone/sse"
      }
    }
  }

  STDIO 模式:
  {
    "mcpServers": {
      "phone-mcp": {
        "command": "/path/to/phone-mcp",
        "args": ["--transport", "stdio"]
      }
    }
  }

【前置要求】
  1. 安装 ADB 并添加到 PATH
  2. Android 设备已连接（USB 或 WiFi）
  3. 设备已开启 USB 调试

==============================================
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="PhoneMCP - Android 设备控制 MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
【基本用法】
  phone-mcp                           # 默认 SSE 模式
  phone-mcp --transport stdio         # STDIO 模式
  phone-mcp --port 8080               # 指定端口

【示例】
  # SSE 模式启动
  phone-mcp -p 9000

  # STDIO 模式（供 Claude Desktop 调用）
  phone-mcp -t stdio

【更多信息】
  GitHub: https://github.com/kengerlwl/phone-mcp
        """
    )

    parser.add_argument(
        "-t", "--transport",
        default="sse",
        choices=["sse", "stdio"],
        metavar="TYPE",
        help="传输模式: sse 或 stdio (默认: sse)"
    )
    parser.add_argument(
        "-H", "--host",
        default="0.0.0.0",
        metavar="HOST",
        help="监听地址 (默认: 0.0.0.0)"
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=8009,
        metavar="PORT",
        help="监听端口 (默认: 8009)"
    )
    parser.add_argument(
        "--path",
        default="/Phone",
        metavar="PATH",
        help="MCP 路径 (默认: /Phone)"
    )
    parser.add_argument(
        "--guide",
        action="store_true",
        help="显示详细使用指南"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # 显示使用指南
    if args.guide:
        print(BANNER)
        print(USAGE_GUIDE)
        return

    print(BANNER)
    print("【服务配置】")
    print(f"  Transport : {args.transport}")
    print(f"  Host      : {args.host}")
    print(f"  Port      : {args.port}")
    print(f"  Path      : {args.path}")
    print()

    if args.transport == "sse":
        print("【MCP 访问地址】")
        print(f"  http://{args.host}:{args.port}{args.path}/sse")
        print()

    print("  提示: 使用 --guide 查看详细使用指南")
    print("=" * 62)

    try:
        from phone_mcp.server import run
        run(
            transport=args.transport,
            host=args.host,
            port=args.port,
            path=args.path
        )
    except KeyboardInterrupt:
        print("\n[PhoneMCP] 用户中断")
    except Exception as e:
        print(f"\n[PhoneMCP] 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

