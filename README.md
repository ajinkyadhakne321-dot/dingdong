# ETF Market Making Simulator

An educational but technically serious end-to-end ETF market making simulation. This project is designed for learning quantitative finance, market microstructure, trading algorithms, and software engineering in a financial context.

## Project Status

**Phase 1: Complete** - Basic Price Simulator

This is a multi-phase project. Phase 1 implements the foundational price simulation using Geometric Brownian Motion. Subsequent phases will add order books, market making strategies, risk management, and a web dashboard.

## What is an ETF?

An Exchange-Traded Fund (ETF) is a basket of securities that trades on an exchange like a stock. ETFs hold assets such as stocks, bonds, commodities, or currencies and generally operate with an arbitrage mechanism designed to keep it trading close to its net asset value.

Key characteristics:
- **Diversification**: Hold multiple underlying assets
- **Liquidity**: Trade throughout the day like stocks
- **Transparency**: Holdings are disclosed daily
- **Cost efficiency**: Generally lower fees than mutual funds

## What is Market Making?

Market making is a trading strategy where a trader (the market maker) continuously quotes both buy (bid) and sell (ask) prices for a financial instrument, providing liquidity to the market.

### How Market Makers Work

1. **Quote Prices**: Market makers post bid prices (what they'll pay) and ask prices (what they'll sell for)
2. **Capture Spread**: They profit from the bid-ask spread (difference between buy and sell prices)
3. **Manage Inventory**: They must balance holding too much or too little of the asset
4. **Manage Risk**: They limit exposure to price movements and inventory concentration

### Why Market Making is Hard

- **Inventory Risk**: Prices can move against your position
- **Adverse Selection**: Informed traders may trade against you when you're mispriced
- **Volatility**: Higher volatility increases risk and requires wider spreads
- **Competition**: Other market makers compete for the same opportunities

## Architecture

The simulator follows a modular architecture:

```
ETF MARKET SIMULATOR
        |
        v
Market Simulator (GBM Price Process)
        |
        v
Market Data Feed
        |
        v
Order Book (Phase 2)
        |
        v
Matching Engine (Phase 2)
        |
    +---+---+
    |       |
    v       v
Market Maker    Other Traders
Strategy         (Phase 3)
    |
    v
Risk Management (Phase 5)
    |
    v
Execution (Phase 4)
    |
    v
Portfolio / P&L (Phase 4)
    |
    v
Analytics (Phase 5)
    |
    v
Web Dashboard (Phase 7)
```

### Current Implementation (Phase 1)

- **Market Simulator**: Geometric Brownian Motion price generator
- **Configuration**: YAML-based configuration with Pydantic validation
- **Testing**: Comprehensive unit tests for price simulation
- **Documentation**: Jupyter notebook demonstrating usage

## Mathematical Model

### Geometric Brownian Motion (GBM)

The price process is modeled using the stochastic differential equation:

```
dS = μSdt + σSdW
```

Where:
- **S(t)**: Asset price at time t
- **μ (mu)**: Drift coefficient (expected annual return)
- **σ (sigma)**: Volatility coefficient (annual volatility)
- **dW**: Wiener process (Brownian motion)

### Discrete-Time Implementation

For simulation, we use the Euler-Maruyama discretization:

```
S(t+dt) = S(t) × exp((μ - 0.5×σ²)dt + σ×√dt × Z)
```

Where **Z ~ N(0,1)** is a standard normal random variable.

### Why GBM?

1. **Positivity**: Ensures prices remain positive (essential for financial assets)
2. **Log-normal returns**: Returns follow a log-normal distribution, matching empirical observations
3. **Analytical tractability**: Used in Black-Scholes and other option pricing models
4. **Standard model**: Widely accepted in quantitative finance

### Assumptions

- Prices follow a continuous-time stochastic process
- Returns are log-normally distributed
- Volatility is constant (simplification - will be relaxed in later phases)
- No jumps or regime changes (simplification)
- No transaction costs or slippage (will be added later)

