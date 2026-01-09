# SOURCE PDF: avatrada_57_topic_001.pdf

Deep Research: Avatrada 57 Topic 001
Engineering Report: Dealer Gamma
Exposure (GEX) Calculation and
Analysis
Authored  By: Autonomous  Technical  Researcher  Date: October  26,  2023
Subject: Deep-Dive  on  Dealer  Gamma  Exposure  (GEX)  Formula  and
Implementation
Executive Summary
This  report  provides  a  detailed  engineering  analysis  of  the  Dealer  Gamma
Exposure (GEX) formula as specified in the source document. GEX is a critical
metric used to estimate the hedging activity of options market makers (dealers),
which in turn can influence market stability and volatility.
We will deconstruct the GEX formula, clarify the underlying assumptions about
dealer  positioning,  and  explain  the  crucial  sign  convention  used  in  its
calculation. An implementation strategy using Python and the Pandas library is
provided, including a code snippet for calculating GEX across an entire options
chain. Finally, the report conducts a critical analysis of the model, identifying its
potential failure modes, limitations, and areas for optimization. The objective is
to provide a comprehensive guide for accurately implementing and interpreting
this financial metric.
1.0 Technical Deconstruction
The core of the analysis is the GEX formula and the assumptions that give it
meaning.

1.1 The GEX Formula
The specified formula for calculating the dollar-denominated Gamma Exposure
for a single options contract is:
GEX_{\$} = \Gamma \times \text{OpenInterest} \times 100 \times S^2 \times 0.01
Let's break down each component:
Γ  (Gamma): This is a second-order option Greek. It measures the rate of
change of an option's Delta (Δ) for a $1 change in the underlying's spot
price (S). Its unit is Δ / $. Gamma is always positive for long option
positions (both calls and puts).
OpenInterest (OI): This represents the total number of outstanding
options contracts for a given strike and expiration. It is our proxy for the
scale of market participation.
100: The standard options contract multiplier. One equity option contract
typically represents 100 shares of the underlying stock.
S  (Spot Price): The current market price of the underlying asset.
S² and 0.01: These terms work together to convert the abstract Gamma
value into a meaningful dollar amount representing the required hedging
flow for a 1% move in the underlying. The derivation is as follows:
Total Gamma (in shares/$): Γ × OI × 100
This calculates the total change in the options position's share-
equivalent delta for a $1 move in the underlying.
Price Move for 1%: S × 0.01
This is the dollar magnitude of a 1% change in the spot price.
Shares to Hedge for a 1% Move: (Total Gamma) × (Price Move for
1%)
(Γ × OI × 100) × (S × 0.01)
This gives the total number of shares that must be bought or
sold to re-establish a delta-neutral position after a 1% price
change.
• 
• 
• 
• 
• 
1. 
▪ 
2. 
▪ 
3. 
▪ 
▪ 

Dollar Value of Hedge: (Shares to Hedge) × S
[(Γ × OI × 100) × (S × 0.01)] × S
Rearranging the terms gives the final formula: 
Γ × OI × 100 × S² × 0.01.
1.2 The Dealer Positioning Assumption
The  entire  GEX  concept  hinges  on  a  crucial  assumption:  Dealers  (Market
Makers) are the net counterparty to public/retail order flow.
The rationale is: *  Public Behavior: Retail and smaller institutional investors
are typically net buyers of options. They buy calls for upside speculation and buy
puts for downside protection (hedging). * Dealer Role: Market Makers provide
liquidity by taking the other side of these trades. If the public is net long options,
dealers are, by definition, net short options.
Therefore, the model assumes: * For Call options with significant Open Interest,
the public is long, and  dealers are short. * For Put options with significant
Open Interest, the public is long, and dealers are short.
1.3 The Sign Convention and Hedging Dynamics
This is the most critical and nuanced part of the calculation. While dealers are
assumed to be short both calls and puts (giving them negative Gamma from
both), their hedging actions are directionally opposite.
Short Calls (Negative Gamma): As the spot price S rises, the call's delta
approaches +1. The dealer's short call delta becomes more negative
(approaches -1). To remain delta-neutral, the dealer must buy the
underlying asset. They chase the price up.
Short Puts (Negative Gamma): As the spot price S falls, the put's delta
approaches -1. The dealer's short put delta becomes more positive
(approaches +1). To remain delta-neutral, the dealer must sell the
underlying asset. They chase the price down.
4. 
▪ 
▪ 
• 
• 

