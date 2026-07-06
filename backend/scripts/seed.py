"""Script d'amorçage : peuple Neo4j avec un jeu d'artistes de référence.

Usage (depuis backend/) :
    python -m scripts.seed
    python -m scripts.seed --file ../data/seed_artists.json --max-recordings 15

Respecte automatiquement le rate limit MusicBrainz (client partagé).
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Permet de lancer le script depuis n'importe où en ajoutant backend/ au path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.clients.musicbrainz import MusicBrainzError, get_musicbrainz_client  # noqa: E402
from app.db.constraints import apply_schema  # noqa: E402
from app.db.neo4j_driver import verify_connectivity  # noqa: E402
from app.services import enrichment_service, import_service, search_service  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("sonora.seed")

DEFAULT_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "seed_artists.json"


def resolve_mbid(entry: dict) -> str | None:
    """Retourne le MBID d'une entrée : explicite si fourni, sinon via recherche."""
    if entry.get("mbid"):
        return entry["mbid"]
    name = entry.get("name")
    if not name:
        return None
    results = search_service.search_artists(name, limit=1)
    if results:
        logger.info("  → « %s » résolu en %s (%s)", name, results[0].mbid, results[0].name)
        return results[0].mbid
    logger.warning("  → Aucun résultat MusicBrainz pour « %s »", name)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Amorçage de la base SONORA")
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE, help="Fichier JSON d'artistes")
    parser.add_argument("--max-recordings", type=int, default=None, help="Limite de morceaux/artiste")
    args = parser.parse_args()

    if not verify_connectivity():
        logger.error("Neo4j injoignable. Lance d'abord `docker compose up -d neo4j`.")
        return 1
    apply_schema()

    data = json.loads(args.file.read_text(encoding="utf-8"))
    artists = data.get("artists", [])
    logger.info("Amorçage de %d artistes depuis %s", len(artists), args.file.name)

    imported = 0
    for entry in artists:
        label = entry.get("name") or entry.get("mbid")
        logger.info("Import de « %s »…", label)
        try:
            mbid = resolve_mbid(entry)
            if not mbid:
                continue
            summary = import_service.import_artist(mbid, max_recordings=args.max_recordings)
            logger.info(
                "  ✓ %s : %d morceaux, %d releases, %d collabs",
                summary.artist.name,
                summary.recordings_imported,
                summary.releases_imported,
                summary.collaborators_detected,
            )
            imported += 1
        except MusicBrainzError as exc:
            logger.error("  ✗ Échec pour « %s » : %s", label, exc)

    # Passe finale : connecte les artistes similaires entre eux (toute la base est
    # maintenant peuplée, donc les liens SIMILAR_TO peuvent se former dans les 2 sens).
    logger.info("Re-liaison des artistes similaires (Deezer/Last.fm)…")
    links = enrichment_service.relink_all_similar()
    logger.info("SIMILAR_TO : %d liens créés.", links)

    get_musicbrainz_client().close()
    logger.info("Terminé : %d/%d artistes importés.", imported, len(artists))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
