# SOURCE PDF: avatrada_57_topic_012.pdf

Deep Research: Avatrada 57 Topic 012
Engineering Report: IBKR Server-Side
Bracket Order Construction
Report  ID: EDR-2023-IBKR-721  Author: Autonomous  Technical  Researcher
Date: October  26,  2023  Subject: Deep-Dive  Analysis  of  Atomic  Server-Side
Bracket Order Construction via the Interactive Brokers API
Executive Summary: This report provides a detailed engineering analysis of the
Interactive Brokers (IBKR) API mechanism for constructing server-side bracket
orders. The core challenge addressed is the mitigation of "leg-in risk," where a
primary entry order is filled before its protective stop-loss and take-profit orders
are  successfully  submitted  to  the  exchange.  The  analysis  confirms  that  the
combination of the  transmit=False flag and  parent_id linking is the correct
and robust methodology for creating an atomic order group. This ensures that
the parent order and its child protective orders are sent to the IBKR servers and
subsequently  to  the  exchange  as  a  single,  indivisible  unit.  This  document
deconstructs  the  mechanism,  provides  a  production-ready  implementation
strategy using the ib_insync Python library, and performs a critical analysis of
potential failure modes and edge cases.
1. Technical Deconstruction
The construction of a server-side atomic bracket order on the IBKR platform is
not a single API call but a sequential assembly of individual orders that are
logically linked on the IBKR server before transmission to the exchange. The
system relies on three key components:
1.1.  The  transmit Flag: This  boolean  flag  on  the  Order object  is  the
cornerstone of the entire process. * transmit=False: When an order is sent to
the TWS or IB Gateway with this flag, the server accepts and validates the order

but does not transmit it to the exchange. It is held server-side, awaiting further
instructions.  This  creates  a  staging  area  for  complex  order  strategies.  *
transmit=True: This is the default behavior. When an order with this flag is
received, the server validates it and immediately transmits it to the exchange. In
our bracket context, this flag is set only on the final order of the group, acting as
the trigger to send the entire linked package.
1.2.  The  parentId Attribute: This  integer  attribute  creates  a  hierarchical
relationship between orders. * Parent Order: The initial entry order is created
with a unique  orderId. *  Child Orders: The subsequent Stop Loss and Take
Profit orders are created with their own unique orderIds, but they must also set
their parentId attribute to the orderId of the parent order. This explicitly tells
the IBKR server that these orders are dependent on the parent.
1.3. Server-Side OCA (One-Cancels-All) Group: When  two  or  more  child
orders are linked to the same  parentId, the IBKR server automatically places
them into a One-Cancels-All (OCA) group. This server-side logic dictates that: *
The child orders (Stop Loss, Take Profit) only become active after the parent
order has been filled. * If one of the child orders executes (e.g., the Stop Loss is
triggered), the server will automatically cancel the other sibling order (the Take
Profit). * This behavior is managed entirely on IBKR's servers, making it robust
against client-side disconnects or application failures after the bracket has been
successfully submitted.
1.4. The Atomic Submission Sequence: The combination of these components
enables an atomic submission, which can be visualized as follows:
Client -> IB Server: placeOrder(Parent_LMT, transmit=False)
Server State: Parent order is received and held. It is not live on the
exchange.
Client -> IB Server: placeOrder(Child_STP, parentId=Parent.orderId,
transmit=False)
Server State: Stop Loss order is received, validated, linked to the held
parent, and also held.
1. 
◦ 
2. 
◦ 

Client -> IB Server: placeOrder(Child_LMT, parentId=Parent.orderId,
transmit=True)
Server State: Take Profit order is received and linked. The 
transmit=True flag signals the end of the group. The server now
validates the entire bracket (Parent + Children) as a single logical
unit.
IB Server -> Exchange: If the entire bracket is valid, the server transmits
the Parent order to the exchange. The child orders remain held on the IB
server, awaiting the parent's execution.
This sequence guarantees that the parent order is never live on the market
without its protective children being successfully registered and linked on the
IBKR server, thus eliminating leg-in risk.
2. Implementation Strategy
This section provides a robust, commented code example using the ib_insync
library, which offers a high-level, synchronous interface that simplifies the logic.
The principles are identical for the lower-level ibapi.
Prerequisites: *  Python  3.7+  *  ib_insync library  installed  (pip install
ib_insync) * IB TWS or Gateway running and API connections enabled.
Python Code Example: ib_insync
importasyncio
fromib_insyncimportIB,Stock,LimitOrder,StopOrder
asyncdefplace_bracket_order(
ib_client:IB,
symbol:str,
quantity:float,
limit_price:float,
take_profit_price:float,
stop_loss_price:float
):
"""
3. 
◦ 
4. 

    Constructs and places a server-side atomic bracket order.
    Args:
        ib_client: An active and connected ib_insync.IB instance.
        symbol: The stock ticker (e.g., 'AAPL').
        quantity: The number of shares to trade.
        limit_price: The limit price for the parent entry order.
        take_profit_price: The limit price for the profit taker order.
        stop_loss_price: The stop price for the stop loss order.
    """
