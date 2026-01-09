# SOURCE: dockerize.pdf

Architecting  High-Performance  
Quantitative

Dockerfile

# Option 1: Install specifically from the development branch zip (Recommended for this repo)
RUN pip install --no-cache-dir https://github.com/twopirllc/pandas-ta/archive/refs/heads/development.zip
Alternatively, you can install using the git+ syntax, which often handles branch resolution better:

Dockerfile

# Option 2: Install via git (Requires git to be installed in the container)
RUN pip install --no-cache-dir git+https://github.com/twopirllc/pandas-ta.git@development


 
Trading
 
Infrastructure:
 
A
 
Comprehensive
 
Guide
 
to
 
Containerizing
 
Python
 
3.10+,
 
FastAPI,
 
PyTorch,
 
and
 
Interactive
 
Brokers
 1.  Executive  Summary  
The  convergence  of  modern  asynchronous  web  frameworks,  sophisticated  machine  learning  
models,
 
and
 
low-latency
 
financial
 
execution
 
systems
 
presents
 
a
 
formidable
 
architectural
 
challenge.
 
The
 
modern
 
algorithmic
 
trading
 
stack
 
is
 
no
 
longer
 
a
 
collection
 
of
 
isolated
 
scripts;
 
it
 
is
 
a
 
distributed
 
system
 
requiring
 
rigorous
 
orchestration.
 
The
 
user's
 
requirement
 
specifies
 
a
 
high-performance
 
integration
 
of
 
FastAPI
 
for
 
asynchronous
 
I/O,
 
Celery
 
for
 
distributed
 
task
 
processing,
 
Interactive
 
Brokers
 
(ib_async)
 
for
 
market
 
access,
 
and
 
a
 
diverse
 
suite
 
of
 
intelligence
 
tools
 
ranging
 
from
 
PyTorch
 
and
 
Transformers
 
to
 
Presidio
 
and
 
Google
 
Generative
 
AI
.
 
Furthermore,
 
strict
 
constraints
 
regarding
 
NumPy
 
<
 
2.0
 
compatibility
 
and
 
Docker
 
Compose
 
V2
 
infrastructure
 
dictate
 
a
 
highly
 
specific
 
implementation
 
strategy.
 
This  report  provides  an  exhaustive  analysis  of  the  architectural  patterns,  build  strategies,  and  
operational
 
methodologies
 
required
 
to
 
deploy
 
this
 
specific
 
technology
 
stack.
 
It
 
addresses
 
the
 
"dependency
 
hell"
 
inherent
 
in
 
combining
 
legacy
 
scientific
 
libraries
 
(py_vollib,
 
pandas-ta)
 
with
 
cutting-edge
 
web
 
tools
 
(pydantic>=2.0)
 
and
 
heavy
 
deep
 
learning
 
frameworks.
 
The
 
analysis
 
focuses
 
on
 
creating
 
an
 
optimized,
 
production-grade
 
Docker
 
environment
 
that
 
balances
 
image
 
size,
 
build
 
time,
 
and
 
runtime
 
performance
 
while
 
adhering
 
to
 
strict
 
version
 
constraints
 
and
 
security
 
best
 
practices.
 
2.  Architectural  Analysis  of  the  Hybrid  Micro-Monolith  
The  requested  technology  stack  implies  a  "Hybrid  Micro-Monolith"  architecture.  While  the  
deployment
 
utilizes
 
container
 
orchestration
 
(Docker
 
Compose)
 
to
 
separate
 
concerns—isolating
 
the
 
database,
 
message
 
broker,
 
and
 
gateway—the
 
Python
 
application
 
itself
 
functions
 
as
 
a
 
monolith,
 
housing
 
web
 
routes,
 
background
 
workers,
 
and
 
quantitative
 
logic
 
within
 
a
 
unified
 
codebase.
 
This
 
approach
 
minimizes
 
code
 
duplication
 
and
 
simplifies
 
dependency
 
management
 
but
 
requires
 
a
 
robust
 
container
 
strategy
 
to
 
handle
 
the
 
divergent
 
resource
 
profiles
 
of
 
web
 
servers
 
versus
 
heavy
 
computational
 
workers.
 
2.1  The  Asynchronous  Web  &  Execution  Layer  

At  the  core  of  the  system  lies  FastAPI ,  chosen  for  its  native  support  of  Python's  asyncio  
capabilities.
 
This
 
selection
 
is
 
critical
 
for
 
financial
 
applications
 
where
 
I/O
 
latency—such
 
as
 
waiting
 
for
 
a
 
database
 
write
 
or
 
a
 
brokerage
 
confirmation—can
 
result
 
in
 
slippage.
 
FastAPI  and  the  ASGI  Standard:  The  inclusion  of  fastapi[all]  brings  in  uvicorn  as  the  ASGI  (Asynchronous  Server  Gateway  
Interface)
 
server.
 
Unlike
 
traditional
 
WSGI
 
servers
 
(like
 
Gunicorn
 
with
 
Flask),
 
Uvicorn
 
runs
 
a
 
continuous
 
event
 
loop.
 
This
 
allows
 
the
 
application
 
to
 
handle
 
thousands
 
of
 
concurrent
 
connections,
 
such
 
as
 
WebSocket
 
streams
 
for
 
real-time
 
market
 
data
 
(websockets
 
library)
 
or
 
incoming
 
webhook
 
signals,
 
without
 
blocking
 
the
 
main
 
execution
 
thread.1
 The  Role  of  Nest_Asyncio:  The  requirement  for  nest_asyncio  points  to  a  specific  complexity  in  this  stack:  the  conflict  
between
 
the
 
Jupyter/IPython
 
environment
 
loops,
 
the
 
Uvicorn
 
loop,
 
and
 
the
 
ib_async
 
client
 
loop.
 
The
 
ib_async
 
library
 
is
 
designed
 
to
 
manage
 
its
 
own
 
asyncio
 
loop
 
to
 
handle
 
the
 
continuous
 
stream
 
of
 
messages
 
from
 
the
 
Interactive
 
Brokers
 
gateway.
 
When
 
running
 
within
 
Uvicorn
 
(which
 
already
 
runs
 
a
 
loop)
 
or
 
when
 
executing
 
tasks
 
that
 
attempt
 
to
 
spin
 
up
 
their
 
own
 
loops
 
