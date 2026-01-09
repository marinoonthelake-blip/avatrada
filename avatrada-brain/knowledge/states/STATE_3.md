
# AVATRADA System State & Architecture Map - PHASE 3
**Version:** 2.2 (Exhaustive Granularity)
**Last Updated:** January 5, 2026

This document serves as the master architectural blueprint for **Phase 3: Integration, Testing, & Reliability**. It outlines every required file and process for ensuring the system is robust, observable, and reliable through automated testing and CI/CD.

---

-   **`./.github/workflows/ci.yml`**
    -   **Purpose**: Defines the Continuous Integration pipeline that automates quality checks and build processes on every code push. It will contain jobs for: 1) Linting (backend Python and frontend TypeScript/JS), 2) Running backend unit tests (`pytest`), 3) Running frontend unit/component tests, 4) Building the backend Docker image for the `linux/amd64` platform, and 5) Pushing the versioned image to a container registry (Google Container Registry).
    -   **Key Tech/Pattern**: Continuous Integration / Continuous Deployment (CI/CD).
    -   **Dependencies**: GitHub Actions, Docker, `requirements.txt`, `frontend/package.json`.

-   **`./frontend/.eslintrc.js`**
    -   **Purpose**: ESLint configuration to programmatically enforce the Feature-Sliced Design (FSD) import boundaries. It prevents architectural decay by making illegal imports (e.g., a `feature` importing a `widget`) a build-time error, ensuring long-term maintainability.
    -   **Key Tech/Pattern**: Static Code Analysis, Architectural Linting.
    -   **Dependencies**: `eslint`, `eslint-plugin-import`, `typescript-eslint/parser`.

-   **`./tests/e2e/chaos.spec.ts`**
    -   **Purpose**: An end-to-end (E2E) test using Playwright that implements a "Chaos Monkey." It registers a Service Worker to intercept and deliberately degrade the WebSocket connection (injecting latency, dropping packets, forcing disconnects) to verify the UI's resilience, reconnection logic, and state synchronization under adverse network conditions.
    -   **Key Tech/Pattern**: Chaos Engineering, End-to-End Testing.
    -   **Dependencies**: `playwright`, Node.js, a running instance of the application.

-   **`./tests/load/rendering.spec.ts`**
    -   **Purpose**: A performance load test using Playwright. It injects a mock WebSocket to simulate a high-frequency data stream (5,000+ updates/sec) and uses the Chrome DevTools Protocol (CDP) to measure key rendering metrics like Frames Per Second (FPS) and JavaScript Heap Size to detect performance degradation and memory leaks.
    -   **Key Tech/Pattern**: Load Testing, Performance Monitoring.
    -   **Dependencies**: `playwright`, Node.js.

-   **`./scripts/run_wfa.py`**
    -   **Purpose**: A standalone Python script for running Walk-Forward Analysis (WFA) on trading algorithms. This provides a more robust validation of strategy parameters than simple backtesting by mitigating the risk of overfitting. It sequentially optimizes parameters on in-sample data and validates them on subsequent out-of-sample data.
    -   **Key Tech/Pattern**: Algorithmic Validation, Out-of-Sample Testing.
    -   **Dependencies**: `pandas`, historical market data source.

---
