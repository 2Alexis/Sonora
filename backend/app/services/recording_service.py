"""Requêtes de lecture centrées sur les enregistrements (Recording)."""
from __future__ import annotations

from typing import Any

from app.db.neo4j_driver import run_query


def list_recordings(limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    cypher = """
    MATCH (rec:Recording)
    OPTIONAL MATCH (a:Artist)-[:PERFORMED|FEATURED_ON]->(rec)
    WITH rec, count(DISTINCT a) AS artist_count
    RETURN rec.mbid AS mbid, rec.title AS title, rec.length AS length,
           rec.first_release_date AS first_release_date, rec.popularity AS popularity,
           rec.deezer_track_id AS deezer_track_id, rec.cover_url AS cover_url,
           rec.deezer_rank AS deezer_rank,
           artist_count
    ORDER BY coalesce(rec.deezer_rank, 0) DESC, rec.popularity DESC, artist_count DESC
    SKIP $offset LIMIT $limit
    """
    return run_query(cypher, {"limit": limit, "offset": offset})


def get_deezer_track_id(mbid: str) -> int | None:
    rows = run_query(
        "MATCH (r:Recording {mbid: $mbid}) RETURN r.deezer_track_id AS id",
        {"mbid": mbid},
    )
    return rows[0]["id"] if rows and rows[0]["id"] is not None else None


def get_recording(mbid: str) -> dict[str, Any] | None:
    rows = run_query(
        "MATCH (rec:Recording {mbid: $mbid}) RETURN rec {.*} AS rec",
        {"mbid": mbid},
    )
    return rows[0]["rec"] if rows else None


def get_recording_artists(mbid: str) -> list[dict[str, Any]]:
    cypher = """
    MATCH (a:Artist)-[rel:PERFORMED|FEATURED_ON]->(rec:Recording {mbid: $mbid})
    RETURN a.mbid AS mbid, a.name AS name, type(rel) AS role
    """
    return run_query(cypher, {"mbid": mbid})


def get_recording_releases(mbid: str) -> list[dict[str, Any]]:
    cypher = """
    MATCH (rec:Recording {mbid: $mbid})-[:APPEARS_ON]->(rel:Release)
    RETURN rel.mbid AS mbid, rel.title AS title, rel.date AS date,
           rel.country AS country, rel.status AS status, rel.release_type AS release_type
    ORDER BY rel.date DESC
    """
    return run_query(cypher, {"mbid": mbid})
