#!/usr/bin/env python3
"""
PhoneMCP - Android 设备控制工具

使用方法:
    phone-mcp                           # 默认启动 MCP 服务器 (SSE, 0.0.0.0:8009)
    phone-mcp serve --port 8080         # MCP 服务器指定端口
    phone-mcp serve --transport stdio   # MCP STDIO 模式
    phone-mcp run '{"action":"screenshot"}'   # CLI 模式（Skill 推荐）
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

【两种使用方式】

  1. CLI 模式（推荐，零配置，配合 Skill 使用）
     phone-mcp run '{"action":"screenshot"}'
     phone-mcp run '{"action":"tap_element","text":"微信"}'
     phone-mcp run '{"action":"list_devices"}'

  2. MCP 服务器模式（需要在 AI 客户端配置）
     phone-mcp serve                    # SSE 模式
     phone-mcp serve -t stdio           # STDIO 模式

【CLI 模式可用的 Actions】
  - list_devices        : 列出已连接设备
  - connect             : 连接远程设备
  - disconnect          : 断开设备连接
  - screenshot          : 获取屏幕截图（保存到文件）
  - get_ui_elements     : 获取UI元素列表 ⭐推荐
  - tap_element         : 通过元素点击 ⭐推荐
  - tap                 : 坐标点击
  - double_tap          : 双击
  - swipe               : 滑动屏幕
  - type_text           : 输入文本
  - clear_text          : 清除文本
  - back                : 返回键
  - home                : 主页键
  - key                 : 发送按键事件
  - launch_app          : 启动应用
  - current_app         : 获取当前应用
  - search_apps         : 搜索已安装应用
  - wait                : 等待

【MCP 客户端配置】
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
        "args": ["serve", "--transport", "stdio"]
      }
    }
  }

【前置要求】
  1. Android 设备已连接（USB 或 WiFi）
  2. 设备已开启 USB 调试

==============================================
"""


def main():
    # Quick detection: if first arg is 'run', route to CLI mode
    if len(sys.argv) >= 2 and sys.argv[1] == "run":
        _run_cli_mode()
        return

    # Quick detection: if first arg is 'serve', route to MCP server mode
    if len(sys.argv) >= 2 and sys.argv[1] == "serve":
        _run_serve_mode(sys.argv[2:])
        return

    # No subcommand or legacy flags → default to MCP server mode (backward compat)
    _run_serve_mode(sys.argv[1:])


def _run_cli_mode():
    """Handle 'phone-mcp run <json>' CLI mode."""
    from phone_mcp.cli import cli_main

    # Pass everything after 'run' to cli_main
    cli_args = sys.argv[2:]
    cli_main(cli_args)


def _run_serve_mode(argv: list):
    """Handle 'phone-mcp serve [options]' or legacy 'phone-mcp [options]' MCP server mode."""
    parser = argparse.ArgumentParser(
        description="PhoneMCP MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
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

    args = parser.parse_args(argv)

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
    print("  提示: 使用 'phone-mcp run' 进入 CLI 模式（配合 Skill 使用）")
    print("=" * 62)

    try:
        # 初始化 ADB（检测系统 ADB 或解压内嵌 ADB）
        from phone_mcp.adb.adb_binary import init_adb
        try:
            adb_path = init_adb()
            print(f"\n  ✅ ADB 路径: {adb_path}")
        except FileNotFoundError as e:
            print(f"\n  ⚠️  {e}")
            print("  程序将继续启动，但设备操作可能会失败。")

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

