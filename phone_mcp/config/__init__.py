"""Configuration module for Phone MCP."""

from phone_mcp.config.apps import APP_PACKAGES, get_package_name, get_app_name, list_supported_apps
from phone_mcp.config.timing import TIMING_CONFIG, TimingConfig, get_timing_config

__all__ = [
    "APP_PACKAGES",
    "get_package_name",
    "get_app_name",
    "list_supported_apps",
    "TIMING_CONFIG",
    "TimingConfig",
    "get_timing_config",
]

