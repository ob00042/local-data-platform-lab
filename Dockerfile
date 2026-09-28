FROM python:3.13-slim-trixie


# Copy a pinned uv binary into the Python image.
COPY --from=ghcr.io/astral-sh/uv:0.12.19 /uv /uvx /bin/


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Make uv copy packages rather than linking them from its cache.
ENV UV_LINK_MODE=copy

WORKDIR /app


# Copy dependency metadata first.
#
# This means application code changes do not necessarily invalidate
# the dependency installation Docker layer.
COPY pyproject.toml uv.lock ./


# Install only production dependencies.
#
# --locked:
#   refuse to silently change uv.lock
#
# --no-dev:
#   don't install pytest, ruff, etc.
#
# --no-install-project:
#   we only need the dependencies; app/ itself isn't installed as a package.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync \
        --locked \
        --no-dev \
        --no-install-project


# Now copy application files.
COPY app ./app
COPY data/processed ./data/processed


# Commands such as "uvicorn" now resolve from this virtual environment.
ENV PATH="/app/.venv/bin:$PATH"


# Don't run the actual API as root.
RUN useradd --create-home appuser
USER appuser


EXPOSE 8000


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
