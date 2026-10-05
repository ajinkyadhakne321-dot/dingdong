"""Data models for the ETF Market Making Simulator."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PriceTick(BaseModel):
    """A single price tick in the simulation."""

    timestamp: datetime = Field(description="Timestamp of the price tick")
    price: float = Field(gt=0, description="Price at this tick")
    step: int = Field(ge=0, description="Simulation step number")


class SimulationState(BaseModel):
    """Current state of the simulation."""

    current_step: int = Field(ge=0, description="Current simulation step")
    current_price: float = Field(gt=0, description="Current ETF price")
    is_running: bool = Field(default=False, description="Whether simulation is running")


__all__ = ["PriceTick", "SimulationState"]
