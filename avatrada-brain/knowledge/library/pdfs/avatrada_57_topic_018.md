# SOURCE PDF: avatrada_57_topic_018.pdf

Deep Research: Avatrada 57 Topic 018
Engineering Report: Analysis of IBKR
Algorithmic Venue Selection
TO: Trading  Systems  Architect  FROM: Autonomous  Technical  Researcher
DATE: October 26, 2023  SUBJECT: Deep-Dive on IBKR SMART vs. Directed
Routing for Algorithmic Trading
Executive Summary
This  report  provides  a  detailed  engineering  analysis  of  Interactive
Brokers' (IBKR) SMART (Smart Market Advantage Routing Technology) routing
versus Directed Routing. The primary objective is to determine the conditions
under which it is mathematically advantageous to override the default SMART
logic and direct an order to a specific venue like ISLAND (NASDAQ) or IEX.
Our analysis concludes that  SMART routing is the optimal choice for the
vast majority of orders, particularly those seeking immediate execution
(liquidity-taking orders). It is a sophisticated, multi-factor system designed to
achieve the best net price by considering price, liquidity, and exchange fees/
rebates.
Directed  routing  becomes  a  viable  strategy  primarily  for  liquidity-
providing (passive) orders where the trader's goal is to capture a specific
exchange  rebate.  The  decision  to  use  directed  routing  hinges  on  a  complex
calculation where the expected rebate must outweigh not only explicit fees but
also the implicit costs of market impact and the opportunity cost of a potential
non-fill. Programmatic access to fee/rebate schedules is not available via a real-
time API; it requires maintaining a local, periodically updated database sourced
from exchange publications.

1. Technical Deconstruction
1.1 IBKR SMART Routing Mechanism
IBKR's SMART is a Smart Order Router (SOR). Its primary objective is to achieve
the best possible net execution price. It is not a simple NBBO (National Best
Bid and Offer) router; it is a dynamic system that continuously scans competing
market centers and exchanges to automatically route orders.
Core Logic Components:
Price Discovery: SMART continuously polls market data from all available
venues, including "lit" exchanges (e.g., ARCA, NASDAQ) and dark pools.
Liquidity Assessment: It maintains a real-time view of the available size
at each price level on each venue.
Cost Analysis: Crucially, SMART's proprietary algorithm incorporates
exchange fee and rebate schedules into its routing decision. It calculates
the "net price" of an execution, factoring in the cost to remove liquidity or
the credit for adding it.
Order Fragmentation: For larger orders, SMART can split the order into
smaller pieces and route them to different venues simultaneously or
sequentially to minimize market impact and source liquidity from multiple
locations.
Dark Pool Integration: SMART will probe dark pools for non-displayed
liquidity. A fill in a dark pool can provide significant price improvement
(e.g., mid-point execution) and, most importantly, has zero market impact
as the trade is not publicly displayed.
In essence, SMART is a complex, proprietary optimization engine designed to
solve for  max(PriceImprovement) - min(ExecutionCost), where  ExecutionCost
includes both explicit fees and implicit impact costs.
1. 
2. 
3. 
4. 
5. 

1.2 Directed Routing Mechanism
Directed routing bypasses the SMART logic entirely. The trader assumes full
responsibility for the routing decision, sending the order to a single, specified
exchange.
Primary Use Cases:
Rebate Capture: This is the most common reason. By posting a non-
marketable limit order (i.e., adding liquidity), a trader can receive a per-
share payment (rebate) from the exchange. This is central to "maker-taker"
exchange models.
Accessing Specific Order Types: Some exchanges offer unique order
types not available through the standard SMART API. A prime example is
the IEX D-Peg (Discretionary Peg) order, which is designed to protect
against latency arbitrage.
Avoiding Specific Fees: Conversely, a trader may wish to direct an order
to a "taker-maker" venue where the fees for taking liquidity are lower, even
if the displayed price is not the absolute best.
1.3 The Core Economic Formula & Decision Framework
The prompt suggests the formula: Rebate > Fee + Impact_Cost. This is a good
starting point, but it must be refined for practical application, as an order cannot
simultaneously earn a rebate (for adding liquidity) and incur a taker fee (for
removing liquidity).
The  decision  must  be  split  based  on  the  order's  intent:  passive  (adding
liquidity) or aggressive (taking liquidity).
For Passive (Liquidity-Adding) Orders:
This is the primary scenario where directed routing is considered. A passive
order is a limit order placed outside the current NBBO (e.g., a bid below the best
bid, or an ask above the best ask).
The refined formula compares the expected value of a directed order versus a
SMART-routed order.
1. 
2. 
3. 

