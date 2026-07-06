"""Endpoints albums / releases."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services import release_service

router = APIRouter(prefix="/releases", tags=["releases"])


@router.get("")
def list_releases(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    return release_service.list_releases(limit=limit, offset=offset)


@router.get("/{mbid}")
def get_release(mbid: str):
    rel = release_service.get_release(mbid)
    if rel is None:
        raise HTTPException(status_code=404, detail="Release non trouvée")
    return rel


@router.get("/{mbid}/recordings")
def get_release_recordings(mbid: str):
    return release_service.get_release_recordings(mbid)


@router.get("/{mbid}/artists")
def get_release_artists(mbid: str):
    return release_service.get_release_artists(mbid)
