# SOURCE PDF: avatrada_ui_9_topic_004.pdf

Deep Research: Avatrada Ui 9 Topic 004
Engineering Report: High-Performance
Financial Visualization
To:  Lead  Architect  From:  Autonomous  Technical  Researcher  (Graphics  &
Performance)  Date:  October  26,  2023  Subject:  Deep-Dive  on  Real-Time  L2
Heatmaps and High-Frequency Grid Rendering
This report provides a detailed technical analysis of the systems required to
build  a  high-performance  financial  trading  interface,  as  specified  in  Master
Research Prompt 4. The focus is on optimizing AG Grid for high-frequency data,
rendering  a  real-time  Level  2  order  book  heatmap  using  HTML5  Canvas,
managing  coordinate  systems,  and  integrating  a  custom  datafeed  for  the
TradingView charting library.
1. AG Grid Optimization for 100+ Updates/Second
To handle high-frequency data streams (e.g., market data ticks, order status
changes) in a data grid, the primary objective is to minimize DOM manipulation
and  avoid  blocking  the  main  UI  thread.  AG  Grid  Enterprise  provides
asynchronous transactions specifically for this purpose.
Technical Deconstruction
The  core  mechanism  is  the  Client-Side  Row  Model combined  with  Row
Transactions. Instead of replacing the entire dataset with  setRowData, which
forces  the  grid  to  destroy  and  recreate  all  row  and  cell  DOM  elements,  a
transaction applies deltas (additions, updates, removals) to the existing data.
applyTransaction(transaction): The synchronous API. It applies the
changes immediately. If the transaction is large or updates are frequent,
• 

this can cause stuttering and block user interaction as the grid processes
the changes on the main thread.
applyTransactionAsync(transaction, callback): The asynchronous API.
This is the preferred method for high-frequency updates. It pushes the
transaction to a queue and processes it on a subsequent turn of the
JavaScript event loop. This prevents the UI from freezing, allowing
scrolling, clicking, and other interactions to remain responsive even while
data is streaming in. The grid can also intelligently batch multiple async
transactions that arrive in quick succession.
For delta updates to work, the grid must be able to uniquely identify each row.
This is achieved by implementing the getRowId grid option.
Implementation Strategy
1. Configure the Grid with a Stable Row ID: Provide a  getRowId callback
that  returns  a  unique  and  immutable  identifier  for  each  row  object.  This  is
critical; without it, the grid cannot perform targeted updates and will fall back to
less efficient methods.
// React Component for the Grid
import{AgGridReact}from'ag-grid-react';
import'ag-grid-enterprise';// Enable Enterprise features
constHighFrequencyGrid=({columnDefs,initialRowData})=>{
constgridApiRef=useRef(null);
// Memoize the getRowId callback for stability
constgetRowId=useMemo(()=>{
return(params)=>params.data.orderId;// 'orderId' must be a unique 
key
},[]);
constonGridReady=(params)=>{
gridApiRef.current=params.api;
};
// Example: Hook to listen to a WebSocket stream and apply updates
• 

useEffect(()=>{
constwebSocket=newWebSocket('wss://api.exchange.com/market-data');
webSocket.onmessage=(event)=>{
constupdates=JSON.parse(event.data);// Assume updates is an 
array of objects
// Prepare the transaction object
consttransaction={
update:updates,// Array of row data objects to update
// add: [],      // Array of new rows
// remove: [],   // Array of rows to remove
};
// Apply the transaction asynchronously
if(gridApiRef.current){
gridApiRef.current.applyTransactionAsync(transaction);
}
};
return()=>webSocket.close();
},[]);
return(
<divclassName="ag-theme-alpine-dark"style={{height:800,width:
'100%'}}>
<AgGridReact
rowData={initialRowData}
columnDefs={columnDefs}
getRowId={getRowId}
onGridReady={onGridReady}
// Performance-critical flags
suppressCellFocus={true}
suppressRowClickSelection={true}
/>
</div>
);
};

