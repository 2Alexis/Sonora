"""Requêtes de lecture centrées sur les artistes stockés dans Neo4j."""
from __future__ import annotations

from typing import Any

from app.db.neo4j_driver import run_query


def list_artists(limit: int = 50, offset: int = 0, search: str | None = None) -> list[dict[str, Any]]:
    cypher = """
    MATCH (a:Artist)
    WHERE $search IS NULL OR toLower(a.name) CONTAINS toLower($search)
    OPTIONAL MATCH (a)-[:PERFORMED|FEATURED_ON]->(rec:Recording)
    WITH a, count(DISTINCT rec) AS tracks
    RETURN a.mbid AS mbid, a.name AS name, a.type AS type, a.country AS country,
           a.begin_date AS begin_date, a.disambiguation AS disambiguation,
           a.image_url AS image_url, a.popularity AS popularity,
           tracks
    ORDER BY tracks DESC, a.name ASC
    SKIP $offset LIMIT $limit
    """
    return run_query(cypher, {"limit": limit, "offset": offset, "search": search})


def get_artist(mbid: str) -> dict[str, Any] | None:
    cypher = """
    MATCH (a:Artist {mbid: $mbid})
    OPTIONAL MATCH (a)-[:FROM_AREA]->(area:Area)
    OPTIONAL MATCH (a)-[:ASSOCIATED_WITH_GENRE]->(g:Genre)
    OPTIONAL MATCH (a)-[:PERFORMED|FEATURED_ON]->(rec:Recording)
    OPTIONAL MATCH (a)-[:COLLABORATED_WITH]-(collab:Artist)
    OPTIONAL MATCH (a)-[:SIMILAR_TO]-(sim:Artist)
    RETURN a {.*} AS artist,
           area.name AS area,
           collect(DISTINCT g.name) AS genres,
           count(DISTINCT rec) AS recording_count,
           count(DISTINCT collab) AS collaborator_count,
           count(DISTINCT sim) AS similar_count
    """
    rows = run_query(cypher, {"mbid": mbid})
    if not rows:
        return None
    row = rows[0]
    artist = row["artist"]
    artist["area"] = row["area"]
    artist["genres"] = [g for g in row["genres"] if g]
    artist["recording_count"] = row["recording_count"]
    artist["collaborator_count"] = row["collaborator_count"]
    artist["similar_count"] = row["similar_count"]
    return artist


def get_artist_recordings(mbid: str) -> list[dict[str, Any]]:
    cypher = """
    MATCH (a:Artist {mbid: $mbid})-[rel:PERFORMED|FEATURED_ON]->(rec:Recording)
    RETURN rec.mbid AS mbid, rec.title AS title, rec.length AS length,
           rec.first_release_date AS first_release_date, rec.popularity AS popularity,
           rec.deezer_track_id AS deezer_track_id, rec.cover_url AS cover_url,
           rec.deezer_rank AS deezer_rank,
           type(rel) AS role
    ORDER BY coalesce(rec.deezer_rank, 0) DESC, rec.popularity DESC, rec.title ASC
    """
    return run_query(cypher, {"mbid": mbid})


def get_artist_releases(mbid: str) -> list[dict[str, Any]]:
    cypher = """
    MATCH (a:Artist {mbid: $mbid})-[:PERFORMED|FEATURED_ON]->(:Recording)-[:APPEARS_ON]->(rel:Release)
    RETURN DISTINCT rel.mbid AS mbid, rel.title AS title, rel.date AS date,
           rel.country AS country, rel.status AS status, rel.release_type AS release_type
    ORDER BY rel.date DESC
    """
    return run_query(cypher, {"mbid": mbid})


def get_artist_collaborations(mbid: str) -> list[dict[str, Any]]:
    cypher = """
    MATCH (a:Artist {mbid: $mbid})-[r:COLLABORATED_WITH]-(other:Artist)
    RETURN other.mbid AS mbid, other.name AS name, other.image_url AS image_url,
           coalesce(r.shared_tracks, 1) AS shared_tracks
    ORDER BY shared_tracks DESC, other.name ASC
    """
    return run_query(cypher, {"mbid": mbid})


def get_artist_similar(mbid: str) -> list[dict[str, Any]]:
    cypher = """
    MATCH (a:Artist {mbid: $mbid})-[s:SIMILAR_TO]-(other:Artist)
    RETURN other.mbid AS mbid, other.name AS name, other.image_url AS image_url,
           s.source AS source, s.score AS score
    ORDER BY coalesce(s.score, 0) DESC, other.name ASC
    """
    return run_query(cypher, {"mbid": mbid})