Both scenarios  accelerate the prevailing price trend, increasing volatility. To
represent this in a single aggregate number, the SqueezeMetrics methodology
introduces a sign convention:
The Gamma contribution from Put options is inverted (multiplied by -1).
Call GEX: Calculated with a positive sign: + (Γ * OI * ...)
Put GEX: Calculated with a negative sign: - (Γ * OI * ...)
This convention aligns the hedging impact. After applying this convention, the
resulting total GEX value can be interpreted:
Positive Total GEX: Indicates a "long gamma" environment for dealers.
This is counterintuitive to the assumption but arises when Put GEX
dominates the calculation. In this regime, dealers sell into rallies and buy
into dips, acting as a stabilizing force and suppressing volatility.
Negative Total GEX: Indicates a "short gamma" environment. This is the
typical state where Call GEX dominates. Dealers must buy into rallies and
sell into dips, acting as an accelerating force and amplifying volatility.
Finally,  since  we  are  calculating  Dealer  GEX,  and  our  initial  calculation
represents  the  public's  exposure,  we  must  invert  the  final  sign.  However,
common practice is to label the aggregate number (with the put sign flipped) as
"GEX" and interpret its sign directly as the market regime. We will follow this
common practice in the implementation.
2.0 Implementation Strategy
We  will  use  Python  with  the  Pandas  and  NumPy  libraries  for  an  efficient,
vectorized implementation.
Libraries: *  pandas:  For  data  manipulation  and  aggregation.  *  numpy:  For
efficient numerical operations, specifically for conditional sign flipping.
Data Schema: The input must be a Pandas DataFrame representing an options
chain with at least these columns: *  strike: The strike price of the option. *
type: The option type, e.g., 'call' or 'put'. * openInterest: The open interest for
the contract. * gamma: The gamma value for the contract.
• 
• 
• 
• 

The current spot price of the underlying is also required as a separate input.
Python/Pandas Implementation
The  following  function  encapsulates  the  logic  for  calculating  GEX  and
aggregating it by strike price.
importpandasaspd
importnumpyasnp
defcalculate_gex(options_chain_df:pd.DataFrame,spot_price:float)->
pd.DataFrame:
"""
    Calculates Gamma Exposure (GEX) for an entire options chain and aggregates 
by strike.
    Args:
        options_chain_df (pd.DataFrame): DataFrame with options data. 
                                         Must contain ['type', 'gamma', 
'openInterest', 'strike'].
        spot_price (float): The current spot price of the underlying asset.
    Returns:
        pd.DataFrame: A DataFrame indexed by strike, showing the total GEX in 
dollars.
    """