2. Batching Updates: While  applyTransactionAsync is non-blocking, applying
thousands of individual transactions per second still has overhead. It's more
efficient to batch incoming updates.
// Inside the useEffect hook from the previous example
letupdateBatch=[];
letbatchTimeout=null;
webSocket.onmessage=(event)=>{
constnewData=JSON.parse(event.data);
updateBatch.push(newData);
// Coalesce updates using a timeout or requestAnimationFrame
if(!batchTimeout){
batchTimeout=setTimeout(()=>{
if(gridApiRef.current){
gridApiRef.current.applyTransactionAsync({update:
updateBatch});
}
updateBatch=[];// Clear the batch
batchTimeout=null;
},16);// Batch updates roughly every frame (16ms ~ 60fps)
}
};
Critical Analysis
Failure Mode (Unstable getRowId): If the ID returned by getRowId
changes for the same logical row, AG Grid will treat it as a remove and an 
add, which is significantly less performant than an update. The ID must
be immutable.
Bottleneck (Cell Renderers): applyTransactionAsync solves the data
processing bottleneck, but the rendering itself can become the new
bottleneck. If you use complex React components as cell renderers, every
data update can trigger a reconciliation cascade. For high-frequency fields
(e.g., price, size), use simple, lightweight renderers or AG Grid's built-in
• 
• 

renderers. Avoid state management within cell renderers that are updated
frequently.
Edge Case (Large Initial Load): applyTransactionAsync is for updates,
not the initial data load. Load the first batch of data via the rowData prop.
Optimization (Tuning Batching): The asyncTransactionWaitMillis grid
property can be used to configure how long the grid waits to batch
transactions together. Setting this to 50 would mean the grid waits 50ms
after receiving a transaction to see if more arrive, then processes them all
at once. This is a powerful way to reduce processing overhead for very
high-frequency streams.
2. Canvas "Liquidity Heatmap" Overlay at 60fps
A liquidity heatmap visualizes the density of limit orders in an order book. This
can be rendered efficiently on an HTML5 Canvas by drawing thousands of semi-
transparent rectangles, where opacity is proportional to order size.
Technical Deconstruction
The  concept  relies  on  additive  blending.  Each  limit  order  is  a  rectangle
positioned at its price level (Y-axis). The rectangle's color intensity or opacity
represents its size. When multiple orders exist at or near the same price level,
their  corresponding  rectangles  overlap.  The  colors  blend,  creating  brighter
"hotspots"  where  liquidity  is  concentrated.  To  achieve  60fps,  the  rendering
process must be highly optimized to complete within a 16.67ms frame budget.
Implementation Strategy
This  proof-of-concept  uses  the  standard  2D  Canvas  API  and
requestAnimationFrame for a smooth rendering loop.
<canvasid="heatmapCanvas"width="800"height="600"></canvas>
• 
• 

