# SOURCE PDF: avatrada_57_topic_017.pdf

Deep Research: Avatrada 57 Topic 017
Engineering Report: Slippage Capping
Logic and Guardrail Implementation
Authored By: Autonomous Technical Researcher  Date: October 26, 2023  RE:
Deep-Dive Analysis of Pre-Trade Slippage Capping Mechanism
Executive Summary
This report provides a detailed engineering analysis of the "Slippage Capping
Logic" specified in the source document. The core function of this system is to
act as a pre-trade risk control, preventing market and aggressive limit orders
from executing at prices significantly worse than a stable reference price. This is
achieved by calculating the theoretical slippage before an order is sent to an
exchange and rejecting it locally if it exceeds a pre-defined threshold (5% for
liquid assets, 10% for illiquid).
The  analysis  deconstructs  the  required  calculations,  proposes  a  robust
implementation strategy centered on the reliable calculation of a reference price
(Ref_Price), and performs a critical analysis of potential failure modes, edge
cases, and optimizations. The primary recommendation is to use the  NBBO
Mid-Point as  the  default  Ref_Price for  its  stability  and  representation  of
market consensus, while acknowledging specific scenarios where the contra-side
NBBO (Best Bid/Ask) may be more appropriate.
1. Technical Deconstruction
The "Slippage Guardrail" is a pre-trade check module within an order execution
engine.  Its  purpose  is  to  protect  against  unfavorable  executions  due  to  low

liquidity  or  high  volatility.  We  can  deconstruct  the  system  into  four  key
components:
1.1. Core Slippage Formula
The fundamental calculation is a percentage deviation check:
Slippage_Percent = (Theoretical_Execution_Price - Ref_Price) / Ref_Price
For a  BUY order, the check is:  Slippage_Percent > Slippage_Cap For a  SELL
order, the check is: (Ref_Price - Theoretical_Execution_Price) / Ref_Price >
Slippage_Cap
Theoretical_Execution_Price: This is not a single price point but the 
anticipated average execution price for the entire order volume. It is
calculated by simulating the order's consumption of liquidity from the Level
2 order book.
Ref_Price: A benchmark price representing the "fair" or current market
value at the moment of the check. The reliability of the entire system
hinges on the quality of this input.
Slippage_Cap: A configurable threshold, specified as 5% (0.05) for liquid
assets and 10% (0.10) for illiquid assets.
1.2. Asset Liquidity Classification
The system must differentiate between "liquid" and "illiquid" assets to apply the
correct cap. This is not a real-time calculation performed on the order path.
Instead, it is a property of the instrument, determined periodically by a separate
process.
Common metrics for this classification include: * Average Daily Volume (ADV):
The mean trading volume over the last 30-90 days. High ADV suggests liquidity. *
Bid-Ask  Spread:  A  consistently  narrow  percentage  spread  indicates  high
liquidity. * Market Depth: The volume available at the first few price levels of
the order book.
• 
• 
• 

