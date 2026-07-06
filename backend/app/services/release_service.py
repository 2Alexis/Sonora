"""Requêtes de lecture centrées sur les albums / releases."""
from __future__ import annotations

from typing import Any

from app.db.neo4j_driver import run_query


def list_releases(limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    cypher = """
    MATCH (rel:Release)
    OPTIONAL MATCH (rec:Recording)-[:APPEARS_ON]->(rel)
    WITH rel, count(DISTINCT rec) AS track_count
    RETURN rel.mbid AS mbid, rel.title AS title, rel.date AS date,
           rel.country AS country, rel.status AS status, rel.release_type AS release_type,
           track_count
    ORDER BY rel.date DESC
    SKIP $offset LIMIT $limit
    """
    return run_query(cypher, {"limit": limit, "offset": offset})


def get_release(mbid: str) -> dict[str, Any] | None:
    rows = run_query(
        "MATCH (rel:Release {mbid: $mbid}) RETURN rel {.*} AS rel",
        {"mbid": mbid},
    )
    return rows[0]["rel"] if rows else None


def get_release_recordings(mbid: str) -> list[dict[str, Any]]:
    cypher = """
    MATCH (rec:Recording)-[:APPEARS_ON]->(rel:Release {mbid: $mbid})
    RETURN rec.mbid AS mbid, rec.title AS title, rec.length AS length,
           rec.first_release_date AS first_release_date, rec.popularity AS popularity
    ORDER BY rec.title ASC
    """
    return run_query(cypher, {"mbid": mbid})


def get_release_artists(mbid: str) -> list[dict[str, Any]]:
    cypher = """
    MATCH (a:Artist)-[rel:PERFORMED|FEATURED_ON]->(:Recording)-[:APPEARS_ON]->(r:Release {mbid: $mbid})
    RETURN DISTINCT a.mbid AS mbid, a.name AS name, type(rel) AS role
    """
    return run_query(cypher, {"mbid": mbid})