(common
 
in
 
some
 
google-cloud
 
libraries
 
or
 
improperly
 
configured
 
asyncpg
 
pools),
 
the
 
"RuntimeError:
 
This
 
event
 
loop
 
is
 
already
 
running"
 
error
 
is
 
prevalent.
 
nest_asyncio
 
patches
 
the
 
standard
 
library
 
to
 
allow
 
re-entrant
 
event
 
loops,
 
a
 
necessary
 
stabilizer
 
for
 
this
 
specific
 
combination
 
of
 
libraries.3
 Serialization  Efficiency  with  Orjson:  The  inclusion  of  orjson  suggests  a  requirement  for  ultra-fast  JSON  serialization.  Financial  
data,
 
particularly
 
Level
 
2
 
order
 
book
 
snapshots,
 
can
 
be
 
voluminous.
 
Standard
 
Python
 
json
 
library
 
performance
 
degrades
 
linearly
 
with
 
object
 
size.
 
orjson,
 
written
 
in
 
Rust,
 
offers
 
serialization
 
speeds
 
10-50x
 
faster
 
than
 
the
 
standard
 
library.
 
For
 
a
 
FastAPI
 
application
 
serving
 
market
 
data
 
to
 
a
 
frontend
 
or
 
logging
 
tick
 
data
 
to
 
disk,
 
replacing
 
the
 
default
 
JSON
 
encoder
 
with
 
orjson
 
significantly
 
reduces
 
CPU
 
overhead
 
during
 
high-frequency
 
events.
 
2.2  The  Brokerage  Connectivity  Paradigm  
The  integration  of  Interactive  Brokers  (IBKR)  via  ib_async  introduces  a  unique  architectural  
constraint:
 
the
 
Gateway
 
Problem.
 
The  Gateway  Sidecar  Pattern:  Unlike  REST-based  brokers  (like  Alpaca  or  Kraken),  IBKR  does  not  provide  a  direct  public  API  
endpoint
 
for
 
trading.
 
The
 
ib_async
 
library
 
functions
 
as
 
a
 
client
 
that
 
speaks
 
a
 
proprietary
 
binary
 
protocol
 
over
 
TCP
 
to
 
a
 
local
 
instance
 
of
 
Trader
 
Workstation
 
(TWS)
 
or
 
IB
 
Gateway.
 
This
 
necessitates
 
a
 
"Sidecar"
 
architecture
 
in
 
Docker
 
Compose.
 
The
 
IB
 
Gateway
 
must
 
run
 
in
 
its
 
own
 
container,
 
exposing
 
a
 
specific
 
port
 
(typically
 
4001
 
or
 
4002)
 
to
 
the
 
application
 
container
 
via
 
a
 
private
 
Docker
 
network.
 
This
 
ensures
 
that
 
the
 
trading
 
engine
 
remains
 
decoupled
 
from
 
the
 
application
 
logic;
 
if
 
the
 
Python
 
app
 
crashes,
 
the
 
Gateway
 
maintains
 
its
 
connection
 
to
 
the
 
exchange.5
 Asynchronous  Brokerage  Logic:  ib_async  is  distinct  from  the  older  ibapi  (official  client)  in  that  it  is  fully  awaitable.  This  allows  

the  FastAPI  application  to  process  an  incoming  HTTP  request  (e.g.,  "Place  Order")  and  await  
the
 
submission
 
to
 
IBKR
 
within
 
the
 
same
 
async
 
context,
 
providing
 
immediate
 
feedback
 
to
 
the
 
caller.
 
This
 
tight
 
integration
 
contrasts
 
with
 
older
 
threaded
 
models
 
where
 
requests
 
had
 
to
 
be
 
handed
 
off
 
to
 
a
 
queue
 
with
 
no
 
immediate
 
return
 
path.3
 
2.3  The  Quantitative  Constraint:  NumPy  <  2.0  
Perhaps  the  most  critical  constraint  in  the  requirements.txt  is  numpy<2.0.  This  is  not  merely  a  
version
 
preference;
 
it
 
is
 
a
 
stability
 
imperative.
 
The  NumPy  2.0  ABI  Rupture:  NumPy  2.0,  released  in  mid-2024,  introduced  significant  changes  to  its  Application  Binary  
Interface
 
(ABI)
 
and
 
C-API.
 
It
 
changed
 
the
 
byte-size
 
of
 
certain
 
scalar
 
types
 
and
 
reorganized
 
internal
 
structures.
 
Libraries
 
that
 
link
 
against
 
NumPy's
 
C-API—specifically
 
pandas-ta
 
(Technical
 
Analysis),
 
py_vollib
 
(Volatility/Greeks
 
calculation),
 
and
 
older
 
binary
 
wheels
 
of
 
scikit-learn—will
 
fail
 
catastrophically
 
(segmentation
 
faults
 
or
 
import
 
errors)
 
if
 
run
 
against
 
NumPy
 
2.0
 
without
 
recompilation.7
 The  Dependency  Resolution  Hazard:  Modern  pip  resolvers  are  aggressive.  If  a  library  like  pandas  or  scikit-learn  releases  a  new  
version
 
compatible
 
with
 
NumPy
 
2.0,
 
pip
 
might
 
attempt
 
to
 
upgrade
 
NumPy
 
to
 
satisfy
 
that
 
constraint,
 
violating
 
the
 
user's
 
manual
 
pin.
 
The
 
architectural
 
defense
 
against
 
this
 
is
 
a
 
strict
 
ordering
 
of
 
installation
 
operations
 
in
 
the
 
Dockerfile,
 
forcing
 
the
 
numpy<2.0
 
constraint
 
to
 
be
 
the
 
anchor
 
around
 
which
 
all
 
other
 
dependencies
 
must
 
resolve.
 
2.4  The  Intelligence  &  NLP  Layer  
The  inclusion  of  presidio-analyzer,  spacy,  torch,  transformers,  and  google-generativeai  
creates
 
a
 
heavy
 
"Intelligence
 
Layer."
 
Presidio  and  PII  Safety:  presidio-analyzer  is  Microsoft's  tool  for  detecting  Personally  Identifiable  Information  (PII).  In  a  
trading
 
context,
 
this
 
is
 
often
 
used
 
to
 
scrub
 
sensitive
 
data
 
from
 
unstructured
 
text
 
(like
 
news
 
feeds,
 
emails,
 
or
 
alternative
 
data
 
sources)
 
before
 
it
 
enters
 