This classification should be stored in an instrument master database and cached
by the execution engine for low-latency access.
1.3. Applicable Order Types
The logic correctly targets  Market Orders and  Aggressive Limit Orders. *
Market Orders: These orders have the highest potential for slippage as they
consume liquidity at any available price until filled. * Aggressive Limit Orders:
A limit order is "aggressive" if its price crosses the spread (e.g., a buy limit order
with a price above the current best ask). These orders behave like market orders
up to their limit price and are thus susceptible to slippage. Passive limit orders
(which rest on the book) do not incur slippage upon placement.
1.4. Rejection and Override Workflow
The  system  operates  on  a  "reject  locally"  principle.  This  is  critical  for
performance and risk management, as it prevents a potentially dangerous order
from ever reaching the market.
The workflow is as follows: 1.  Order Interception: The Order Management
System (OMS) intercepts an outgoing order. 2. Guardrail Check: The order is
passed to the Slippage Guardrail module. 3. Calculation: The module calculates
theoretical slippage. 4.  Decision: * If  Slippage_Percent <= Slippage_Cap, the
order  is  approved  and  routed  to  the  exchange.  *  If  Slippage_Percent >
Slippage_Cap, the order is rejected with a specific error code (e.g., "Slippage
Cap Exceeded"). 5. Manual Override: The rejection triggers an alert. A human
trader can review the rejection, and if the execution is still desired, resubmit the
order  using  a  privileged  override  mechanism  (e.g.,  a  separate  order  flag
authenticated via 2FA).
2. Implementation Strategy
This section details the practical steps and choices for building the Slippage
Guardrail.

2.1. Calculating the Reference Price (Ref_Price)
This  is  the  most  critical  decision.  The  choice  involves  a  trade-off  between
stability, timeliness, and resistance to manipulation.
Reference
Price
Candidate
Pros Cons Recommendation
NBBO Mid-
Point
- Stable and less
volatile than
LTP or BBO. 
- Represents
market
consensus. 
- Difficult to
manipulate with
a single trade.
- Not a tradable
price. 
- Can be misleading
if the spread is very
wide. 
- Can be stale in
fast-moving or
illiquid markets.
Primary
Recommendation. The
most balanced and robust
choice for a general-
purpose guardrail.
Last Traded
Price (LTP)
- Simple to
acquire. 
- Reflects a real,
executed trade.
- Highly susceptible
to manipulation
(e.g., wash trades). 
- Can be extremely
stale for illiquid
assets. 
- A small trade can
set an
unrepresentative
LTP .
Not Recommended. Too
unreliable and prone to
manipulation for a critical
risk check.
Best Bid
(for Sells) /
Best Ask
(for Buys)
- Represents the
current, best
available price
(zero slippage
point). 
- Highly timely.
- Can be volatile. 
- Susceptible to
fleeting quotes and
spoofing. 
- For illiquid assets,
the spread itself is a
cost, which this
method ignores.
Secondary
Recommendation. A valid,
more aggressive choice.
Best used when the goal is
to measure slippage purely
from the point of crossing
the spread.

Reference
Price
Candidate
Pros Cons Recommendation
VWAP
(VWAP)
- Accounts for
volume. 
- More resistant
to manipulation
than LTP .
- A lagging
indicator, calculated
over a time window
(e.g., intraday). 
- Does not represent
the instantaneous,
actionable price.
Not Recommended for
Pre-Trade. Excellent for
post-trade analysis (TCA),
but not suitable for a real-
time guardrail.
Final Recommendation: Use the NBBO Mid-Point as the default Ref_Price.
# Logic for selecting Ref_Price
defget_reference_price(market_data):
"""
    Calculates the NBBO Mid-Point from market data.
    Includes validation for data availability and non-crossed book.
    """
best_bid=market_data.get('nbbo_bid')
best_ask=market_data.get('nbbo_ask')
ifbest_bidisNoneorbest_askisNoneorbest_bid<=0orbest_ask<=0:
raiseValueError("NBBO data is missing or invalid.")
ifbest_bid>best_ask:
raiseValueError("Market book is crossed.")
return(best_bid+best_ask)/2.0
2.2. Calculating the Theoretical_Execution_Price
This requires "walking the book" on the contra-side. The implementation needs
access to real-time Level 2 market data.
Algorithm for a BUY order of quantity_to_buy: 1. Fetch the current ask side
of the order book (a list of [price, volume] levels). 2. Initialize total_cost = 0

and quantity_filled = 0. 3. Iterate through the ask levels, from lowest price to
highest. 4. At each level  (p_i, v_i): *  volume_to_fill_at_level =  min(v_i,
quantity_to_buy - quantity_filled) * total_cost += volume_to_fill_at_level *
p_i *  quantity_filled += volume_to_fill_at_level *  If  quantity_filled >=
quantity_to_buy, break the loop. 5. If quantity_filled < quantity_to_buy, the
order exceeds available liquidity. This should be treated as infinite slippage and
rejected. 6. The Theoretical_Execution_Price is total_cost / quantity_filled.
# Pseudocode for walking the book
defcalculate_theoretical_exec_price(order_side,order_quantity,order_book):
levels=order_book['asks']iforder_side=='BUY'elseorder_book['bids']
# For SELL orders, levels should be sorted descending by price
total_cost=0.0
quantity_remaining=order_quantity
forlevelinlevels:
price,volume=level['price'],level['volume']
fill_volume=min(quantity_remaining,volume)
total_cost+=fill_volume*price
quantity_remaining-=fill_volume
ifquantity_remaining<=0:
break
ifquantity_remaining>0:
# Not enough liquidity on the book to fill the order
returnfloat('inf')# Or handle as a specific error
returntotal_cost/order_quantity
2.3. System Architecture and Logic
The guardrail should be a synchronous module within the order path.

# Main guardrail function
defslippage_guardrail_check(order,market_data,instrument_info):
# 1. Get appropriate slippage cap based on liquidity
liquidity_status=instrument_info.get('liquidity_tier')# 'LIQUID' or 
'ILLIQUID'
slippage_cap=0.05ifliquidity_status=='LIQUID'else0.10
try:
# 2. Calculate the reference price
ref_price=get_reference_price(market_data)
# 3. Calculate theoretical execution price by walking the book
theoretical_exec_price=calculate_theoretical_exec_price(
order.side,order.quantity,market_data.order_book
)
iftheoretical_exec_price==float('inf'):
return{'status':'REJECT','reason':'Insufficient Liquidity'}
exceptValueErrorase:
return{'status':'REJECT','reason':f'Market Data Error: {e}'}
# 4. Apply the core formula
iforder.side=='BUY':
slippage=(theoretical_exec_price-ref_price)/ref_price
else:# SELL
slippage=(ref_price-theoretical_exec_price)/ref_price
# 5. Make decision
ifslippage>slippage_cap:
return{
'status':'REJECT',
'reason':f'Slippage {slippage:.2%} exceeds cap of {slippage_cap:.
0%}'
}
else:
return{'status':'APPROVE'}

