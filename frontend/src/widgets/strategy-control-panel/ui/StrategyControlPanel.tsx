import React from 'react';
import { PlaceOrderForm } from '@/features/place-order/ui/PlaceOrderForm';

export const StrategyControlPanel = () => {
  return (
    <div className="h-full w-full p-4 overflow-y-auto bg-neutral-100">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Manual Execution Column */}
        <div>
          <PlaceOrderForm />

          <div className="mt-6 p-4 bg-neutral-200 rounded border border-neutral-400">
            <h3 className="font-bold text-neutral-900 mb-2">ACTIVE STRATEGIES</h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center bg-white p-2 border border-neutral-300">
                <span className="font-mono text-sm">GAMMA_SCALPER_SPY</span>
                <span className="text-xs bg-state-success text-white px-2 py-0.5 rounded">RUNNING</span>
              </div>
              <div className="flex justify-between items-center bg-white p-2 border border-neutral-300">
                <span className="font-mono text-sm">VOL_TARGET_QQQ</span>
                <span className="text-xs bg-neutral-500 text-white px-2 py-0.5 rounded">PAUSED</span>
              </div>
            </div>
          </div>
        </div>

        {/* System Status Column */}
        <div className="space-y-4">
           <div className="p-4 bg-neutral-800 text-white rounded">
              <h3 className="font-bold text-sm mb-2 text-neutral-400">SYSTEM HEALTH</h3>
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div>BUNKER: <span className="text-signal-bullish">ONLINE</span></div>
                <div>IBKR: <span className="text-signal-bullish">CONNECTED</span></div>
                <div>THETA: <span className="text-signal-bullish">STREAMING</span></div>
                <div>AI: <span className="text-signal-bullish">READY</span></div>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
};
