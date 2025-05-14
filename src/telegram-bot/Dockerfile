FROM python:3.10-slim

WORKDIR /app

# Устанавливаем aiogram
RUN pip install --no-cache-dir aiogram

# Копируем код и фото
COPY . .

# Запускаем бота
CMD ["python", "main.py"]
