# Użyj oficjalnego obrazu Pythona
FROM python:3.11-slim

# Ustaw katalog roboczy
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc

# Skopiuj pliki do kontenera
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Uruchom aplikację Flask
CMD ["python", "app.py"]
