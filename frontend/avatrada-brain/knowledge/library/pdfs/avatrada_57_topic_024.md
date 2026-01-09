# SOURCE PDF: avatrada_57_topic_024.pdf

Deep Research: Avatrada 57 Topic 024
Engineering Report: Volatility Targeting
and Scaling
Report ID: EDR-2023-VS-001
Subject: Deep-Dive on Volatility Scaling for Position Sizing (ATR/IV)
Author: Autonomous Technical Researcher
Date: October 26, 2023 
1.0 Executive Summary
This report provides a rigorous engineering analysis of the "Volatility Targeting"
position  sizing  methodology  as  specified  in  the  source  document.  The  core
objective of this technique is to normalize position risk across different assets,
ensuring  each  contributes  a  consistent,  predefined  amount  of  risk  to  the
portfolio. We will deconstruct the mechanisms for both equities (using Average
True Range - ATR) and options (using Implied Volatility - IV), provide a detailed
implementation strategy, and conduct a critical analysis of the system's potential
failure  modes,  limitations,  and  areas  for  optimization.  The  central  challenge
addressed is the normalization of an option's Implied Volatility (a percentage)
into a concrete dollar-risk equivalent for accurate sizing.
2.0 Technical Deconstruction
Volatility  targeting  is  a  risk  management  framework  that  sizes  positions
inversely to their recent or expected volatility. The fundamental principle is:
higher volatility leads to a smaller position size, and lower volatility leads
to a larger position size, for the same target risk budget.

2.1 Equity Position Sizing (ATR-Based)
For equities, the system uses Average True Range (ATR), a measure of realized
(historical) price volatility.
2.1.1 Core Components & Formula
The provided formula is: Shares = (Account_Value * Target_Risk_Pct) / (ATR *
Multiplier)
Let's break down each component:
Account_Value: Total market value of the trading account (e.g.,
$1,000,000).
Target_Risk_Pct: The percentage of the account value to be risked on a
single position. For example, 1% (0.01).
Risk_Budget: This is the numerator (Account_Value * Target_Risk_Pct). It
represents the maximum acceptable loss in dollar terms for this position if
the asset moves against the trade by a "standard" volatile amount (e.g.,
$10,000).
ATR (Average True Range): The primary volatility metric. It is the moving
average (typically 14-day) of the True Range.
True Range (TR) is the greatest of the following:
Current High - Current Low
abs(Current High - Previous Close)
abs(Current Low - Previous Close)
ATR is expressed in dollars (e.g., $2.50 for a stock), representing the
average daily price range, accounting for overnight gaps.
Multiplier: A scalar used to adjust the risk denominator. A multiplier of
1.0 means you are sizing the position based on a 1-ATR move. A multiplier
of 2.0 means you are sizing for a 2-ATR move, effectively halving the
position size and the risk taken. This is a crucial parameter for tuning the
system's overall risk appetite.
• 
• 
• 
• 
◦ 
1. 
2. 
3. 
◦ 
• 

2.1.2 Mathematical Logic
The formula can be re-written to highlight its logic:
# Total dollar risk allowed for the position
Risk_Budget_USD = Account_Value * Target_Risk_Pct
# The expected dollar move per share that defines our risk event
Risk_Per_Share_USD = ATR * Multiplier
# How many shares can we hold so that a 'Risk_Per_Share' event equals our 
'Risk_Budget'?
Number_of_Shares = Risk_Budget_USD / Risk_Per_Share_USD
2.2 Option Position Sizing (IV-Based)
Options are derivative instruments, and their risk profile is multi-faceted (the
"Greeks").  The  challenge  is  converting  Implied  Volatility  (IV),  an  annualized
percentage, into a practical dollar-risk metric for a single options contract.
2.2.1 Normalizing Implied Volatility to Dollar Risk
IV represents the market's expectation of the annualized 1-standard-deviation
move of the  underlying asset. A direct comparison to ATR is not possible. We
must  translate  this  percentage  into  the  expected  dollar  price  change  of  the
option contract itself over a short time horizon (e.g., one day).
A  robust  method  involves  using  the  option's  Greeks,  primarily  Delta and
Gamma, to approximate this change.
Calculate the Expected 1-Day Move of the Underlying: First, we de-
annualize the IV to find the expected 1-standard-deviation move for a single
trading day.
```latex
1. 

S = Underlying Price, IV = Implied
Volatility (e.g., 0.30 for 30%)
T_days = Number of trading days in a
year (approx. 252)
Expected_1_Day_Underlying_Move_USD = S * (IV / sqrt(T_days)) `` For a
$100 stock with 30% IV, this is$100 * (0.30 / sqrt(252)) ≈ $1.89`. This
means  the  market  expects  a  daily  move  of  about  $1.89  with  ~68%
probability.
Estimate the Option Price Change (The Dollar-Risk Equivalent): The
option's price will not move by $1.89. Its change is a function of its Greeks.
We can use a second-order Taylor series expansion to estimate the option's
price change for a given move in the underlying. This is the Delta-Gamma
Approximation.
```latex
2. 

ΔP_option = Change in Option Price
ΔS = Change in Underlying Price
(from step 1)
Note: Gamma is per $1 move, so the
formula is 0.5 * Gamma * (ΔS)^2
ΔP_option ≈ (Delta * ΔS) + (0.5 * Gamma * (ΔS)^2) `` ThisΔP_option` is
our  Dollar-Risk Equivalent per Contract. It represents the projected
profit or loss on the option for a 1-standard-deviation adverse move in the
underlying.
2.2.2 Final Option Sizing Formula
With  the  dollar  risk  per  contract  established,  the  sizing  formula  becomes
analogous to the equity formula:
# Dollar risk per contract, as calculated above
Dollar_Risk_Per_Contract = abs(ΔP_option) * 100_shares_per_contract
# Risk budget remains the same
Risk_Budget_USD = Account_Value * Target_Risk_Pct
# Final formula for number of contracts
Number_of_Contracts = Risk_Budget_USD / Dollar_Risk_Per_Contract