### Why Volatility Matters for Market Makers

Higher volatility means:
- **Larger price swings**: Both profits and losses can be larger
- **Wider spreads needed**: To compensate for increased risk
- **Higher inventory risk**: Positions can move against you quickly
- **More aggressive quoting**: May need to adjust quotes more frequently

The simulator allows testing different volatility regimes to understand their impact on market making strategies.

## Project Structure

```
etf-market-making-simulator/
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── api/                    # API routes (Phase 6)
│   │   ├── core/
│   │   │   └── config.py           # Configuration management
│   │   ├── market/
│   │   │   └── price_simulator.py  # GBM price simulator
│   │   ├── orderbook/              # Order book (Phase 2)
│   │   ├── matching/               # Matching engine (Phase 2)
│   │   ├── strategy/               # Trading strategies (Phase 3)
│   │   ├── risk/                   # Risk management (Phase 5)
│   │   ├── portfolio/              # Portfolio tracking (Phase 4)
│   │   ├── analytics/              # Performance analytics (Phase 5)
│   │   ├── simulation/             # Simulation orchestration (Phase 6)
│   │   └── models/                 # Data models
│   │
│   └── tests/
│       └── test_price_simulator.py # Unit tests
│
├── frontend/                       # React dashboard (Phase 7)
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── charts/
│       ├── hooks/
│       ├── services/
│       └── types/
│
├── notebooks/
│   └── 01_price_simulation_demo.ipynb  # Demo notebook
│
├── data/                           # Data storage
├── docs/                           # Documentation (Phase 1+)
├── config/
│   └── default.yaml                # Default configuration
│
├── requirements.txt                # Python dependencies
├── .gitignore
└── README.md
```

## Installation

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Git (for version control)

### Setup

1. **Clone the repository** (if using git):
   ```bash
   git clone <repository-url>
   cd etf-market-making-simulator
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**:
   ```bash
   python -c "import numpy, pandas, fastapi; print('Dependencies installed successfully')"
   ```

## Running the Project

### Running Tests

Phase 1 includes comprehensive unit tests for the price simulator:

```bash
cd backend
pytest tests/test_price_simulator.py -v
```

Expected output: 26 tests passing

### Running the Demo Notebook

The Jupyter notebook demonstrates the price simulator with visualizations:

```bash
cd notebooks
jupyter notebook 01_price_simulation_demo.ipynb
```

The notebook covers:
- Basic price simulation
- Visualization of price paths
- Returns and volatility analysis
- Effect of different volatility regimes
- Monte Carlo simulations
- Reproducibility with random seeds
- Step-by-step simulation

### Running the API Server (Phase 6+)

For Phase 1, the FastAPI server is minimal:

```bash
cd backend
python -m app.main
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API endpoints:
- `GET /`: Basic API information
- `GET /health`: Health check

## Configuration

Configuration is managed through YAML files in the `config/` directory.

### Default Configuration (config/default.yaml)

```yaml
market:
  initial_price: 100.0
  volatility: 0.20
  drift: 0.05
  time_step: 0.01
  random_seed: 42

market_maker:
  spread_bps: 5
  max_inventory: 1000
  order_size: 100

risk:
  max_order_size: 100
  max_daily_loss: 5000
  max_inventory: 1000

simulation:
  steps: 1000
  speed: "real-time"
```

### Using Configuration in Code

```python
from app.core.config import get_config
from pathlib import Path

# Load default configuration
config = get_config()

# Or load from a specific file
config = get_config(config_path=Path("config/custom.yaml"))

# Access configuration values
print(config.market.initial_price)
print(config.market.volatility)
```

## Example Usage

### Basic Price Simulation

```python
from app.market.price_simulator import PriceSimulator

# Create simulator
simulator = PriceSimulator(
    initial_price=100.0,
    drift=0.05,      # 5% annual return
    volatility=0.20, # 20% annual volatility
    time_step=0.01,  # ~3.65 days per step
    random_seed=42   # For reproducibility
)

# Generate a price path
price_path = simulator.generate_path(num_steps=252)  # One trading year

# Extract prices
prices = [tick.price for tick in price_path]

print(f"Initial price: ${prices[0]:.2f}")
print(f"Final price: ${prices[-1]:.2f}")
```

