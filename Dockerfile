# syntax=docker/dockerfile:1.4
# ==========================================
# STAGE 1: Builder (Compilers & Heavy Lifting)
# ==========================================
FROM python:3.10-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    swig \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 2. Upgrade pip and install build anchors
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 3. Anchor Numpy < 2.0 (Doctrine Rule 2.3)
RUN pip install --no-cache-dir "numpy<2.0"

# 4. Install Torch CPU-only (Doctrine Rule 2.4)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 5. Install pandas-ta-classic
RUN pip install --no-cache-dir pandas-ta-classic

# 6. Install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. Asset Hydration: Spacy Model (Doctrine Rule 3.2)
RUN python -m spacy download en_core_web_lg

# ==========================================
# STAGE 2: Runtime (Slim & Secure)
# ==========================================
FROM python:3.10-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Install runtime-only libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy venv from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application source code
COPY ./src ./src

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "asyncio"]