the
 
analysis
 
pipeline.
 
It
 
depends
 
on
 
spacy
 
for
 
Named
 
Entity
 
Recognition
 
(NER).
 
The
 
requirement
 
for
 
the
 
en_core_web_lg
 
model
 
implies
 
a
 
need
 
for
 
higher
 
accuracy
 
than
 
the
 
small
 
model
 
provides,
 
at
 
the
 
cost
 
of
 
a
 
significantly
 
larger
 
memory
 
footprint
 
and
 
Docker
 
image
 
size.10
 PyTorch  on  CPU:  The  presence  of  torch  alongside  standard  web  libraries  indicates  a  local  inference  workload.  
However,
 
standard
 
PyTorch
 
installations
 
include
 
NVIDIA
 
CUDA
 
binaries,
 
which
 
can
 
add
 
3GB+
 
to
 
a
 
Docker
 
image.
 
For
 
a
 
container
 
that
 
may
 
run
 
on
 
standard
 
CPU
 
instances
 
(common
 
for
 
web
 
servers),
 
this
 
is
 
wasted
 
space.
 
The
 
architecture
 
must
 
explicitly
 
target
 
the
 
CPU-optimized
 
wheels
 
of
 
PyTorch
 
to
 
maintain
 
a
 
reasonable
 
container
 
size.13
 
3.  Advanced  Docker  Build  Strategy:  The  Multi-Stage  

Approach  
To  satisfy  the  requirements  of  "exhaustive  detail"  and  "best  practices,"  we  cannot  simply  use  a  
monolithic
 
FROM
 
python:3.10
 
Dockerfile.
 
We
 
must
 
employ
 
a
 
multi-stage
 
build
 
strategy.
 
This
 
approach
 
is
 
essential
 
for
 
compiling
 
C-extensions
 
(required
 
by
 
Cython,
 
orjson,
 
python-Levenshtein)
 
while
 
keeping
 
the
 
final
 
runtime
 
image
 
free
 
of
 
bulky
 
compilers
 
and
 
build
 
artifacts.
 
3.1  Base  Image  Selection:  The  Alpine  vs.  Debian  Debate  
For  this  specific  stack,  Debian  Slim  (Bookworm)  is  strictly  superior  to  Alpine  Linux.  
The  Musl  Libc  Incompatibility:  Alpine  Linux  uses  musl  libc  to  minimize  size.  However,  the  vast  majority  of  Python  data  science  
wheels
 
(NumPy,
 
Pandas,
 
PyTorch)
 
are
 
compiled
 
for
 
manylinux
 
(which
 
uses
 
glibc).
 
Installing
 
these
 
libraries
 
on
 
Alpine
 
forces
 
pip
 
to
 
compile
 
them
 
from
 
source.
 ●  Impact  on  numpy  and  pandas:  Compilation  takes  minutes  instead  of  seconds.  ●  Impact  on  torch:  Compilation  is  virtually  impossible  without  an  extensive  and  fragile  
toolchain.
 ●  Impact  on  spacy:  Snippets  confirm  that  Spacy  installation  on  Alpine  is  "extremely  slow"  
or
 
prone
 
to
 
failure.
16  
●  Impact  on  python-Levenshtein:  This  library  requires  GCC.  On  Alpine,  linking  issues  with  
musl
 
are
 
common.
18  
Recommendation:  Use  python:3.10-slim-bookworm.  This  image  is  based  on  Debian  12,  uses  
glibc,
 
and
 
is
 
compatible
 
with
 
pre-compiled
 
binary
 
wheels,
 
ensuring
 
fast,
 
reliable
 
builds
 
while
 
remaining
 
relatively
 
small
 
(~120MB
 
base).
 
3.2  Stage  1:  The  Builder  (Compiler  Environment)  
The  first  stage  of  the  Dockerfile  acts  as  the  construction  yard.  It  must  contain  all  the  tools  
necessary
 
to
 
build
 
the
 
software,
 
which
 
will
 
be
 
discarded
 
in
 
the
 
final
 
stage.
 
System  Dependencies:  We  require  apt-get  install  build-essential  libpq-dev  git  curl  tesseract-ocr-dev.  ●  build-essential:  Provides  gcc,  g++,  and  make.  Essential  for  building  Cython  extensions  
and
 
python-Levenshtein.
18  
●  libpq-dev:  The  header  files  for  PostgreSQL.  Although  psycopg2-binary  is  requested,  
having
 
the
 
headers
 
ensures
 
that
 
asyncpg
 
(which
 
compiles
 
its
 
own
 
binary
 
protocol
 
extensions)
 
builds
 
correctly
 
if
 
no
 
wheel
 
is
 
found
 
for
 
the
 
specific
 
architecture.
 ●  tesseract-ocr-dev:  Required  if  presidio-image-redactor  needs  to  link  against  Tesseract  
headers
 
during
 
installation,
 
though
 
often
 
the
 
runtime
 
binary
 
is
 
sufficient.
20  
Dependency  Ordering  Strategy:  

To  respect  the  numpy<2.0  constraint,  we  utilize  a  phased  installation  approach:  1.  Upgrade  Pip:  pip  install  --upgrade  pip  setuptools  wheel.  Old  versions  of  pip  handle  
dependency
 
resolution
 
poorly.
 2.  Anchor  Numpy:  pip  install  "numpy<2.0".  This  installs  a  version  like  1.26.4.  3.  Install  Torch  CPU:  pip  install  torch  --index-url  https://download.pytorch.org/whl/cpu.  
This
 
directs
 
pip
 
to
 
the
 
CPU-specific
 
repository,
 
preventing
 
the
 
download
 
of
 
CUDA
 
blobs.
21  
4.  Install  Remaining  Requirements:  pip  install  -r  requirements.txt.  
Asset  Hydration  (Spacy):  A  common  anti-pattern  is  downloading  NLP  models  at  runtime  (e.g.,  
spacy.load('en_core_web_lg')
 
triggering
 
a
 
download).
 
This
 
slows
 
down
 
container
 
startup
 
and
 
requires
 
external
 
connectivity,
 
which
 
might
 
be
 
blocked
 
in
 
secure
 
production
 
environments.
 ●  Solution:  Execute  python  -m  spacy  download  en_core_web_lg  during  the  build  phase .  
This
 
places
 
the
 
model
 
data
 
into
 
the
 
site-packages
 
directory
 
of
 
