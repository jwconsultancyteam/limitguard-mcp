# Runs the stdio server locally in a container (Docker MCP Catalog, Glama builds).
FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir . && useradd --create-home --uid 10001 app
USER app
ENTRYPOINT ["limitguard-mcp"]
