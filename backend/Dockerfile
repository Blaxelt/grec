FROM python:3.12-slim

RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --extra backend

COPY ./backend/app ./app

CMD ["uv", "run", "--extra", "backend", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]