the
 
virtual
 
environment,
 
ensuring
 
it
 
is
 
baked
 
into
 
the
 
image.
10  
3.3  Stage  2:  The  Runtime  (Slim  &  Secure)  
The  final  stage  copies  the  artifacts  from  the  builder  and  sets  up  the  execution  environment.  
Runtime  Dependencies:  We  install  libpq5  (Postgres  runtime  library),  tesseract-ocr  (the  binary  executable  for  OCR),  
and
 
libgomp1
 
(OpenMP
 
library
 
required
 
by
 
PyTorch
 
and
 
Scikit-learn
 
for
 
threading).
 
We
 
strictly
 
avoid
 
installing
 
build-essential
 
here
 
to
 
keep
 
the
 
image
 
secure
 
and
 
small.
 User  Permissions:  Running  as  root  is  a  security  risk,  especially  for  a  web  application  parsing  untrusted  input  (via  
FastAPI
 
or
 
Presidio).
 
We
 
create
 
a
 
system
 
user
 
(appuser)
 
and
 
change
 
ownership
 
of
 
the
 
application
 
directory.
 
4.  Deep  Dive:  Library  Configuration  &  Integration  4.1  Quantitative  Core:  py_vollib  and  pandas-ta  
py_vollib:  This  library  is  the  industry  standard  for  Black-Scholes-Merton  option  pricing  and  Greeks  
calculation
 
in
 
Python.
 
It
 
is
 
heavily
 
dependent
 
on
 
scipy
 
and
 
numpy.
 ●  The  Nuance:  py_vollib  relies  on  numba  for  JIT  compilation  in  some  modules.  numba  is  
notoriously
 
sensitive
 
to
 
NumPy
 
versions.
 
The
 
numpy<2.0
 
pin
 
is
 
largely
 
to
 
protect
 
this
 
integration.
 
If
 
NumPy
 
2.0
 
were
 
installed,
 
py_vollib's
 
underlying
 
C-struct
 
definitions
 
for
 
volatility
 
surfaces
 
would
 
misalign,
 
causing
 
calculation
 
errors
 
or
 
crashes.
7  
pandas-ta:  Used  for  generating  technical  indicators  (RSI,  MACD,  Bollinger  Bands).  

●  Performance:  pandas-ta  can  leverage  multiprocessing.  However,  inside  a  Docker  
container
 
orchestrated
 
by
 
Celery,
 
one
 
must
 
be
 
careful.
 
If
 
Celery
 
is
 
configured
 
with
 
pool=prefork
 
(the
 
default),
 
and
 
pandas-ta
 
attempts
 
to
 
spawn
 
its
 
own
 
sub-processes,
 
it
 
can
 
lead
 
to
 
a
 
"daemonic
 
processes
 
are
 
not
 
allowed
 
to
 
have
 
children"
 
error.
 ●  Configuration:  For  containerized  environments,  it  is  often  safer  to  configure  pandas-ta  
to
 
use
 
a
 
single
 
core
 
per
 
worker
 
process,
 
relying
 
on
 
Celery's
 
horizontal
 
scaling
 
(adding
 
more
 
worker
 
containers)
 
rather
 
than
 
vertical
 
scaling
 
(threads
 
per
 
worker).
 
4.2  Brokerage  Data:  pyarrow  vs.  psycopg2  
The  user  requests  both  pyarrow  and  psycopg2-binary.  This  implies  a  hybrid  data  storage  
strategy.
 
The  Case  for  PyArrow  (Parquet):  For  high-frequency  tick  data  (Level  1  quotes,  trades),  Relational  Databases  (PostgreSQL)  are  
often
 
too
 
slow
 
and
 
storage-inefficient.
 
pyarrow
 
allows
 
the
 
application
 
to
 
write
 
data
 
to
 
Parquet
 
files.
 ●  Mechanism:  Parquet  is  a  columnar  storage  format.  It  compresses  repetitive  market  data  
(like
 
timestamps
 
and
 
exchange
 
IDs)
 
extremely
 
efficiently.
 ●  Workflow:  The  ib_async  client  receives  streaming  ticks  ->  buffers  them  in  memory  ->  
pyarrow
 
writes
 
a
 
batch
 
to
 
a
 
.parquet
 
file
 
in
 
a
 
Docker
 
volume
 
->
 
These
 
files
 
are
 
later
 
uploaded
 
to
 
google-cloud-storage
 
for
 
archiving.
 
This
 
bypasses
 
the
 
overhead
 
of
 
SQL
 
INSERT
 
statements
 
for
 
high-volume
 
data.
7  
The  Case  for  Psycopg2  (SQL):  PostgreSQL  is  used  for  transactional  data:  Trade  logs,  Account  Balance  history,  and  
configuration
 
state.
 ●  Binary  vs.  Source:  The  user  requested  psycopg2-binary.  This  is  a  pre-compiled  wheel.  
While
 
convenient,
 
the
 
psycopg2
 
documentation
 
warns
 
that
 
the
 
binary
 
version
 
is
 
not
 
intended
 
for
 
heavy
 
production
 
due
 
to
 
potential
 
ABI
 
conflicts
 
with
 
libssl.
 
However,
 
in
 
a
 
controlled
 
Docker
 
environment
 
where
 
we
 
install
 
libpq5,
 
it
 
is
 
generally
 
stable.
 ●  Asyncpg:  The  web  layer  (FastAPI)  uses  asyncpg  for  non-blocking  access.  psycopg2  is  
likely
 
reserved
 
for
 
synchronous
 
worker
 
tasks
 
(Celery)
 
or
 
legacy
 
migrations
 
(SQLAlchemy
 
synchronous
 
engine).
23  
4.3  NLP  Pipeline:  presidio,  spacy,  vaderSentiment,  PRAW  
PRAW  (Python  Reddit  API  Wrapper):  This  library  allows  the  extraction  of  sentiment  data  from  Reddit  (e.g.,  r/WallStreetBets).  ●  Dependency:  PRAW  is  a  synchronous  library  wrapper.  Using  it  directly  in  FastAPI  routes  
will
 
block
 
the
 
server.
 ●  Architecture:  PRAW  interactions  must  be  offloaded  to  Celery  tasks .  The  FastAPI  route  
initiates
 
a
 
"Sentiment
 
Analysis"
 
job,
 
pushes
 
it
 
to
 
Redis,
 
and
 
returns
 
