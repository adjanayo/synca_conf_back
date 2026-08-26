FROM python:3.12-alpine AS builder

WORKDIR /build

RUN apk add --no-cache gcc musl-dev openssl-dev

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


FROM builder AS builder-dev

COPY requirements-dev.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements-dev.txt


FROM python:3.12-alpine AS runtime

# The base image tag is a floating snapshot -- apk upgrade pulls whatever
# OS-package security fixes Alpine has published since that snapshot was
# built (e.g. openssl CVEs), independent of when this Dockerfile last
# changed. Keeps the CI Trivy gate (image-scan job) green on its own.
RUN apk upgrade --no-cache

RUN addgroup -S app && adduser -S -G app -H app

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels requirements.txt \
    && find /usr/local/lib/python3.12 -type d -name "__pycache__" -prune -exec rm -rf {} \; \
    && python -m pip uninstall -y pip setuptools \
    && BOTOCORE_DATA=$(python -c "import botocore, os; print(os.path.join(botocore.__path__[0], 'data'))") \
    && find "$BOTOCORE_DATA" -mindepth 1 -maxdepth 1 -type d ! -name s3 -exec rm -rf {} + \
    && apk add --no-cache --virtual .strip-deps binutils \
    && find /usr/local/lib/python3.12/site-packages -name "*.so" -exec strip --strip-unneeded {} \; \
    && apk del .strip-deps

COPY app/ app/

RUN mkdir -p /app/logs && chown app:app /app/logs

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM python:3.12-alpine AS dev

RUN apk upgrade --no-cache

RUN addgroup -S app && adduser -S -G app -H app

WORKDIR /app

COPY --from=builder-dev /wheels /wheels
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements-dev.txt \
    && rm -rf /wheels

RUN mkdir -p /app/logs && chown app:app /app/logs

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
