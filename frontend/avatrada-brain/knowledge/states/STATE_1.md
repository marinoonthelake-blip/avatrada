
# AVATRADA System State & Architecture Map - PHASE 1
**Version:** 2.2 (Exhaustive Granularity)
**Last Updated:** January 5, 2026

This document serves as the master architectural blueprint for **Phase 1: Backend Infrastructure & Core Services ("The Bunker")**. It outlines every required file, its purpose, technology, and dependencies for the headless, cloud-native trading system.

---

### 1.1 Infrastructure (IaC)

-   **`./terraform/main.tf`**
    -   **Purpose**: Provisions the GCP C2 instance, Persistent Disk, Firewall Rules, and auto-healing Managed Instance Group (MIG). Includes the startup script for kernel tuning (CPU isolation, C-states).
    -   **Key Tech/Pattern**: Infrastructure as Code (IaC).
    -   **Dependencies**: Terraform, GCP Provider, `startup-script.sh` (embedded).

### 1.2 Core Application & Configuration

-   **`./src/main.py`**
    -   **Purpose**: The main FastAPI application entry point. Initializes all services, mounts API routers, and defines the WebSocket gateway.
    -   **Key Tech/Pattern**: ASGI Web Server.
    -   **Dependencies**: `fastapi`, `uvicorn`, `src/api/*`, `src/core/database.py`, `src/core/config.py`.

-   **`./src/core/config.py`**
    -   **Purpose**: Loads, validates, and provides a typed configuration object from environment variables (`.env`) to the entire application.
    -   **Key Tech/Pattern**: Centralized Configuration (Pydantic).
    -   **Dependencies**: `.env` file, `pydantic`.

-   **`./src/core/database.py`**
    -   **Purpose**: Manages the asynchronous PostgreSQL connection pool.
    -   **Key Tech/Pattern**: Async DB Connection Pool.
    -   **Dependencies**: `sqlalchemy`, `asyncpg`, `src/core/config.py`.

-   **`./src/core/logging_config.py`**
    -   **Purpose**: Configures structured (JSON) logging with `trace_id` for observability.
    -   **Key Tech/Pattern**: Structured Logging.
    -   **Dependencies**: `logging`.

-   **`./src/core/security.py`**
    -   **Purpose**: Implements WebAuthn (Hardware 2FA) logic for user authentication.
    -   **Key Tech/Pattern**: Public-Key Cryptography.
    -   **Dependencies**: `fastapi`, `webauthn`, `passlib`.

### 1.3 API Transport Layer

-   **`./src/api/trading_routes.py`**:
    -   **Purpose**: Defines API endpoints for manual order submission and strategy control.
    -   **Key Tech/Pattern**: API Router.
    -   **Dependencies**: `fastapi`, `src/services/execution/order_gateway.py`.
-   **`./src/api/backtest_routes.py`**:
    -   **Purpose**: Defines endpoints to start and monitor backtests.
    -   **Key Tech/Pattern**: API Router.
    -   **Dependencies**: `fastapi`, `celery_worker/tasks.py`.
-   **`./src/api/websocket_gateway.py`**:
    -   **Purpose**: Contains the `ConnectionManager` for handling real-time WebSocket subscriptions and broadcasts.
    -   **Key Tech/Pattern**: WebSocket Gateway.
    -   **Dependencies**: `fastapi`, `redis` (for scaling).

### 1.4 Asynchronous Task Processing (Celery)

-   **`./celery_worker/main.py`**:
    -   **Purpose**: Entry point for the Celery worker process.
    -   **Key Tech/Pattern**: Distributed Task Queue.
    -   **Dependencies**: `celery`, `redis`, `src/core/config.py`.
-   **`./celery_worker/tasks.py`**:
    -   **Purpose**: Defines asynchronous tasks, primarily `run_backtest`.
    -   **Key Tech/Pattern**: Task Definition.
    -   **Dependencies**: `celery`, `redis`, `pandas`.

### 1.5 External Service Adapters