# 1. Define the contract for the asset
contract=Stock(symbol,'SMART','USD')
awaitib_client.qualifyContractsAsync(contract)
# 2. Determine the action (BUY or SELL) based on price relationship
# This is a simple example; real logic may vary.
# Assuming a BUY order if current price is above limit_price.
# For this example, we will hardcode a BUY order.
parent_action='BUY'
child_action='SELL'
# 3. Request the next valid order ID from TWS/Gateway for the parent
parent_order_id=ib_client.reqIds(-1)
print(f"Obtained Parent Order ID: {parent_order_id}")
# 4. Create the Parent Order (LMT Entry)
# This order is held on the IB server and not sent to the exchange yet.
parent_order=LimitOrder(
action=parent_action,
totalQuantity=quantity,
lmtPrice=limit_price,
orderId=parent_order_id,
transmit=False# CRUCIAL: Do not transmit yet
)
print("Step 1: Created Parent LMT Order (transmit=False)")
# 5. Create the Take Profit Order (LMT Exit)
# This child order is linked to the parent via parentId.
# It is also held on the server.
take_profit_order=LimitOrder(

action=child_action,
totalQuantity=quantity,
lmtPrice=take_profit_price,
orderId=parent_order_id+1,# Child orders need their own unique IDs
parentId=parent_order_id,
transmit=False# CRUCIAL: Do not transmit yet
)
print("Step 2: Created Child Take Profit LMT Order (transmit=False)")
# 6. Create the Stop Loss Order (STP Exit)
# This is the final order in the bracket. Its transmit=True flag
# will trigger the atomic submission of the entire group.
stop_loss_order=StopOrder(
action=child_action,
totalQuantity=quantity,
stopPrice=stop_loss_price,
orderId=parent_order_id+2,
parentId=parent_order_id,
transmit=True# CRUCIAL: Transmit the whole bracket now
)
print("Step 3: Created Child Stop Loss STP Order (transmit=True)")
# 7. Place all orders in sequence
# The order of placement matters for clarity, but the linking is what 
counts.
print("\nPlacing orders...")
ib_client.placeOrder(contract,parent_order)
ib_client.placeOrder(contract,take_profit_order)
ib_client.placeOrder(contract,stop_loss_order)
print("Bracket order submitted as an atomic group.")
asyncdefmain():
ib=IB()
try:
# Connect to TWS/Gateway
awaitib.connectAsync('127.0.0.1',7497,clientId=10)
# --- Example Usage ---
awaitplace_bracket_order(

ib_client=ib,
symbol='TSLA',
quantity=1,
limit_price=170.00, # Price to buy at
take_profit_price=180.00,# Price to sell for profit
stop_loss_price=165.00 # Price to sell for loss
)
# Give some time for orders to appear in TWS
awaitasyncio.sleep(5)
print("\nOpen Orders:")
print(ib.openOrders())
exceptExceptionase:
print(f"An error occurred: {e}")
finally:
print("\nDisconnecting...")
ib.disconnect()
if__name__=="__main__":
asyncio.run(main())
3. Critical Analysis
While this methodology is robust, a comprehensive engineering assessment must
consider its limitations, failure modes, and edge cases.
3.1. Potential Failure Modes
Client-Side Disconnection During Submission: If the client application
disconnects from the TWS/Gateway after sending the first or second order
(transmit=False) but before sending the final order (transmit=True), the
partial orders will be orphaned on the IB server. They will not be sent to the
exchange.
Mitigation: The application's startup/reconnect logic must include a
routine to query for all open orders (ib.reqOpenOrders()) and cancel
• 
◦ 

any non-transmitted, orphaned parent or child orders before
attempting to submit new ones.
Group Order Rejection: If any part of the bracket order is invalid (e.g.,
stop price is through the market for a BUY stop, insufficient margin, invalid
quantity), the entire group will be rejected by the IB server when the final
transmit=True order is processed.
Mitigation: The application must have robust error handling logic
that listens for API error messages (specifically codes related to order
rejection). Upon rejection, the application should log the error and not
assume any part of the order was placed.
3.2. Edge Cases
Partial Fills of the Parent Order: This is a key strength of the server-side
approach. If the parent order is partially filled (e.g., 50 out of 100 shares),
the  IBKR  server  automatically  scales  the  child  orders  to  match  the
executed quantity. The Stop Loss and Take Profit will become active for the
50 filled shares. This behavior is difficult and unreliable to replicate with a
client-side solution.
Cancelling the Bracket: To cancel the entire bracket before the parent
order executes, the client only needs to send a cancellation request for the
parent_id. The IBKR server will automatically cancel the parent and all its
dependent children. This simplifies cancellation logic significantly.
Market Gaps: The construction of the bracket does not protect against
market  risk.  If  the  market  gaps  through  the  stopPrice,  the  resulting
market order will be filled at the next available price, which can result in
significant slippage. For more price protection, a StopLimit order could be
used instead of a  StopOrder, but this introduces the risk that the order
may not fill at all if the market continues to move away.
3.3. Optimizations and Best Practices
Order ID Management: The example uses a simple parent_order_id + 1
and + 2 scheme. In a high-throughput, multi-threaded environment, it is
• 
◦ 
• 
• 
• 
• 

critical to have a robust, centralized, and persistent order ID generator to
prevent collisions. Requesting a block of IDs from IBKR is a viable strategy.
Explicit OCA Grouping: While parentId implicitly creates an OCA group
for the children, one can also explicitly set the ocaGroup (a unique string)
and ocaType attributes on the child orders. For a standard bracket, this is
redundant, but it can be useful for more complex strategies where multiple
orders need to be linked without a direct parent-child relationship.
ibapi vs. ib_insync: The logic presented here is universal. In the native
ibapi,  the  implementation  would  be  more  verbose,  requiring  the
developer to manage the EClientSocket and EWrapper callbacks. However,
the  sequence  of  creating  Order objects  with  the  correct  orderId, 
parentId, and  transmit flags and calling  placeOrder remains identical.
ib_insync is recommended for its superior readability and error handling
for this task.
• 
• 

