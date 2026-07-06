"""Schémas Pydantic : contrats d'entrée/sortie de l'API SONORA."""
from __future__ import annotations

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Recherche MusicBrainz
# --------------------------------------------------------------------------- #
class ArtistSearchResult(BaseModel):
    mbid: str
    name: str
    type: str | None = None
    country: str | None = None
    begin_date: str | None = None
    disambiguation: str | None = None
    score: int | None = None


# --------------------------------------------------------------------------- #
# Nœuds
# --------------------------------------------------------------------------- #
class Artist(BaseModel):
    mbid: str
    name: str
    type: str | None = None
    country: str | None = None
    gender: str | None = None
    begin_date: str | None = None
    end_date: str | None = None
    disambiguation: str | None = None


class Recording(BaseModel):
    mbid: str
    title: str
    length: int | None = None
    first_release_date: str | None = None
    popularity: float | None = None
    source: str = "musicbrainz"


class Release(BaseModel):
    mbid: str
    title: str
    date: str | None = None
    country: str | None = None
    status: str | None = None
    release_type: str | None = None
    cover_url: str | None = None


class Genre(BaseModel):
    name: str
    count: int | None = None


class Area(BaseModel):
    mbid: str | None = None
    name: str
    type: str | None = None


# --------------------------------------------------------------------------- #
# Import
# --------------------------------------------------------------------------- #
class ImportArtistRequest(BaseModel):
    mbid: str = Field(..., description="Identifiant MusicBrainz de l'artiste à importer")
    include_recordings: bool = True
    max_recordings: int | None = Field(
        default=None, description="Surcharge la limite d'import de morceaux"
    )


class ImportSummary(BaseModel):
    artist: Artist
    recordings_imported: int
    releases_imported: int
    collaborators_detected: int
    features_detected: int
    similar_detected: int = 0
    previews_added: int = 0
    message: str


# --------------------------------------------------------------------------- #
# Collaborations & graphe
# --------------------------------------------------------------------------- #
class Collaborator(BaseModel):
    mbid: str
    name: str
    shared_tracks: int


class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # Artist | Recording | Release | Genre | Area | Label


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


# --------------------------------------------------------------------------- #
# Statistiques
# --------------------------------------------------------------------------- #
class StatsOverview(BaseModel):
    artists: int
    recordings: int
    releases: int
    genres: int
    collaborations: int


class TopArtist(BaseModel):
    mbid: str
    name: str
    connections: int


class TopCollaboration(BaseModel):
    source: str
    target: str
    shared_tracks: int


class TopGenre(BaseModel):
    name: str
    artists: int
