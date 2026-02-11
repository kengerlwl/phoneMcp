#!/usr/bin/env python3
"""
PhoneMCP 打包脚本

使用方法:
    python build.py          # 打包当前平台
    python build.py --all    # 提示如何打包所有平台
    python build.py --clean  # 清理构建文件
"""

import platform
import shutil
import subprocess
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"


def get_output_name() -> str:
    """获取输出文件名"""
    system = platform.system()
    if system == "Windows":
        return "phone-mcp.exe"
    return "phone-mcp"


def clean():
    """清理构建目录"""
    print("[Build] 清理旧的构建文件...")
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)

    # 清理 .spec 文件
    for spec in PROJECT_ROOT.glob("*.spec"):
        spec.unlink()


def build():
    """执行打包"""
    output_name = get_output_name()

    print(f"[Build] 目标平台: {platform.system()} {platform.machine()}")
    print(f"[Build] 输出文件: {output_name}")

    # PyInstaller 参数
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # 单文件
        "--name", output_name.replace(".exe", ""),
        "--clean",                      # 清理临时文件
        "--noconfirm",                  # 不确认覆盖
        # 收集完整包 (包含 metadata)
        "--collect-all", "fastmcp",
        "--collect-all", "mcp",
        "--collect-all", "phone_mcp",
        # Hidden imports
        "--hidden-import", "uvicorn",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols",
        "--hidden-import", "uvicorn.protocols.http",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "starlette",
        "--hidden-import", "anyio",
        "--hidden-import", "httpx",
        "--hidden-import", "pydantic",
        "--hidden-import", "httpcore",
        "--hidden-import", "h11",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        # 入口文件
        str(PROJECT_ROOT / "main.py")
    ]

    print(f"[Build] 执行命令: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode == 0:
        output_path = DIST_DIR / output_name
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"\n[Build] ✅ 打包成功!")
            print(f"[Build] 输出文件: {output_path}")
            print(f"[Build] 文件大小: {size_mb:.2f} MB")
        else:
            print(f"\n[Build] ⚠️  打包完成但未找到输出文件")
    else:
        print(f"\n[Build] ❌ 打包失败!")
        sys.exit(1)


def show_cross_compile_help():
    """显示跨平台编译帮助"""
    print("""
=== 跨平台打包说明 ===

PyInstaller 不支持交叉编译，需要在目标平台上分别打包：

1. macOS (在 Mac 上执行):
   python build.py

2. Windows (在 Windows 机器上执行):
   python build.py

3. Linux (在 Linux 机器上执行):
   python build.py

=== 使用 Docker 打包 Linux 版本 ===

# 在任意平台上打包 Linux 版本
docker run --rm -v $(pwd):/app python:3.11 bash -c "
    cd /app &&
    pip install -r requirements.txt pyinstaller &&
    python build.py
"

=== 使用 GitHub Actions 自动打包 ===

推荐使用 CI/CD 在多平台上自动打包，创建 .github/workflows/build.yml:

name: Build
on:
  push:
    tags: ['v*']
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: python build.py
      - uses: actions/upload-artifact@v4
        with:
          name: phone-mcp-${{ matrix.os }}
          path: dist/
""")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="PhoneMCP 打包脚本")
    parser.add_argument("--all", action="store_true", help="显示跨平台打包说明")
    parser.add_argument("--clean", action="store_true", help="仅清理构建文件")
    args = parser.parse_args()

    if args.all:
        show_cross_compile_help()
        return

    if args.clean:
        clean()
        print("[Build] 清理完成")
        return

    clean()
    build()


if __name__ == "__main__":
    main()

