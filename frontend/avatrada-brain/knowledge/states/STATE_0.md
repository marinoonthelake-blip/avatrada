
# AVATRADA System State & Architecture Map - PHASE 0
**Version:** 2.2 (Exhaustive Granularity)
**Last Updated:** January 5, 2026

This document serves as the master architectural blueprint for **Phase 0: Project Scaffolding & Core Configuration**. It outlines every required file, its purpose, technology, and dependencies for establishing the project's foundation.

---

-   **`./STATE_0.md`**
    -   **Purpose**: This master document for Phase 0. Tracks the architecture, component map, and state of the system's foundation.
    -   **Key Tech/Pattern**: Markdown.
    -   **Dependencies**: N/A.

-   **`./.env`**
    -   **Purpose**: Stores all secrets and environment-specific configurations. This file is NEVER committed to version control.
    -   **Key Tech/Pattern**: Environment Variables.
    -   **Dependencies**: N/A.
    -   **Required Variables**:
        -   `GCP_PROJECT_ID`: Google Cloud Project ID.
        -   `GCP_REGION`: Primary GCP region (e.g., `us-east4`).
        -   `GCP_ZONE`: Primary GCP zone (e.g., `us-east4-a`).
        -   `GOOGLE_APPLICATION_CREDENTIALS`: Path to the GCP service account JSON key.
        -   `POSTGRES_USER`: Username for the PostgreSQL database.
        -   `POSTGRES_PASSWORD`: Password for the PostgreSQL user.
        -   `POSTGRES_DB`: Name of the PostgreSQL database.
        -   `POSTGRES_HOST`: Hostname for the PostgreSQL server (e.g., `postgres` in Docker).
        -   `POSTGRES_PORT`: Port for the PostgreSQL server (e.g., `5432`).
        -   `REDIS_HOST`: Hostname for the Redis server (e.g., `redis` in Docker).
        -   `REDIS_PORT`: Port for the Redis server (e.g., `6379`).
        -   `IBKR_ACCOUNT_ID`: Interactive Brokers account number for API access.
        -   `IBKR_HOST`: Hostname for the IBKR Gateway (e.g., `ib-gateway` in Docker).
        -   `IBKR_PORT`: Port for the IBKR Gateway API (e.g., `4004`).
        -   `THETADATA_API_KEY`: API key for ThetaData.
        -   `BENZINGA_API_KEY`: API key for Benzinga Pro.
        -   `TAVILY_API_KEY`: API key for Tavily.
        -   `GEMINI_API_KEY`: API key for Google Gemini.
        -   `OPERATOR_KEY_PASSWORD`: Passphrase for encrypting the operator's private key for the AI Firewall.

-   **`./.gitignore`**
    -   **Purpose**: Excludes sensitive files, environment files, compiled artifacts, and local state from version control.
    -   **Key Tech/Pattern**: Git.
    -   **Dependencies**: N/A.
    -   **Required Entries**: `__pycache__/`, `*.pyc`, `venv/`, `*.egg-info/`, `.env`, `.vscode/`, `.idea/`, `.terraform/`, `*.tfstate`, `*.tfstate.backup`, `*.pem`, `*.key`, `credentials.json`, `node_modules/`, `build/`, `dist/`, `*.log`, `returns_cache.csv`.

-   **`./docker-compose.yml`**
    -   **Purpose**: Defines and orchestrates all services for local development and staging.
    -   **Key Tech/Pattern**: Docker Compose.
    -   **Dependencies**: Docker, `.env` file.
    -   **Defined Services**:
        -   `postgres`: PostgreSQL 15 database service with a persistent volume.
        -   `redis`: Redis 7 service with AOF persistence enabled and a persistent volume.
        -   `ib-gateway`: `ghcr.io/gnzsnz/ib-gateway` service, configured for paper trading and read/write API access.
        -   `app`: The FastAPI backend service, built from `./Dockerfile`.
        -   `celery-worker`: The Celery worker service, built from `./Dockerfile` with a different entrypoint command.

-   **`./Dockerfile`**
    -   **Purpose**: Defines the container image for the Python backend application, including installation of system dependencies and Python packages.
    -   **Key Tech/Pattern**: Docker.
    -   **Dependencies**: `requirements.txt`.

-   **`./requirements.txt`**
    -   **Purpose**: Lists all Python dependencies for the backend application.
    -   **Key Tech/Pattern**: Pip.
    -   **Dependencies**: Python 3.11+.
    -   **Required Packages**:
        -   `fastapi[all]`: Core web framework with all optional dependencies (like `uvicorn`).
        -   `asyncpg`: High-performance asynchronous driver for PostgreSQL.
        -   `SQLAlchemy`: ORM and Core for database interaction.
        -   `redis`: Client library for Redis.
        -   `celery`: Distributed task queue for background jobs.
        -   `ib_async`: Asynchronous client for the Interactive Brokers API.
        -   `nest_asyncio`: To patch the asyncio event loop for `ib_async` compatibility.
        -   `httpx`: Modern, asynchronous HTTP client for API adapters.
        -   `websockets`: For connecting to WebSocket data feeds.
        -   `orjson`: High-performance JSON parsing library.
        -   `pandas`: Core data manipulation and analysis library.
        -   `numpy`: Fundamental package for numerical computing.
        -   `scipy`: For scientific and technical computing (e.g., root-finding).
        -   `pandas-ta`: Technical analysis library for indicators like ATR.
        -   `py_vollib`: For calculating option greeks (Delta, Gamma, Vega).
        -   `QuantLib-Python`: (Optional, advanced) For more complex financial modeling.
        -   `vaderSentiment`: Rule-based sentiment analysis for the fast-pass filter.
        -   `transformers`: For using advanced NLP models like FinBERT.
        -   `torch`: Required backend for `transformers`.
        -   `presidio-analyzer`: For robust PII detection in the LLM router.
        -   `spacy`: For general-purpose NLP tasks.
        -   `python-Levenshtein`: C-extension for fast fuzzy string matching.
        -   `thefuzz`: For fuzzy string matching in the Hallucination Guardrail.
        -   `google-generativeai`: Official client library for Google Gemini.
        -   `tiktoken`: For accurately counting tokens for LLM prompts.
        -   `cryptography`: For implementing the AI Firewall's cryptographic signature verification.
        -   `webauthn`: For implementing hardware key 2FA.
        -   `passlib`: For password hashing alongside WebAuthn.
        -   `pydantic`: For data validation and settings management.
        -   `scikit-learn`: For calculating the Brier Score in the Confidence Drift monitor.
        -   `google-cloud-storage`: For interacting with GCS for the Cold Storage tier.
        -   `pyarrow`: For reading and writing the efficient Parquet file format.
        -   `psycopg2-binary`: Required by SQLAlchemy for some operations, good to have.
        -   `PRAW`: Python Reddit API Wrapper for social media scraping.

---
