"""
Main entry point for the ETF Market Making Simulator backend.

This module provides the FastAPI application that will eventually serve:
- REST API endpoints
- WebSocket connections for real-time simulation updates
- Simulation control

For Phase 1, this is a minimal setup that will be expanded in later phases.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_config

# Initialize FastAPI app
app = FastAPI(
    title="ETF Market Making Simulator",
    description="An educational end-to-end ETF market making simulation",
    version="0.1.0",
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    config = get_config()
    return {
        "name": "ETF Market Making Simulator",
        "version": "0.1.0",
        "phase": "Phase 1 - Basic Price Simulator",
        "status": "In Development",
        "config": {
            "initial_price": config.market.initial_price,
            "volatility": config.market.volatility,
            "drift": config.market.drift,
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    config = get_config()
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
