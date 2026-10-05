"""
Unit tests for the Price Simulator.

Tests cover:
- Basic price generation
- Reproducibility with random seeds
- Configuration validation
- Return calculations
- Volatility calculations
"""

import numpy as np
import pytest

from app.market.price_simulator import (
    PriceSimulator,
    PriceSimulatorConfig,
    calculate_returns,
    calculate_volatility,
)


class TestPriceSimulatorConfig:
    """Tests for PriceSimulatorConfig validation."""

    def test_default_config(self):
        """Test that default configuration is valid."""
        config = PriceSimulatorConfig()
        assert config.initial_price == 100.0
        assert config.drift == 0.05
        assert config.volatility == 0.20
        assert config.time_step == 0.01
        assert config.random_seed is None

    def test_custom_config(self):
        """Test custom configuration values."""
        config = PriceSimulatorConfig(
            initial_price=150.0,
            drift=0.10,
            volatility=0.30,
            time_step=0.02,
            random_seed=123,
        )
        assert config.initial_price == 150.0
        assert config.drift == 0.10
        assert config.volatility == 0.30
        assert config.time_step == 0.02
        assert config.random_seed == 123

    def test_invalid_initial_price(self):
        """Test that non-positive initial price is rejected."""
        with pytest.raises(ValueError):
            PriceSimulatorConfig(initial_price=0.0)

        with pytest.raises(ValueError):
            PriceSimulatorConfig(initial_price=-100.0)

    def test_invalid_volatility_zero(self):
        """Test that zero volatility is rejected."""
        with pytest.raises(ValueError):
            PriceSimulatorConfig(volatility=0.0)

    def test_invalid_volatility_too_high(self):
        """Test that excessive volatility is rejected."""
        with pytest.raises(ValueError):
            PriceSimulatorConfig(volatility=6.0)

    def test_invalid_time_step(self):
        """Test that non-positive time step is rejected."""
        with pytest.raises(ValueError):
            PriceSimulatorConfig(time_step=0.0)

        with pytest.raises(ValueError):
            PriceSimulatorConfig(time_step=-0.01)


class TestPriceSimulator:
    """Tests for PriceSimulator class."""

    def test_initialization(self):
        """Test that simulator initializes correctly."""
        simulator = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.20,
            time_step=0.01,
        )
        assert simulator.get_current_price() == 100.0
        assert simulator.get_current_step() == 0

    def test_step_generates_price(self):
        """Test that step() generates a valid price."""
        simulator = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.20,
            time_step=0.01,
            random_seed=42,
        )

        price = simulator.step()
        assert price > 0
        assert isinstance(price, float)
        assert simulator.get_current_step() == 1

    def test_multiple_steps(self):
        """Test that multiple steps generate increasing step count."""
        simulator = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.20,
            time_step=0.01,
            random_seed=42,
        )

        for i in range(10):
            simulator.step()
            assert simulator.get_current_step() == i + 1

    def test_reset(self):
        """Test that reset() returns simulator to initial state."""
        simulator = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.20,
            time_step=0.01,
            random_seed=42,
        )

        # Take some steps
        for _ in range(10):
            simulator.step()

        # Reset
        simulator.reset()

        assert simulator.get_current_price() == 100.0
        assert simulator.get_current_step() == 0

    def test_reproducibility_with_seed(self):
        """Test that using the same seed produces identical results."""
        # First simulation
        sim1 = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.20,
            time_step=0.01,
            random_seed=42,
        )
        prices1 = [sim1.step() for _ in range(100)]

        # Second simulation with same seed
        sim2 = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.20,
            time_step=0.01,
            random_seed=42,
        )
        prices2 = [sim2.step() for _ in range(100)]

        # Prices should be identical
        assert len(prices1) == len(prices2)
        for p1, p2 in zip(prices1, prices2):
            assert p1 == pytest.approx(p2)

    def test_different_seeds_produce_different_results(self):
        """Test that different seeds produce different results."""
        sim1 = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.20,
            time_step=0.01,
            random_seed=42,
        )
        prices1 = [sim1.step() for _ in range(100)]

        sim2 = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.20,
            time_step=0.01,
            random_seed=123,
        )
        prices2 = [sim2.step() for _ in range(100)]

        # Prices should differ
        assert prices1 != prices2

    def test_no_seed_produces_different_results(self):
        """Test that no seed produces different results each time."""
        sim1 = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.20,
            time_step=0.01,
        )
        prices1 = [sim1.step() for _ in range(100)]

        sim2 = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.20,
            time_step=0.01,
        )
        prices2 = [sim2.step() for _ in range(100)]

        # Prices should differ (very unlikely to be identical)
        assert prices1 != prices2

    def test_generate_path(self):
        """Test that generate_path() produces correct number of ticks."""
        simulator = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.20,
            time_step=0.01,
            random_seed=42,
        )

        num_steps = 50
        path = simulator.generate_path(num_steps)

        assert len(path) == num_steps
        assert path[0].step == 1
        assert path[-1].step == num_steps

        # All prices should be positive
        for tick in path:
            assert tick.price > 0

    def test_generate_path_reproducibility(self):
        """Test that generate_path() is reproducible with seed."""
        sim1 = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.20,
            time_step=0.01,
            random_seed=42,
        )
        path1 = sim1.generate_path(100)

        sim2 = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.20,
            time_step=0.01,
            random_seed=42,
        )
        path2 = sim2.generate_path(100)

        # Paths should be identical
        assert len(path1) == len(path2)
        for t1, t2 in zip(path1, path2):
            assert t1.price == pytest.approx(t2.price)

    def test_volatility_effect(self):
        """Test that higher volatility produces larger price swings."""
        # Low volatility simulation
        sim_low = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.10,
            time_step=0.01,
            random_seed=42,
        )
        prices_low = [sim_low.step() for _ in range(100)]

        # High volatility simulation
        sim_high = PriceSimulator(
            initial_price=100.0,
            drift=0.05,
            volatility=0.50,
            time_step=0.01,
            random_seed=42,
        )
        prices_high = [sim_high.step() for _ in range(100)]

        # Calculate standard deviation of prices
        std_low = np.std(prices_low)
        std_high = np.std(prices_high)

        # High volatility should produce larger swings
        assert std_high > std_low

    def test_from_config(self):
        """Test creating simulator from MarketConfig."""
        from app.core.config import MarketConfig

        market_config = MarketConfig(
            initial_price=150.0,
            drift=0.08,
            volatility=0.25,
            time_step=0.02,
            random_seed=99,
        )

        simulator = PriceSimulator.from_config(market_config)

        assert simulator.get_current_price() == 150.0
        assert simulator.config.drift == 0.08
        assert simulator.config.volatility == 0.25
        assert simulator.config.time_step == 0.02
        assert simulator.config.random_seed == 99


