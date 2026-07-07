import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api, errMessage } from "../api/client.js";
import { Loader, ErrorState } from "../components/States.jsx";
import { IconSearch, IconWave } from "../components/Icons.jsx";
import { initials } from "../utils/format.js";

const SUGGESTIONS = ["Daft Punk", "Stromae", "Beyoncé", "Kendrick Lamar", "PNL", "Angèle"];

// Emplacements de la constellation (x%, y%, rotation°) — hors de la zone centrale.
const SLOTS = [
  { x: 10, y: 24, rot: -7, delay: 0 },
  { x: 9, y: 58, rot: 5, delay: 1.4 },
  { x: 8, y: 84, rot: -4, delay: 2.1 },
  { x: 26, y: 10, rot: -5, delay: 0.7 },
  { x: 90, y: 22, rot: 6, delay: 0.3 },
  { x: 91, y: 56, rot: -6, delay: 1.8 },
  { x: 92, y: 82, rot: 4, delay: 2.6 },
  { x: 74, y: 10, rot: 5, delay: 1.1 },
  { x: 34, y: 95, rot: 4, delay: 2.3 },
  { x: 66, y: 94, rot: -5, delay: 0.9 },
];

export default function Search() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [importing, setImporting] = useState({});
  const [floats, setFloats] = useState([]);
  const navigate = useNavigate();

  // Constellation : mélange d'artistes (photo) et de morceaux (pochette).
  useEffect(() => {
    Promise.all([
      api.listArtists({ limit: 30 }).catch(() => []),
      api.listRecordings({ limit: 30 }).catch(() => []),
    ]).then(([artists, recs]) => {
      const a = artists.filter((x) => x.image_url).map((x) => ({
        type: "artist", to: `/artists/${x.mbid}`, img: x.image_url, label: x.name,
      }));
      const r = recs.filter((x) => x.cover_url).map((x) => ({
        type: "track", to: `/recordings/${x.mbid}`, img: x.cover_url, label: x.title,
      }));
      // Interleave a/r pour varier, puis on remplit les slots.
      const mixed = [];
      for (let i = 0; i < Math.max(a.length, r.length); i++) {
        if (a[i]) mixed.push(a[i]);
        if (r[i]) mixed.push(r[i]);
      }
      setFloats(mixed.slice(0, SLOTS.length));
    });
  }, []);

  async function runSearch(term) {
    const query = term ?? q;
    if (!query.trim()) return;
    setQ(query);
    setLoading(true);
    setError(null);
    try {
      setResults(await api.searchArtists(query, 12));
    } catch (e) {
      setError(errMessage(e));
    } finally {
      setLoading(false);
    }
  }

  async function importArtist(mbid) {
    setImporting((s) => ({ ...s, [mbid]: "loading" }));
    try {
      await api.importArtist(mbid);
      setImporting((s) => ({ ...s, [mbid]: "done" }));
    } catch (e) {
      setImporting((s) => ({ ...s, [mbid]: "error" }));
      setError(errMessage(e));
    }
  }

  const showCollage = results === null && !loading;

  return (
    <div className="page">
      <div className="container">
        <div className={"search-hero" + (showCollage ? "" : " compact")}>
          {/* Constellation de cartes (desktop only) */}
          {showCollage && floats.length > 0 && (
            <>
              <svg className="float-lines" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
                {floats.map((_, i) => (
                  <line
                    key={i}
                    x1="50" y1="47" x2={SLOTS[i].x} y2={SLOTS[i].y}
                    stroke="#2dd4bf" strokeWidth="1" strokeDasharray="1 2"
                    vectorEffect="non-scaling-stroke" opacity="0.14"
                  />
                ))}
              </svg>
              {floats.map((f, i) => (
                <div
                  key={f.to + i}
                  className="float-slot"
                  style={{ left: `${SLOTS[i].x}%`, top: `${SLOTS[i].y}%`, animationDelay: `${SLOTS[i].delay}s` }}
                >
                  <Link
                    to={f.to}
                    className={"float-card fc-" + f.type}
                    style={{ "--rot": `${SLOTS[i].rot}deg` }}
                    title={f.label}
                  >
                    <img src={f.img} alt="" loading="lazy" />
                    <div className="fc-meta">
                      <span className="fc-type">{f.type === "artist" ? "Artiste" : "Morceau"}</span>
                      <span className="fc-title">{f.label}</span>
                    </div>
                  </Link>
                </div>
              ))}
            </>
          )}

          {/* Bloc central */}
          <div className="search-center">
            <span className="badge accent"><IconWave width={14} height={14} /> MusicBrainz</span>
            <h1 className="search-title">Rechercher un <span className="gradient-text">artiste</span></h1>
            <p className="muted search-sub">
              Cherche sur MusicBrainz, puis importe l'artiste dans le graphe SONORA —
              morceaux, albums et collaborations inclus.
            </p>

            <form
              className="search-bigbar"
              onSubmit={(e) => { e.preventDefault(); runSearch(); }}
            >
              <IconSearch className="search-bigbar-icon" width={20} height={20} />
              <input
                className="input"
                placeholder="Ex : Daft Punk, Damso, Beyoncé…"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                autoFocus
              />
              <button className="btn btn-primary" type="submit">Rechercher</button>
            </form>

            <div className="search-suggestions">
              <span className="dim">Essaie :</span>
              {SUGGESTIONS.map((s) => (
                <button key={s} className="chip" onClick={() => runSearch(s)}>{s}</button>
              ))}
            </div>
          </div>
        </div>

        {error && <ErrorState message={error} />}
        {loading && <Loader label="Recherche sur MusicBrainz…" />}

        {results && !loading && (
          <div className="grid grid-cards" style={{ marginTop: 8 }}>
            {results.map((r) => {
              const state = importing[r.mbid];
              return (
                <div className="card" key={r.mbid}>
                  <div className="row between">
                    <div className="artist-avatar" style={{ width: 44, height: 44, fontSize: "1.1rem" }}>
                      {initials(r.name)}
                    </div>
                    {r.score != null && <span className="badge accent">score {r.score}</span>}
                  </div>
                  <h3 style={{ margin: "12px 0 6px" }}>{r.name}</h3>
                  {r.disambiguation && <div className="dim" style={{ fontSize: "0.8rem", marginBottom: 8 }}>{r.disambiguation}</div>}
                  <div className="meta-row">
                    {r.type && <span className="badge">{r.type}</span>}
                    {r.country && <span className="badge">📍 {r.country}</span>}
                    {r.begin_date && <span className="badge">{String(r.begin_date).slice(0, 4)}</span>}
                  </div>
                  <div className="mt">
                    {state === "done" ? (
                      <button className="btn btn-sm" style={{ width: "100%" }} onClick={() => navigate(`/artists/${r.mbid}`)}>
                        ✓ Importé — voir la fiche
                      </button>
                    ) : (
                      <button
                        className="btn btn-primary btn-sm"
                        style={{ width: "100%" }}
                        disabled={state === "loading"}
                        onClick={() => importArtist(r.mbid)}
                      >
                        {state === "loading" ? "Import en cours…" : "⬇ Importer dans le graphe"}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
