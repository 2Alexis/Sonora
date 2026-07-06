"""Construction des graphes pour la visualisation frontend.

Format de sortie standardisé : { nodes: [...], edges: [...] } directement
consommable par des libs comme react-force-graph / cytoscape / vis-network.
"""
from __future__ import annotations

from typing import Any

from app.db.neo4j_driver import run_query
from app.models.schemas import GraphEdge, GraphNode, GraphResponse


def _build_response(rows: list[dict[str, Any]]) -> GraphResponse:
    """Agrège des lignes {s_id,s_label,s_type,t_id,t_label,t_type,rel} en graphe dédupliqué."""
    nodes: dict[str, GraphNode] = {}
    edges: dict[tuple[str, str, str], GraphEdge] = {}

    for row in rows:
        for prefix in ("s", "t"):
            nid = row.get(f"{prefix}_id")
            if nid and nid not in nodes:
                nodes[nid] = GraphNode(
                    id=nid,
                    label=row.get(f"{prefix}_label") or nid,
                    type=row.get(f"{prefix}_type") or "Unknown",
                )
        s, t, rel = row.get("s_id"), row.get("t_id"), row.get("rel")
        if s and t and rel:
            key = (s, t, rel)
            edges.setdefault(key, GraphEdge(source=s, target=t, type=rel))

    return GraphResponse(nodes=list(nodes.values()), edges=list(edges.values()))


def get_global_graph(limit: int = 150) -> GraphResponse:
    """Vue d'ensemble : réseau d'artistes reliés par collaborations ET similarités."""
    cypher = """
    MATCH (a:Artist)-[r:COLLABORATED_WITH|SIMILAR_TO]-(b:Artist)
    WITH a, b, r WHERE a.mbid < b.mbid
    RETURN a.mbid AS s_id, a.name AS s_label, 'Artist' AS s_type,
           b.mbid AS t_id, b.name AS t_label, 'Artist' AS t_type,
           type(r) AS rel
    LIMIT $limit
    """
    return _build_response(run_query(cypher, {"limit": limit}))


def get_artist_graph(mbid: str, depth: int = 1) -> GraphResponse:
    """Ego-network d'un artiste : ses morceaux, collaborateurs et albums."""
    cypher = """
    MATCH (a:Artist {mbid: $mbid})
    OPTIONAL MATCH (a)-[pr:PERFORMED|FEATURED_ON]->(rec:Recording)
    OPTIONAL MATCH (rec)-[:APPEARS_ON]->(rel:Release)
    OPTIONAL MATCH (a)-[:COLLABORATED_WITH]-(collab:Artist)
    WITH a, collect(DISTINCT {rec: rec, role: type(pr)}) AS recs,
         collect(DISTINCT rel) AS rels, collect(DISTINCT collab) AS collabs
    UNWIND recs AS rc
    WITH a, rc, rels, collabs WHERE rc.rec IS NOT NULL
    RETURN a.mbid AS s_id, a.name AS s_label, 'Artist' AS s_type,
           rc.rec.mbid AS t_id, rc.rec.title AS t_label, 'Recording' AS t_type,
           rc.role AS rel
    """
    rows = run_query(cypher, {"mbid": mbid})

    # Ajout des artistes liés (collaborations + similarités).
    collab_rows = run_query(
        """
        MATCH (a:Artist {mbid: $mbid})-[r:COLLABORATED_WITH|SIMILAR_TO]-(c:Artist)
        RETURN a.mbid AS s_id, a.name AS s_label, 'Artist' AS s_type,
               c.mbid AS t_id, c.name AS t_label, 'Artist' AS t_type,
               type(r) AS rel
        """,
        {"mbid": mbid},
    )

    # Ajout des albums rattachés aux morceaux.
    release_rows = run_query(
        """
        MATCH (a:Artist {mbid: $mbid})-[:PERFORMED|FEATURED_ON]->(rec:Recording)-[:APPEARS_ON]->(rel:Release)
        RETURN rec.mbid AS s_id, rec.title AS s_label, 'Recording' AS s_type,
               rel.mbid AS t_id, rel.title AS t_label, 'Release' AS t_type,
               'APPEARS_ON' AS rel
        """,
        {"mbid": mbid},
    )

    return _build_response(rows + collab_rows + release_rows)


def get_collaborations_graph(limit: int = 200) -> GraphResponse:
    """Graphe global des collaborations (alias sémantique de get_global_graph)."""
    return get_global_graph(limit=limit)
