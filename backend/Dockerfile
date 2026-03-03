FROM python:3.12-slim

RUN pip install uv 

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --extra backend

COPY ./backend/app .

CMD ["uv", "run", "--extra", "backend", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]