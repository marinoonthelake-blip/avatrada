
# AVATRADA System State & Architecture Map - PHASE 2
**Version:** 2.2 (Exhaustive Granularity)
**Last Updated:** January 5, 2026

This document serves as the master architectural blueprint for **Phase 2: Frontend Architecture & Core UI ("The Cockpit")**. It outlines every required file, its purpose, technology, and dependencies for the multi-monitor, high-performance user interface.

---

-   **`./frontend/package.json`**
    -   **Purpose**: Manages all frontend dependencies, scripts, and project metadata.
    -   **Key Tech/Pattern**: Node Package Manager (NPM or Yarn).
    -   **Dependencies**: `react`, `react-dom`, `electron`, `redux`, `react-redux`, `tailwindcss`, `ag-grid-enterprise`, `lightweight-charts` (or `tradingview-widget`), `playwright`, `eslint`, `eslint-plugin-import`, `typescript`, `@types/react`.

-   **`./electron/main.js`**
    -   **Purpose**: The Electron Main Process. Acts as the "Shared Brain" for the application. Responsibilities include: 1) Creating and programmatically positioning the three `BrowserWindow` instances across multiple monitors. 2) Listening for and handling renderer process crashes for graceful degradation. 3) Hosting the central Redux store and acting as the IPC relay for state synchronization.
    -   **Key Tech/Pattern**: Main Process Orchestration, Inter-Process Communication (IPC).
    -   **Dependencies**: `electron` (specifically `app`, `BrowserWindow`, `ipcMain`, `screen` modules).

-   **`./electron/preload.js`**
    -   **Purpose**: A secure script that runs in a privileged context to bridge the isolated renderer process and the Node.js environment of the main process. It exposes specific, safe functions (e.g., `sendAction`, `onStateUpdate`) to the renderer via `contextBridge`.
    -   **Key Tech/Pattern**: Secure IPC Bridge, Context Isolation.
    -   **Dependencies**: `electron` (specifically `contextBridge`, `ipcRenderer`).

-   **`./frontend/public/shared-worker.js`**
    -   **Purpose**: The centralized data hub, acting as a singleton for all UI tabs. Responsibilities include: 1) Managing the lifecycle of all 5 WebSocket connections (ThetaData, IBKR, Gemini, Tavily, Benzinga). 2) Performing data arbitration and failover between primary/secondary feeds. 3) Throttling high-frequency updates using a buffer-flush pattern. 4) Handling backpressure and detecting frozen UI tabs via a heartbeat mechanism.
    -   **Key Tech/Pattern**: Shared Web Worker, Singleton Pattern, Data Arbitration, Buffer-Flush.
    -   **Dependencies**: Browser APIs (`WebSocket`, `BroadcastChannel`, `MessagePort`, `requestAnimationFrame`).

-   **`./frontend/src/app/store.ts`**
    -   **Purpose**: Configures the Redux store for each renderer process. Includes a custom middleware that intercepts actions, forwards them to the main process via the preload script, and handles the hydration of new state received from the main process.
    -   **Key Tech/Pattern**: State Management, Redux Middleware.
    -   **Dependencies**: `@reduxjs/toolkit`, `electron/preload.js`.

-   **`./frontend/tailwind.config.js`**
    -   **Purpose**: Defines the entire "Military-Grade" design system. Configures semantic color tokens, high-density typography utilities (`tabular-nums`), the Z-Index layering strategy, and custom animations for alerts.
    -   **Key Tech/Pattern**: Design System Configuration.
    -   **Dependencies**: `tailwindcss`.

-   **`./frontend/src/widgets/`**
    -   **Purpose**: Directory for large, composite UI components as per Feature-Sliced Design (FSD). These widgets are assembled on pages and often combine multiple features and entities.
    -   **Key Tech/Pattern**: FSD Widgets.
    -   **Dependencies**: `react`, `ag-grid-enterprise`, `lightweight-charts`, `frontend/src/features/*`, `frontend/src/entities/*`.
    -   **Files**:
        -   `LiveTickerGrid.tsx`: Implements the AG Grid with `applyTransactionAsync` for high-frequency updates.
        -   `PriceChart.tsx`: Integrates the TradingView library with a custom Redux datafeed adapter.
        -   `OrderBookHeatmap.tsx`: Implements the Level 2 heatmap using HTML5 Canvas and off-screen rendering optimizations.
        -   `StrategyControlPanel.tsx`: UI for monitoring and controlling automated trading strategies.
        -   `PositionsPanel.tsx`: Displays current portfolio positions.
        -   `LLMResearchCenter.tsx`: The main interface for the AI "research council."
        -   `ScoutInterrogationModal.tsx`: UI for manually querying the 5 data scouts.
        -   `RiskScenarioAnalysis.tsx`: UI for portfolio stress testing.
        -   `CriticalAlert.tsx`: The non-dismissible, attention-demanding modal component.

-   **`./frontend/src/features/`**
    -   **Purpose**: FSD directory for components that encapsulate user actions or business logic (the "verbs" of the application).
    -   **Key Tech/Pattern**: FSD Features.
    -   **Dependencies**: `react`, `redux`, `frontend/src/entities/*`.
    -   **Files**:
        -   `PlaceOrderForm.tsx`: The complete form for manual order entry with bracket management.
        -   `EmergencyStopButton.tsx`: The global "kill switch" button.
        -   `CancelOrderButton.tsx`: A button to cancel a specific working order.
        -   `ToggleStrategy.tsx`: A component to pause/resume an automated strategy.

-   **`./frontend/src/entities/`**
    -   **Purpose**: FSD directory for core business data models (the "nouns") and their most basic, reusable UI representations.
    -   **Key Tech/Pattern**: FSD Entities.
    -   **Dependencies**: `react`.
    -   **Files**:
        -   `Order.ts`: TypeScript type definition for an order.
        -   `Position.ts`: TypeScript type definition for a position.
        -   `Instrument.ts`: TypeScript type definition for a financial instrument.
        -   `OrderRow.tsx`: A single row component for displaying an order in a list or grid.
        -   `PositionRow.tsx`: A single row component for displaying a position.

---