a
 
Job
 
ID.
 
The
 
Celery
 
worker,
 
which
 
can
 
block
 
safely,
 
executes
 
the
 
PRAW
 
API
 
calls,
 
rates
 
limits
 
handling,
 
and
 

then  processes  the  text.
24  
VaderSentiment  vs.  Transformers:  ●  VaderSentiment:  A  lexicon-based  sentiment  analyzer.  It  is  fast,  CPU-efficient,  and  
requires
 
no
 
GPU.
 
It
 
is
 
ideal
 
for
 
an
 
initial
 
pass
 
on
 
high-volume
 
data
 
streams.
 ●  Transformers:  The  transformers  library  allows  loading  BERT  or  RoBERTa  models  for  
nuanced
 
sentiment
 
detection.
 
These
 
are
 
computationally
 
expensive.
 ●  Integration:  The  system  should  likely  use  a  tiered  approach:  Use  Vader  for  real-time  
filtering
 
of
 
noisy
 
streams,
 
and
 
pass
 
high-interest
 
text
 
to
 
a
 
Transformer
 
model
 
running
 
on
 
PyTorch
 
(CPU)
 
for
 
deep
 
analysis.
 
Presidio-Analyzer:  This  is  used  to  redact  entities.  ●  Configuration:  We  must  configure  the  NlpEngineProvider  in  Python  to  explicitly  use  the  
en_core_web_lg
 
model
 
we
 
downloaded
 
in
 
the
 
Dockerfile.
 
Without
 
this
 
explicit
 
configuration,
 
Presidio
 
defaults
 
to
 
en_core_web_sm
 
and
 
may
 
fail
 
if
 
it's
 
not
 
present.
26  
4.4  Security:  webauthn,  passlib,  cryptography  
WebAuthn  (FIDO2):  The  request  for  webauthn  suggests  a  requirement  for  passwordless  or  2FA  hardware  
authentication
 
(YubiKey,
 
TouchID).
 ●  Statefulness  Challenge:  WebAuthn  is  a  challenge-response  protocol.  The  server  
generates
 
a
 
random
 
challenge,
 
stores
 
it
 
temporarily,
 
sends
 
it
 
to
 
the
 
client,
 
and
 
verifies
 
the
 
signed
 
response.
 ●  Redis  Implementation:  Since  FastAPI  is  stateless,  we  must  use  Redis  to  store  the  
pending
 
WebAuthn
 
challenges
 
(with
 
a
 
short
 
TTL).
 
The
 
redis
 
library
 
in
 
requirements.txt
 
supports
 
this.
 
Passlib  &  Cryptography:  ●  Passlib:  Used  for  password  hashing.  The  industry  standard  is  Argon2  or  Bcrypt .  
passlib[bcrypt]
 
is
 
the
 
typical
 
install.
 ●  Cryptography:  This  library  provides  low-level  encryption  primitives.  It  is  used  by  
google-cloud-storage
 
for
 
signing
 
requests
 
and
 
by
 
fernet
 
if
 
the
 
application
 
needs
 
to
 
encrypt
 
sensitive
 
fields
 
(like
 
IBKR
 
passwords)
 
in
 
the
 
database.
27  
5.  Docker  Compose  V2  Architecture  &  Networking  
Orchestration  is  handled  via  Docker  Compose  V2.  The  architecture  consists  of  five  primary  
services:
 
web,
 
worker,
 
db,
 
redis,
 
and
 
ib-gateway.
 
5.1  Service  Definitions  

Web  Service  (FastAPI):  ●  Build:  Uses  the  multi-stage  Dockerfile.  ●  Command:  uvicorn  main:app  --host  0.0.0.0  --port  8000.  ●  Environment:  Loads  pydantic-settings  from  environment  variables.  ●  Depends_on:  strictly  waits  for  db  and  redis.  
Worker  Service  (Celery):  ●  Image:  Reuses  the  same  image  as  web.  ●  Command:  celery  -A  app.worker  worker  --loglevel=info.  ●  Concurrency:  Configured  to  respect  CPU  limits.  For  CPU-bound  tasks  (PyTorch),  setting  
OMP_NUM_THREADS=1
 
is
 
crucial
 
to
 
prevent
 
thread
 
oversubscription
 
when
 
running
 
multiple
 
worker
 
processes.
15  
IB  Gateway  (Sidecar):  ●  Image:  ghcr.io/gnzsnz/ib-gateway:stable.  ●  Function:  Runs  the  Java-based  IB  Gateway  headless.  ●  Ports:  Exposes  4001  (Live)  /  4002  (Paper)  to  the  internal  network.  Exposes  5900  (VNC)  
to
 
localhost
 
for
 
authentication
 
handling.
 ●  Healthcheck:  The  ib_async  library  depends  on  this  service  being  fully  booted  (which  
takes
 
~30
 
seconds).
 
We
 
implementation
 
a
 
healthcheck
 
that
 
probes
 
the
 
TCP
 
port.
28  
Data  Layer  (Postgres  &  Redis):  ●  Postgres:  Uses  postgres:15-alpine.  Why  Alpine  here?  Because  the  official  Postgres  
Alpine
 
image
 
is
 
highly
 
optimized
 
and
 
stable,
 
unlike
 
Python
 
Alpine
 
images.
 ●  Redis:  configured  with  appendonly  yes  to  ensure  that  the  Celery  task  queue  is  persisted  
to
 
disk.
 
If
 
the
 
container
 
restarts,
 
pending
 
jobs
 
are
 
not
 
lost.
 
5.2  Network  &  Security  
The  trading_net  Bridge:  All  services  are  attached  to  a  user-defined  bridge  network  trading_net.  This  provides  
automatic
 
DNS
 
resolution.
 ●  The  FastAPI  app  connects  to  Postgres  via  db:5432.  ●  The  FastAPI  app  connects  to  IB  Gateway  via  ib-gateway:4001.  
Secrets  Management:  The  google-cloud-storage  credentials  (JSON  key)  are  sensitive.  ●  Volume  Mount:  We  mount  the  key  from  the  host  to  /app/secrets/key.json  as  read-only  
(:ro).
 ●  Env  Var:  We  set  GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/key.json.  The  
Google
 
client
 
libraries
 
automatically
 
detect
 
this
 
variable
 
and
 
authenticate.
30  

6.  Implementation  Manual  6.1  The  Dockerfile  
 
