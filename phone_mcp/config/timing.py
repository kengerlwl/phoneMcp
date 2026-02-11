"""Timing configuration for Phone MCP.

This module defines all configurable waiting times used throughout the application.
Users can customize these values by modifying this file or by setting environment variables.
"""

import os
from dataclasses import dataclass


@dataclass
class DeviceTimingConfig:
    """Configuration for device operation timing delays."""

    # Default delays for various device operations (in seconds)
    default_tap_delay: float = 1.0
    default_double_tap_delay: float = 1.0
    double_tap_interval: float = 0.1
    default_long_press_delay: float = 1.0
    default_swipe_delay: float = 1.0
    default_back_delay: float = 1.0
    default_home_delay: float = 1.0
    default_launch_delay: float = 1.0

    def __post_init__(self):
        """Load values from environment variables if present."""
        self.default_tap_delay = float(
            os.getenv("PHONE_MCP_TAP_DELAY", self.default_tap_delay)
        )
        self.default_double_tap_delay = float(
            os.getenv("PHONE_MCP_DOUBLE_TAP_DELAY", self.default_double_tap_delay)
        )
        self.double_tap_interval = float(
            os.getenv("PHONE_MCP_DOUBLE_TAP_INTERVAL", self.double_tap_interval)
        )
        self.default_long_press_delay = float(
            os.getenv("PHONE_MCP_LONG_PRESS_DELAY", self.default_long_press_delay)
        )
        self.default_swipe_delay = float(
            os.getenv("PHONE_MCP_SWIPE_DELAY", self.default_swipe_delay)
        )
        self.default_back_delay = float(
            os.getenv("PHONE_MCP_BACK_DELAY", self.default_back_delay)
        )
        self.default_home_delay = float(
            os.getenv("PHONE_MCP_HOME_DELAY", self.default_home_delay)
        )
        self.default_launch_delay = float(
            os.getenv("PHONE_MCP_LAUNCH_DELAY", self.default_launch_delay)
        )


@dataclass
class ConnectionTimingConfig:
    """Configuration for ADB connection timing delays."""

    adb_restart_delay: float = 2.0
    server_restart_delay: float = 1.0

    def __post_init__(self):
        """Load values from environment variables if present."""
        self.adb_restart_delay = float(
            os.getenv("PHONE_MCP_ADB_RESTART_DELAY", self.adb_restart_delay)
        )
        self.server_restart_delay = float(
            os.getenv("PHONE_MCP_SERVER_RESTART_DELAY", self.server_restart_delay)
        )


@dataclass
class TimingConfig:
    """Master timing configuration combining all timing settings."""

    device: DeviceTimingConfig
    connection: ConnectionTimingConfig

    def __init__(self):
        """Initialize all timing configurations."""
        self.device = DeviceTimingConfig()
        self.connection = ConnectionTimingConfig()


# Global timing configuration instance
TIMING_CONFIG = TimingConfig()


def get_timing_config() -> TimingConfig:
    """Get the global timing configuration."""
    return TIMING_CONFIG

