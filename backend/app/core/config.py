"""
Configuration management for the ETF Market Making Simulator.

This module provides type-safe configuration using Pydantic settings.
Configuration can be loaded from YAML files and environment variables.
"""

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class MarketConfig(BaseModel):
    """Market simulation parameters."""

    initial_price: float = Field(default=100.0, gt=0, description="Initial ETF price")
    volatility: float = Field(default=0.20, gt=0, description="Annual volatility (σ)")
    drift: float = Field(default=0.05, description="Annual drift rate (μ)")
    time_step: float = Field(default=0.01, gt=0, description="Time step for simulation (dt)")
    random_seed: Optional[int] = Field(default=42, description="Random seed for reproducibility")

    @field_validator("volatility")
    @classmethod
    def validate_volatility(cls, v: float) -> float:
        """Ensure volatility is reasonable."""
        if v <= 0 or v > 5.0:
            raise ValueError("Volatility must be between 0 and 5.0 (500%)")
        return v


class MarketMakerConfig(BaseModel):
    """Market maker strategy parameters."""

    spread_bps: int = Field(default=5, ge=0, description="Spread in basis points")
    max_inventory: int = Field(default=1000, gt=0, description="Maximum inventory position")
    order_size: int = Field(default=100, gt=0, description="Standard order size")


class RiskConfig(BaseModel):
    """Risk management parameters."""

    max_order_size: int = Field(default=100, gt=0, description="Maximum order size")
    max_daily_loss: float = Field(default=5000.0, gt=0, description="Maximum daily loss limit")
    max_inventory: int = Field(default=1000, gt=0, description="Maximum inventory position")


class SimulationConfig(BaseModel):
    """Simulation execution parameters."""

    steps: int = Field(default=1000, gt=0, description="Number of simulation steps")
    speed: str = Field(default="real-time", description="Simulation speed: fast, real-time, or step")

    @field_validator("speed")
    @classmethod
    def validate_speed(cls, v: str) -> str:
        """Ensure speed is a valid option."""
        valid_speeds = ["fast", "real-time", "step"]
        if v not in valid_speeds:
            raise ValueError(f"Speed must be one of {valid_speeds}")
        return v


class Config(BaseSettings):
    """Main configuration class."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    market: MarketConfig = Field(default_factory=MarketConfig)
    market_maker: MarketMakerConfig = Field(default_factory=MarketMakerConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "Config":
        """
        Load configuration from a YAML file.

        Args:
            yaml_path: Path to the YAML configuration file.

        Returns:
            Config instance with values from the YAML file.
        """
        with open(yaml_path, "r") as f:
            yaml_data = yaml.safe_load(f)

        return cls(**yaml_data)


# Global configuration instance
_config: Optional[Config] = None


def get_config(config_path: Optional[Path] = None) -> Config:
    """
    Get the global configuration instance.

    Args:
        config_path: Optional path to a YAML configuration file.

    Returns:
        The global Config instance.
    """
    global _config

    if _config is None:
        if config_path is not None:
            _config = Config.from_yaml(config_path)
        else:
            _config = Config()

    return _config


def reset_config() -> None:
    """Reset the global configuration instance (useful for testing)."""
    global _config
    _config = None