-   **`./src/adapters/ibkr_adapter.py`**:
    -   **Purpose**: Manages connection and communication with the IBKR Gateway.
    -   **Key Tech/Pattern**: Broker Adapter Pattern.
    -   **Dependencies**: `ib_async`, `nest_asyncio`, `src/core/config.py`.
-   **`./src/adapters/thetadata_adapter.py`**:
    -   **Purpose**: Manages the high-speed WebSocket connection to ThetaData.
    -   **Key Tech/Pattern**: Data Feed Adapter.
    -   **Dependencies**: `httpx`, `websockets`, `src/core/config.py`.
-   **`./src/adapters/benzinga_adapter.py`**:
    -   **Purpose**: Connects to the Benzinga Pro API to fetch real-time news.
    -   **Key Tech/Pattern**: Data Feed Adapter.
    -   **Dependencies**: `httpx`, `src/core/config.py`.
-   **`./src/adapters/tavily_adapter.py`**:
    -   **Purpose**: Connects to the Tavily API for web intelligence.
    -   **Key Tech/Pattern**: Data Feed Adapter.
    -   **Dependencies**: `httpx`, `src/core/config.py`.

### 1.6 AI & Quantitative Services

-   **`./src/services/ai/router.py`**:
    -   **Purpose**: Contains the `LLMModelRouter` to select the appropriate model (Gemini Pro/Flash, local Gemma).
    -   **Key Tech/Pattern**: AI Model Routing.
    -   **Dependencies**: `google-generativeai`, `presidio-analyzer`, `src/core/config.py`.
-   **`./src/services/ai/guardrails.py`**:
    -   **Purpose**: Contains the `HallucinationGuardrail` to validate AI-generated symbols.
    -   **Key Tech/Pattern**: AI Safety Layer.
    -   **Dependencies**: `pandas`, `thefuzz`.
-   **`./src/services/ai/research_agent.py`**:
    -   **Purpose**: The "research council" that orchestrates data gathering from all adapters to build context for the LLM.
    -   **Key Tech/Pattern**: Multi-Agent Orchestration.
    -   **Dependencies**: all `src/adapters/*`, `src/services/ai/router.py`.
-   **`./src/services/quant/gex_calculator.py`**:
    -   **Purpose**: Calculates Gamma Exposure (GEX) from options chain data.
    -   **Key Tech/Pattern**: Financial Mathematics.
    -   **Dependencies**: `pandas`, `numpy`.
-   **`./src/services/quant/zero_gamma_finder.py`**:
    -   **Purpose**: Implements the root-finding algorithm to locate the Zero Gamma "flip point".
    -   **Key Tech/Pattern**: Numerical Methods.
    -   **Dependencies**: `scipy`, `numpy`.
-   **`./src/services/quant/signal_aggregator.py`**:
    -   **Purpose**: Contains the `SignalAggregationEngine` for `UNANIMOUS` or `WEIGHTED_VOTE` logic.
    -   **Key Tech/Pattern**: Signal Processing.
    -   **Dependencies**: N/A.
-   **`./src/services/quant/sentiment_analyzer.py`**:
    -   **Purpose**: Implements the hybrid VADER/FinBERT model for high-performance local sentiment scoring.
    -   **Key Tech/Pattern**: NLP Pipeline.
    -   **Dependencies**: `vaderSentiment`, `transformers`, `torch`.

### 1.7 Execution Services

-   **`./src/services/execution/order_gateway.py`**:
    -   **Purpose**: The single entry point for all order requests. Contains the **AI Execution Firewall** and the **Pre-Flight Validation Layer**.
    -   **Key Tech/Pattern**: Gateway/Facade Pattern.
    -   **Dependencies**: all `src/services/risk/*`, all `src/services/execution/*`, `cryptography`.
-   **`./src/services/execution/base_executor.py`**:
    -   **Purpose**: Defines an abstract base class for all execution algorithms.
    -   **Key Tech/Pattern**: Abstract Base Class.
    -   **Dependencies**: N/A.
-   **`./src/services/execution/simple_executor.py`**:
    -   **Purpose**: Handles basic Market and Limit order submissions.
    -   **Key Tech/Pattern**: Simple Executor.
    -   **Dependencies**: `src/adapters/ibkr_adapter.py`.
