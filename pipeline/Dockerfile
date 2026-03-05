FROM python:3.12-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --extra pipeline

COPY ./pipeline ./pipeline

CMD ["uv", "run", "--extra", "pipeline", "python", "-m", "pipeline.run"]