//Decision: RouteDirectedifEV_Directed>EV_SMART
//ExpectedValueofaDirectedPassiveOrder
EV_Directed=(Rebate_per_share*P_fill)-(Opportunity_Cost_no_fill*(1-
P_fill))
//ExpectedValueofaSMART-routedPassiveOrder
//SMARTmayfindbetternetpricingorpriceimprovementopportunities.
EV_SMART=(Expected_Price_Improvement_per_share)-(Net_Fee_SMART)
Rebate_per_share: The credit received from the venue (e.g., +$0.002 per
share).
P_fill: The probability that your limit order gets executed. This is the
most difficult variable to model, depending on volatility, queue position, and
market direction.
Opportunity_Cost_no_fill: The cost incurred if the market moves away
from your order and you fail to get a fill, missing a profitable trade. This is
a form of adverse selection.
Expected_Price_Improvement_per_share: The benefit from SMART routing
to a venue (like a dark pool) that offers a better price than the one you
would have posted.
For Aggressive (Liquidity-Taking) Orders:
An aggressive order is a market order or a marketable limit order (e.g., a bid at
or above the best ask). Here, you are paying a fee.
The decision is to minimize total cost.
//Decision: RouteDirectedifTotal_Cost_Directed<Total_Cost_SMART
//TotalCostofaDirectedAggressiveOrder
Total_Cost_Directed=(Taker_Fee_per_share)+(Impact_Cost_per_share)
//TotalCostofaSMART-routedAggressiveOrder
Total_Cost_SMART=(Effective_Net_Fee_SMART)+(Impact_Cost_SMART)
• 
• 
• 
• 

In this scenario, SMART is almost always superior. It is explicitly designed to
minimize  Total_Cost_SMART by  finding  hidden  liquidity  (reducing
Impact_Cost_SMART) and intelligently routing to minimize fees. Attempting to
manually select a venue is unlikely to outperform SMART's comprehensive, low-
latency search.
2. Implementation Strategy
2.1 Decision Tree Logic
This decision tree formalizes the logic from section 1.3.
graphTD
A[Start: New Order]-->B{OrderType?};
B-->C[Aggressive / Liquidity-Taking<br>(Market Order, Marketable Limit)];
B-->D[Passive / Liquidity-Adding<br>(Non-Marketable Limit)];
C-->E[ROUTE VIA SMART];
E-->F[End];
C-.->G((Justification:SMARTisoptimized<br>tominimizetotalcost(fees
+impact)<br>byscanningallvenues,includingdarkpools.<br>Manualoverride
isunlikelytoimproveresults.));
D-->H{CalculateEV_Directed};
H-->I["1. Fetch Rebate for Target Venue<br>(e.g., ISLAND = +$0.002/
share)"];
I-->
J["2. Model P(fill) for the order<br>(e.g., based on volatility, order book 
depth)"];
J-->K["3. Model Opportunity Cost<br>(e.g., based on short-term alpha 
signal decay)"];
K-->L[EV_Directed = (Rebate * P_fill) - (Opp_Cost * (1-P_fill))];
D-->M{CalculateEV_SMART};
M-->
N["1. Estimate potential price improvement<br>(often small for passive orders, 
but non-zero,<br>e.g., from dark pool mid-point routing)"];

N-->O["2. Estimate Net Fee/Rebate from SMART<br>(assume near-zero or 
slightly negative)"];
O-->P[EV_SMART = Price_Improvement - Net_Fee];
L-->Q{EV_Directed>EV_SMART?};
P-->Q;
Q--Yes-->R[ROUTE DIRECTED to Venue];
Q--No-->S[ROUTE VIA SMART];
R-->F;
S--> F;
2.2 Programmatic Access to Fee/Rebate Tables
There is no direct, real-time IBKR API endpoint to query exchange fee
and rebate schedules. This data is not considered real-time market data. The
implementation requires a semi-manual, out-of-band process.
Strategy:
Source Data: The definitive sources are the exchange websites themselves
(e.g., NASDAQ, NYSE, CBOE). They publish their fee schedules publicly,
usually as web pages or PDFs.
Data Ingestion: Create a parser or a manual process to extract the
relevant data for the venues you intend to use (e.g., ARCA, IEX, BATS,
ISLAND). The data points needed are typically:
Liquidity-Adding Rebate (per share)
Liquidity-Removing Fee (per share)
Tiers based on monthly volume (if applicable)
Rules for specific security types (e.g., stocks < $1.00)
Local Storage: Store this structured data in a configuration file (e.g., 
fees.json) or a local database (e.g., SQLite) that your trading application
can read at startup.
Update Cadence: These schedules do not change daily, but they are
updated periodically (e.g., quarterly or monthly). Implement a monthly or
quarterly check-and-update process for your local fee database.
1. 
2. 
◦ 
◦ 
◦ 
◦ 
3. 
4. 