3.0 Implementation Strategy
This system will be implemented in Python, leveraging standard financial and
data analysis libraries.
3.1 Required Libraries
pip install pandas numpy yfinance py_vollib
pandas: For data manipulation and time-series analysis.
numpy: For numerical operations.
yfinance: For fetching stock and option data (for prototyping; a production
system requires a premium data provider like Polygon.io or Bloomberg).
py_vollib: A library for calculating option prices and Greeks.
3.2 Equity Sizing Implementation
importpandasaspd
importnumpyasnp
importyfinanceasyf
defcalculate_atr(data:pd.DataFrame,period:int=14)->float:
"""Calculates the Average True Range (ATR) for a given period."""
high_low=data['High']-data['Low']
high_close=np.abs(data['High']-data['Close'].shift())
low_close=np.abs(data['Low']-data['Close'].shift())
tr=pd.concat([high_low,high_close,low_close],axis=1).max(axis=1)
atr=tr.ewm(alpha=1/period,adjust=False).mean()# Using EMA for ATR
returnatr.iloc[-1]
defget_equity_position_size(
symbol:str,
account_value:float,
target_risk_pct:float,
• 
• 
• 
• 

atr_period:int=14,
atr_multiplier:float=2.0
)->float:
"""Calculates position size for an equity based on ATR volatility."""
# 1. Define Risk Budget
risk_budget_usd=account_value*target_risk_pct
# 2. Fetch Data and Calculate ATR
# Fetch enough data for ATR calculation (e.g., period + buffer)
hist_data=yf.Ticker(symbol).history(period=f"{atr_period*2}d")
ifhist_data.empty:
raiseValueError(f"No data found for symbol {symbol}")
current_atr=calculate_atr(hist_data,period=atr_period)
# 3. Calculate Risk Per Share
risk_per_share_usd=current_atr*atr_multiplier
ifrisk_per_share_usd==0:
return0# Avoid division by zero
# 4. Calculate Position Size
num_shares=risk_budget_usd/risk_per_share_usd
returnnp.floor(num_shares)# Return whole shares
# --- Example Usage ---
account_val=1000000
risk_pct=0.01# 1% risk
shares_to_buy=get_equity_position_size("AAPL",account_val,risk_pct)
print(f"Calculated Position Size for AAPL: {shares_to_buy} shares")
3.3 Option Sizing Implementation
frompy_vollib.black_scholes.greeksimportanalyticalasgreeks
defget_option_position_size(
underlying_symbol:str,

option_data:dict,# Expects {'K', 'T', 'r', 'sigma', 'flag'}
account_value:float,
target_risk_pct:float,
trading_days_per_year:int=252
)->float:
"""
    Calculates position size for an option based on IV and Greeks.
    option_data contains:
    K: Strike Price
    T: Time to expiration in years
    r: Risk-free rate
    sigma: Implied Volatility (IV)
    flag: 'c' for call, 'p' for put
    """
# 1. Define Risk Budget
risk_budget_usd=account_value*target_risk_pct
# 2. Get Underlying Price
underlying=yf.Ticker(underlying_symbol)
S=underlying.history(period="1d")['Close'].iloc[-1]
# 3. Calculate Expected 1-Day Underlying Move
iv=option_data['sigma']
expected_move_usd=S*(iv/np.sqrt(trading_days_per_year))
# 4. Calculate Greeks
delta=greeks.delta(option_data['flag'],S,option_data['K'],
option_data['T'],option_data['r'],iv)
gamma=greeks.gamma(option_data['flag'],S,option_data['K'],
option_data['T'],option_data['r'],iv)
# 5. Calculate Dollar Risk per Contract (Delta-Gamma Approximation)
# We assume an adverse move, so for a long call, the move is down. For a 
long put, up.
# For simplicity, we can use the absolute value of the price change.
# The direction of the move should align with the trade direction for 
accurate risk.
# E.g., for a long call, risk is a downward move (-expected_move_usd).

