# SOURCE PDF: avatrada_57_topic_027.pdf

Deep Research: Avatrada 57 Topic 027
Engineering Report: FINRA Rule 2360
Delta Aggregation
TO: Engineering  &  Compliance  Teams  FROM: Autonomous  Technical
Researcher DATE: October 26, 2023 SUBJECT: Deep-Dive on FINRA Rule 2360
Delta-Based Position Limit Calculation
1.0 Technical Deconstruction
This  section  deconstructs  the  mechanisms  and  logic  behind  the  delta-based
aggregation method for FINRA Rule 2360 position limits.
1.1 Objective of FINRA Rule 2360
FINRA Rule 2360 establishes position limits on equity options to prevent any
single entity or group from establishing an excessively large position that could
be used to manipulate the market for the underlying security. Compliance is
traditionally measured by counting the total number of contracts on the same
"side of the market" (e.g., long calls and short puts are bullish; long puts and
short calls are bearish).
However, FINRA provides a more sophisticated alternative: the  Delta-Based
Method. This method acknowledges that not all options carry the same market
risk. An at-the-money option has a much larger impact on the underlying than a
deep  out-of-the-money  option.  The  delta-based  approach  converts  all  option
positions into a "Delta-Equivalent Share Count," which represents the portfolio's
net equivalent long or short share position in the underlying security.

