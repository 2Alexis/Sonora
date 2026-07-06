import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, errMessage } from "../api/client.js";
import { Loader, ErrorState } from "../components/States.jsx";
import { initials } from "../utils/format.js";

const SUGGESTIONS = ["Daft Punk", "Stromae", "Beyoncé", "Kendrick Lamar", "PNL", "Angèle"];

export default function Search() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [importing, setImporting] = useState({});
  const navigate = useNavigate();

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

  return (
    <div className="page">
      <div className="container">
        <div className="page-header">
          <h1>Rechercher un artiste</h1>
          <p>Cherche sur MusicBrainz, puis importe l'artiste dans le graphe SONORA (morceaux, albums et collaborations inclus).</p>
        </div>

        <form
          className="search-bar"
          onSubmit={(e) => {
            e.preventDefault();
            runSearch();
          }}
        >
          <input
            className="input"
            placeholder="Ex : Daft Punk, Damso, Beyoncé…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            autoFocus
          />
          <button className="btn btn-primary" type="submit">Rechercher</button>
        </form>

        <div className="row mt">
          <span className="dim" style={{ fontSize: "0.85rem" }}>Suggestions :</span>
          {SUGGESTIONS.map((s) => (
            <button key={s} className="badge" style={{ cursor: "pointer" }} onClick={() => runSearch(s)}>
              {s}
            </button>
          ))}
        </div>

        {error && <div className="mt-lg"><ErrorState message={error} /></div>}
        {loading && <Loader label="Recherche sur MusicBrainz…" />}

        {results && !loading && (
          <div className="grid grid-cards mt-lg">
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
                  <div className="dim mt" style={{ fontSize: "0.72rem", wordBreak: "break-all" }}>{r.mbid}</div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
