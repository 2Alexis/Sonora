# ============================================================================ #
# SONORA — image tout-en-un (frontend build + backend FastAPI qui le sert).
# Une seule origine → aucun CORS à configurer. Idéale pour un déploiement
# simple (ex : Render) : il ne reste qu'à brancher une base Neo4j (Aura).
# Build depuis la RACINE du repo :  docker build -t sonora .
# ============================================================================ #

# --- Étape 1 : build du frontend (Vite / React) ---------------------------- #
FROM node:20-slim AS frontend
WORKDIR /fe
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# VITE_API_URL non défini -> le client tape "/api" sur la même origine.
RUN npm run build

# --- Étape 2 : backend + service du frontend ------------------------------- #
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FRONTEND_DIR=/app/static

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
# Récupère le build du frontend dans le dossier servi par l'API.
COPY --from=frontend /fe/dist /app/static

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
