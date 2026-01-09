/// <reference lib="webworker" />

declare const self: SharedWorkerGlobalScope;

const ports = new Set<MessagePort>();
let socket: WebSocket | null = null;

const connectWebSocket = () => {
    // Use the environment variable for the WebSocket URL
    const wsUrl = `${import.meta.env.VITE_API_BASE_URL}/ws/stream`;
    console.log('[Worker] Attempting to connect to WebSocket:', wsUrl);

    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log('[Worker] WebSocket connection established.');
        broadcast({ type: 'SYSTEM_STATUS', payload: 'WebSocket Connected' });
    };

    socket.onmessage = (event) => {
        broadcast({ type: 'DATA', payload: event.data });
    };

    socket.onclose = (event) => {
        console.log(`[Worker] WebSocket disconnected. Code: ${event.code}. Reconnecting in 3s...`);
        socket = null;
        broadcast({ type: 'SYSTEM_STATUS', payload: 'WebSocket Disconnected' });
        setTimeout(connectWebSocket, 3000);
    };

    socket.onerror = (error) => {
        console.error('[Worker] WebSocket error:', error);
        broadcast({ type: 'SYSTEM_STATUS', payload: 'WebSocket Error' });
        socket?.close();
    };
};

const broadcast = (message: any) => {
    const payload = JSON.stringify(message);
    ports.forEach(port => {
        port.postMessage(payload);
    });
};

self.onconnect = (e: MessageEvent) => {
    const port = e.ports[0];
    ports.add(port);
    console.log(`[Worker] UI client connected. Total clients: ${ports.size}`);

    port.onmessage = (event) => {
        console.log('[Worker] Message from UI:', event.data);
    };

    port.start();
};

connectWebSocket();
