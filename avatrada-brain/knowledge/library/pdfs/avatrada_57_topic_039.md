# SOURCE PDF: avatrada_57_topic_039.pdf

Deep Research: Avatrada 57 Topic 039
Engineering Report: Staleness Guard
for Phantom Fill Prevention
1.0 Executive Summary
This  report  provides  a  detailed  engineering  analysis  of  the  "Phantom  Fill
Prevention"  mechanism,  referred  to  as  the  "Staleness  Guard."  The  system's
primary objective is to mitigate the risk of executing trades at unfavorable, stale
prices by ensuring the execution feed's market data is not significantly older
than the signal-generating feed's data. This is critical in trading systems where a
faster, specialized data feed (e.g., ThetaData) is used for signal generation, while
a  broker's  API  feed  (e.g.,  Interactive  Brokers)  is  used  for  execution.  A  lag
between these two feeds can lead to "phantom fills"—orders filled at prices that
no longer reflect the true market state, resulting in immediate losses.
This analysis deconstructs the core logic, provides a concrete implementation
strategy using Python, and performs a critical analysis of failure modes, edge
cases, and potential optimizations. A key focus is placed on the foundational
requirement  of  robust  time  synchronization  via  the  Network  Time  Protocol
(NTP).
2.0 Technical Deconstruction
The Staleness Guard is a pre-trade risk check designed to abort an order if the
data used for execution is considered "stale" relative to the data that generated
the trading signal.

2.1 System Components
Signal  Feed  (Source  of  Truth): This  is  the  high-speed,  low-latency
market data feed upon which the trading algorithm makes decisions.
Provider: ThetaData
Key Data Point:Signal_Time (T_signal): The timestamp of the
market data event (e.g., a specific quote or trade) that triggered the
trading signal. This should ideally be the exchange-provided
timestamp to minimize ambiguity.
Execution Feed (Source of Action): This is the data feed provided by the
execution venue (the broker). The prices from this feed are what the broker
will honor for an immediate fill.
Provider: Interactive Brokers (IBKR)
Key Data Point:Execution_Feed_Time (T_execution): The timestamp
of the most recent market data update received from the broker's
feed.
The Staleness Guard Logic: This is the core decision-making module that
sits between the signal generation and the order submission modules.
2.2 Core Mechanism & Formula
The  fundamental  principle  is  to  calculate  the  time  delta  (Δt)  between  the
timestamp of the signal-triggering event and the timestamp of the last known
state of the execution venue.
The core formula is:
Δt=T_signal-T_execution
The rejection logic, as specified, is:
1. 
◦ 
◦ 
2. 
◦ 
◦ 
3. 

IF Δt>300millisecondsTHENREJECT_ORDER
ELSEPROCEED_TO_EXECUTION
This logic acts as a gate. It acknowledges that the IBKR feed will almost always
lag  the  ThetaData  feed.  However,  it  places  a  hard  upper  bound  on  this
acceptable lag. A lag exceeding 300ms implies a significant risk that the price
quoted  by  IBKR  is  no  longer  valid,  and  executing  the  trade  could  result  in
substantial slippage or a "phantom fill."
2.3 Architectural Flow
A typical event-driven flow incorporating the Staleness Guard would be:
Data Ingestion: The system concurrently receives data from both
ThetaData and IBKR feeds. The latest quote from IBKR (price and
timestamp) is stored in a state variable.
Signal Generation: A new tick arrives from ThetaData. The trading
algorithm processes it and generates a buy/sell signal. The Signal_Time is
the timestamp of this ThetaData tick.
Staleness Check: Before routing an order, the Staleness Guard is invoked.
It retrieves the Signal_Time from the trigger event.
It retrieves the Execution_Feed_Time from the last stored IBKR quote.
It computes Δt and applies the rejection logic.
Order Routing:
If the check passes, the order is sent to the IBKR execution API.
If the check fails, the signal is discarded, and an alert/log is
generated.
3.0 Implementation Strategy
This section details the practical steps for building the Staleness Guard, focusing
on Python, data handling, and time synchronization.
1. 
2. 
3. 
◦ 
◦ 
◦ 
4. 
◦ 
◦ 