Example fees.json Structure:
{
"last_updated":"2023-10-01",
"venues":{
"ISLAND":{
"add_liquidity_rebate":0.0020,
"remove_liquidity_fee":0.0030,
"notes":"Standard NASDAQ fee for stocks > $1.00"
},
"ARCA":{
"add_liquidity_rebate":0.0022,
"remove_liquidity_fee":0.0030,
"notes":"Check for tiered pricing based on volume."
},
"IEX":{
"add_liquidity_rebate":0.0000,
"remove_liquidity_fee":0.0009,
"notes":"Taker-maker model, no rebate for adding liquidity."
}
}
}
2.3 Estimating Market Impact Cost
Estimating  Impact_Cost is  a  core  challenge  in  quantitative  finance.  For  a
practical implementation, a simplified model is often sufficient. The "square root
model" is a widely used heuristic.
importnumpyasnp
defestimate_impact_cost_per_share(order_size_Q,daily_volume_V,
daily_volatility_sigma,book_spread_S):
"""
    Estimates per-share market impact cost using a square root model.
    Args:
        order_size_Q (int): Number of shares in the order.

        daily_volume_V (int): Average daily volume for the stock.
        daily_volatility_sigma (float): Annualized volatility / sqrt(252).
        book_spread_S (float): Current bid-ask spread.
    Returns:
        float: Estimated temporary impact cost per share.
    """
# Participation rate of the order relative to daily volume
participation_rate=order_size_Q/daily_volume_V
# A common heuristic for the impact coefficient. This can be calibrated.
impact_coefficient_Y=0.5
# Temporary impact from the Almgren-Chriss model family
temporary_impact=impact_coefficient_Y*daily_volatility_sigma*
np.sqrt(participation_rate)
# Total impact cost per share is half the spread plus the temporary market 
impact
# We assume we cross half the spread on average for a market order.
impact_cost=(book_spread_S/2)+temporary_impact
returnimpact_cost
# Example Usage:
# Cost to buy 10,000 shares of a stock with 5M ADV, 30% ann. vol, and $0.02 
spread
# daily_sigma = 0.30 / np.sqrt(252) 
# cost = estimate_impact_cost_per_share(10000, 5000000, 0.0189, 0.02) 
# print(f"Estimated impact cost per share: ${cost:.4f}")
This model provides a baseline. More advanced implementations would involve
calibrating impact_coefficient_Y against historical execution data.

3. Critical Analysis: Failure Modes &
Optimizations
3.1 Potential Failure Modes
Stale Fee/Rebate Data: The entire directed routing logic is predicated on
accurate cost data. If the local fees.json is out of date, the algorithm will
make suboptimal decisions, potentially incurring unexpected costs. 
Mitigation: A robust, scheduled process for updating fee schedules is
critical.
Model Risk (P_fill & Impact_Cost): The models for P(fill) and 
Impact_Cost are estimations. In volatile markets or for illiquid stocks,
these models can be highly inaccurate. An overly optimistic P(fill) could
lead to significant opportunity costs. Mitigation: Start with conservative
estimates. Backtest models extensively and add circuit breakers to default
to SMART routing during periods of extreme volatility.
Adverse Selection: When you post a passive limit order, you are most
likely to be filled when the market is moving against you. The model's 
Opportunity_Cost term must accurately capture this risk. If it doesn't, the
calculated EV_Directed will be artificially inflated.
Latency: The time taken to perform the EV calculation, read the fee
database, and route the order adds latency. While minimal, in fast-moving
markets this could be enough to miss the desired execution window. 
Mitigation: Ensure the decision logic is highly optimized and runs on co-
located hardware if necessary.
3.2 Key Optimizations & Considerations
Hybrid Approach: Instead of a binary SMART vs. Directed choice,
consider a hybrid model. For a large order, route a small "iceberg" portion
via a directed, passive order to capture rebates, while routing the bulk of
the order through SMART to minimize impact.
Venue-Specific Behavior: The model assumes all venues are equal except
for fees. This is untrue. IEX has its "speed bump," and other venues have
1. 
2. 
3. 
4. 
1. 
2. 

different order matching algorithms. A sophisticated strategy would model 
P(fill) differently for each venue.
The Futility of Outsmarting SMART: It is crucial to recognize that
IBKR's SMART router already considers fees and rebates. You are
attempting to create a specialized model that outperforms their general-
purpose, low-latency, proprietary model. The only sustainable edge is to
have a different optimization goal than SMART. For example, if your goal is
"maximize rebate capture, even at the expense of a small amount of price
improvement," then this custom logic is valid. If your goal is simply "best
net price," it is highly probable that SMART is already the superior
solution.
3. 