### Step-by-Step Simulation

```python
from app.market.price_simulator import PriceSimulator

simulator = PriceSimulator(
    initial_price=100.0,
    drift=0.05,
    volatility=0.20,
    time_step=0.01,
    random_seed=42
)

# Simulate step by step
for i in range(10):
    price = simulator.step()
    print(f"Step {i+1}: ${price:.2f}")

# Reset to initial state
simulator.reset()
```

### Calculating Returns and Volatility

```python
from app.market.price_simulator import calculate_returns, calculate_volatility

# Calculate log returns
returns = calculate_returns(prices)

# Calculate realized volatility
volatility = calculate_volatility(returns, annualize=True)

print(f"Realized volatility: {volatility*100:.2f}%")
```

## Testing

The project uses pytest for testing.

### Run all tests:

```bash
cd backend
pytest
```

### Run specific test file:

```bash
pytest tests/test_price_simulator.py -v
```

### Run with coverage:

```bash
pytest --cov=app tests/
```

### Test Coverage (Phase 1)

- Price simulator configuration validation
- Price generation and step-by-step simulation
- Reproducibility with random seeds
- Reset functionality
- Return calculations
- Volatility calculations
- Volatility effect on price paths

## Development Roadmap

### Phase 1: Complete ✅
- Repository structure
- Python environment
- Configuration management
- Basic market simulator (GBM)
- Unit tests
- Demo notebook
- Documentation

### Phase 2: Next
- Order data model
- Order book implementation
- Matching engine
- Price-time priority
- Trade records
- Unit tests

### Phase 3: Planned
- Simulated traders (random, momentum, mean-reversion)
- Trade generation
- Market data feed

### Phase 4: Planned
- Basic market maker strategy
- Inventory tracking
- P&L calculation
- Portfolio management

### Phase 5: Planned
- Risk engine
- Performance metrics
- Analytics

### Phase 6: Planned
- FastAPI implementation
- WebSocket endpoints
- Simulation control

### Phase 7: Planned
- React dashboard
- Charts and visualizations
- Order book UI

### Phase 8: Planned
- Full integration
- End-to-end testing

### Phase 9: Planned
- Advanced strategies
- Multiple ETFs
- Options market making

## Known Limitations (Phase 1)

- **Single asset**: Only simulates one ETF
- **Constant volatility**: Real markets have time-varying volatility
- **No jumps**: Real markets can have sudden price jumps
- **No microstructure**: No order book, bid-ask spread, or trading
- **No market maker**: Only price simulation, no trading strategy
- **No risk management**: No position limits or loss limits
- **No external factors**: No news, earnings, or macro events

These limitations will be addressed in subsequent phases.

## Future Improvements

- Multiple ETFs with correlation
- ETF basket/constituent relationships
- Statistical arbitrage strategies
- Options market making
- Realistic order arrival models
- Latency simulation
- Transaction costs and slippage
- Adverse selection modeling
- Regime change detection
- Historical market replay
- Machine learning models
- C++ performance-critical components

## Contributing

This is an educational project. Contributions are welcome, especially:
- Documentation improvements
- Additional trading strategies
- Performance optimizations
- Bug fixes
- Educational examples

## License

[To be determined]

## Educational Resources

### Recommended Reading
- "Options, Futures, and Other Derivatives" by John Hull
- "Algorithmic Trading" by Ernest Chan
- "Trading and Exchanges" by Larry Harris
- "Active Portfolio Management" by Grinold and Kahn

### Online Resources
- Investopedia: Market Making
- CFA Institute: Market Microstructure
- Quantitative Finance Stack Exchange

## Contact

[To be added]

---

**Note**: This is a simulation only. It does NOT connect to real brokers, exchanges, or execute real trades. Do not use this for actual trading.
