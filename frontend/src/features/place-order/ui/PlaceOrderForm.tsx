import React, { useState } from 'react';
import { getApiBaseUrl } from '@/shared/config/api';

export const PlaceOrderForm = () => {
  const [symbol, setSymbol] = useState('SPY');
  const [quantity, setQuantity] = useState(10);
  const [price, setPrice] = useState(450.00);
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [status, setStatus] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('Sending...');

    try {
      const response = await fetch(`${getApiBaseUrl()}/trading/order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          action: side,
          quantity: Number(quantity),
          price: Number(price),
          source: 'MANUAL_USER'
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setStatus(`SUCCESS: ${data.status}`);
      } else {
        setStatus(`ERROR: ${data.detail || 'Unknown error'}`);
      }
    } catch (err) {
      setStatus(`FAILURE: Network Error`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-neutral-200 p-4 rounded border border-neutral-400 space-y-4">
      <h3 className="font-bold text-neutral-900 border-b border-neutral-400 pb-2">MANUAL ORDER ENTRY</h3>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-bold text-neutral-600">SYMBOL</label>
          <input 
            type="text" 
            value={symbol} 
            onChange={e => setSymbol(e.target.value.toUpperCase())}
            className="w-full bg-white border border-neutral-400 p-1 font-mono"
          />
        </div>
        <div>
          <label className="block text-xs font-bold text-neutral-600">QTY</label>
          <input 
            type="number" 
            value={quantity} 
            onChange={e => setQuantity(Number(e.target.value))}
            className="w-full bg-white border border-neutral-400 p-1 font-mono"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-bold text-neutral-600">PRICE</label>
          <input 
            type="number" 
            step="0.01"
            value={price} 
            onChange={e => setPrice(Number(e.target.value))}
            className="w-full bg-white border border-neutral-400 p-1 font-mono"
          />
        </div>
        <div className="flex items-end">
          <div className="flex w-full space-x-1">
            <button
              type="button"
              onClick={() => setSide('BUY')}
              className={`flex-1 py-1 font-bold text-sm ${side === 'BUY' ? 'bg-signal-bullish text-white' : 'bg-neutral-300 text-neutral-600'}`}
            >
              BUY
            </button>
            <button
              type="button"
              onClick={() => setSide('SELL')}
              className={`flex-1 py-1 font-bold text-sm ${side === 'SELL' ? 'bg-signal-bearish text-white' : 'bg-neutral-300 text-neutral-600'}`}
            >
              SELL
            </button>
          </div>
        </div>
      </div>

      <button 
        type="submit" 
        className="w-full bg-action-primary hover:bg-action-primary-hover text-white font-bold py-2 rounded shadow-sm"
      >
        SUBMIT ORDER
      </button>

      {status && (
        <div className={`text-xs font-mono p-2 rounded ${status.includes('SUCCESS') ? 'bg-state-success text-white' : 'bg-state-critical text-white'}`}>
          {status}
        </div>
      )}
    </form>
  );
};
