"""Tests unitaires de la détection de collaborations (aucune dépendance externe)."""
from __future__ import annotations

from app.utils.collaborations import (
    collaboration_pairs,
    parse_artist_credit,
    split_performers_and_features,
    title_suggests_collaboration,
)


def test_title_detects_feat_variants():
    assert title_suggests_collaboration("Get Lucky feat. Pharrell Williams")
    assert title_suggests_collaboration("Ma Meilleure ft. Untel")
    assert title_suggests_collaboration("Song (featuring Someone)")
    assert title_suggests_collaboration("Toi & Moi")
    assert title_suggests_collaboration("A x B")
    assert not title_suggests_collaboration("Around the World")
    assert not title_suggests_collaboration("")


def test_parse_artist_credit_marks_featured():
    credit = [
        {"artist": {"id": "a1", "name": "Daft Punk"}, "joinphrase": " feat. "},
        {"artist": {"id": "a2", "name": "Pharrell Williams"}, "joinphrase": ""},
    ]
    parsed = parse_artist_credit(credit)
    assert len(parsed) == 2
    assert parsed[0]["is_featured"] is False  # 1er artiste = principal
    assert parsed[1]["is_featured"] is True   # précédé de " feat. "


def test_split_performers_and_features():
    credit = [
        {"artist": {"id": "a1", "name": "Main"}, "joinphrase": " feat. "},
        {"artist": {"id": "a2", "name": "Guest"}, "joinphrase": ""},
    ]
    performers, features = split_performers_and_features(parse_artist_credit(credit))
    assert [p["mbid"] for p in performers] == ["a1"]
    assert [f["mbid"] for f in features] == ["a2"]


def test_split_treats_ampersand_as_coperformers():
    # "A & B" sans marqueur de featuring -> deux performers principaux.
    credit = [
        {"artist": {"id": "a1", "name": "A"}, "joinphrase": " & "},
        {"artist": {"id": "a2", "name": "B"}, "joinphrase": ""},
    ]
    performers, features = split_performers_and_features(parse_artist_credit(credit))
    assert len(performers) == 2
    assert features == []


def test_collaboration_pairs_are_unique_and_ordered():
    credit = parse_artist_credit(
        [
            {"artist": {"id": "b", "name": "B"}, "joinphrase": " & "},
            {"artist": {"id": "a", "name": "A"}, "joinphrase": " & "},
            {"artist": {"id": "c", "name": "C"}, "joinphrase": ""},
        ]
    )
    pairs = collaboration_pairs(credit)
    assert pairs == [("a", "b"), ("a", "c"), ("b", "c")]


def test_no_pairs_for_single_artist():
    credit = parse_artist_credit([{"artist": {"id": "solo", "name": "Solo"}, "joinphrase": ""}])
    assert collaboration_pairs(credit) == []
