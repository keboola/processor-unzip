FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code/
COPY flake8.cfg .
COPY pyproject.toml .
COPY uv.lock .
RUN uv add flake8

ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync --all-groups --frozen

COPY src/ src
CMD ["python", "-u", "/code/src/component.py"]
