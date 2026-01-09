import React, { useState, useCallback } from 'react';
import { useSharedWorker } from '@/shared/lib/useSharedWorker';

interface TradeIdea {
  ticker: string;
  signal: 'BUY' | 'SELL' | 'NEUTRAL';
  confidence: number;
  reasoning: string;
  time_horizon: string;
}

export const ResearchFeed = () => {
  const [ideas, setIdeas] = useState<TradeIdea[]>([]);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  const handleMessage = useCallback((message: any) => {
    try {
      const data = JSON.parse(message.payload);
      if (data.type === 'TRADE_IDEAS') {
        setIdeas(data.ideas);
        setLastUpdate(new Date(data.timestamp).toLocaleTimeString());
      }
    } catch (e) { }
  }, []);

  useSharedWorker(handleMessage);

  return (
    <div className="h-full w-full bg-neutral-100 text-neutral-900 flex flex-col border border-neutral-300">
      <div className="p-3 border-b border-neutral-300 flex justify-between items-center bg-white">
        <h3 className="font-bold text-sm tracking-wider text-action-primary">AI RESEARCH COUNCIL</h3>
        <span className="text-xs text-neutral-500">UPDATED: {lastUpdate || 'WAITING...'}</span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-neutral-50">
        {ideas.length === 0 ? (
          <div className="text-center text-neutral-500 mt-10 animate-pulse font-mono text-sm">
            Scanning Global Markets...
          </div>
        ) : (
          ideas.map((idea, idx) => (
            <div key={idx} className="bg-white border border-neutral-300 rounded p-4 shadow-sm hover:border-action-primary transition-colors">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <span className="text-xl font-bold font-mono text-neutral-900 mr-2">{idea.ticker}</span>
                  <span className={`text-xs font-bold px-2 py-1 rounded ${
                    idea.signal === 'BUY' ? 'bg-signal-bullish text-white' : 
                    idea.signal === 'SELL' ? 'bg-signal-bearish text-white' : 
                    'bg-neutral-500 text-white'
                  }`}>
                    {idea.signal}
                  </span>
                </div>
                <div className="text-right">
                  <div className="text-xs text-neutral-500">CONFIDENCE</div>
                  <div className="font-mono font-bold text-action-primary">{(idea.confidence * 100).toFixed(0)}%</div>
                </div>
              </div>

              <p className="text-sm text-neutral-700 mb-3 leading-relaxed">
                {idea.reasoning}
              </p>

              <div className="flex justify-between items-center pt-2 border-t border-neutral-200">
                <span className="text-xs text-neutral-500 font-mono">{idea.time_horizon.toUpperCase()}</span>
                <button className="bg-action-primary hover:bg-action-primary-hover text-white text-xs font-bold py-1 px-3 rounded">
                  EXECUTE
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