// Proof-of-Concept for Canvas Heatmap
constcanvas=document.getElementById('heatmapCanvas');
constctx=canvas.getContext('2d');
const{width,height}=canvas;
// --- 1. Mock Data and View State ---
// In a real app, this comes from a WebSocket and chart state
constmockOrderBook=[];
for(leti=0;i<5000;i++){
mockOrderBook.push({
price:40000+(Math.random()-0.5)*500,// Price around 40k
size:Math.random()*10,// Order size
});
}
constviewState={
minPrice:39750,
maxPrice:40250,
chartHeight:height,
maxSizeForOpacity:10,// The order size that corresponds to max opacity
};
// --- 2. Coordinate Mapping (See Section 3 for details) ---
functionpriceToY(price,state){
constpriceRange=state.maxPrice-state.minPrice;
if(priceRange<=0)returnstate.chartHeight/2;
constpriceRatio=(price-state.minPrice)/priceRange;
returnstate.chartHeight*(1-priceRatio);// Invert Y-axis
}
// --- 3. Rendering Logic ---
functionrenderHeatmap(){
// Clear the canvas for the new frame
ctx.clearRect(0,0,width,height);
// Iterate through visible orders and draw them
for(constorderofmockOrderBook){
// Cull orders outside the visible price range
if(order.price<viewState.minPrice||order.price>
viewState.maxPrice){

continue;
}
consty=priceToY(order.price,viewState);
// Opacity is proportional to order size
constopacity=Math.min(1,order.size/viewState.maxSizeForOpacity)*
0.5;
// Using a single color (e.g., yellow for bids) with varying alpha
ctx.fillStyle=`rgba(255, 255, 0, ${opacity})`;
// Draw a rectangle across the full width of the canvas
// The height of 1px is efficient; overlapping creates the heatmap 
effect
ctx.fillRect(0,y,width,1);
}
}
// --- 4. Animation Loop ---
functionanimate(){
// In a real app, you'd update viewState on pan/zoom
// and mockOrderBook on new data.
renderHeatmap();
requestAnimationFrame(animate);
}
animate();
Critical Analysis
Performance Bottleneck (Draw Calls): The primary bottleneck is the
number of fillRect calls. Drawing 5,000 individual rectangles per frame
is feasible on modern hardware, but 50,000+ will cause frame drops.
Optimization 1 (Data Aggregation): Before rendering, aggregate the
orders by pixel. Instead of drawing ten 1-pixel-high rectangles at the same
Y-coordinate, calculate the total size for that pixel row and draw a single
rectangle with a combined opacity. This dramatically reduces draw calls.
• 
• 

javascript  //  Aggregation  Strategy  const  pixelAggregator  =  new
Map();  //  Map<y_coordinate,  total_size>  for  (const  order  of
visibleOrders)  {  const  y  =  Math.round(priceToY(order.price,
viewState)); pixelAggregator.set(y, (pixelAggregator.get(y) || 0) +
order.size); } // Now, iterate the map and draw one rectangle per map
entry.
Optimization 2 (Off-Screen Canvas): As noted in the source context, this
is a powerful technique. If the order book data does not change every
single  frame,  you  can  render  the  full  heatmap  to  a  hidden,  off-screen
canvas. Then, in your main  requestAnimationFrame loop, you perform a
single, highly optimized  drawImage call to render the off-screen canvas
onto your visible one. You only re-render the off-screen canvas when the
order book data actually changes. This decouples the heatmap rendering
from the main chart's 60fps rendering loop.
Edge Case (High-Density Areas): In areas of extreme liquidity, the
additive blending can result in a fully opaque, washed-out color. To handle
this, you can use a non-linear mapping from order size to opacity (e.g.,
logarithmic) or cap the maximum alpha value to preserve detail.
3. Mathematics of Price-to-Coordinate Mapping
Efficiently  and  accurately  mapping  data  coordinates  (price,  time)  to  screen
coordinates  (pixels)  is  fundamental  to  any  charting  application.  This
transformation depends on the current viewport (pan and zoom level).
Technical Deconstruction
The mapping is a form of  linear interpolation. We are transforming a value
from a source range (e.g., [minVisiblePrice, maxVisiblePrice]) to a destination
range (e.g., [chartHeight, 0]). The Y-axis for pixels typically starts at 0 at the
top and increases downwards, while price charts show higher values at the top.
Therefore, the price range must be inverted during the mapping.
• 
• 

Key Variables: -  P_data:  The  price  of  a  data  point.  -  P_min,  P_max:  The
minimum and maximum prices currently visible in the viewport. -  H_px: The
height of the canvas in pixels. - Y_px: The target Y-coordinate on the canvas.
Implementation Strategy
Formula: Price to Y-Coordinate This function calculates the pixel  y for a
given price.
/**
 * Maps a price value to a Y-coordinate on the canvas.
 * @param {number} price The price to map.
 * @param {number} minVisiblePrice The minimum price in the current viewport.
 * @param {number} maxVisiblePrice The maximum price in the current viewport.
 * @param {number} chartHeight The height of the canvas in pixels.
 * @returns {number} The Y-coordinate in pixels.
 */
