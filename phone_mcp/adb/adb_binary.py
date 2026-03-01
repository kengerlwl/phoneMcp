"""Bundled ADB binary management.

When PhoneMCP is distributed as a standalone executable, ADB may not be
installed on the user's machine.  This module:

1. Checks whether ``adb`` is already available on *PATH*.
2. If not, extracts the bundled ADB binary (shipped inside the PyInstaller
   package) to a persistent user directory (``~/.phonemcp/platform-tools/``).
3. Provides :func:`get_adb_path` which always returns a valid path to the
   ``adb`` executable.
"""

import platform
import shutil
import stat
import subprocess
import sys
from pathlib import Path

# Sentinel – will be set once by :func:`init_adb`.
_adb_path: str | None = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_adb_path() -> str:
    """Return the path to the ``adb`` executable.

    Call :func:`init_adb` once at startup; afterwards this function is safe
    to call from anywhere without extra cost.
    """
    global _adb_path
    if _adb_path is None:
        _adb_path = init_adb()
    return _adb_path


def init_adb() -> str:
    """Detect or extract ADB binary and return its path.

    Resolution order:
    1. System-installed ``adb`` on *PATH* → use it directly.
    2. Previously-extracted bundled ADB in ``~/.phonemcp/platform-tools/``.
    3. Extract from bundled resources (PyInstaller ``_MEIPASS`` data).

    Returns:
        Absolute path to the ``adb`` executable.

    Raises:
        FileNotFoundError: If ADB cannot be found or extracted.
    """
    global _adb_path

    # 1) Try system PATH first
    system_adb = shutil.which("adb")
    if system_adb is not None:
        _adb_path = system_adb
        print(f"[ADB] Using system ADB: {_adb_path}")
        return _adb_path

    # 2) Check if we previously extracted bundled ADB
    user_adb = _user_adb_path()
    if user_adb.exists():
        _ensure_executable(user_adb)
        _adb_path = str(user_adb)
        print(f"[ADB] Using cached bundled ADB: {_adb_path}")
        return _adb_path

    # 3) Extract from bundled resources
    bundled = _bundled_adb_source()
    if bundled is not None and bundled.exists():
        _extract_platform_tools(bundled, user_adb.parent)
        _ensure_executable(user_adb)
        _adb_path = str(user_adb)
        print(f"[ADB] Extracted bundled ADB to: {_adb_path}")
        return _adb_path

    raise FileNotFoundError(
        "ADB not found. Please install ADB and add it to your PATH.\n"
        "  → https://developer.android.com/tools/adb"
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _user_adb_path() -> Path:
    """Return expected path for the user-local ADB binary."""
    adb_name = "adb.exe" if platform.system() == "Windows" else "adb"
    return Path.home() / ".phonemcp" / "platform-tools" / adb_name


def _bundled_adb_source() -> Path | None:
    """Return the path to the bundled platform-tools directory.

    When running from a PyInstaller bundle ``sys._MEIPASS`` points to the
    temp directory containing all bundled data.  We expect the build to
    include ``platform-tools/`` there.
    """
    base: str | None = getattr(sys, "_MEIPASS", None)
    if base is None:
        # Running from source – no bundled binary available.
        return None
    return Path(base) / "platform-tools"


def _extract_platform_tools(src_dir: Path, dest_dir: Path) -> None:
    """Copy the entire ``platform-tools`` folder to *dest_dir*."""
    dest_dir.parent.mkdir(parents=True, exist_ok=True)
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    shutil.copytree(str(src_dir), str(dest_dir))


def _ensure_executable(path: Path) -> None:
    """Make sure the file is executable (no-op on Windows)."""
    if platform.system() != "Windows":
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _start_adb_server(adb_path: str) -> None:
    """Start the ADB server if it is not already running."""
    try:
        subprocess.run(
            [adb_path, "start-server"],
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass

