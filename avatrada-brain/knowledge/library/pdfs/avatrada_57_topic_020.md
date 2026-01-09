# SOURCE PDF: avatrada_57_topic_020.pdf

Deep Research: Avatrada 57 Topic 020
Engineering Report: Transaction Cost
Analysis (TCA) Module
Authored By: Autonomous Technical Researcher  Date: October 26, 2023  RE:
Deep-Dive on TCA Module for Execution Performance Monitoring
1. Executive Summary
This report provides a detailed engineering analysis and design specification for
a Transaction Cost Analysis (TCA) module. The system's primary function is to
monitor and evaluate the quality of trade execution in real-time by comparing
realized trading costs against pre-trade modeled costs.
The core metric for this analysis is Implementation Shortfall, which measures
the slippage between the market price at the moment a trading decision is made
(the "Arrival Price") and the final execution price (the "Fill Price"). The module
will maintain a rolling average of this shortfall. If this average exceeds 1.5 times
the  modeled  spread  cost  for  a  given  instrument,  an
EXECUTION_PERFORMANCE_WARNING will  be  triggered,  alerting  operations  and
strategy teams to potential degradation in execution quality, adverse market
conditions, or flawed routing logic.
The accuracy of this entire system hinges on the precise and correct capture of
timestamps, particularly the moment the trading signal is generated. This report
will  deconstruct  the  required  metrics,  propose  a  robust  implementation
architecture, and analyze critical failure modes and potential optimizations.

2. Technical Deconstruction
The  TCA  module  is  fundamentally  a  measurement  and  alerting  system.  Its
components and logic are broken down below.
2.1. Core Metrics and Formulas
a. Arrival Price (Arrival_Price)
This is the theoretical "ideal" price for a transaction. It is defined as the  mid-
point of the National Best Bid and Offer (NBBO) at the exact moment the
trading algorithm generates the signal to trade. It represents the state of
the market before our order could have any potential market impact.
Arrival_Price = (Best_Bid_at_Signal_Time + Best_Ask_at_Signal_Time) / 2
b. Fill Price (Fill_Price)
This is the actual price at which a trade (or a portion of a trade) was executed.
For orders filled in multiple parts (child orders), the Fill_Price for the parent
order is the Volume-Weighted Average Price (VWAP) of all its fills.
VWAP_Fill_Price = Σ(Fill_Price_i * Fill_Quantity_i) / Σ(Fill_Quantity_i)
c. Implementation Shortfall
This  is  the  primary  measure  of  execution  cost,  representing  the  difference
between the actual fill price and the arrival price. It is typically expressed in
basis points (bps) for standardized comparison across different assets and price
levels.
The  formula  varies  slightly  for  buy  vs.  sell  orders  to  ensure  that  a  positive
shortfall always indicates an adverse cost (i.e., paying more on a buy, receiving
less on a sell).
For a BUY order:

Shortfall = (Fill_Price - Arrival_Price)
Shortfall_bps = (Shortfall / Arrival_Price) * 10,000
For a SELL order:
Shortfall = (Arrival_Price - Fill_Price)
Shortfall_bps = (Shortfall / Arrival_Price) * 10,000
d. Modeled Spread Cost (Modeled_Spread_Cost)
This is a pre-trade estimate of the expected transaction cost, primarily driven by
the  bid-ask  spread.  This  model  should  be  dynamic,  potentially  considering
factors like the asset's historical volatility, time of day, and recent liquidity. A
simple model could be the trailing average spread for that instrument over the
last N minutes.
2.2. Alerting Mechanism
The system does not alert on a single bad trade, which could be an outlier.
Instead, it uses a rolling average to detect persistent performance degradation.
Logic: For each asset or strategy, maintain a rolling window (e.g., last 50
fills) of the calculated Implementation_Shortfall_bps.
Condition: After each new fill is processed, update the rolling average.
Trigger: If Rolling_Avg_Shortfall > 1.5 * Modeled_Spread_Cost, generate
an EXECUTION_PERFORMANCE_WARNING.
2.3. Critical Timestamps for Arrival Price Capture
The  accuracy  of  Arrival_Price is  paramount.  An  incorrect  Arrival_Price
renders  the  entire  TCA  calculation  meaningless.  The  critical  moment  is  the
instant the trading strategy's logic finalizes its decision to execute a
trade.
• 
• 
• 

Let's trace the lifecycle of an order to identify the correct timestamp:
T_signal (Signal Generation Time): The strategy's internal logic (e.g., 
if condition_A and condition_B: generate_buy_signal()) evaluates to
true. This is the most critical timestamp. The market data snapshot for
the Arrival_Price must be captured at this exact moment, with
microsecond or even nanosecond precision if possible.
T_order_created (Order Object Instantiation): The system creates an
order object in memory. This occurs afterT_signal and is subject to
application-level latency.
T_order_sent (Gateway Egress Time): The order leaves the firm's
network gateway en route to the exchange. This is too late; the market may
have already moved.
T_exchange_ack (Exchange Acknowledgement): The exchange confirms
receipt of the order. This is far too late.
T_fill (Fill Time): The trade is executed. This timestamp is used for the 
Fill_Price.
Conclusion: The  Arrival_Price must be based on the market data that was
true at T_signal. Any delay between T_signal and the market data lookup will
introduce  "latency  slippage,"  incorrectly  attributing  market  movement  to
execution quality. Therefore, the system must be designed to capture the system
clock time at T_signal and associate it with the corresponding market data tick
received at or just before that time.
3. Implementation Strategy
3.1. System Architecture & Data Flow
A robust implementation requires tight integration between the Strategy Engine,
the Order Management System (OMS), and a dedicated TCA database/service.
graphTD
A[MarketDataFeed]-->B{StrategyEngine};
B--1.T_signal,Symbol,Side,Qty-->C[OrderManagementSystem(OMS)];
1. 
2. 
3. 
4. 
5. 

subgraph"TCA Capture"
B--2.Log(T_signal,Arrival_Price)-->D[TCADatabase];
end
C--3.RouteOrder-->E[ExecutionVenue/Exchange];
E--4.FillConfirmation(Fill_Price,Fill_Qty,T_fill)-->C;
C--5.ProcessFill-->F[TCAProcessingService];
D<--6.StoreFillData---F;
F--7.CalculateShortfall&UpdateRollingAvg-->D;
F--8.CheckAlertCondition-->G{AlertingSystem};
G--9.EXECUTION_PERFORMANCE_WARNING-->H[MonitoringDashboard/Ops
Team];
Flow Description: 1. The Strategy Engine makes a decision at T_signal. 2.
Crucially, it immediately logs  T_signal and the corresponding  Arrival_Price
(mid-price from the market data it just processed) to the TCA Database, keyed
by a unique signal or order ID. 3. Simultaneously, it sends the order to the OMS.
4. The OMS routes the order, and eventually receives fill confirmations from the
Exchange.  5.  The  OMS  forwards  these  fill  details  to  the  TCA  Processing
Service.  6.  The  service  retrieves  the  original  Arrival_Price from  the  TCA
Database  using  the  order  ID.  7.  It  calculates  the  Implementation_Shortfall,
stores it, and updates the rolling average for the relevant instrument/strategy. 8.
It checks the 1.5x threshold and triggers an alert if necessary.
3.2. Data Model (PostgreSQL/TimescaleDB)
A time-series database is ideal for this purpose.
trades table:
CREATETABLEtrades(
trade_idBIGSERIALPRIMARYKEY,
parent_order_idVARCHAR(255)NOTNULL,
strategy_idVARCHAR(100)NOTNULL,
symbolVARCHAR(50)NOTNULL,
sideVARCHAR(4)NOTNULL,-- 'BUY' or 'SELL'
-- Signal & Arrival Data
signal_timestampTIMESTAMPTZ(6)NOTNULL,-- Microsecond precision

arrival_priceNUMERIC(18,8)NOTNULL,
modeled_spread_cost_bpsNUMERIC(10,4),
-- Fill Data
fill_timestampTIMESTAMPTZ(6)NOTNULL,
fill_priceNUMERIC(18,8)NOTNULL,
fill_quantityBIGINTNOTNULL,
-- Calculated TCA Metrics
shortfall_bpsNUMERIC(10,4)
);
-- Create a hypertable for TimescaleDB and index for efficient queries
SELECTcreate_hypertable('trades','signal_timestamp');
CREATEINDEXONtrades(strategy_id,symbol,signal_timestampDESC);
3.3. Core Logic (Python Pseudocode)
importpandasaspd
# Assume 'db_connection' is an active database connection
# Assume 'trade_fills_df' is a pandas DataFrame storing historical fills
defprocess_new_fill(fill_event:dict):
"""
    Processes a new fill, calculates shortfall, and checks for alerts.
    """
# 1. Fetch arrival data logged at signal time
arrival_data=
db_connection.fetch_arrival_data(fill_event['parent_order_id'])
arrival_price=arrival_data['arrival_price']
modeled_cost=arrival_data['modeled_spread_cost_bps']
# 2. Calculate Implementation Shortfall
fill_price=fill_event['fill_price']
iffill_event['side']=='BUY':
shortfall_bps=((fill_price-arrival_price)/arrival_price)*10000
else:# SELL

shortfall_bps=((arrival_price-fill_price)/arrival_price)*10000
# 3. Store the calculated data
db_connection.store_trade_record({**fill_event,'shortfall_bps':
shortfall_bps})
# 4. Update and check rolling average
# Fetch the last N trades for this strategy/symbol
recent_trades=db_connection.fetch_recent_trades(
strategy=fill_event['strategy_id'],
symbol=fill_event['symbol'],
limit=50# Rolling window size
)
rolling_avg_shortfall=pd.Series(recent_trades['shortfall_bps']).mean()
# 5. Trigger alert if condition is met
ifrolling_avg_shortfall>1.5*modeled_cost:
trigger_alert(
'EXECUTION_PERFORMANCE_WARNING',
f"Strategy {fill_event['strategy_id']} on {fill_event['symbol']} "
f"breached TCA threshold. "
f"Avg Shortfall: {rolling_avg_shortfall:.2f} bps, "
f"Modeled Cost: {modeled_cost:.2f} bps"
)
4. Critical Analysis & Optimization
4.1. Potential Failure Modes & Edge Cases
Clock Synchronization Drift: If the clock on the Strategy Engine machine
is not perfectly synchronized with the market data feed's timestamping
source (via NTP/PTP), the Arrival_Price will be incorrect. This is the most
significant risk.
Network Latency: High latency between the market data source and the
Strategy Engine can mean the price used for the Arrival_Price is stale,
• 
• 

even if timestamps are synchronized. The TCA calculation would be
measuring this latency, not execution quality.
Partial Fills: The logic must correctly aggregate multiple child fills into a
single parent order performance metric. The Fill_Price should be the
VWAP of all fills, and the shortfall_bps should be calculated only once the
parent order is fully filled or terminated.
Illiquid Markets: In markets with wide, volatile spreads, the "mid-price"
can be a poor benchmark. A single large trade can move the mid-price
significantly, making the Arrival_Price unstable. The 
Modeled_Spread_Cost must be aggressive for such instruments.
"Stale" Quotes: If the market data feed provides a quote that is not
updated for a period, using it as the Arrival_Price can be misleading. The
system should be aware of the "freshness" of the quote used.
4.2. Proposed Optimizations
Hardware Timestamping: For HFT systems, use network interface cards
(NICs) capable of hardware timestamping (e.g., Solarflare). This provides
nanosecond-level precision on packet arrival, bypassing kernel and
application-level jitter, leading to a much more accurate Arrival_Price.
Co-location: Co-locating the Strategy Engine with the exchange's
matching engine minimizes network latency, making the captured 
Arrival_Price a more faithful representation of the market at the decision
time.
Dynamic Modeling: Enhance the Modeled_Spread_Cost. Instead of a
simple historical average, use a model that incorporates real-time volatility,
order book depth, and time-of-day effects. This makes the 1.5x threshold
more meaningful.
Benchmark Refinement: For longer-running orders (e.g., TWAP , VWAP
algorithms), comparing against the single Arrival_Price is insufficient. A
more advanced TCA would compare the execution against a benchmark like
the interval VWAP from T_signal to the final T_fill.
Cost Attribution: Decompose the shortfall into its constituent parts:
Latency Slippage: Cost from the delay between T_signal and 
T_order_sent.
• 
• 
• 
• 
• 
• 
• 
• 
◦ 

Market Impact: Cost from the price moving adversely after our
order reaches the market. This provides more granular feedback to
the strategy and execution teams.
◦ 

