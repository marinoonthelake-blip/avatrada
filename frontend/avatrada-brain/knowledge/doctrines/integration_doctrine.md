# SOURCE PDF: System Integration Doctrine_ ThetaData & IBKR Gateway.pdf

System  Integration  Doctrine:  ThetaData  
&
 
IBKR
 
Gateway
 
Status:  Definitve  /  Post-Trial  Version:  2026.1  Architecture:  Topo-Grid  (Hybrid  Cloud)  
1.  Topo-Grid  Architecture  
The  system  operates  on  a  hybrid  cloud  node  model  designed  for  maximum  bandwidth  
efficiency
 
and
 
security.
 ●  The  Cloud  Node  ("The  Bunker"):  Handles  high-bandwidth  decompression  (ThetaData)  
and
 
state
 
management.
 ●  The  Local  Client  ("The  Cockpit"):  Handles  complex  visualization  and  command  
injection.
 ●  Transport  Layer:  Tailscale  (WireGuard)  provides  the  secure  mesh  between  the  node  and  
client.
 
2.  Interactive  Brokers  (IBKR)  Integration  
Primary  Role:  Execution  Engine  &  Account  Telemetry.  
A.  Docker  Infrastructure  
●  Container  Image:  ghcr.io/gnzsnz/ib-gateway:latest  ●  Network  Config:  ○  Port  4002:  Internal  Standard  Port.  ○  Port  4004:  Relay  Port  (Socat)  —  Required  for  external/container-to-container  
access.
 ●  Critical  Environment  Variables:  ○  TRADING_MODE=paper  (Hard-gate  for  staging  environments).  ○  READ_ONLY_API=no  (Mandatory  for  Order  Entry  permissions).  
B.  Python  Library  &  Concurrency  
●  Library:  ib_async  (Community  fork  of  ib_insync).  ●  The  Concurrency  Conflict:  FastAPI  uses  uvloop  or  standard  asyncio.  ib_async  attempts  
to
 
manage
 
its
 
own
 
loop,
 
leading
 
to
 
RuntimeError:
 
this
 
event
 
loop
 
is
 
already
 
running.
 ●  The  Fix:  1.  Code  Injection:  Apply  nest_asyncio  immediately  upon  app  startup. import  nest_asyncio  
nest_asyncio.apply()
 
 

2.  Uvicorn  Arguments:  Force  the  loop  strategy. uvicorn  main:app  --loop  asyncio  
 
C.  Method  Signatures  (2026  Standards)  
The  ib_async  library  is  strictly  positional/keyword  sensitive.  ●  Streaming  Data:  ○  ib.reqAccountUpdates(subscribe=True,  acctCode=account_id)  ●  Snapshot  Data  (Reliability  Protocol):  ○  Avoid  callback  bindings  for  snapshots.  Use  the  async  getter  to  ensure  data  integrity  
before
 
proceeding.
 ○  Syntax:  summary  =  await  ib.accountSummaryAsync()  
3.  ThetaData  Pro  Integration  
Primary  Role:  Total  Market  Omniscience  (Options/Indices).  
A.  The  Middleware  (Theta  Terminal)  
ThetaData  is  a  Decompression  Middleware,  not  a  standard  REST  API.  ●  JVM  Tuning:  Critical  to  prevent  Garbage  Collection  pauses  from  dropping  ticks.  ○  Flags:  -Xms4G  -Xmx8G  -XX:+UseZGC  ●  Port  Allocation:  ○  25503:  High-Bandwidth  Binary  Cluster  Port.  ○  25510:  Client  Gateway  Port  (REST/WebSocket).  
B.  V3  API  Standards  
●  Deprecation  Warning:  V2  paths  are  deprecated.  Unified  V3  endpoints  are  mandatory.  ●  Protocol:  Headers  must  be  set  to  Accept:  application/x-ndjson.  ●  Payload  parsing:  Returns  Newline  Delimited  JSON .  Do  not  parse  as  a  single  JSON  
blob;
 
parse
 
line-by-line.
 ●  Endpoint  Variance:  ○  Single:  /v3/snapshot/stock/quote?root=SPY  ○  Bulk:  /v2/bulk_snapshot/stock/quote?roots=SPY,QQQ,NVDA  ○  Note:  Observe  the  plural  roots  parameter  in  bulk  requests.  
4.  The  Data  Bridge  (Client-Side)  
Primary  Role:  Off-main-thread  processing  and  UI  synchronization.  
A.  SharedWorker  Implementation  
●  File:  scout.worker.ts  ●  Logic:  All  WebSocket  ingestion  occurs  here.  This  acts  as  a  singleton  network  agent,  

ensuring  Monitors  1,  2,  and  3  remain  perfectly  synced  without  tripling  the  network  load.  
B.  UI  Throttling  
●  Constraint:  60Hz  (16ms)  Rendering  Cap.  ●  Pattern:  Buffer-Flush.  Data  is  buffered  in  the  worker  and  flushed  to  the  React  Context  
state
RUN curl -L -o ThetaTerminal.jar https://download-unstable.thetadata.us/ThetaTerminalv3.jar 
at
 
fixed
 
intervals
 
to
 
prevent
 
React
 
DOM
 
thrashing
 
during
 
high-volatility
 
events.
 
5.  Recovery  Protocols  &  Troubleshooting  The  "403  Forbidden"  
●  Cause:  Client  attempting  WebSocket  connection  with  invalid  origin  headers.  ●  Fix:  Ensure  CORS  is  set  to  ["*"]  on  the  VM  hosting  the  API  for  Tailscale  subnets.  
The  "White  Screen"  
●  Cause:  React  Context  failure,  typically  circular  dependencies  between  account-context  
and
 
market-context.
 ●  Fix:  Decouple  context  providers  or  use  a  single  global  store.  
The  "Zero  Overwrite"  
●  Cause:  IBKR  sends  multiple  NetLiquidation  tags  (P,  S,  and  Total).  ●  Fix:  Implement  strict  string  matching:  if  (tag  ==  'NetLiquidation').  This  prevents  partial  
partition
 
values
 
from
 
momentarily
 
zeroing
 
out
 
the
 
dashboard
 
total.
 
6.  Master  Integration  Summary  
Integration  Library  Port  Protocol  Logic  
IBKR  ib_async  4004  Proprietary/Socket  
accountSummaryAsync()  
ThetaData  httpx  25503  NDJSON  /v2/bulk_snapshot?roots=  
Frontend  Vite/React  5173  WebSocket  STREAM_UPDATE  payload  
7.  Immediate  Next  Steps  
1.  GEX  Calculation  Engine:  Implement  GEX  =  Gamma  *  OI  *  100  in  a  ProcessPoolExecutor  
to
 
offload
 
math
 
from
 
the
 
data
 
stream.
 2.  Order  Execution:  Convert  UI  "Submit"  logs  into  live  ib.placeOrder()  calls  using  

Server-Side  Brackets.  