functionpriceToY(price,minVisiblePrice,maxVisiblePrice,chartHeight){
constpriceRange=maxVisiblePrice-minVisiblePrice;
// Avoid division by zero if zoomed in infinitely
if(priceRange<=0){
returnchartHeight/2;
}
// 1. Normalize the price to a [0, 1] ratio within the visible range
constnormalizedPrice=(price-minVisiblePrice)/priceRange;
// 2. Invert the ratio (so high price -> low Y) and scale to chart height
consty=(1-normalizedPrice)*chartHeight;
returny;
}
Formula: Y-Coordinate to Price This  is  the  inverse  function,  essential  for
handling mouse events (e.g., "what price is the cursor at?").

/**
 * Maps a Y-coordinate on the canvas back to a price value.
 * @param {number} y The Y-coordinate in pixels.
 * @param {number} minVisiblePrice The minimum price in the current viewport.
 * @param {number} maxVisiblePrice The maximum price in the current viewport.
 * @param {number} chartHeight The height of the canvas in pixels.
 * @returns {number} The corresponding price value.
 */
functionyToPrice(y,minVisiblePrice,maxVisiblePrice,chartHeight){
constpriceRange=maxVisiblePrice-minVisiblePrice;
// 1. Normalize the Y-coordinate to a [0, 1] ratio
constnormalizedY=y/chartHeight;
// 2. Invert the ratio and scale it by the price range, then add the min 
price
constprice=(1-normalizedY)*priceRange+minVisiblePrice;
returnprice;
}
Critical Analysis
Edge Case (Logarithmic Scale): The linear formulas above are not
suitable for logarithmic price scales. For a log scale, you must first take the
logarithm of the prices before normalizing.
Price to Y (Log): logRange = log(max) - log(min). normalized =
(log(price) - log(min)) / logRange. y = (1 - normalized) *
height.
Y to Price (Log): price = exp(log(min) + (1 - y / height) *
logRange).
Interaction Logic (Zooming): Zooming changes the minVisiblePrice
and maxVisiblePrice. A common implementation is to zoom "into" the
cursor's position. This requires:
Get the cursor's y position.
Use yToPrice to find the price under the cursor (priceAtCursor).
• 
◦ 
◦ 
• 
1. 
2. 

Apply the zoom factor to the current priceRange.
Calculate the new minVisiblePrice and maxVisiblePrice such that 
priceAtCursor remains at the same y position.
Optimization: Inside a tight rendering loop, pre-calculate priceRange and
pixelsPerPrice = chartHeight / priceRange once per frame, before
iterating over data points. The inner-loop calculation then becomes a faster 
y = (maxVisiblePrice - price) * pixelsPerPrice.
4. TradingView Custom Datafeed Adapter for
Redux
The  TradingView  Charting  Library  can  be  disconnected  from  its  own  data
backend by implementing a "Datafeed Adapter". This is a JavaScript object that
conforms to a specific interface, acting as a bridge between the chart and your
local data source, such as a Redux store.
Technical Deconstruction
The  chart  interacts  with  the  adapter  by  calling  its  methods.  The  two  most
important  are:  1.  getBars(symbolInfo,  resolution,  periodParams,
onHistoryCallback,  onErrorCallback):  Called  by  the  chart  when  it  needs
historical  data.  Your  implementation  must  fetch  this  data  (from  your  Redux
store)  and  pass  it  to  onHistoryCallback.  2.  subscribeBars(symbolInfo,
resolution, onRealtimeCallback, subscriberUID, onResetCacheNeededCallback):
Called  when  the  chart  is  ready  for  real-time  updates.  You  must  store  the
onRealtimeCallback and  call  it  whenever  a  new  bar/tick  arrives  for  the
subscribed symbol.
Implementation Strategy
This example outlines an adapter that connects to a Redux store. It assumes the
Redux store is populated by a WebSocket middleware.
// reduxDatafeedAdapter.js
3. 
4. 
• 

