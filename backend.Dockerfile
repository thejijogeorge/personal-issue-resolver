FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/main.py .
COPY ai_clients.py .
COPY config.py .
COPY database.py .
COPY vectordatabase.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]