# --- 1. Define Constants ---
CONTRACT_MULTIPLIER=100.0
PERCENT_MOVE_FACTOR=0.01
# --- 2. Handle potential missing data ---
# Gamma or OI being NaN/None should result in zero exposure.
df=options_chain_df.copy()
df[['gamma','openInterest']]=df[['gamma','openInterest']].fillna(0)
# --- 3. Calculate GEX for each option contract ---
# This is the core formula: GEX = Gamma * OI * 100 * S^2 * 0.01
gex=(
df['gamma']*

df['openInterest']*
CONTRACT_MULTIPLIER*
(spot_price**2)*
PERCENT_MOVE_FACTOR
)
# --- 4. Apply the Sign Convention ---
# Puts have their gamma contribution flipped to align hedging impact.
# We create a sign multiplier: +1 for calls, -1 for puts.
sign_multiplier=np.where(df['type']=='put',-1,1)
# This is the GEX from the public's perspective
df['gex_public']=gex*sign_multiplier
# --- 5. Aggregate by Strike Price ---
gex_by_strike=df.groupby('strike')['gex_public'].sum()
# --- 6. Format Output ---
# Dealer GEX is the inverse of Public GEX. We can analyze either.
# For reporting, we'll show both total public and dealer GEX.
total_public_gex=gex_by_strike.sum()
total_dealer_gex=-total_public_gex
print(f"Total GEX (Public Perspective): ${total_public_gex:,.0f}")
print(f"Total GEX (Dealer Perspective): ${total_dealer_gex:,.0f}")
print("---")
print("Interpretation:")
iftotal_dealer_gex>0:
print("Positive Dealer GEX Regime: Dealers may act as a stabilizing 
force (sell rallies, buy dips).")
else:
print("Negative Dealer GEX Regime: Dealers may act as an accelerating 
force (buy rallies, sell dips).")
returngex_by_strike.to_frame('gex_dollars')
# --- Example Usage ---
# Create a sample options chain DataFrame
data={

'strike':[100,105,110,115,120,100,105,110,115,120],
'type':['call','call','call','call','call','put','put','put',
'put','put'],
'gamma':[0.05,0.08,0.10,0.07,0.04,0.05,0.08,0.10,0.07,0.04],
'openInterest':[5000,8000,12000,7000,3000,6000,9000,10000,6000,
2500]
}
sample_chain=pd.DataFrame(data)
underlying_spot_price=112.50
# Run the calculation
gex_profile=calculate_gex(sample_chain,underlying_spot_price)
# Display the aggregated results
print("\nGamma Exposure Profile by Strike:")
print(gex_profile.apply(lambdax:x.map('{:,.0f}'.format)))
3.0 Critical Analysis
While GEX is a powerful conceptual tool, its implementation is subject to several
limitations and potential failure modes.
3.1 Potential Failure Modes & Edge Cases
The Core Assumption is a Generalization: The model's foundation—that
dealers are always the counterparty to a monolithic "public"—is its greatest
weakness. In reality, the options market is a complex ecosystem of retail,
hedge funds, and large institutions. A hedge fund selling covered calls has
a  different  profile  than  a  retail  trader  buying  speculative  calls.  GEX  is
therefore a high-level proxy, not a precise measure of positioning.
Data  Quality  and  Latency: The  calculation  is  highly  sensitive  to  the
quality of its inputs.
Stale Data: Using stale gamma or spot_price values will lead to an
inaccurate GEX snapshot. Gamma is dynamic and changes with price
and volatility.
1. 
2. 
◦ 

Inaccurate Open Interest: OI data is typically updated once per day
(End-of-Day). It does not reflect intraday position changes, which can
be significant during volatile periods or on expiration days.
Scope of Included Options: The choice of which options to include is
critical and can drastically alter the result.
Expiration Dates: Including very long-dated options (LEAPs) can
distort the GEX figure, as their near-term hedging impact is minimal.
Most analyses focus on expiries within 30-90 days.
Liquidity: Illiquid, far out-of-the-money (OTM) options may have non-
zero OI but negligible gamma and hedging impact. Including them
adds noise. Filtering by a minimum OI or volume threshold is a
common practice.
3.2 Optimizations and Best Practices
Filtering: Before  calculation,  the  options  chain  should  be  filtered  to  a
relevant scope. A good starting point is to include options expiring within
the next 90 days and filter out contracts with zero open interest.
Vectorization: The  provided  Pandas/NumPy  implementation  is  highly
efficient  as  it  avoids  explicit  loops  in  Python,  leveraging  vectorized
operations for performance. This is the standard for this type of financial
data processing.
Dynamic Analysis: GEX is not a static number. Its true power comes from
observing  how  it  changes  over  time  and  how  the  profile  shifts  as  the
underlying price moves. A robust system would calculate GEX periodically
(e.g., every 5-15 minutes) to track the evolving hedging landscape.
"Gamma Flip" Level: A key level to monitor is the strike price where the
aggregate GEX could "flip" from positive to negative (or vice-versa). This
price level, often called the "Zero Gamma" level, can act as a pivot point in
the market, where dealer hedging behavior is expected to change regimes.
This can be found by calculating the cumulative sum of GEX across strikes.
◦ 
3. 
◦ 
◦ 
1. 
2. 
3. 
4. 

