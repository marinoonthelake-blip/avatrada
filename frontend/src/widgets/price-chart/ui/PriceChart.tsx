import React, { useEffect, useRef, useCallback } from 'react';
import { createChart, IChartApi, ISeriesApi, Time } from 'lightweight-charts';
import { useSharedWorker } from '@/shared/lib/useSharedWorker';

export const PriceChart = () => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const lineSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);

  const handleWorkerMessage = useCallback((message: any) => {
    try {
      const data = JSON.parse(message.payload);
      if (data.type === 'HEARTBEAT' && lineSeriesRef.current) {
        const newPoint = {
          time: Math.floor(new Date(data.timestamp).getTime() / 1000) as Time,
          value: new Date(data.timestamp).getSeconds(),
        };
        lineSeriesRef.current.update(newPoint);
      }
    } catch (e) { /* Ignore non-JSON */ }
  }, []);

  useSharedWorker(handleWorkerMessage);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight,
      layout: {
        background: { color: '#F1F3F5' }, // neutral-200
        textColor: '#212529', // neutral-900
      },
      grid: {
        vertLines: { color: '#E9ECEF' }, // neutral-300
        horzLines: { color: '#E9ECEF' },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: true,
      },
    });

    chartRef.current = chart;
    lineSeriesRef.current = chart.addLineSeries({
      color: '#0066CC', // action-primary
      lineWidth: 2,
    });

    // Handle chart resizing
    const resizeObserver = new ResizeObserver(entries => {
      if (entries.length > 0 && entries[0].contentRect) {
        const { width, height } = entries[0].contentRect;
        chart.applyOptions({ width, height });
      }
    });
    resizeObserver.observe(chartContainerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
    };
  }, []);

  return <div ref={chartContainerRef} className="w-full h-full" />;
};