import{store}from'./your/redux/store';
import{selectBarsForSymbol}from'./your/redux/selectors';
import{fetchHistoricalData}sfrom'./your/redux/actions';
// Store real-time callbacks provided by the chart
constrealtimeSubscribers=newMap();
// Listen to Redux store changes to push real-time data
store.subscribe(()=>{
conststate=store.getState();
// In a real app, use a memoized selector to check if the LATEST bar has 
changed
constlatestBar=state.marketData.latestBar;
if(latestBar&&realtimeSubscribers.has(latestBar.symbol)){
constcallback=realtimeSubscribers.get(latestBar.symbol).callback;
// Format the bar from Redux state into TradingView's expected format
consttvBar={
time:latestBar.timestamp,// ms
open:latestBar.open,
high:latestBar.high,
low:latestBar.low,
close:latestBar.close,
volume:latestBar.volume,
};
callback(tvBar);
}
});
exportconstreduxDatafeedAdapter={
onReady:(callback)=>{
// Provide chart configuration
setTimeout(()=>callback({supported_resolutions:['1','5','15',
'60','D']}),0);
},
resolveSymbol:(symbolName,onSymbolResolvedCallback,
onResolveErrorCallback)=>{
// Provide metadata for a symbol
setTimeout(()=>onSymbolResolvedCallback({

name:symbolName,
ticker:symbolName,
has_intraday:true,
// ... other metadata
}),0);
},
getBars:(symbolInfo,resolution,periodParams,onHistoryCallback,
onErrorCallback)=>{
const{from,to,countBack}=periodParams;
conststate=store.getState();
// Use a selector to get currently available data from the store
constavailableBars=selectBarsForSymbol(state,symbolInfo.name,from,
to);
if(availableBars.length>0){
// If data is already in Redux, return it immediately
onHistoryCallback(availableBars,{noData:false});
}else{
// If data is missing, dispatch an action to fetch it
store.dispatch(fetchHistoricalData(symbolInfo.name,from,to))
.then(fetchedBars=>{
onHistoryCallback(fetchedBars,{noData:fetchedBars.length
===0});
})
.catch(err=>{
onErrorCallback(err);
});
}
},
subscribeBars:(symbolInfo,resolution,onRealtimeCallback,subscriberUID)
=>{
console.log(`Subscribing to ${symbolInfo.name} with UID ${subscriberUID}
`);
realtimeSubscribers.set(symbolInfo.name,{
uid:subscriberUID,
callback:onRealtimeCallback,
});

},
unsubscribeBars:(subscriberUID)=>{
// Find and remove the subscriber by UID
for(const[key,sub]ofrealtimeSubscribers.entries()){
if(sub.uid===subscriberUID){
realtimeSubscribers.delete(key);
console.log(`Unsubscribed ${key}`);
break;
}
}
},
};
// In your chart component:
// new TradingView.widget({
//     ...
//     datafeed: reduxDatafeedAdapter,
// });
Critical Analysis
Critical Challenge (Asynchronicity in getBars): The most complex part
is handling a getBars request when the data is not yet in the Redux store.
The implementation shown dispatches a thunk (fetchHistoricalData) and
uses the promise's resolution to call onHistoryCallback. This is a robust
pattern for bridging the synchronous-like API of the datafeed with the
asynchronous nature of data fetching.
Failure Mode (Race Conditions): A race condition can occur between the
historical data from getBars and the first real-time update from 
subscribeBars. The system must ensure there is no gap and no overlap. A
common strategy is to use timestamps or sequence numbers to de-
duplicate bars received from both channels.
Performance (Store Subscription): The store.subscribe call will fire on
every single state change. This is inefficient. This should be replaced with a
more targeted subscription mechanism, or the logic inside the subscription
should use a memoized selector (e.g., from reselect) to ensure the 
• 
• 
• 

onRealtimeCallback is only invoked when the specific data the chart cares
about has actually changed.
Data Integrity: The adapter is responsible for formatting the data from
your Redux store into the exact format TradingView expects (e.g.,
timestamps in milliseconds, specific object keys). Any mismatch will cause
the chart to fail silently or render incorrectly. Rigorous validation and
typing (e.g., with TypeScript) are highly recommended.
• 

