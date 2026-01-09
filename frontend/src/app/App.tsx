import React from 'react';
import { Layout, Model, TabNode } from 'flexlayout-react';
import 'flexlayout-react/style/light.css';
import { layoutModel } from '@/shared/config/layoutConfig';

// Import Widgets
import LiveTickerGrid from '@/widgets/live-ticker-grid/ui/LiveTickerGrid'; // Corrected import
import { NewsFeed } from '@/widgets/news-feed/ui/NewsFeed';
import { StrategyControlPanel } from '@/widgets/strategy-control-panel/ui/StrategyControlPanel';
import { PriceChart } from '@/widgets/price-chart/ui/PriceChart';
import { LLMResearchCenter } from '@/widgets/llm-research-center/ui/LLMResearchCenter';

const model = Model.fromJson(layoutModel);

const factory = (node: TabNode) => {
  const component = node.getComponent();
  switch (component) {
    case 'liveTickerGrid':
      return <LiveTickerGrid />;
    case 'newsFeed':
      return <NewsFeed />;
    case 'strategyControlPanel':
      return <StrategyControlPanel />;
    case 'priceChart':
      return <PriceChart />;
    case 'llmResearchCenter':
      return <LLMResearchCenter />;
    default:
      return null;
  }
};

function App() {
  return (
    <div className="relative w-screen h-screen bg-neutral-100">
      <Layout model={model} factory={factory} />
    </div>
  );
}

export default App;
