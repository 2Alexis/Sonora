"""Détection des collaborations et featurings.

Deux signaux combinés (cf. cahier des charges, section 5) :
1. STRUCTUREL : plusieurs artistes crédités sur un même enregistrement
   (le champ `artist-credit` de MusicBrainz contient >1 entrée).
2. TEXTUEL : présence de marqueurs (feat., ft., featuring, avec, x, &, vs)
   dans le titre du morceau ou dans les "joinphrase" des crédits.
"""
from __future__ import annotations

import re
from typing import Any

# Marqueurs de COLLABORATION dans un TITRE (large : feat, x, &, avec, vs…).
# Utilisé sur le texte libre d'un titre de morceau.
COLLAB_TITLE_PATTERN = re.compile(
    r"""
    (?:^|\s|\()               # début, espace ou parenthèse ouvrante
    (?:
        feat\.? | ft\.? | featuring | avec |
        with | x | vs\.? | &
    )
    (?:\s|$)                  # suivi d'un espace ou de la fin
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Marqueurs de FEATURING dans une JOINPHRASE de crédit (étroit).
# Convention MusicBrainz : une joinphrase " & " ou " x " = co-crédit à parts
# égales (deux performers), tandis que " feat. " = artiste invité (featured).
FEATURED_JOINPHRASE_PATTERN = re.compile(
    r"feat\.?|ft\.?|featuring", re.IGNORECASE
)


def title_suggests_collaboration(title: str) -> bool:
    """Vrai si le titre contient un marqueur de featuring/collaboration."""
    if not title:
        return False
    return bool(COLLAB_TITLE_PATTERN.search(title))


def parse_artist_credit(artist_credit: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Normalise la liste `artist-credit` de MusicBrainz.

    Retourne une liste de dicts : {mbid, name, joinphrase, is_featured}.
    `is_featured` est déduit de la joinphrase précédente (ex: " feat. ").
    """
    if not artist_credit:
        return []

    credits: list[dict[str, Any]] = []
    previous_joinphrase = ""
    for entry in artist_credit:
        artist = entry.get("artist", {}) or {}
        mbid = artist.get("id")
        if not mbid:
            continue
        joinphrase = entry.get("joinphrase", "") or ""
        credits.append(
            {
                "mbid": mbid,
                "name": artist.get("name") or entry.get("name") or "",
                "joinphrase": joinphrase,
                # Un artiste est "featured" si la joinphrase qui le précède
                # contient un marqueur de featuring (feat./ft./featuring).
                "is_featured": bool(FEATURED_JOINPHRASE_PATTERN.search(previous_joinphrase)),
            }
        )
        previous_joinphrase = joinphrase

    return credits


def split_performers_and_features(
    credits: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Sépare les artistes principaux (PERFORMED) des featurings (FEATURED_ON).

    Convention : le premier artiste crédité est toujours un performer principal.
    Les suivants sont "featured" si leur joinphrase précédente le suggère,
    sinon ils sont considérés comme co-performers (collaboration à parts égales).
    """
    performers: list[dict[str, Any]] = []
    features: list[dict[str, Any]] = []
    for idx, credit in enumerate(credits):
        if idx == 0:
            performers.append(credit)
        elif credit["is_featured"]:
            features.append(credit)
        else:
            performers.append(credit)
    return performers, features


def collaboration_pairs(credits: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """Retourne toutes les paires (mbid_a, mbid_b) d'artistes ayant collaboré.

    Chaque paire est ordonnée (min, max) pour éviter les doublons dirigés.
    Une paire n'est renvoyée que s'il y a au moins 2 artistes distincts.
    """
    mbids = sorted({c["mbid"] for c in credits})
    pairs: list[tuple[str, str]] = []
    for i in range(len(mbids)):
        for j in range(i + 1, len(mbids)):
            pairs.append((mbids[i], mbids[j]))
    return pairs
