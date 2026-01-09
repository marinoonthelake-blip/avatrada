# SOURCE PDF: avatrada_ui_9_topic_001.pdf

Deep Research: Avatrada Ui 9 Topic 001
Engineering Report: High-Frequency
Frontend Architecture
To:  Lead  Engineering  Team  From:  Autonomous  Technical  Researcher  Date:
October 26, 2023  Subject: Deep-Dive Analysis of a High-Frequency Trading
Frontend using Feature-Sliced Design (FSD) and React 18
1. Executive Summary
This  report  provides  a  detailed  technical  specification  for  building  a  high-
performance,  scalable,  and  maintainable  frontend  for  a  financial  trading
terminal.  The  architecture  is  based  on  the  Feature-Sliced  Design  (FSD)
methodology for structural integrity and React 18's concurrent features for UI
responsiveness under heavy data load.
The  analysis  deconstructs  four  key  areas:  1.  FSD  Folder  Structure:  A
prescriptive layout for a trading application to ensure modularity and prevent
dependency hell. 2.  Architectural Enforcement: An ESLint configuration to
programmatically enforce FSD's strict import boundaries. 3. High-Throughput
State Management: A custom Redux middleware designed to ingest and batch
over  1,000  WebSocket  messages  per  second  without  compromising  a  60fps
render loop. 4. Concurrent UI Rendering: A practical application of React 18's
useTransition hook to maintain critical UI responsiveness during non-urgent,
heavy state updates.
The findings conclude that this architectural combination is exceptionally well-
suited  for  the  demands  of  a  high-frequency  trading  environment,  offering  a
robust framework for both development velocity and runtime performance.

2. FSD Folder Structure for a Trading Terminal
2.1. Technical Deconstruction
Feature-Sliced Design is a prescriptive architectural methodology for frontend
applications. Its primary goal is to manage complexity by organizing code into
layers and slices, enforcing a unidirectional data and dependency flow. This is
critical in a trading terminal where features like "Order Entry," "Charting," and
"Position  Management"  must  be  developed  and  maintained  in  isolation  to
prevent system-wide failures.
The layers are arranged from most abstract to most specific: - app: Application-
wide setup (store, routing, global styles). -  processes: Multi-step user flows
(e.g., authentication, multi-leg order execution). -  pages: Unique application
screens, composed of widgets. - widgets: Composite UI blocks (e.g., the entire
order  book).  -  features:  User-driven  actions  (e.g.,  placing  an  order).  -
entities:  Core  business  data  models  (e.g.,  Order,  Instrument).  -  shared:
Reusable, business-agnostic code (UI kits, formatters, API clients).
2.2. Implementation Strategy
The following folder structure is tailored for a typical trading terminal. Each
slice  (e.g.,  features/place-order)  exposes  a  controlled  public  API  via  its
index.ts file.
src/
├──app/
│ ├──providers/ # React Context, Redux Provider, Router
│ ├──styles/ # Global styles, theme variables
│ └──index.tsx # Application entry point
│
├──processes/
│ ├──auth/ # Login, 2FA, logout flow
│ └──trade-execution/# Multi-stage trade confirmation process
│
├──pages/
│ ├──trading-terminal/# The main trading dashboard

│ │ └──index.tsx
│ ├──portfolio/
│ │ └──index.tsx
│ └──settings/
│ └──index.tsx
│
├──widgets/
│ ├──order-book/
│ │ ├──ui/OrderBook.tsx
│ │ └──index.ts # export { OrderBook } from './ui/OrderBook';
│ ├──price-chart/
│ ├──positions-panel/
│ └──news-feed/
│
├──features/
│ ├──place-order/
│ │ ├──ui/PlaceOrderForm.tsx
│ │ ├──model/orderSlice.ts
│ │ └──index.ts # export { PlaceOrderForm } from './ui/
PlaceOrderForm';
│ ├──cancel-order/
│ └──switch-instrument/
│
├──entities/
│ ├──order/
│ │ ├──model/types.ts# Order type definitions
│ │ ├──ui/OrderRow.tsx
│ │ └──index.ts # export * from './model/types'; export 
{ OrderRow } ...
│ ├──position/
│ ├──instrument/
│ └──user/
│
└──shared/
├──ui/ # Generic components: Button, Input, Spinner
├──lib/ # Business-agnostic helpers: formatters, hooks
├──api/ # WebSocket client, HTTP client setup
└──config/ # Environment variables, constants

