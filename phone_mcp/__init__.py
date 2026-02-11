"""
Phone MCP - Android automation via MCP protocol.

A clean, independent MCP server for controlling Android devices through ADB.
"""

from phone_mcp.server import mcp, run

__version__ = "0.1.0"

__all__ = ["mcp", "run", "__version__"]