adverse_move=-expected_move_usdifoption_data['flag']=='c'else
expected_move_usd
option_price_change=(delta*adverse_move)+(0.5*gamma*
(adverse_move**2))
# Dollar risk is per share; multiply by 100 for a standard contract
dollar_risk_per_contract=abs(option_price_change*100)
ifdollar_risk_per_contract==0:
return0
# 6. Calculate Position Size
num_contracts=risk_budget_usd/dollar_risk_per_contract
returnnp.floor(num_contracts)
# --- Example Usage ---
# Fictional data for an AAPL call option
aapl_call_data={
'K':175, # Strike Price
'T':30/365.25, # Time to expiration (30 days)
'r':0.05, # Risk-free rate (5%)
'sigma':0.25, # Implied Volatility (25%)
'flag':'c' # It's a call
}
contracts_to_buy=get_option_position_size("AAPL",aapl_call_data,
account_val,risk_pct)
print(f"Calculated Position Size for AAPL Call: {contracts_to_buy} contracts")
4.0 Critical Analysis
While powerful, the Volatility Targeting model is not infallible. It is a model with
specific assumptions and is subject to several failure modes and edge cases.

4.1 Potential Failure Modes & Edge Cases
Non-Stationary  Volatility:  The  model's  primary  weakness.  Both  ATR
(backward-looking) and IV (forward-looking but model-dependent) assume
that  the  near-future  volatility  will  resemble  the  measured  volatility.  A
sudden event (e.g., earnings announcement, geopolitical news) can cause a
regime shift, rendering the historical or implied metric obsolete. A position
sized  for  low  volatility  can  incur  massive  losses  if  volatility  spikes
unexpectedly.
Gap Risk: ATR incorporates gaps in its calculation, but an extreme "black
swan"  gap  (e.g.,  a  5-ATR  move  overnight)  will  violate  the  model's  risk
budget. The Multiplier parameter provides a buffer, but it cannot protect
against tail events.
Liquidity Constraints & Market Impact: The model is blind to market
liquidity. It may calculate a position size of 50,000 shares for a stock that
only trades 100,000 shares per day. Attempting to execute this order would
cause significant slippage and market impact, altering the entry price and
invalidating the risk calculation.
Options-Specific Failures:
Gamma Risk near Expiration: As an option approaches expiration,
its Gamma can become extremely large. The Delta-Gamma
approximation becomes unstable, and small moves in the underlying
can cause massive, unpredictable swings in the option's value (and
risk). The model may severely underestimate risk in the final days of
an option's life.
Vega Risk (Volatility Crush): The model primarily sizes based on
the underlying's price risk (Delta/Gamma). It does not explicitly
budget for Vega risk—the risk of a collapse in Implied Volatility. After
a major event like earnings, IV often plummets, which can cause large
losses on long option positions even if the underlying price moves
favorably.
1. 
2. 
3. 
4. 
◦ 
◦ 

Data Integrity: Option chains can have erroneous IV or Greek values,
especially for illiquid strikes. Sizing based on bad data will lead to
incorrect risk allocation.
4.2 Optimizations and Enhancements
Hybrid  Volatility  Models:  For  equities,  blend  historical  and  implied
volatility. For example, use the maximum of (14-day ATR, 30-day Implied
Volatility converted to a daily dollar value). This makes the model more
responsive to market expectations.
Portfolio-Level  Correlation  Analysis:  This  is  the  most  critical
enhancement. The described model sizes each position in isolation. It
completely  ignores  the  correlation  between  assets.  Holding  two  highly
correlated  positions,  each  sized  for  1%  risk,  does  not result  in  a  2%
portfolio risk; the combined risk is likely closer to 2% on each, for a total of
nearly 4% during an adverse market move. A robust system must use a
covariance matrix to calculate the marginal contribution to risk of a new
position and size it accordingly to maintain a target portfolio volatility.
Dynamic Multiplier: The Multiplier can be dynamic. In high-uncertainty
environments (e.g., VIX > 30), the multiplier could be increased (e.g., from
2.0 to 3.0) to systematically reduce risk across the board.
Liquidity-Aware Sizing: The final position size should be capped as a
percentage of the average daily volume (ADV). For example, final_size =
min(calculated_shares,  0.02  *  ADV).  This  prevents  the  model  from
establishing untenable positions.
Stress Testing: The model's risk assumptions should be regularly stress-
tested  against  historical  crises  (e.g.,  2008,  2020)  to  understand  how  it
would behave under extreme market conditions. This helps in refining the
Multiplier and other risk control parameters.
◦ 
1. 
2. 
3. 
4. 
5. 