class TestCalculateReturns:
    """Tests for calculate_returns function."""

    def test_empty_prices(self):
        """Test with empty price list."""
        returns = calculate_returns([])
        assert returns == []

    def test_single_price(self):
        """Test with single price (no returns possible)."""
        returns = calculate_returns([100.0])
        assert returns == []

    def test_basic_returns(self):
        """Test basic return calculation."""
        prices = [100.0, 101.0, 102.0, 101.5]
        returns = calculate_returns(prices)

        assert len(returns) == 3
        # All returns should be floats
        assert all(isinstance(r, float) for r in returns)

    def test_return_calculation_accuracy(self):
        """Test that returns are calculated correctly."""
        prices = [100.0, 110.0]
        returns = calculate_returns(prices)

        # log(110/100) = log(1.1) ≈ 0.09531
        expected = np.log(110.0 / 100.0)
        assert returns[0] == pytest.approx(expected, rel=1e-6)


class TestCalculateVolatility:
    """Tests for calculate_volatility function."""

    def test_empty_returns(self):
        """Test with empty returns."""
        vol = calculate_volatility([])
        assert vol == 0.0

    def test_single_return(self):
        """Test with single return (no volatility)."""
        vol = calculate_volatility([0.01])
        assert vol == 0.0

    def test_basic_volatility(self):
        """Test basic volatility calculation."""
        returns = [0.01, -0.02, 0.03, -0.01, 0.02]
        vol = calculate_volatility(returns, annualize=False)

        assert vol > 0
        assert isinstance(vol, float)

    def test_annualized_volatility(self):
        """Test that annualization increases volatility."""
        returns = [0.01, -0.02, 0.03, -0.01, 0.02]
        vol_daily = calculate_volatility(returns, annualize=False)
        vol_annual = calculate_volatility(returns, annualize=True)

        # Annualized should be larger (multiplied by sqrt(252))
        assert vol_annual > vol_daily
        assert vol_annual == pytest.approx(vol_daily * np.sqrt(252), rel=1e-6)

    def test_zero_volatility(self):
        """Test with constant returns (zero volatility)."""
        returns = [0.01, 0.01, 0.01, 0.01]
        vol = calculate_volatility(returns, annualize=False)
        assert vol == pytest.approx(0.0, abs=1e-10)
