# 🗺️ Modèle de données SONORA (Neo4j)

Ce document décrit le graphe de propriétés utilisé par SONORA, les choix de
modélisation et les garanties de qualité des données.

## Pourquoi un graphe ?

Les relations musicales (collaborations, featurings, appartenance à un album,
genre, provenance géographique) forment naturellement un **réseau**. Une base
relationnelle imposerait de multiples tables de jointure et des requêtes
récursives coûteuses pour répondre à « quel chemin relie l'artiste A à
l'artiste B ? ». Neo4j traite ces parcours comme des opérations natives.

## Sources de données

| Source | Rôle | Auth |
|--------|------|------|
| **MusicBrainz** | Colonne vertébrale du graphe : artistes, morceaux, albums, crédits, collaborations (MBID = clé anti-doublon) | User-Agent |
| **Deezer** | Enrichissement : image artiste, nb de fans, extraits audio 30s, pochettes, artistes similaires | Aucune |
| **Last.fm** | Enrichissement (optionnel) : artistes similaires (score), auditeurs/lectures, tags | Clé gratuite |

## Nœuds

| Label       | Clé unique   | Propriétés principales |
|-------------|--------------|------------------------|
| `Artist`    | `mbid`       | `name`, `type`, `country`, `gender`, `begin_date`, `end_date`, `disambiguation`, `image_url`*, `fans`*, `listeners`*, `popularity`* |
| `Recording` | `mbid`       | `title`, `length` (ms), `first_release_date`, `popularity`, `source`, `preview_url`*, `cover_url`*, `deezer_rank`* |
| `Release`   | `mbid`       | `title`, `date`, `country`, `status`, `release_type` |
| `Label`     | `mbid`       | `name`, `country` |
| `Genre`     | `name`       | `name` (normalisé en minuscules) |
| `Area`      | `mbid`/`name`| `name`, `type` |

> `*` = champs ajoutés par l'enrichissement Deezer / Last.fm. `popularity` d'un
> artiste = nb de fans Deezer (ou auditeurs Last.fm à défaut), une popularité
> **réelle** et non plus un proxy.

> **`popularity`** est un *score interne* : proxy simple = nombre de releases sur
> lesquelles le morceau apparaît. Plus un titre est réédité / compilé, plus il
> est considéré comme populaire. La source (`musicbrainz`) est tracée sur chaque
> `Recording` (règle « source de récupération »).

## Relations

```
(:Artist)   -[:PERFORMED]->            (:Recording)
(:Artist)   -[:FEATURED_ON]->          (:Recording)
(:Artist)   -[:COLLABORATED_WITH]-     (:Artist)     // non dirigée, {shared_tracks}
(:Artist)   -[:SIMILAR_TO]-            (:Artist)     // non dirigée, {source, score}
(:Recording)-[:APPEARS_ON]->           (:Release)
(:Release)  -[:RELEASED_BY]->          (:Label)
(:Artist)   -[:ASSOCIATED_WITH_GENRE]->(:Genre)      // {count}
(:Artist)   -[:FROM_AREA]->            (:Area)
(:Release)  -[:RELEASED_IN]->          (:Area)
```

> **`COLLABORATED_WITH` vs `SIMILAR_TO`** — distinction volontaire et importante :
> `COLLABORATED_WITH` est une **vraie collaboration** (artistes co-crédités sur un
> morceau, données factuelles MusicBrainz). `SIMILAR_TO` est une **recommandation**
> (artistes similaires selon Deezer/Last.fm) — ce n'est PAS une collaboration.
> Les deux sont séparées pour que l'analyse des collaborations reste honnête.
> `SIMILAR_TO` ne relie que des artistes déjà présents dans le graphe (modèle
> propre, tout reste indexé par MBID).

### Schéma visuel

```
              FROM_AREA                    ASSOCIATED_WITH_GENRE
   (Area) <------------- (Artist) -------------------------> (Genre)
     ^                    |     \
     |                    |      \  COLLABORATED_WITH
     | RELEASED_IN        |       \--------------------> (Artist)
     |          PERFORMED |  FEATURED_ON
   (Release) <----------- (Recording) <----- (Artist)
        ^   APPEARS_ON        |
        |                     |
   RELEASED_BY                |
        |                     |
     (Label)                  |
```

## Détection des collaborations

Deux signaux combinés (`app/utils/collaborations.py`) :

1. **Structurel** — plusieurs artistes dans le champ `artist-credit` d'un même
   enregistrement ⇒ une relation `COLLABORATED_WITH` est créée pour **chaque
   paire** d'artistes, avec un compteur `shared_tracks` incrémenté à chaque
   morceau commun.
2. **Textuel** — marqueurs `feat.`, `ft.`, `featuring`, `avec`, `x`, `&`, `vs`
   détectés dans le titre ou dans les `joinphrase` des crédits. Le premier
   artiste crédité est toujours un `PERFORMED` ; un artiste précédé d'un marqueur
   de featuring devient `FEATURED_ON`.

## Qualité des données

| Règle | Implémentation |
|-------|----------------|
| Pas de doublons | Contraintes d'unicité sur `mbid` + `MERGE` systématique |
| Normalisation | Genres en minuscules, dates ISO conservées telles quelles |
| Données manquantes | `coalesce()` en écriture (ne jamais écraser une valeur par `null`) |
| Erreurs API | Retries + backoff sur 429/503, exceptions typées `MusicBrainzError` |
| Rate limiting | 1 requête/s sérialisée via verrou global côté client |

## Limites connues

- **Areas par pays** : les releases sont rattachées à une `Area` créée par *nom
  de pays* (code ISO), qui peut différer de l'`Area` d'origine d'un artiste
  (nom complet). Une réconciliation ISO → nom complet est une amélioration
  possible.
- **Profondeur d'import bornée** (`IMPORT_MAX_RECORDINGS`) pour rester poli
  envers l'API MusicBrainz — le graphe est un échantillon représentatif, pas un
  miroir exhaustif.
- **Labels** : le nœud `Label` et la relation `RELEASED_BY` sont modélisés ;
  leur peuplement complet nécessite un lookup release additionnel (extension).

## Requêtes Cypher d'exemple

```cypher
// Chemin le plus court entre deux artistes
MATCH p = shortestPath(
  (a:Artist {name: "Daft Punk"})-[:COLLABORATED_WITH*..6]-(b:Artist {name: "Jay-Z"})
)
RETURN p;

// Artistes les plus connectés
MATCH (a:Artist)-[:COLLABORATED_WITH]-(x)
RETURN a.name, count(x) AS degre ORDER BY degre DESC LIMIT 10;

// Morceaux qui font le pont entre plusieurs artistes
MATCH (a:Artist)-[:PERFORMED|FEATURED_ON]->(r:Recording)<-[:PERFORMED|FEATURED_ON]-(b:Artist)
WHERE a <> b
RETURN r.title, count(DISTINCT a) + count(DISTINCT b) AS artistes ORDER BY artistes DESC LIMIT 10;
```
