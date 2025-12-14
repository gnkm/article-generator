FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
ENV UV_LINK_MODE=copy
RUN uv sync --frozen --no-cache

# Copy source code
COPY . .

EXPOSE 8900

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

CMD ["chainlit", "run", "src/app.py", "-w", "--host", "0.0.0.0", "--port", "8900"]
