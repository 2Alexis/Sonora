# 🚀 Déploiement de SONORA (démo en ligne gratuite)

SONORA est une app **multi-services** : base de données graphe (Neo4j) + API (FastAPI) + frontend (React). On la déploie sur 3 services gratuits :

| Composant | Service | Rôle |
|---|---|---|
| Base Neo4j | **Neo4j Aura Free** | stocke le graphe des collaborations |
| API FastAPI | **Render** (Docker) | expose `/api`, lit MusicBrainz/Deezer |
| Frontend React | **Vercel** | interface web statique |

> Tous les fichiers de config nécessaires sont déjà dans le repo (`render.yaml`, `frontend/vercel.json`, `Dockerfile`). Aucun changement de code requis (le code ne dépend pas d'APOC → compatible Aura).

⏱️ Compter ~30-40 min la première fois. Ordre important : **1 → 2 → 3 → 4**.

---

## 1) Base de données — Neo4j Aura Free

1. Va sur **https://neo4j.com/product/auradb/** → **Start Free** → connecte-toi.
2. **Create instance** → **AuraDB Free**.
3. **Télécharge / copie bien** le fichier d'identifiants qui s'affiche **une seule fois** :
   - `NEO4J_URI` (format `neo4j+s://xxxx.databases.neo4j.io`)
   - `NEO4J_USERNAME` (= `neo4j`)
   - `NEO4J_PASSWORD`
4. Attends que l'instance passe en **Running** (~2 min).

---

## 2) Remplir la base (seed) — depuis ta machine

Le seed lit `data/seed_artists.json`, interroge MusicBrainz, enrichit via Deezer/Last.fm et écrit dans Neo4j.

```bash
cd Sonora/backend
pip install -r requirements.txt

# Variables pointant vers ton instance Aura (adapte les valeurs) :
# Windows PowerShell :
$env:NEO4J_URI="neo4j+s://xxxx.databases.neo4j.io"
$env:NEO4J_PASSWORD="ton_mot_de_passe_aura"
$env:MUSICBRAINZ_USER_AGENT="SONORA/1.0 ( ton-email@exemple.com )"

python -m scripts.seed
```

> ⏳ Le seed respecte la limite MusicBrainz (~1 req/s) → laisse-le finir (quelques minutes). Tu peux réduire avec `--max-recordings 10`.

Vérifie dans **Aura → Query** : `MATCH (a:Artist) RETURN count(a)` doit renvoyer > 0.

---

## 3) API — Render (Docker)

1. Va sur **https://render.com** → **Sign in with GitHub**.
2. **New +** → **Blueprint** → sélectionne le repo `2Alexis/Sonora`.
   Render lit `render.yaml` et pré-configure le service `sonora-backend`.
3. Renseigne les **variables secrètes** (onglet Environment) :
   - `NEO4J_URI` = l'URI Aura (`neo4j+s://…`)
   - `NEO4J_PASSWORD` = mot de passe Aura
   - `MUSICBRAINZ_USER_AGENT` = `SONORA/1.0 ( ton-email@exemple.com )`
   - `LASTFM_API_KEY` = (laisse vide, optionnel)
   - `CORS_ORIGINS` = _à remplir à l'étape 4_ (mets provisoirement `*`)
4. **Deploy**. Une fois « Live », note l'URL : `https://sonora-backend.onrender.com`.
5. Teste : ouvre `https://sonora-backend.onrender.com/health` → doit répondre `{"status":"ok"}`.

---

## 4) Frontend — Vercel

1. Va sur **https://vercel.com** → **Add New… → Project** → importe `2Alexis/Sonora`.
2. **Root Directory** : `frontend` (important, le front est dans un sous-dossier).
   Framework **Vite** détecté ; build/output déjà définis dans `vercel.json`.
3. **Environment Variables** → ajoute :
   - `VITE_API_URL` = `https://sonora-backend.onrender.com/api`  *(l'URL Render + `/api`)*
4. **Deploy**. Tu obtiens `https://sonora.vercel.app`.
5. **Reviens sur Render** → mets `CORS_ORIGINS` = `https://sonora.vercel.app` (l'URL Vercel exacte) → le backend redéploie.

---

## ✅ C'est en ligne !

Ouvre `https://sonora.vercel.app` → recherche un artiste, explore le graphe.

### ⚠️ Limites du gratuit (à savoir)
- **Render Free** : le backend « s'endort » après 15 min d'inactivité → 1er appel ~50 s (cold start), puis rapide.
- **Aura Free** : l'instance se met en pause après quelques jours d'inactivité → la relancer d'un clic dans la console Aura.
- Idéal comme **démo de portfolio** ; pas pour de la production intensive.

### 🔗 Ajouter au portfolio
Une fois l'URL Vercel obtenue, ajoute-la comme lien « démo » sur la carte projet SONORA.
