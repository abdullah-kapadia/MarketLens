# ============================================================================
# MarketLens Backend -- Production Dockerfile
# Base: Python 3.11 slim (Debian Bookworm)
# ============================================================================

FROM python:3.11-slim AS base

# -- Metadata ----------------------------------------------------------------
LABEL maintainer="MarketLens Team"
LABEL description="MarketLens AI-agentic stock analysis backend"
LABEL version="1.0.0"

# -- System dependencies -----------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# -- Application user (non-root) ---------------------------------------------
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home appuser

# -- Working directory --------------------------------------------------------
WORKDIR /app

# -- Install Python dependencies first (layer caching) -----------------------
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -- Copy application code ----------------------------------------------------
COPY . .

# -- Create output directories ------------------------------------------------
RUN mkdir -p /app/output/reports /app/data && \
    chown -R appuser:appuser /app

# -- Switch to non-root user --------------------------------------------------
USER appuser

# -- Expose port --------------------------------------------------------------
EXPOSE 8000

# -- Health check -------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# -- Entrypoint ---------------------------------------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