3.1 Data Structures and State Management
Timestamps must be handled with care. Using timezone-aware datetime objects
in Python is highly recommended to prevent ambiguity. The source timestamps
from the feeds should be parsed into UTC.
We need a simple stateful object to hold the latest quote from the execution feed.
importdatetime
fromdataclassesimportdataclass
# Use timezone-aware UTC for all timestamps
UTC=datetime.timezone.utc
@dataclass
classMarketQuote:
"""Represents a single market data update from any feed."""
symbol:str
bid:float
ask:float
timestamp:datetime.datetime
classExecutionFeedState:
"""Manages the last known state of the execution feed."""
def__init__(self):
self.last_quote:MarketQuote=None
defupdate(self,new_quote:MarketQuote):
# This method is called by the IBKR feed handler
self.last_quote=new_quote
defget_last_timestamp(self)->datetime.datetime:
ifself.last_quote:
returnself.last_quote.timestamp
# Return a very old timestamp if no data has been received yet
# to ensure the first check fails safely.
returndatetime.datetime.fromtimestamp(0,tz=UTC)

3.2 Staleness Guard Logic
The core logic can be encapsulated in a single function or class method.
classStalenessGuard:
"""Implements the staleness check logic."""
def__init__(self,max_latency_ms:int=300):
self.max_latency=datetime.timedelta(milliseconds=max_latency_ms)
defis_stale(self,signal_time:datetime.datetime,execution_feed_time:
datetime.datetime)->bool:
"""
        Checks if the execution feed is stale relative to the signal time.
        Args:
            signal_time: The timestamp of the event that triggered the signal 
(from ThetaData).
            execution_feed_time: The timestamp of the last known quote from the 
execution feed (IBKR).
        Returns:
            True if stale (reject), False if acceptable (proceed).
        """
