FROM python:alpine

WORKDIR /app

RUN apk update && apk add --no-cache ca-certificates

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
