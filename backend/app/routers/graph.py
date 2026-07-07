"""Endpoints graphe (données prêtes pour la visualisation frontend)."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.models.schemas import GraphResponse
from app.services import graph_service

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("", response_model=GraphResponse)
def get_graph(limit: int = Query(300, ge=1, le=5000)):
    """Graphe global des collaborations + similarités entre artistes."""
    return graph_service.get_global_graph(limit=limit)


@router.get("/artists/{mbid}", response_model=GraphResponse)
def get_artist_graph(mbid: str):
    """Ego-network d'un artiste : morceaux, albums, collaborateurs."""
    return graph_service.get_artist_graph(mbid)


@router.get("/collaborations", response_model=GraphResponse)
def get_collaborations_graph(limit: int = Query(300, ge=1, le=5000)):
    """Graphe dédié aux collaborations."""
    return graph_service.get_collaborations_graph(limit=limit)
