"""
ETF Price Simulator using Geometric Brownian Motion.

This module implements a synthetic ETF price process using the geometric Brownian motion (GBM) model.

Mathematical Model:
------------------
The GBM model is described by the stochastic differential equation:

    dS = μSdt + σSdW

Where:
- S(t) is the asset price at time t
- μ (mu) is the drift coefficient (expected return)
- σ (sigma) is the volatility coefficient
- dW is a Wiener process (Brownian motion)

Discrete-time implementation:
----------------------------
For simulation, we discretize the SDE using the Euler-Maruyama method:

    S(t+dt) = S(t) * exp((μ - 0.5*σ²)dt + σ*√dt * Z)

Where Z is a standard normal random variable Z ~ N(0,1).

Why GBM for ETFs?
-----------------
1. GBM ensures prices remain positive (important for financial assets)
2. It's the standard model for stock/ETF price dynamics in quantitative finance
3. It captures both drift (trend) and diffusion (random volatility)
4. It's analytically tractable and widely used in options pricing (Black-Scholes)

Assumptions:
-----------
- Prices follow a continuous-time stochastic process
- Returns are log-normally distributed
- Volatility is constant (in this basic implementation)
- No jumps or regime changes (simplification)

Why does a market maker care about volatility?
----------------------------------------------
Higher volatility means:
- Larger price swings → larger potential profits AND larger potential losses
- Wider spreads are needed to compensate for risk
- Higher inventory risk (positions can move against you quickly)
- More aggressive quoting may be needed to capture opportunities

The simulator allows testing different volatility regimes to understand their impact
on market making strategies.
"""

from datetime import datetime, timedelta
from typing import List, Optional

import numpy as np
from pydantic import BaseModel, Field, field_validator

from ..core.config import MarketConfig
from ..models import PriceTick


class PriceSimulatorConfig(BaseModel):
    """Configuration for the price simulator."""

    initial_price: float = Field(default=100.0, gt=0, description="Initial price")
    drift: float = Field(default=0.05, description="Annual drift rate (μ)")
    volatility: float = Field(default=0.20, gt=0, description="Annual volatility (σ)")
    time_step: float = Field(default=0.01, gt=0, description="Time step (dt) in years")
    random_seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")

    @field_validator("volatility")
    @classmethod
    def validate_volatility(cls, v: float) -> float:
        """Ensure volatility is reasonable."""
        if v <= 0 or v > 5.0:
            raise ValueError("Volatility must be between 0 and 5.0 (500%)")
        return v


