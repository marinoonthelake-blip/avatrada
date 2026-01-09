# SOURCE PDF: avatrada_57_topic_014.pdf

Deep Research: Avatrada 57 Topic 014
Engineering Report: Orphaned Position
Monitor State Machine
1. Executive Summary
This report provides a detailed engineering analysis of the "Orphaned Position
Monitor," a critical safety component within an automated trading system. The
system's primary function is to prevent "naked" or "orphaned" positions, which
occur when an entry order (Parent) is successfully filled, but its corresponding
protective  stop-loss  order  (Child)  is  rejected  by  the  exchange.  This  failure
scenario exposes the trading account to potentially unlimited risk.
The proposed solution is a state machine that subscribes to the system's event
stream,  specifically  monitoring  order  status  updates  and  error  codes.  Upon
detecting the specific sequence of a parent fill followed by a child rejection
(error code 201), the state machine transitions to a critical state and executes an
immediate "Panic Close" by submitting a market order to neutralize the newly
opened, unprotected position.
This analysis deconstructs the state machine's architecture, proposes a robust
implementation  strategy  using  event-driven  patterns,  and  performs  a  critical
analysis of potential failure modes, edge cases, and necessary enhancements for
a production-grade system.
2. Technical Deconstruction
The Orphaned Position Monitor is fundamentally an event-driven, finite state
machine (FSM). Its purpose is to track the lifecycle of a paired parent-child
order strategy and intervene decisively upon failure.

2.1. Core Components
State: The current condition of the monitored position (e.g., 
AWAITING_FILL, CRITICAL_ORPHAN).
Events: Incoming data points that trigger state transitions (e.g., 
ParentOrderFilled, ChildOrderRejected).
Transitions: The rules that define how the machine moves from one state
to another based on a specific event.
Actions: The operations executed upon entering or exiting a state (e.g., 
SubmitMarketCloseOrder).
2.2. State Machine Diagram & Logic
The state machine manages the lifecycle of a single parent-child order pair. A
new instance of this machine is created or activated for each new pair.
States:
IDLE: The default state. No active position is being monitored.
AWAITING_PARENT_FILL: A parent-child order pair has been submitted. The
machine is now actively listening for the parent order's fill confirmation.
AWAITING_CHILD_CONFIRMATION: The parent order has been filled. The
system is now in a temporary high-risk state, waiting for confirmation that
the child stop order has been accepted by the exchange.
POSITION_PROTECTED: The child stop order has been successfully accepted.
The position is no longer an orphan risk. The monitor's job for this position
is complete.
CRITICAL_ORPHAN: The critical failure state. The parent filled, but the child
stop was rejected.
CLOSING_POSITION: An action state. The machine has submitted the panic
market close order and is awaiting its fill confirmation.
Events (Inputs):
StrategySubmitted(parent_id, child_id, symbol, quantity, side)
OrderStatusUpdate(order_id, status)
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 

OrderError(order_id, error_code, message)
Actions (Outputs):
SubmitMarketCloseOrder(symbol, quantity, side)
LogCriticalAlert(message)
NotifyOperator(details)
2.3. State Transition Table
Current State Event Condition Next State Action
IDLE StrategySubmitted- AWAITING_PARENT_FILL Store position details.
AWAITING_PARENT_FILL OrderStatusUpdate
order_id ==
parent_id
AND 
status ==
Filled
AWAITING_CHILD_CONFIRMATIONLog parent fill.
AWAITING_CHILD_CONFIRMATIONOrderStatusUpdate
order_id ==
child_id AND 
status ==
Accepted
POSITION_PROTECTED Log success, end
monitoring.
AWAITING_CHILD_CONFIRMATIONOrderError
order_id ==
child_id AND
error_code ==
201
CRITICAL_ORPHAN Log CRITICAL,
trigger Panic Close.
CRITICAL_ORPHAN (Entry Action) - CLOSING_POSITION SubmitMarketCloseOrder
CLOSING_POSITION OrderStatusUpdate
order_id ==
close_order_id
AND 
status ==
Filled
IDLE Log successful close,
notify operator.
AWAITING_CHILD_CONFIRMATIONTimeout No child status
after X secondsCRITICAL_ORPHAN Log timeout, trigger
Panic Close.
• 
• 
• 
• 

