# --- SONORA backend (FastAPI) ---
FROM python:3.12-slim

# Empêche Python de bufferiser les logs (utile en conteneur).
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Dépendances (couche cache séparée du code source).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code source.
COPY . .

EXPOSE 8000

# curl pour le healthcheck docker-compose.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