class PriceSimulator:
    """
    ETF Price Simulator using Geometric Brownian Motion.

    This class generates synthetic ETF price paths using the GBM model.
    It supports deterministic random seeds for reproducible simulations.

    Example:
        >>> simulator = PriceSimulator(
        ...     initial_price=100.0,
        ...     drift=0.05,
        ...     volatility=0.20,
        ...     time_step=0.01,
        ...     random_seed=42
        ... )
        >>> prices = simulator.generate_path(num_steps=1000)
    """

    def __init__(
        self,
        initial_price: float = 100.0,
        drift: float = 0.05,
        volatility: float = 0.20,
        time_step: float = 0.01,
        random_seed: Optional[int] = None,
    ):
        """
        Initialize the price simulator.

        Args:
            initial_price: Starting price of the ETF
            drift: Annual drift rate (μ). 0.05 = 5% annual return
            volatility: Annual volatility (σ). 0.20 = 20% annual volatility
            time_step: Time step in years. 0.01 ≈ 3.65 days
            random_seed: Seed for random number generator (for reproducibility)
        """
        self.config = PriceSimulatorConfig(
            initial_price=initial_price,
            drift=drift,
            volatility=volatility,
            time_step=time_step,
            random_seed=random_seed,
        )

        # Set random seed if provided for reproducibility
        if random_seed is not None:
            np.random.seed(random_seed)

        # Current price state
        self.current_price = initial_price
        self.current_step = 0
        self.start_time = datetime.now()

    @classmethod
    def from_config(cls, config: MarketConfig) -> "PriceSimulator":
        """
        Create a PriceSimulator from a MarketConfig.

        Args:
            config: MarketConfig instance

        Returns:
            PriceSimulator instance
        """
        return cls(
            initial_price=config.initial_price,
            drift=config.drift,
            volatility=config.volatility,
            time_step=config.time_step,
            random_seed=config.random_seed,
        )

    def step(self) -> float:
        """
        Generate a single price step using GBM.

        The discretized GBM equation:
            S(t+dt) = S(t) * exp((μ - 0.5*σ²)dt + σ*√dt * Z)

        Where Z ~ N(0,1) is a standard normal random variable.

        Returns:
            The new price after one time step.
        """
        dt = self.config.time_step
        mu = self.config.drift
        sigma = self.config.volatility

        # Generate random shock from standard normal distribution
        Z = np.random.standard_normal()

        # Calculate price change using GBM formula
        # The term (mu - 0.5*sigma^2) corrects for Itô's lemma
        drift_term = (mu - 0.5 * sigma**2) * dt
        diffusion_term = sigma * np.sqrt(dt) * Z

        # Update price
        self.current_price = self.current_price * np.exp(drift_term + diffusion_term)
        self.current_step += 1

        return self.current_price

    def generate_path(self, num_steps: int) -> List[PriceTick]:
        """
        Generate a complete price path.

        Args:
            num_steps: Number of time steps to simulate

        Returns:
            List of PriceTick objects containing timestamp and price
        """
        prices = []
        current_time = self.start_time
        dt_years = self.config.time_step
        dt_seconds = dt_years * 365.25 * 24 * 60 * 60  # Convert to seconds

        for _ in range(num_steps):
            price = self.step()
            tick = PriceTick(
                timestamp=current_time,
                price=price,
                step=self.current_step,
            )
            prices.append(tick)
            current_time = current_time + timedelta(seconds=dt_seconds)

        return prices

    def reset(self) -> None:
        """Reset the simulator to initial state."""
        self.current_price = self.config.initial_price
        self.current_step = 0
        self.start_time = datetime.now()

        # Reset random seed if configured for reproducibility
        if self.config.random_seed is not None:
            np.random.seed(self.config.random_seed)

    def get_current_price(self) -> float:
        """Get the current price."""
        return self.current_price

    def get_current_step(self) -> int:
        """Get the current simulation step."""
        return self.current_step


def calculate_returns(prices: List[float]) -> List[float]:
    """
    Calculate log returns from a price series.

    Log returns are calculated as:
        r_t = ln(S_t / S_{t-1})

    Log returns are preferred over simple returns because:
    - They are additive over time
    - They are symmetric (same interpretation for gains and losses)
    - They follow a normal distribution under GBM

    Args:
        prices: List of prices

    Returns:
        List of log returns (length = len(prices) - 1)
    """
    if len(prices) < 2:
        return []

    returns = []
    for i in range(1, len(prices)):
        ret = np.log(prices[i] / prices[i - 1])
        returns.append(ret)

    return returns


def calculate_volatility(returns: List[float], annualize: bool = True) -> float:
    """
    Calculate historical volatility from returns.

    Volatility is the standard deviation of returns.

    If annualize=True, converts to annual volatility:
        σ_annual = σ_daily * √252
    (252 is the typical number of trading days in a year)

    Args:
        returns: List of log returns
        annualize: Whether to annualize the volatility

    Returns:
        Volatility measure
    """
    if len(returns) < 2:
        return 0.0

    returns_array = np.array(returns)
    vol = np.std(returns_array, ddof=1)  # Sample standard deviation

    if annualize:
        # Assuming daily returns, annualize with sqrt(252)
        vol = vol * np.sqrt(252)

    return vol
