"""Endpoints artistes (lecture depuis Neo4j)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services import artist_service

router = APIRouter(prefix="/artists", tags=["artists"])


@router.get("")
def list_artists(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    search: str | None = Query(None, description="Filtre par nom (contient)"),
):
    """Liste les artistes importés, triés par nombre de morceaux."""
    return artist_service.list_artists(limit=limit, offset=offset, search=search)


@router.get("/{mbid}")
def get_artist(mbid: str):
    artist = artist_service.get_artist(mbid)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artiste non trouvé dans la base")
    return artist


@router.get("/{mbid}/recordings")
def get_artist_recordings(mbid: str):
    return artist_service.get_artist_recordings(mbid)


@router.get("/{mbid}/releases")
def get_artist_releases(mbid: str):
    return artist_service.get_artist_releases(mbid)


@router.get("/{mbid}/collaborations")
def get_artist_collaborations(mbid: str):
    return artist_service.get_artist_collaborations(mbid)


@router.get("/{mbid}/similar")
def get_artist_similar(mbid: str):
    """Artistes similaires (SIMILAR_TO) issus de Deezer / Last.fm."""
    return artist_service.get_artist_similar(mbid)
