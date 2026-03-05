FROM python:3.12-slim

RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --extra pipeline

COPY ./pipeline ./pipeline

CMD ["uv", "run", "--extra", "pipeline", "python", "-m", "pipeline.run"]