-   **`./src/services/execution/bracket_executor.py`**:
    -   **Purpose**: Implements the client-side state machine for Bracket Orders.
    -   **Key Tech/Pattern**: State Machine.
    -   **Dependencies**: `src/adapters/ibkr_adapter.py`.
-   **`./src/services/execution/iceberg_executor.py`**:
    -   **Purpose**: Implements the client-side logic for Iceberg Orders.
    -   **Key Tech/Pattern**: Algorithmic Executor.
    -   **Dependencies**: `src/adapters/ibkr_adapter.py`.

### 1.8 Risk Management Services

-   **`./src/services/risk/pre_flight_validator.py`**:
    -   **Purpose**: Performs initial, fast checks: Max Position Size, Buying Power, Fat Finger, and NBBO Enforcement.
    -   **Key Tech/Pattern**: Pre-Trade Hook.
    -   **Dependencies**: `src/adapters/ibkr_adapter.py`.
-   **`./src/services/risk/concentration_validator.py`**:
    -   **Purpose**: Enforces Sector (40%) and Single Ticker (15%) concentration limits.
    -   **Key Tech/Pattern**: Pre-Trade Hook.
    -   **Dependencies**: `pandas`.
-   **`./src/services/risk/correlation_validator.py`**:
    -   **Purpose**: Implements the "Correlation Hard-Block" to prevent adding a 3rd highly correlated position.
    -   **Key Tech/Pattern**: Pre-Trade Hook.
    -   **Dependencies**: `pandas`, `numpy`.
-   **`./src/services/risk/sizing/kelly_sizer.py`**:
    -   **Purpose**: Implements the Fractional Kelly Criterion for position sizing.
    -   **Key Tech/Pattern**: Financial Formula.
    -   **Dependencies**: `numpy`.
-   **`./src/services/risk/sizing/volatility_scaler.py`**:
    -   **Purpose**: Implements ATR/IV-based volatility targeting for position sizing.
    -   **Key Tech/Pattern**: Financial Formula.
    -   **Dependencies**: `pandas-ta`, `py_vollib`.
-   **`./src/services/risk/monitors/drawdown_monitor.py`**:
    -   **Purpose**: Contains the `DrawdownScaler` logic to reduce size at 10% DD and halt at 20% DD.
    -   **Key Tech/Pattern**: Circuit Breaker.
    -   **Dependencies**: N/A.
-   **`./src/services/risk/monitors/streak_monitor.py`**:
    -   **Purpose**: Implements the "Losing Streak Breaker" to pause a strategy after 5 consecutive losses.
    -   **Key Tech/Pattern**: Circuit Breaker.
    -   **Dependencies**: N/A.
-   **`./src/services/risk/monitors/edge_decay_monitor.py`**:
    -   **Purpose**: Implements the rolling Sharpe ratio check to detect and pause decaying strategies.
    -   **Key Tech/Pattern**: Performance Monitoring.
    -   **Dependencies**: `pandas`, `numpy`.
-   **`./src/services/risk/monitors/orphan_monitor.py`**:
    -   **Purpose**: Implements the state machine to detect and liquidate orphaned positions.
    -   **Key Tech/Pattern**: State Machine / Safety Monitor.
    -   **Dependencies**: N/A.

### 1.9 Database & Migrations

-   **`./db/migrations/001_initial_schema.sql`**:
    -   **Purpose**: Creates core tables: `trade_ledger`, `strategies`, `signal_sources`, and the immutable `audit_log` with its `prevent_modification` trigger.
    -   **Key Tech/Pattern**: SQL DDL.
    -   **Dependencies**: PostgreSQL 15.
-   **`./db/migrations/002_tca_schemas.sql`**:
    -   **Purpose**: Adds tables required for Transaction Cost Analysis and data quality monitoring: `correlation_snapshots`, `nbbo_snapshots`, `execution_quality_log`.
    -   **Key Tech/Pattern**: SQL DDL.
    -   **Dependencies**: PostgreSQL 15.

---
