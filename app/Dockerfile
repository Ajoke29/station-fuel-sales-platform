# syntax=docker/dockerfile:1

# ---------- Stage 1: build a virtual environment with the dependencies ----------
FROM python:3.13.16-slim-trixie AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip uninstall --yes pip

# ---------- Stage 2: small runtime image, no build tools, non-root ----------
FROM python:3.13.16-slim-trixie AS runtime

LABEL org.opencontainers.image.title="station-fuel-sales" \
      org.opencontainers.image.description="Fictional daily fuel sales per station (demo)" \
      org.opencontainers.image.source="https://github.com/Ajoke29/station-fuel-sales-platform" \
      org.opencontainers.image.authors="Ajoke Soyombo" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

# The app never installs packages at runtime, so remove pip (and the libraries it
# bundles) to shrink the attack surface. Then add a dedicated unprivileged user
# with a fixed UID so Kubernetes can enforce runAsNonRoot.
RUN python -m pip uninstall --yes pip \
    && rm -rf /usr/local/lib/python3.13/ensurepip \
    && groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /srv
COPY --from=builder /opt/venv /opt/venv
COPY --chown=root:root fuel_sales ./fuel_sales

USER 10001:10001
EXPOSE 8000

# Uses Python itself, so no curl/wget needs to be installed in the image
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import os,urllib.request,sys; sys.exit(0 if urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",\"8000\")}/healthz', timeout=2).status == 200 else 1)"]

CMD ["sh", "-c", "exec uvicorn fuel_sales.main:app --host 0.0.0.0 --port ${PORT} --no-access-log --proxy-headers"]
