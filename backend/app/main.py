"""SONORA — API FastAPI.

Explore le graphe du son : artistes, morceaux, albums et collaborations,
à partir de MusicBrainz, stockés dans Neo4j.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.constraints import apply_schema
from app.db.neo4j_driver import close_driver, verify_connectivity
from app.routers import (
    artists,
    graph,
    imports,
    recordings,
    releases,
    search,
    stats,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("sonora")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Applique le schéma Neo4j au démarrage (tolère une base pas encore prête)."""
    logger.info("Démarrage de %s (%s)", settings.app_name, settings.app_env)
    try:
        if verify_connectivity():
            apply_schema()
        else:
            logger.warning("Neo4j non disponible au démarrage — schéma non appliqué.")
    except Exception as exc:  # ne bloque pas le démarrage de l'API
        logger.warning("Impossible d'appliquer le schéma Neo4j : %s", exc)
    yield
    close_driver()


app = FastAPI(
    title="SONORA API",
    description="Explore le graphe du son — collaborations musicales via MusicBrainz & Neo4j.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers (tous préfixés par /api) ---
for r in (search, imports, artists, recordings, releases, graph, stats):
    app.include_router(r.router, prefix=settings.api_prefix)


@app.get("/health", tags=["meta"])
def health():
    """Healthcheck utilisé par docker-compose / Render."""
    neo4j_ok = verify_connectivity()
    return {
        "status": "ok" if neo4j_ok else "degraded",
        "neo4j": "up" if neo4j_ok else "down",
    }


# --- Service du frontend (déploiement tout-en-un) ---------------------------
# Si un build frontend est présent (image Docker de prod), l'API le sert aussi :
# une seule origine, aucun CORS à configurer. En local (dev), ce dossier n'existe
# pas → l'API se contente d'exposer /api et le front tourne via Vite (:5173).
import os

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

_FRONTEND_DIR = os.path.abspath(
    os.environ.get("FRONTEND_DIR", os.path.join(os.path.dirname(__file__), "..", "static"))
)
_SERVE_FRONTEND = os.path.isfile(os.path.join(_FRONTEND_DIR, "index.html"))

if _SERVE_FRONTEND:
    app.mount("/assets", StaticFiles(directory=os.path.join(_FRONTEND_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        """Sert les fichiers statiques du build, avec repli SPA sur index.html."""
        if full_path.startswith("api") or full_path in ("health", "docs", "openapi.json", "redoc"):
            raise HTTPException(status_code=404)
        candidate = os.path.join(_FRONTEND_DIR, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(_FRONTEND_DIR, "index.html"))
else:
    @app.get("/", tags=["meta"])
    def root():
        return {
            "name": settings.app_name,
            "tagline": "Explore le graphe du son.",
            "docs": "/docs",
            "api": settings.api_prefix,
        }