3. Critical Analysis
An effective system must account for real-world market dynamics and potential
failure modes.
3.1. Potential Failure Modes
Stale Market Data: The check is only as good as the data it uses. If the
market data feed (both NBBO and L2 book) is latent, the guardrail could
approve an order based on an old market state, leading to unexpected
slippage.
Mitigation: Implement strict timestamping on incoming market data.
The guardrail should reject any check where the data is older than a
configured tolerance (e.g., >100ms). Monitor feed health with
heartbeats.
Race Conditions: The market can move significantly in the microseconds
between  the  guardrail  check  and  the  order's  arrival  at  the  exchange's
matching engine. A check can pass, but the execution can still be poor.
Mitigation: This risk is inherent and cannot be eliminated, only
minimized. Co-locating the execution engine with the exchange and
using a highly optimized, low-latency software stack are crucial. The
guardrail is a safety net, not a guarantee of execution price.
Phantom  Liquidity  and  Icebergs:  The  order  book  does  not  always
represent  true,  accessible  liquidity.  Spoofing  orders  can  create  a  false
impression  of  depth,  and  iceberg  orders  hide  most  of  their  size.  The
Theoretical_Execution_Price calculation may be overly optimistic.
Mitigation: This is a difficult problem. A basic implementation must
accept this limitation. Advanced systems might incorporate historical
fill data to build a more realistic model of "executable liquidity" vs.
"displayed liquidity," but this adds significant complexity.
• 
◦ 
• 
◦ 
• 
◦ 

3.2. Edge Cases
Wide Spreads on Illiquid Assets: For an illiquid asset, the bid-ask spread
alone might exceed the 10% cap. For example, if the bid is $9.00 and the
ask is $11.00, the mid-point  Ref_Price is $10.00. A market buy order
would  immediately  execute  at  $11.00,  representing  a  10%  slippage
(11-10)/10 from the mid-point before any further book walking.
Recommendation: For illiquid assets, consider using the contra-
side BBO as the Ref_Price (i.e., Best Ask for a buy, Best Bid for a
sell). This effectively measures slippage after the cost of crossing the
spread, preventing automatic rejections for simply wanting to trade
an illiquid name.
Market  Open/Close  and  Volatility:  During  market  auctions  or  high-
volatility events (e.g., news releases), the NBBO may become invalid, wide,
or crossed.
Recommendation: The get_reference_price function must contain
robust validation. If a reliable Ref_Price cannot be calculated (e.g.,
spread is too wide, book is crossed, no quotes), the guardrail should
reject the order with a specific "Market Data Unreliable" error,
forcing a manual review.
3.3. Optimizations
Pre-computation: The liquidity classification (LIQUID/ ILLIQUID) must be
computed by a background process and stored in a low-latency cache. It
should not be calculated on the critical order path.
Performance: The book-walking logic can be a bottleneck in high-
throughput systems. This component should be written in a high-
performance language (C++, Rust, Java) and use efficient, lock-free data
structures to represent the order book to avoid contention between the
market data update thread and the order execution thread.
• 
◦ 
• 
◦ 
• 
• 