2.3. Critical Analysis
Failure Mode (Boundary Violation): A developer in the features/place-
order slice might be tempted to directly import the widgets/positions-
panel to trigger a refresh. This is an illegal import (feature -> widget)
that creates tight coupling. The correct approach is for the feature to
dispatch a Redux action, and the widget, subscribed to the relevant state,
updates independently.
Edge Case (Cross-Slice Logic): A feature like "Close All Positions" needs
to interact with multiple position entities. This logic should reside within
the feature itself, which orchestrates actions on the entities via the store,
respecting the FSD flow. The feature acts as the orchestrator, while the
entity remains the passive data model.
Optimization (Public API): The index.ts barrel files are critical. They
must be curated to expose only what is necessary. Exposing internal state
or helper functions breaks encapsulation and makes the slice difficult to
refactor. A strict "Public API" discipline is paramount.
3. ESLint Configuration for FSD Boundary
Enforcement
3.1. Technical Deconstruction
To  prevent  architectural  decay,  FSD's  layer  boundaries  must  be  enforced
automatically. Manual code reviews are insufficient and error-prone. The ideal
tool for this is a static analyzer like ESLint, configured with rules that restrict
import paths between different layers. This turns architectural rules into a CI/
CD-enforced reality.
3.2. Implementation Strategy
We will use the  eslint-plugin-import package, specifically its  no-restricted-
paths rule. This allows us to define zones for each FSD layer and specify which
other zones they are forbidden from importing. This configuration assumes path
• 
• 
• 

