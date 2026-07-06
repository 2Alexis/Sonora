"""Endpoints statistiques / analyse data."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.services import stats_service

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview")
def overview():
    """Statistiques globales : nb d'artistes, morceaux, releases, genres, collabs."""
    return stats_service.overview()


@router.get("/top-artists")
def top_artists(limit: int = Query(10, ge=1, le=50)):
    """Artistes les plus connectés."""
    return stats_service.top_artists(limit=limit)


@router.get("/top-collaborations")
def top_collaborations(limit: int = Query(10, ge=1, le=50)):
    """Collaborations les plus fréquentes."""
    return stats_service.top_collaborations(limit=limit)


@router.get("/top-genres")
def top_genres(limit: int = Query(10, ge=1, le=50)):
    """Genres musicaux les plus représentés."""
    return stats_service.top_genres(limit=limit)


@router.get("/top-recordings")
def top_recordings(limit: int = Query(10, ge=1, le=50)):
    """Morceaux les plus populaires (score interne)."""
    return stats_service.top_recordings(limit=limit)