Dockerfile  
  #  syntax=docker/dockerfile:1.4 
 #  ========================================== #  STAGE  1:  Builder  (Compilers  &  Heavy  Lifting) #  ========================================== FROM python:3.10-slim-bookworm  AS  builder  
 #  Prevent  python  from  writing  pyc  files  and  buffering  stdout ENV PYTHONDONTWRITEBYTECODE=1 ENV PYTHONUNBUFFERED=1 
 #  Install  system  dependencies #  build-essential:  for  Cython,  python-Levenshtein #  libpq-dev:  for  psycopg2  build  fallback #  git:  for  pip  installing  from  git  repos RUN apt-get  update  &&  apt-get  install  -y  --no-install-recommends  \  
    
build-essential
 
\
 
    
libpq-dev
 
\
 
    
git
 
\
 
    
curl
 
\
 
    
&&
 
rm
 
-rf
 
/var/lib/apt/lists/* 
 WORKDIR /app 
 #  Create  virtual  environment RUN python  -m  venv  /opt/venv ENV PATH="/opt/venv/bin:$PATH" 
 #  Upgrade  pip  to  handle  modern  wheel  standards RUN pip  install  --upgrade  pip  setuptools  wheel 
 COPY requirements.txt. 
 #  --------------------------------------------------------------------------- #  NUMPY  &  TORCH  OPTIMIZATION #  --------------------------------------------------------------------------- 

#  1.  Anchor  Numpy  <  2.0  to  prevent  ABI  breakage  in  py_vollib/pandas-ta RUN pip  install  "numpy<2.0" 
 #  2.  Install  PyTorch  CPU-only. #  The  --index-url  is  critical  to  avoid  downloading  3GB+  of  CUDA  libraries. RUN pip  install  --no-cache-dir  torch  --index-url  https://download.pytorch.org/whl/cpu 
 #  3.  Install  remaining  dependencies. #  --extra-index-url  allows  pip  to  search  PyPI  if  not  found  in  the  Torch  repo RUN pip  install  --no-cache-dir  -r  requirements.txt 
 #  --------------------------------------------------------------------------- #  ASSET  HYDRATION #  --------------------------------------------------------------------------- #  Download  Spacy  model  to  /opt/venv/lib/python3.10/site-packages RUN python  -m  spacy  download  en_core_web_lg 
 #  ========================================== #  STAGE  2:  Runtime  (Slim  &  Secure) #  ========================================== FROM python:3.10-slim-bookworm  AS  runtime  
 ENV PYTHONDONTWRITEBYTECODE=1 ENV PYTHONUNBUFFERED=1 ENV PATH="/opt/venv/bin:$PATH" #  Configure  HuggingFace  to  use  a  writable  temp  dir  for  model  caching  if  needed ENV HF_HOME="/tmp/huggingface" 
 #  Install  runtime  libs  (no  compilers) #  tesseract-ocr:  for  Presidio  image  redaction/OCR #  libpq5:  for  Postgres  connectivity #  libgomp1:  for  OpenMP  threading  (Torch/Scikit-learn) RUN apt-get  update  &&  apt-get  install  -y  --no-install-recommends  \  
    
tesseract-ocr
 
\
 
    
tesseract-ocr-eng
 
\
 
    
libpq5
 
\
 
    
libgomp1
 
\
 
    
curl
 
\
 
    
&&
 
rm
 
-rf
 
/var/lib/apt/lists/* 
 #  Create  non-root  user RUN addgroup  --system  --gid  1001  appgroup  &&  \  
    
adduser
 
--system
 
--uid
 
1001
 
--gid
 
1001
 
appuser 
 #  Copy  venv  from  builder COPY --from=builder  --chown=appuser:appgroup  /opt/venv  /opt/venv 

 WORKDIR /app COPY --chown=appuser:appgroup./src  /app 
 USER appuser  
 EXPOSE 8000 
 CMD ["uvicorn",  "main:app",  "--host",  "0.0.0.0",  "--port",  "8000"] 
 
6.2  The  docker-compose.yml  
 
YAML  
  services: 
  web: 
    build:. 
    image: quant-stack:latest 
    container_name: quant_web 
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload 
    volumes: 
      -./src:/app:ro 
      -./secrets:/app/secrets:ro 
    ports: 
      - "8000:8000" 
    environment: 
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/quantdb 
      - REDIS_URL=redis://redis:6379/0 
      - IB_GATEWAY_HOST=ib-gateway 
      - IB_GATEWAY_PORT=4002 #  Paper  trading 
      - GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/gcp-key.json 
      - SPACY_MODEL=en_core_web_lg 
    depends_on: 
      db: 
        condition: service_healthy 
      redis: 
        condition: service_started 
      ib-gateway: 
        condition: service_started 
    networks: 

      - trading_net 
 
  worker: 
    image: quant-stack:latest 
    container_name: quant_worker 
    command: celery -A app.celery_worker worker --loglevel=info 
    volumes: 
      -./src:/app:ro 
      -./secrets:/app/secrets:ro 
    environment: 
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/quantdb 
      - REDIS_URL=redis://redis:6379/0 
      - GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/gcp-key.json 
      - OMP_NUM_THREADS=1 #  Restrict  PyTorch  threading 
    depends_on: 
      redis: 
        condition: service_started 
    networks: 
      - trading_net 
 
  ib-gateway: 
    image: ghcr.io/gnzsnz/ib-gateway:stable 
    restart: unless-stopped 
    ports: 
      - "127.0.0.1:4002:4002" 
      - "127.0.0.1:5900:5900" 
    environment: 
      - TWS_USERID=${IB_USER} 
      - TWS_PASSWORD=${IB_PASSWORD} 
      - TRADING_MODE=paper 
      - READ_ONLY_API=no 
    networks: 
      - trading_net 
 
  db: 
    image: postgres:15-alpine 
    environment: 
      - POSTGRES_USER=user 
      - POSTGRES_PASSWORD=password 
      - POSTGRES_DB=quantdb 
    volumes: 
      - postgres_data:/var/lib/postgresql/data 
    healthcheck: 

      test: 
      interval: 5s 
      timeout: 5s 
      retries: 5 
    networks: 
      - trading_net 
 
  redis: 
    image: redis:7-alpine 
    command: redis-server --appendonly yes 
    volumes: 
      - redis_data:/data 
    networks: 
      - trading_net 
 volumes: 
  postgres_data: 
  redis_data: 
 networks: 
  trading_net: 
    driver: bridge 
 
6.3  Pydantic  V2  Configuration  
To  handle  the  pydantic>=2.0  requirement  effectively,  we  use  pydantic-settings.  
 
Python  
  from pydantic_settings  import BaseSettings,  SettingsConfigDict  from pydantic  import Field  
 class Settings(BaseSettings): 
    #  System 
    
env_state:
 str =  Field("dev",  alias="ENV_STATE")  
    
 
    #  Database 
    
database_url:
 str 
    
 
    #  Brokerage 

    ib_gateway_host:  str 
    
ib_gateway_port:
 int 
    
 
    #  Google  AI 
    
google_api_key:
 str =  Field(...,  alias="GOOGLE_API_KEY")  
    
 
    #  NLP 
    
spacy_model:
 str =  "en_core_web_lg" 
 
    
model_config
 
=
 
SettingsConfigDict(
 
        
env_file=".env",  
        
extra="ignore" 
    
)
 
 
settings
 
=
 
Settings()
 
 
6.4  Presidio  &  Spacy  Integration  Code  
 
Python  
  from presidio_analyzer  import AnalyzerEngine  from presidio_analyzer.nlp_engine  import NlpEngineProvider  
 #  Explicitly  configure  Presidio  to  use  the  baked-in  model #  This  prevents  runtime  download  attempts  and  ensures  the  'lg'  model  is  used 
configuration
 
=
 
{
 
    "nlp_engine_name":  "spacy",  
    "models":  [{"lang_code":  "en",  "model_name":  "en_core_web_lg"}],  
}
 
 
provider
 
=
 
NlpEngineProvider(nlp_configuration=configuration)
 
nlp_engine
 
=
 
provider.create_engine()
 
 
analyzer
 
=
 
AnalyzerEngine(nlp_engine=nlp_engine)
 
 def analyze_text(text:  str): 
    return analyzer.analyze(text=text,  language="en")  
 
7.  Operational  Best  Practices  

7.1  Managing  google-generativeai  &  Rate  Limits  
The  google-generativeai  library  connects  to  Gemini.  ●  Tiktoken  Usage:  Before  sending  a  prompt  to  the  API,  use  tiktoken  to  count  tokens.  This  
allows
 
you
 
to
 
estimate
 
costs
 
and
 
ensure
 
you
 
stay
 
within
 
the
 
context
 
window
 
limits.
 ●  Celery  Offloading:  Do  not  call  genai.generate_text()  directly  in  a  FastAPI  view.  It  is  a  
blocking
 
network
 
call
 
(unless
 
using
 
the
 
async
 
client).
 
Offload
 
generation
 
tasks
 
to
 
Celery,
 
and
 
use
 
Redis
 
to
 
store
 
the
 
result.
 
7.2  The  py_vollib  &  numpy  Stability  Check  
Upon  container  startup,  it  is  prudent  to  run  a  sanity  check  to  ensure  the  ABI  is  intact.  ●  Startup  Script:  In  main.py,  include  a  startup  event  that  calculates  a  simple  Black-Scholes  
price
 
using
 
py_vollib.
 
If
 
it
 
segfaults
 
or
 
raises
 
an
 
ImportError,
 
the
 
container
 
should
 
crash
 
immediately
 
(Fail
 
Fast)
 
rather
 
than
 
failing
 
silently
 
during
 
a
 
live
 
trade.
 
7.3  WebAuthn  State  Management  
For  webauthn:  1.  Registration:  Client  requests  registration  ->  Server  (FastAPI)  generates  options  ->  
Stored
 
in
 
Redis
 
(key:
 
webauthn:challenge:{user_id})
 
->
 
Sent
 
to
 
Client.
 2.  Verification:  Client  signs  challenge  ->  Sends  to  Server  ->  Server  retrieves  challenge  from  
Redis
 
->
 
Verifies
 
signature
 
using
 
webauthn
 
library
 
->
 
Updates
 
User
 
DB
 
(Postgres).
 
8.  Conclusion  
This  architecture  successfully  navigates  the  complex  requirements  of  a  modern  quantitative  
trading
 
stack.
 
By
 
rigorously
 
controlling
 
the
 
build
 
environment
 
with
 
a
 
multi-stage
 
Dockerfile,
 
we
 
satisfy
 
the
 
critical
 
numpy<2.0
 
constraint
 
and
 
optimize
 
the
 
torch
 
installation
 
for
 
CPU
 
workloads.
 
The
 
Docker
 
Compose
 
configuration
 
establishes
 
a
 
secure,
 
robust
 
network
 
topology
 
that
 
integrates
 
legacy
 
brokerage
 
gateways
 
with
 
high-performance
 
asynchronous
 
web
 
services.
 
This
 
system
 
provides
 
a
 
scalable
 
foundation
 
for
 
deploying
 
sophisticated
 
financial
 
models,
 
capable
 
of
 
processing
 
real-time
 
market
 
data
 
while
 
leveraging
 
state-of-the-art
 
NLP
 
and
 
generative
 
AI
 
capabilities.
 
Table  1:  Service  Resource  &  Constraint  Summary  
Service  Primary  Libs  Critical  Constraint  Docker  Strategy  
Web  fastapi,  ib_async,  pydantic  
AsyncIO  Event  Loop  Conflicts  
Use  nest_asyncio;  Sidecar  pattern  for  IB  Gateway.  

Worker  celery,  torch,  py_vollib  
numpy<2.0  ABI,  Torch  Size  
Multi-stage  build;  CPU-only  wheels;  OMP_NUM_THREADS=1.  
Broker  ib-gateway  (Java)  GUI/VNC  Requirement  
Headless  image  (gnzsnz);  expose  VNC  port  locally  only.  
NLP  presidio,  spacy  Model  Availability  Bake  en_core_web_lg  into  image  during  build.  
Data  asyncpg,  pyarrow  Write  Throughput  Use  Parquet  for  tick  data;  Postgres  for  transactional  data.  
Works  cited  
1.  Docker  Compose  Step-by-Step:  Deploy  FastAPI,  Postgres,  Redis  &  Celery  -  
YouTube,
 
accessed
 
January
 
8,
 
2026,
 https://www.youtube.com/watch?v=IDrRtiGkTaI 2.  FastAPI-PostgreSQL-Celery-RabbitMQ-Redis  backend  with  Docker  
containerization
 
-
 
Reddit,
 
accessed
 
January
 
8,
 
2026,
 https://www.reddit.com/r/FastAPI/comments/nshn5b/fastapipostgresqlceleryrabbitmqredis_backend_with/ 3.  ib-api-reloaded/ib_async:  Python  sync/async  framework  for  Interactive  Brokers  
API
 
(replaces
 
ib_insync)
 
-
 
GitHub,
 
accessed
 
January
 
8,
 
2026,
 https://github.com/ib-api-reloaded/ib_async 4.  ib_async  -  PyPI,  accessed  January  8,  2026,  https://pypi.org/project/ib_async/1.0.2/ 5.  Interactive  Brokers  API  with  Python  and  ib_async  -  YouTube,  accessed  January  8,  2026,  https://www.youtube.com/watch?v=EYDLlnmM5x8 6.  ib_insync  in  docker  ·  Issue  #261  -  GitHub,  accessed  January  8,  2026,  https://github.com/erdewit/ib_insync/issues/261 7.  scikit-learn  -  PyPI,  accessed  January  8,  2026,  https://pypi.org/project/scikit-learn/ 8.  NumPy  2.0  migration  guide,  accessed  January  8,  2026,  https://numpy.org/devdocs/numpy_2_0_migration_guide.html 9.  Maintenance  releases  for  1.1.x  and  1.2.x  with  numpy  <  2.0?  ·  Issue  #29630  -  
GitHub,
 
accessed
 
January
 
8,
 
2026,
 https://github.com/scikit-learn/scikit-learn/issues/29630 

10.  Build  a  named  entity  recognition  app  -  Docker  Docs,  accessed  January  8,  2026,  https://docs.docker.com/guides/named-entity-recognition/ 11.  Using  Presidio  in  Docker,  accessed  January  8,  2026,  https://microsoft.github.io/presidio/samples/docker/ 12.  Installing  Presidio  -  Microsoft  Open  Source,  accessed  January  8,  2026,  https://microsoft.github.io/presidio/installation/ 13.  torch  -  PyPI,  accessed  January  8,  2026,  https://pypi.org/project/torch/ 14.  how  to  integrate  torch  into  a  docker  image  while  keeping  image  size  reasonable?,  
accessed
 
January
 
8,
 
2026,
 https://stackoverflow.com/questions/73274526/how-to-integrate-torch-into-a-docker-image-while-keeping-image-size-reasonable 15.  Reducing  docker  size  with  PyTorch  model  -  deployment,  accessed  January  8,  
2026,
 https://discuss.pytorch.org/t/reducing-docker-size-with-pytorch-model/78991 16.  spacy  installation  extremely  slow  in  docker  ·  Issue  #6158  -  GitHub,  accessed  January  8,  2026,  https://github.com/explosion/spaCy/issues/6158 17.  spaCy  and  Docker:  can't  "dockerize"  Flask  app  that  uses  spaCy  modules  -  Stack  
Overflow,
 
accessed
 
January
 
8,
 
2026,
 https://stackoverflow.com/questions/67394064/spacy-and-docker-cant-dockerize-flask-app-that-uses-spacy-modules 18.  Logiqx/python-lev:  Official  Python  image  with  python-Levenshtein  installed  for  
Alpine
 
Linux
 
+
 
Debian
 
Slim
 
-
 
GitHub,
 
accessed
 
January
 
8,
 
2026,
 https://github.com/Logiqx/python-lev 19.  How  to  install  python-levenshtein  on  Windows?  -  Stack  Overflow,  accessed  
January
 
8,
 
2026,
 https://stackoverflow.com/questions/13200330/how-to-install-python-levenshtein-on-windows 20.  Dockerfile  ·  master  ·  Workers  /  Tesseract  -  GitLab,  accessed  January  8,  2026,  https://gitlab.teklia.com/workers/tesseract/-/blob/master/Dockerfile?ref_type=heads 21.  Installing  CPU-only  PyTorch  results  in  unnecessary  CUDA  dependencies  during  
Docker
 
build.
 
·
 
Issue
 
#146786
 
-
 
GitHub,
 
accessed
 
January
 
8,
 
2026,
 https://github.com/pytorch/pytorch/issues/146786 22.  Install  spaCy  ·  spaCy  Usage  Documentation,  accessed  January  8,  2026,  https://spacy.io/usage 23.  Dockerizing  Celery  and  FastAPI  -  TestDriven.io,  accessed  January  8,  2026,  https://testdriven.io/courses/fastapi-celery/docker/ 24.  Contributing  to  PRAW  -  PRAW  7.8.2.dev0  documentation,  accessed  January  8,  2026,  https://praw.readthedocs.io/en/latest/package_info/contributing.html 25.  Installing  PRAW  -  PRAW  7.8.2.dev0  documentation,  accessed  January  8,  2026,  https://praw.readthedocs.io/en/latest/getting_started/installation.html 26.  Customizing  the  NLP  engine  in  Presidio  Analyzer  -  Microsoft  Open  Source,  
accessed
 
January
 
8,
 
2026,
 https://microsoft.github.io/presidio/analyzer/customizing_nlp_models/ 27.  Settings  management  -  Pydantic,  accessed  January  8,  2026,  

https://docs.pydantic.dev/1.10/usage/settings/ 28.  Docker  Basics  |  IB  Gateway  Automation  (IBGA)  -  He  Shiming  ·  at  GitHub,  accessed  January  8,  2026,  https://heshiming.github.io/ibga/references/docker-basics.html 29.  Configure  reconnect  interval?  ·  gnzsnz  ib-gateway-docker  ·  Discussion  #168  -  
GitHub,
 
accessed
 
January
 
8,
 
2026,
 https://github.com/gnzsnz/ib-gateway-docker/discussions/168 30.  How  do  I  put  application_default_credentials.json  from  Google  cloud  to  
Docker-compose,
 
accessed
 
January
 
8,
 
2026,
 https://forums.docker.com/t/how-do-i-put-application-default-credentials-json-from-google-cloud-to-docker-compose/145195 31.  Simple  way  to  pass  gcloud  credentials  to  a  docker  container  for  Terraform  google  
provider,
 
accessed
 
January
 
8,
 
2026,
 https://www.reddit.com/r/googlecloud/comments/zhbfil/simple_way_to_pass_gcloud_credentials_to_a_docker/ 