aliases  (e.g.,  @/features)  are  set  up  in  the  project's  tsconfig.json or
jsconfig.json.
// .eslintrc.js
module.exports={
// ... other ESLint settings (extends, parser, etc.)
plugins:['import'],
rules:{
'import/no-restricted-paths':[
'error',
{
zones:[
// Rule: Shared can't import from anywhere else
{
target:'./src/shared',
from:['./src/entities','./src/features','./src/widgets','./src/
pages','./src/processes','./src/app'],
message:'Violation: The `shared` layer cannot import from higher-
level FSD layers.',
},
// Rule: Entities can only import from Shared
{
target:'./src/entities',
from:['./src/features','./src/widgets','./src/pages','./src/
processes','./src/app'],
message:'Violation: The `entities` layer cannot import from higher-
level FSD layers.',
},
// Rule: Features can only import from Entities and Shared
{
target:'./src/features',
from:['./src/widgets','./src/pages','./src/processes','./src/
app'],
message:'Violation: A `feature` cannot import from `widgets`, 
`pages`, `processes`, or `app`.',
},
// Rule: Widgets can only import from Features, Entities, and Shared
{
target:'./src/widgets',

from:['./src/pages','./src/processes','./src/app'],
message:'Violation: A `widget` cannot import from `pages`, 
`processes`, or `app`.',
},
// Rule: Pages can only import from Widgets, Features, Entities, and 
Shared
{
target:'./src/pages',
from:['./src/processes','./src/app'],
message:'Violation: A `page` cannot import from `processes` or 
`app`.',
},
// Rule: Processes can import from any layer except App
{
target:'./src/processes',
from:['./src/app'],
message:'Violation: A `process` cannot import from `app`.',
},
],
},
],
},
settings:{
'import/resolver':{
typescript:{// or 'node' if using JS with jsconfig
alwaysTryTypes:true,
},
},
},
};
3.3. Critical Analysis
Failure Mode (Configuration Drift): If a new layer is added or path
aliases change, this ESLint configuration must be updated. Failure to do so
will render the rules ineffective or cause false positives. This file should be
considered a core architectural artifact.
• 

Edge Case (Type Imports): Sometimes, a lower layer may need to import
a TypeScript type from a higher layer without importing any runtime
code. The import type { ... } from '...' syntax can sometimes bypass
simple path restrictions depending on the parser. More advanced static
analysis or custom rules might be needed if this becomes a problem, but 
no-restricted-paths is generally sufficient.
Optimization (IDE Integration): For maximum effectiveness, the ESLint
plugin must be integrated into the developers' IDEs (e.g., VS Code ESLint
extension). This provides immediate feedback, preventing boundary
violations before the code is even committed.
4. High-Frequency Redux Middleware for
WebSocket Data
4.1. Technical Deconstruction
A  trading  terminal's  primary  data  source  is  often  a  WebSocket  connection
streaming market data (ticks). A naive implementation would dispatch a Redux
action for every incoming message. At 1,000+ messages/sec, this would trigger
1,000+ state updates and re-renders, overwhelming the React reconciler and
freezing the browser's main thread.
The solution is to create a custom Redux middleware that acts as a buffer. It
intercepts incoming tick actions, collects them, and dispatches a single, batched
update  action  synchronized  with  the  browser's  paint  cycle  using
requestAnimationFrame. This ensures the UI updates at a maximum of 60fps (or
the monitor's refresh rate), regardless of the incoming message frequency.
4.2. Implementation Strategy
This middleware buffers ticks in a Map to ensure only the latest price for each
instrument is stored within a single frame. It uses a flag (isUpdateScheduled) to
prevent scheduling more than one requestAnimationFrame callback per frame.
• 
• 

// src/shared/api/websocket-middleware.ts
import{Middleware,Dispatch,AnyAction}from'@reduxjs/toolkit';
import{marketSlice}from'../../entities/instrument/model/marketSlice';
// A Map is used to store the latest tick for each symbol, overwriting older 
ones.
consttickBuffer=newMap<string,number>();
letisUpdateScheduled=false;
exportconstwebsocketTickBufferingMiddleware: Middleware=
(store)=>(next: Dispatch)=>(action: AnyAction)=>{
// Intercept only the specific raw tick action from the WebSocket client
if(action.type!=='websocket/rawTickReceived'){
returnnext(action);
}
const{symbol,price}=action.payload;
tickBuffer.set(symbol,price);
// If an update is not already scheduled for the next frame, schedule one.
if(!isUpdateScheduled){
isUpdateScheduled=true;
requestAnimationFrame(()=>{
// Dispatch a single batched action with all collected ticks
store.dispatch(marketSlice.actions.updateTicks(Object.fromEntries(tickBuffer)));
// Clear the buffer and reset the flag for the next frame
tickBuffer.clear();
isUpdateScheduled=false;
});
}
};
// Example usage in Redux store configuration:
// configureStore({
//   reducer: { ... },
//   middleware: (getDefaultMiddleware) =>

//     getDefaultMiddleware().concat(websocketTickBufferingMiddleware),
// });
// In the marketSlice reducer (using RTK's Immer for efficient mutation):
// updateTicks: (state, action: PayloadAction<Record<string, number>>) => {
//   for (const symbol in action.payload) {
//     if (state.prices[symbol]) {
//       state.prices[symbol] = action.payload[symbol];
//     }
//   }
// }
4.3. Critical Analysis
Failure Mode (Main Thread Blocking): If another part of the application
blocks the main thread for an extended period (e.g., > 100ms), the 
requestAnimationFrame callback will be delayed. During this time, the 
tickBuffer could accumulate a large number of messages, leading to a
memory spike upon the thread's release. A potential mitigation is to cap the
buffer size, though this would mean dropping data.
Edge Case (Tab Throttling): Browsers heavily throttle 
requestAnimationFrame for background tabs. This is generally desired
behavior, as it saves resources. However, if the application needs to
maintain a precise state log even when backgrounded, this middleware is
insufficient. A Web Worker would be required to process the WebSocket
stream off the main thread.
Optimization (Data Structure): Using a Map is highly efficient for this
use case. It provides O(1) insertion and update complexity, and it naturally
de-duplicates ticks for the same instrument within a single animation
frame, ensuring only the most recent data is processed.
• 
• 
• 

5. useTransition for UI Responsiveness
5.1. Technical Deconstruction
React  18  introduces  concurrency,  allowing  React  to  work  on  multiple  state
updates simultaneously. The  useTransition hook is a key tool for leveraging
this. It allows us to mark specific state updates as "non-urgent." React can then
interrupt the rendering of these non-urgent updates to handle more critical,
"urgent" updates, such as user input.
In a trading terminal, an "Emergency Stop" button click is an urgent update that
must be instantaneous. In contrast, updating a large, complex news feed is a
non-urgent update that can be deferred or interrupted if the user performs a
critical action.
5.2. Implementation Strategy
In  this  example,  a  TradingDashboard component  receives  news  updates.  We
wrap the state update for the news feed in  startTransition. This tells React
that rendering the new news feed can be de-prioritized. The onClick handler for
the "Emergency Stop" button updates state directly, making it an urgent update
that will interrupt the news feed render if necessary.
//src/widgets/trading-dashboard/ui/TradingDashboard.tsx
importReact,{useState,useTransition,useEffect}from'react';
import{NewsFeed}from'../../news-feed';
import{EmergencyStopButton}from'../../../features/emergency-stop';
//MockAPItosimulateincomingnewsdata
constmockNewsApi={
subscribe:(callback:(data:any[])=>void)=>{
setInterval(()=>callback(generateHeavyNewsData()),2000);
}
};
functionTradingDashboard(){
const[newsItems,setNewsItems]=useState([]);

const[isPending,startTransition]=useTransition();
useEffect(()=>{
//Subscribetonewsupdates
mockNewsApi.subscribe(newNewsData=>{
//Thisisanon-urgentupdate.Itcanbeinterrupted.
startTransition(()=>{
setNewsItems(newNewsData);
});
});
},[]);
consthandleEmergencyStop=()=>{
//ThisisanURGENTupdate.Itwillinterruptthenewsfeedrender.
console.log('EMERGENCY STOP INITIATED - IMMEDIATE ACTION');
//...logictodispatchstopaction
};
return(
<div>
<h1>TradingDashboard</h1>
<EmergencyStopButtononClick={handleEmergencyStop}/>
<hr/>
<h2>LiveNewsFeed</h2>
{isPending&&<divclassName="spinner">Updatingnews...</div>}
<NewsFeeditems={newsItems}/>
</div>
);
}
5.3. Critical Analysis
Failure Mode (Incorrect Usage): If startTransition is used to wrap an
urgent update (like a controlled input's onChange), it will introduce
noticeable input lag, degrading the user experience. useTransition must
be applied selectively only to state updates that can tolerate a delay.
• 

Edge Case (Stale Data Perception): During a transition, the UI can be in
a state where some parts have updated (urgent changes) while others have
not (the pending transition). The isPending state is crucial for providing
user feedback (e.g., a loading spinner or dimmed view) to clearly indicate
that a background update is in progress, preventing user confusion.
Optimization (useDeferredValue): For cases where you don't control the
state update logic (e.g., a value comes from a parent component's props), 
useDeferredValue provides a similar de-prioritization mechanism. It can be
used to defer rendering a computationally expensive component based on a
prop value, preventing it from blocking more critical UI elements.
• 
• 

