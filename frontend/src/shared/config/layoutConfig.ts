import { IJsonModel } from 'flexlayout-react';

export const layoutModel: IJsonModel = {
  global: {
    tabEnableFloat: true, // Allow tabs to be dragged out into new windows
  },
  layout: {
    type: 'row',
    weight: 100,
    children: [
      {
        type: 'tabset',
        weight: 25,
        children: [
          {
            type: 'tab',
            name: 'Ticker Grid',
            component: 'liveTickerGrid',
          },
          {
            type: 'tab',
            name: 'News Feed',
            component: 'newsFeed',
          },
        ],
      },
      {
        type: 'tabset',
        weight: 50,
        id: 'command-center',
        children: [
          {
            type: 'tab',
            name: 'Command Center',
            component: 'strategyControlPanel',
            enableClose: false,
          },
        ],
      },
      {
        type: 'tabset',
        weight: 25,
        children: [
          {
            type: 'tab',
            name: 'Analysis Chart',
            component: 'priceChart',
          },
          {
            type: 'tab',
            name: 'AI Research',
            component: 'llmResearchCenter',
          },
        ],
      },
    ],
  },
};
