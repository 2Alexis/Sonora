"""Normalisation de texte pour rapprocher des noms entre sources (MB, Deezer, Last.fm).

Ex : "JAY‐Z", "Jay-Z", "jay z" -> "jayz". Permet de matcher un artiste similaire
renvoyé par Deezer/Last.fm avec un nœud déjà présent dans Neo4j.
"""
from __future__ import annotations

import re
import unicodedata


def normalize_name(name: str | None) -> str:
    if not name:
        return ""
    # Décompose les accents puis retire les diacritiques.
    decomposed = unicodedata.normalize("NFKD", name)
    without_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    # Minuscules + suppression de tout ce qui n'est pas alphanumérique.
    return re.sub(r"[^a-z0-9]", "", without_accents.lower())
