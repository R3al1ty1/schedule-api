FROM python:3.10-slim

WORKDIR /app

# Устанавливаем необходимые SSL сертификаты
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
