FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml .

RUN uv pip install --system -e .

COPY . .

RUN mkdir -p uploads

CMD ["python", "main.py"]