# Ensure both timestamps are timezone-aware for correct subtraction
ifsignal_time.tzinfoisNoneorexecution_feed_time.tzinfoisNone:
# Or raise a more specific error
print("ERROR: Timestamps must be timezone-aware.")
returnTrue# Fail safe
latency=signal_time-execution_feed_time
iflatency>self.max_latency:
print(f"REJECT: Staleness detected. Latency: 
{latency.total_seconds()*1000:.2f}ms")
returnTrue
returnFalse
# --- Example Usage in a trading loop ---

# Initialize components
ibkr_state=ExecutionFeedState()
staleness_guard=StalenessGuard(max_latency_ms=300)
defon_theotadata_tick(signal_quote:MarketQuote):
# 1. Signal logic runs and decides to place an order
#    ... signal_is_generated = True ...
ifsignal_is_generated:
# 2. Perform the staleness check
last_ibkr_time=ibkr_state.get_last_timestamp()
ifstaleness_guard.is_stale(signal_quote.timestamp,last_ibkr_time):
# 3a. Logic for rejection
return# Abort order
else:
# 3b. Logic for proceeding
# place_order(...)
pass
defon_ibkr_tick(ibkr_quote:MarketQuote):
# This callback updates the state whenever a new IBKR quote arrives
ibkr_state.update(ibkr_quote)
3.3 Time Synchronization (NTP)
Accurate  and  synchronized  clocks  are  non-negotiable for  this  system  to
function correctly. If the local machine's clock is skewed relative to the feed
servers, the  Δt calculation will be meaningless, representing clock skew, not
feed latency.
The  goal  is  to  synchronize  the  local  machine's  clock  to  a  reliable,
external time source.
Method: System-Level NTP Daemon (Recommended)
This is the most robust and standard approach. Do not attempt to implement
NTP logic within the application itself for synchronization purposes. Rely on the
operating system's battle-tested services.

For Linux (e.g., Ubuntu/Debian with chrony):
Install  chrony: It's  a  modern,  high-performance  NTP  implementation.
bash sudo apt-get update sudo apt-get install chrony
Configure Servers: Edit /etc/chrony/chrony.conf. Use a pool of reliable,
low-latency  servers.  Google's  or  NIST's  public  servers  are  excellent
choices. For financial applications, if the exchange or broker provides an
NTP server, it should be prioritized. ```conf # /etc/chrony/chrony.conf #
Use servers from the pool.ntp.org project. pool pool.ntp.org iburst
Add Google's public NTP servers for
redundancy
server time1.google.com iburst server time2.google.com iburst
Allow the system clock to be stepped
in the first three updates
if its offset is larger than 1 second.
makestep 1.0 3 ```
Enable and Verify: ```bash sudo systemctl restart chrony sudo systemctl
enable chrony
Check synchronization status
chronyc tracking
1. 
2. 
3. 

Look for 'System time' to be within a
few milliseconds of 'Reference time'.
Check sources and their offsets
chronyc sources -v
The '*' indicates the currently synced
source. The offset should be very
small (ms or µs).
```
For Windows:
The built-in w32time service can be configured for higher accuracy.
Configure via Command Prompt (as Administrator): ```cmd REM Set
reliable  NTP  peers  w32tm  /config  /manualpeerlist:"time.google.com,0x8
time.nist.gov,0x8" /syncfromflags:MANUAL /reliable:yes /update
REM Restart the service net stop w32time net start w32time
REM Force a resync and check status w32tm /resync /rediscover w32tm /
query /status
Look for the 'Source' and 'Last
Successful Sync Time'.
```
1. 

4.0 Critical Analysis
4.1 Potential Failure Modes
NTP Service Failure / Clock Drift: If the NTP daemon fails or cannot
reach  its  servers,  the  local  clock  will  begin  to  drift.  This  completely
invalidates the staleness check. A small drift could silently corrupt the
logic, while a large drift could render the system inoperable.
Mitigation: Implement a separate monitoring process that
periodically runs chronyc tracking or w32tm /query /status, parses
the output, and raises a critical alert if the clock offset exceeds a
predefined threshold (e.g., > 10ms). Halt all trading if the clock is not
synchronized.
Execution  Feed  Disconnection: If  the  IBKR  feed  disconnects,  the
ExecutionFeedState will  hold  a  progressively  older  last_quote.  The
Execution_Feed_Time will become increasingly stale, causing the guard to
(correctly) reject every single new signal.
Analysis: This is a "fail-safe" behavior, which is desirable. However,
the system should be able to distinguish this from normal high-latency
conditions.
Mitigation: Implement a "heartbeat" or "liveness" check on the IBKR
connection itself. If no new quote has been received from IBKR for a
longer threshold (e.g., > 1 second), declare the execution feed as
"Disconnected" and halt trading, providing a more specific reason
than "stale."
Inconsistent  Timestamp  Sources: The  entire  premise  relies  on
comparing two timestamps. If one feed provides the exchange timestamp
(when the event occurred on the matching engine) and the other provides
an ingestion timestamp (when the provider's server received the event),
you are not comparing apples to apples.
Mitigation: Perform rigorous due diligence on the documentation for
both data feeds. Understand precisely what each timestamp
represents. If possible, normalize both to use exchange-generated
1. 
◦ 
2. 
◦ 
◦ 
3. 
◦ 

timestamps. If not, document the inherent discrepancy and factor it
into the latency threshold.
4.2 Edge Cases
Market Open/Close: During the first and last minutes of trading, feeds
can be erratic, and latency can spike. The fixed 300ms threshold may be
too aggressive, leading to missed opening opportunities.
Consideration: Potentially relax the threshold for the first minute of
trading or implement a dynamic threshold.
High-Volatility Events (News, Fed Announcements): During extreme
volatility,  the  latency  between  feeds  can  naturally  exceed  300ms.  The
Staleness  Guard  will  correctly  reject  trades,  acting  as  a  crucial  safety
brake. This is the intended behavior and a feature, not a bug.
4.3 Optimizations and Enhancements
Dynamic Latency Threshold: A fixed 300ms is a good starting point, but
a more advanced system could use a dynamic threshold. This could be a
function of a market volatility indicator (e.g., VIX, ATR).
Logic:threshold_ms = baseline_ms + (volatility_factor *
volatility_index)
Benefit: Allows the system to be more aggressive in calm markets
(e.g., 150ms threshold) while being more cautious in volatile markets
(e.g., 450ms threshold).
Latency  Monitoring  and  Analytics: Do  not  just  discard  the  latency
information on rejected trades. Log the calculated  Δt for  every signal,
both accepted and rejected.
Benefit: This creates a valuable time-series dataset of the
performance and latency characteristics of your data feeds. It can be
used to:
Validate or refine the 300ms threshold.
Detect degradation in feed performance over time.
1. 
◦ 
2. 
1. 
◦ 
◦ 
2. 
◦ 
▪ 
▪ 

Provide evidence when disputing issues with feed providers.
Precision Time Protocol (PTP): For institutional-grade, ultra-low-latency
systems co-located in data centers, NTP is often replaced by PTP (IEEE
1588).  PTP  offers  significantly  higher  synchronization  accuracy  (sub-
microsecond) by using hardware-level timestamping on network interface
cards (NICs) and switches. This is likely overkill for the specified context
but represents the next level of time-synchronization rigor.
▪ 
3. 

