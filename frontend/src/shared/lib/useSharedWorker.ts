import { useEffect, useState } from 'react';

export function useSharedWorker(onMessage: (data: any) => void) {
  const [status, setStatus] = useState('Connecting...');

  useEffect(() => {
    const worker = new SharedWorker(new URL('/shared-worker.ts', import.meta.url), { type: 'module' });

    worker.port.onmessage = (event: MessageEvent) => {
      try {
        const parsedData = JSON.parse(event.data);
        if (parsedData.type === 'SYSTEM_STATUS') {
          setStatus(parsedData.payload);
        } else {
          onMessage(parsedData);
        }
      } catch (e) {
        console.error("Failed to parse worker message:", event.data);
      }
    };

    worker.port.start();

    return () => {
      worker.port.close();
    };
  }, [onMessage]);

  return { status };
}