3. Implementation Strategy
A  robust  implementation  should  be  decoupled  from  the  core  trading  logic,
operating as an independent, resilient service. An event-driven architecture is
the ideal pattern.
3.1. Architectural Pattern
Event Bus: The trading system should publish all order status and error
events to a central message bus (e.g., RabbitMQ, Kafka, Redis Pub/Sub).
Monitor Service: The Orphan Monitor will be a dedicated service that
subscribes to this event stream.
State Persistence: The state of each monitored position must be persisted
to a fast key-value store (e.g., Redis). This ensures the system can recover
from a crash without losing track of positions in the critical 
AWAITING_CHILD_CONFIRMATION state.
Order Execution Interface: The monitor must have a secure interface to
the order execution gateway to submit the market close order.
3.2. State Machine Library
Instead  of  implementing  the  FSM  logic  from  scratch  with  complex  if/else
blocks, use a dedicated library to ensure correctness and maintainability.
Python:transitions or pytransitions
JavaScript/TypeScript:XState
Java/C#:Stateless
These libraries formalize state definitions, transitions, and callbacks, reducing
the risk of bugs.
3.3. Pseudocode Implementation
Here is a Python-like pseudocode demonstrating the core logic.
1. 
2. 
3. 
4. 
• 
• 
• 

# Using the 'transitions' library for clarity
fromtransitionsimportMachine
# Data store for state persistence (e.g., a Redis-backed dictionary)
# key: parent_order_id, value: PositionMonitor instance
active_monitors={}
classPositionMonitor:
def__init__(self,parent_id,child_id,symbol,quantity,side):
self.parent_id=parent_id
self.child_id=child_id
self.symbol=symbol
self.quantity=quantity
self.side=side# 'BUY' or 'SELL'
self.close_order_id=None
states=['awaiting_parent_fill','awaiting_child_confirmation',
'position_protected','critical_orphan','closing_position']
# Define transitions
transitions=[
{'trigger':'parent_filled','source':'awaiting_parent_fill',
'dest':'awaiting_child_confirmation'},
{'trigger':'child_accepted','source':
'awaiting_child_confirmation','dest':'position_protected'},
{'trigger':'child_rejected','source':
'awaiting_child_confirmation','dest':'critical_orphan','before':
'on_enter_critical_orphan'},
{'trigger':'close_order_filled','source':'closing_position',
'dest':'position_protected'}# Or a final 'closed' state
]
self.machine=Machine(model=self,states=states,
transitions=transitions,initial='awaiting_parent_fill')
defon_enter_critical_orphan(self):
""" ACTION: This is the core panic logic. """
print(f"CRITICAL: Position {self.symbol}{self.quantity} is ORPHANED. 
Parent {self.parent_id} filled, Child {self.child_id} rejected.")

# Determine the closing side
close_side='SELL'ifself.side=='BUY'else'BUY'
print(f"ACTION: Submitting MARKET {close_side} order for 
{self.quantity}{self.symbol}.")
# This function call interacts with the trading gateway
self.close_order_id=trading_gateway.submit_market_order(
symbol=self.symbol,
quantity=self.quantity,
side=close_side
)
# Transition to wait for the close confirmation
self.to_closing_position()
# --- Event Listener Logic ---
defon_event_received(event):
# Example event: {'type': 'OrderStatusUpdate', 'order_id': 123, 'status': 
'Filled'}
# Example event: {'type': 'OrderError', 'order_id': 124, 'error_code': 201}
# Find the relevant monitor instance
monitor=find_monitor_by_order_id(event['order_id'])
ifnotmonitor:
return
# Trigger state transitions based on the event
ifevent['type']=='OrderStatusUpdate'andevent['status']=='Filled':
ifevent['order_id']==monitor.parent_id:
monitor.parent_filled()
elifevent['order_id']==monitor.close_order_id:
monitor.close_order_filled()
# Clean up the completed monitor
delactive_monitors[monitor.parent_id]
elifevent['type']=='OrderStatusUpdate'andevent['status']=='Accepted':
ifevent['order_id']==monitor.child_id:
monitor.child_accepted()
# Clean up the completed monitor

delactive_monitors[monitor.parent_id]
elifevent['type']=='OrderError'andevent['error_code']==201:
ifevent['order_id']==monitor.child_id:
monitor.child_rejected()
# Persist the new state of the monitor
save_monitor_state(monitor)
4. Critical Analysis & Enhancements
While the core design is sound, a production system must account for numerous
failure modes and edge cases.
4.1. Potential Failure Modes
Panic Close Rejection: The market close order itself could be rejected
(e.g., market halted, insufficient margin after slippage).
Mitigation: The system must transition to a permanent failure state
like PANIC_FAILED. This state must trigger the most urgent alerts
possible (e.g., PagerDuty, SMS) for immediate manual intervention by
a human trader.
System Crash / Restart: If the monitor service crashes, it must be able to
recover its state.
Mitigation: As mentioned, state must be persisted in a durable store
like Redis or a database. On restart, the service must re-hydrate all
active state machines and reconcile their state with the exchange's
view of open orders and positions.
Connectivity Loss: The monitor could lose connection to the event stream
or the execution gateway.
Mitigation: Implement a "heartbeat" or "watchdog" timer. If no child
order status is received within a configurable timeout (e.g., 5 seconds)
after a parent fill, the machine should proactively transition to 
1. 
◦ 
2. 
◦ 
3. 
◦ 

CRITICAL_ORPHAN and attempt to close. This assumes no news is bad
news.
Race Conditions / Event Ordering: An  event-driven  system  does  not
guarantee event order. The child rejection event could theoretically arrive
before the parent fill event.
Mitigation: The state machine logic must be idempotent and robust
to ordering. If a rejection for a known child order arrives, its state can
be flagged. When the parent fill event eventually arrives, the system
can immediately see the pre-existing rejection and transition directly
to CRITICAL_ORPHAN.
4.2. Edge Cases
Partial Fills: The specification mentions "fills," but parent orders can be
filled partially over time.
Analysis: The monitor should trigger on the first partial fill. Any filled
quantity without a corresponding accepted stop is an orphan. The
panic close logic must then close only the quantity that was filled. The
state machine must be ableto handle subsequent fills and potential
subsequent rejections.
Non-atomic Order Submission: The entire concept relies on a parent and
child being linked. If the API calls to submit the parent and then the child
are not atomic, the system could crash after the parent is sent but before
the child is sent.
Analysis: This is a system-level design concern. The best solution is to
use exchange-native bracket orders (e.g., Order-Sends-Order or OSO)
if available. If not, the order submission logic must be wrapped in a
persistent transaction that can be resumed upon restart.
4.3. Recommended Enhancements
Configurable Error Codes: The system is hardcoded to listen for 201.
This should be a configurable list, as different exchanges or brokers may
4. 
◦ 
1. 
◦ 
2. 
◦ 
1. 

use different codes for similar rejection reasons (e.g., 202 as mentioned in
the source).
Idempotency Key: When submitting the panic close order, use a unique
idempotency key. If the monitor crashes and restarts, it might try to submit
the close order again. This key prevents duplicate orders from being
executed.
Comprehensive Logging and Metrics: Every state transition, action, and
error must be logged with structured data (e.g., JSON). Key metrics like 
orphans_detected, panic_closes_executed, and panic_closes_failed
should be exported to a monitoring dashboard (e.g., Grafana, Datadog).
Reconciliation Loop: In addition to listening to real-time events, a
separate process should run periodically (e.g., every minute) to query all
open positions and all active stop orders from the exchange. It should
compare this list against the monitor's internal state to catch any
discrepancies that were missed due to event loss or system downtime.
2. 
3. 
4. 