1.2 The Core Aggregation Formula
The "Delta-Equivalent Share Count" is the net sum of the delta-adjusted values of
all  option  positions  on  a  single  underlying  security.  The  formula  for  this
calculation is:
Delta-Equivalent Share Count = Σ (Δ_i * C_i * M)
Where:  *  Σ (Sigma)  represents  the  summation  across  all  individual  option
positions (legs) in the portfolio for a given underlying. * Δ_i (Delta) is the delta of
the specific option leg i. * Long Calls have a delta between 0 and +1. * Short
Calls have a delta between 0 and -1. * Long Puts have a delta between -1 and 0. *
Short Puts have a delta between 0 and +1. * C_i (Contracts) is the number of
contracts for leg i. This value is positive for long positions and negative for
short positions. * M (Multiplier) is the number of shares per contract, which is
typically 100 for standard US equity options.
1.3 Example Calculation: Mixed SPY Portfolio
Let's deconstruct a hypothetical portfolio of SPY options to calculate its single
Delta-Equivalent Share Count.
Portfolio Positions: 1.  Long 2,000 SPY 450 Calls (Bullish Spread Leg) 2.
Short 2,000 SPY 460 Calls (Bearish Spread Leg) 3. Long 500 SPY 440 Puts
(Bearish Position) 4. Short 1,000 SPY 430 Puts (Bullish Position)
Assumed Market Data & Deltas: * SPY Underlying Price: $452.00 * Position 1
(Long 2000 C @ 450): Delta (Δ) =  +0.65 * Position 2 (Short 2000 C @ 460):
Delta (Δ) = +0.35 (Note: The option's delta is positive, but the position is short).
* Position 3 (Long 500 P @ 440): Delta (Δ) = -0.20 * Position 4 (Short 1000 P @
430): Delta (Δ) = -0.10 (Note: The option's delta is negative, but the position is
short).
Calculation Steps:
Leg 1 (Long Calls):
Δ_1 = +0.65
1. 
◦ 

C_1 = +2000 (Long position)
Share Count = 0.65 * 2000 * 100 = +130,000
Leg 2 (Short Calls):
Δ_2 = +0.35
C_2 = -2000 (Short position)
Share Count = 0.35 * (-2000) * 100 = -70,000
Leg 3 (Long Puts):
Δ_3 = -0.20
C_3 = +500 (Long position)
Share Count = -0.20 * 500 * 100 = -10,000
Leg 4 (Short Puts):
Δ_4 = -0.10
C_4 = -1000 (Short position)
Share Count = -0.10 * (-1000) * 100 = +10,000
Final Aggregation:
Total Delta-Equivalent Shares = 130,000 - 70,000 - 10,000 + 10,000
Total Delta-Equivalent Shares = +60,000
This portfolio has a net Delta-Equivalent Share Count of  60,000 long shares.
This final number is what would be compared against the FINRA position limit
for SPY, which is expressed in shares for firms using the delta-based method.
1.4 Application to a Principal's Personal Account
FINRA  rules  are  designed  to  prevent  circumvention  by  spreading  positions
across multiple accounts. The key concept is control and acting in concert.
Aggregation is Required: A Principal acting as a sole proprietorship is,
for regulatory purposes, indistinct from their firm. Any accounts over which
◦ 
◦ 
2. 
◦ 
◦ 
◦ 
3. 
◦ 
◦ 
◦ 
4. 
◦ 
◦ 
◦ 
• 

the Principal has direct or indirect control, including personal brokerage
accounts, must be aggregated with the firm's accounts.
Rationale: The rule applies to a "person," which includes any entity, sole
proprietorship, or individual. If the Principal's personal account and the
firm's proprietary account both hold SPY options, they are considered to be
under common control.
Conclusion: The positions in the Principal's personal account must be
included in the firm's total Delta-Equivalent Share Count calculation for
SPY. Failure to do so would be a serious violation of Rule 2360.
2.0 Implementation Strategy
Building  a  robust,  real-time  system  for  this  calculation  requires  integrating
position data, market data, and a financial modeling library.
2.1 System Architecture & Data Flow
Position Ingestion: The system must have access to a real-time feed of all
option positions from all relevant accounts (firm prop, principal's personal,
etc.). This is typically sourced from a portfolio management system or a
direct drop-copy from the executing broker.
Market Data Service: A low-latency market data provider is needed for:
Underlying asset price (e.g., SPY).
Implied Volatility (IV) for each option series.
Risk-free interest rate.
Dividend yield for the underlying.
Delta Calculation Engine: This core component takes the position and
market data to calculate the delta for each leg.
Aggregation & Limit Check: The engine sums the delta-equivalent shares
and compares the absolute value against the pre-configured FINRA limit for
the specific symbol.
Alerting & Reporting: If a pre-defined threshold (e.g., 90% of the limit) or
the limit itself is breached, the system must generate immediate alerts to
the trading and compliance desks.
• 
• 
1. 
2. 
◦ 
◦ 
◦ 
◦ 
3. 
4. 
5. 

2.2 Technology Stack (Python Example)
Python is well-suited for this task due to its powerful financial and data analysis
libraries.
Libraries:
pandas: For managing and manipulating position data in a structured
DataFrame.
py_vollib: A standard, open-source library for calculating option
greeks, including delta, based on the Black-Scholes-Merton model.
requests or a dedicated SDK: For fetching data from market data
provider APIs (e.g., Polygon.io, Bloomberg).
Execution Environment: Can be run as a scheduled job (e.g., every
minute) or a streaming application for real-time monitoring.
2.3 Pseudocode & Python Snippet
Here is a Python function demonstrating the core logic for the SPY portfolio
example.
importpandasaspd
frompy_vollib.black_scholesimportblack_scholes
# Note: In a real system, 'greeks' would be calculated using a library
# that takes live market data (price, vol, rate) as input.
# For this example, we use the pre-determined deltas.
defcalculate_delta_equivalent_shares(portfolio_df:pd.DataFrame)->float:
"""
    Calculates the total Delta-Equivalent Share Count for a portfolio.
    Args:
        portfolio_df: A pandas DataFrame with columns:
                      ['symbol', 'type', 'strike', 'contracts', 'delta']
                      'contracts' is positive for long, negative for short.
    Returns:
• 
◦ 
◦ 
◦ 
• 

        The total delta-equivalent share count.
    """
OPTION_MULTIPLIER=100
# Vectorized calculation for efficiency
portfolio_df['delta_shares']=(
portfolio_df['delta']*
portfolio_df['contracts']*
OPTION_MULTIPLIER
)
total_delta_equivalent_shares=portfolio_df['delta_shares'].sum()
returntotal_delta_equivalent_shares
# 1. Define the portfolio from our example
data={
'symbol':['SPY','SPY','SPY','SPY'],
'type':['Call','Call','Put','Put'],
'strike':[450,460,440,430],
'contracts':[2000,-2000,500,-1000],# Note the negative sign for shorts
'delta':[0.65,0.35,-0.20,-0.10]
}
portfolio=pd.DataFrame(data)
# 2. Run the calculation
net_delta_shares=calculate_delta_equivalent_shares(portfolio)
# 3. Output the result
print(f"Portfolio DataFrame:\n{portfolio}\n")
print(f"Total Delta-Equivalent Share Count: {net_delta_shares:,.0f}")
# Example Limit Check
SPY_POSITION_LIMIT=900000# Example limit
ifabs(net_delta_shares)>SPY_POSITION_LIMIT:
print("\n*** ALERT: POSITION LIMIT BREACHED ***")
else:
print(f"\nPosition is within the {SPY_POSITION_LIMIT:,} share limit.")

3.0 Critical Analysis
While powerful, the delta-based method introduces complexities and potential
points of failure that must be managed.
3.1 Potential Failure Modes
Stale Market Data: The entire calculation is highly sensitive to the inputs,
especially the underlying price and implied volatility. A stale data feed will
produce an inaccurate delta, leading to a "phantom" compliance status. The
system must have data health checks and fail-safes if a data feed becomes
latent.
Model Risk (Black-Scholes): The Black-Scholes model has known
limitations. It assumes constant volatility and risk-free rates, which is not
true in reality. For American-style options (most equity options), a model
like Binomial/Trinomial pricing is technically more accurate, especially
around dividends. However, Black-Scholes is the industry standard for its
speed and simplicity in this context.
Data Aggregation Failure: The system must be architected to guarantee
that positions from all required accounts are included. A failure to connect
to a data source for one account (e.g., the Principal's personal account)
should trigger a system-wide alert, as the resulting calculation would be
incomplete and non-compliant.
3.2 Edge Cases
Gamma Risk at Expiration: As options near expiration, their delta can
change extremely rapidly with small moves in the underlying price (high
gamma). A portfolio that is compliant mid-day could rapidly breach its limit
near the 4:00 PM ET close. Monitoring frequency must be increased
significantly for near-expiry positions.
Illiquid Options: For deep in-the-money or far out-of-the-money options,
the calculated delta from a model might not reflect the option's true
hedging reality. A deep ITM call's delta may approach 1.0, effectively
making it a stock-equivalent position.
• 
• 
• 
• 
• 

Corporate Actions: Stock splits, mergers, or special dividends require
careful handling. A standard 2-for-1 split would double the number of
shares and halve the strike, but the option multiplier (100) might change to
reflect a non-standard deliverable. The system must correctly ingest and
apply these adjustments.
3.3 Optimizations
Vectorization: As shown in the Python example, performing calculations
on the entire portfolio array at once (vectorization) using libraries like
NumPy and Pandas is orders of magnitude faster than iterating through
positions one by one.
Caching: Market data inputs (especially IV and rates) do not change tick-
by-tick. Caching these values for a short duration (e.g., 1-5 seconds) can
significantly reduce the load on market data services without sacrificing
meaningful accuracy.
Tiered Alerting: Implement multiple alert thresholds. For example:
Level 1 (80% of limit): Informational alert to the trading desk.
Level 2 (95% of limit): High-priority warning to trading and
compliance.
Level 3 (100% breach): Critical, "cease trading" alert and
automated reporting. This allows for proactive risk management
rather than reactive damage control.
• 
• 
• 
• 
◦ 
◦ 
◦ 

