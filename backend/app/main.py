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


@app.get("/", tags=["meta"])
def root():
    return {
        "name": settings.app_name,
        "tagline": "Explore le graphe du son.",
        "docs": "/docs",
        "api": settings.api_prefix,
    }


@app.get("/health", tags=["meta"])
def health():
    """Healthcheck utilisé par docker-compose."""
    neo4j_ok = verify_connectivity()
    return {
        "status": "ok" if neo4j_ok else "degraded",
        "neo4j": "up" if neo4j_ok else "down",
    }
