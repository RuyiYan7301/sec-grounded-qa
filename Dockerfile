# Public demo image (Hugging Face Spaces, Render, or any Docker host). No model and no GPU: the Ask page serves
# answers precomputed by `secqa demo-build` (data/demo/), the Companies and 10-K changes pages run live on XBRL facts
# fetched from SEC EDGAR at start-up. Set SEC_USER_AGENT ("Your Name you@example.com", SEC policy) as a secret.
FROM node:22-slim AS web
WORKDIR /w
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.11-slim
RUN useradd -m -u 1000 user
WORKDIR /app
RUN pip install --no-cache-dir requests pyyaml jsonschema beautifulsoup4 lxml numpy "fastapi>=0.110" "uvicorn>=0.29"
COPY pyproject.toml README.md ./
COPY src ./src
COPY data ./data
RUN pip install --no-cache-dir --no-deps -e .
COPY --from=web /w/dist ./web/dist
RUN mkdir -p /app/runtime && chown -R user /app
USER user
ENV SECQA_DEMO=1 SECQA_DATA_DIR=/app/runtime PYTHONUNBUFFERED=1
EXPOSE 7860
CMD ["sh", "-c", "python -m secqa fetch-facts && python -m secqa web --host 0.0.0.0 --port 7860"]
