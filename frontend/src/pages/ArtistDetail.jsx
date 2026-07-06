import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { api, errMessage } from "../api/client.js";
import { Loader, ErrorState, EmptyState } from "../components/States.jsx";
import GraphView from "../components/GraphView.jsx";
import { PlayButton } from "../components/Player.jsx";
import { initials, formatDuration, year } from "../utils/format.js";

const TABS = ["Morceaux", "Albums", "Collaborations", "Similaires", "Graphe"];

export default function ArtistDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [artist, setArtist] = useState(null);
  const [recordings, setRecordings] = useState([]);
  const [releases, setReleases] = useState([]);
  const [collabs, setCollabs] = useState([]);
  const [similar, setSimilar] = useState([]);
  const [graph, setGraph] = useState(null);
  const [tab, setTab] = useState("Morceaux");
  const [error, setError] = useState(null);

  useEffect(() => {
    setError(null);
    setArtist(null);
    Promise.all([
      api.getArtist(id),
      api.getArtistRecordings(id),
      api.getArtistReleases(id),
      api.getArtistCollaborations(id),
      api.getArtistSimilar(id),
      api.getArtistGraph(id),
    ])
      .then(([a, r, rel, c, s, g]) => {
        setArtist(a);
        setRecordings(r);
        setReleases(rel);
        setCollabs(c);
        setSimilar(s);
        setGraph(g);
      })
      .catch((e) => setError(errMessage(e)));
  }, [id]);

  if (error) return <div className="page"><div className="container"><ErrorState message={error} /></div></div>;
  if (!artist) return <div className="page"><div className="container"><Loader /></div></div>;

  return (
    <div className="page">
      <div className="container">
        <Link to="/artists" className="link-accent" style={{ fontSize: "0.85rem" }}>← Tous les artistes</Link>

        {/* En-tête */}
        <div className="card mt" style={{ padding: 28 }}>
          <div className="row" style={{ gap: 20 }}>
            {artist.image_url ? (
              <img className="artist-hero-photo" src={artist.image_url} alt={artist.name} />
            ) : (
              <div className="artist-avatar" style={{ width: 76, height: 76, fontSize: "1.9rem", borderRadius: 20 }}>
                {initials(artist.name)}
              </div>
            )}
            <div style={{ flex: 1 }}>
              <h1 style={{ fontSize: "2.2rem" }}>{artist.name}</h1>
              {artist.disambiguation && <p className="muted">{artist.disambiguation}</p>}
              <div className="meta-row mt">
                {artist.type && <span className="badge">{artist.type}</span>}
                {artist.country && <span className="badge">📍 {artist.country}</span>}
                {artist.area && <span className="badge">{artist.area}</span>}
                {artist.begin_date && <span className="badge">Début {year(artist.begin_date)}</span>}
                {artist.end_date && <span className="badge">Fin {year(artist.end_date)}</span>}
              </div>
              {artist.genres?.length > 0 && (
                <div className="meta-row mt">
                  {artist.genres.map((g) => <span className="badge accent" key={g}>{g}</span>)}
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-stats mt-lg">
            <MiniStat value={artist.recording_count} label="Morceaux" />
            <MiniStat value={artist.collaborator_count} label="Collaborateurs" />
            <MiniStat value={artist.similar_count} label="Similaires" />
            <MiniStat value={releases.length} label="Albums" />
            {artist.fans != null && <MiniStat value={formatCount(artist.fans)} label="Fans (Deezer)" />}
            {artist.listeners != null && <MiniStat value={formatCount(artist.listeners)} label="Auditeurs (Last.fm)" />}
          </div>
        </div>

        {/* Onglets */}
        <div className="row mt-lg" style={{ gap: 8 }}>
          {TABS.map((t) => (
            <button
              key={t}
              className={"nav-link" + (tab === t ? " active" : "")}
              style={{ cursor: "pointer", border: "1px solid var(--border)" }}
              onClick={() => setTab(t)}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="mt">
          {tab === "Morceaux" && (
            recordings.length === 0 ? <EmptyState title="Aucun morceau" /> : (
              <table className="table">
                <thead><tr><th></th><th></th><th>Titre</th><th>Durée</th><th>1ère sortie</th><th>Rôle</th></tr></thead>
                <tbody>
                  {recordings.map((r) => (
                    <tr key={r.mbid}>
                      <td><PlayButton track={r} /></td>
                      <td>{r.cover_url ? <img className="cover-thumb" src={r.cover_url} alt="" loading="lazy" /> : null}</td>
                      <td><Link to={`/recordings/${r.mbid}`} className="row-title">{r.title}</Link></td>
                      <td className="muted">{formatDuration(r.length)}</td>
                      <td className="muted">{year(r.first_release_date)}</td>
                      <td>{r.role === "FEATURED_ON" ? <span className="badge teal">feat.</span> : <span className="badge">principal</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          )}

          {tab === "Albums" && (
            releases.length === 0 ? <EmptyState title="Aucun album" /> : (
              <table className="table">
                <thead><tr><th>Titre</th><th>Année</th><th>Pays</th><th>Type</th><th>Statut</th></tr></thead>
                <tbody>
                  {releases.map((r) => (
                    <tr key={r.mbid}>
                      <td>{r.title}</td>
                      <td className="muted">{year(r.date)}</td>
                      <td className="muted">{r.country || "—"}</td>
                      <td>{r.release_type ? <span className="badge">{r.release_type}</span> : "—"}</td>
                      <td className="muted">{r.status || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          )}

          {tab === "Collaborations" && (
            collabs.length === 0 ? <EmptyState title="Aucune collaboration détectée" /> : (
              <div className="grid grid-cards">
                {collabs.map((c) => (
                  <div className="card artist-card" key={c.mbid} onClick={() => navigate(`/artists/${c.mbid}`)}>
                    <div className="row between">
                      <div className="artist-avatar" style={{ width: 42, height: 42, fontSize: "1rem" }}>{initials(c.name)}</div>
                      <span className="badge teal">{c.shared_tracks} en commun</span>
                    </div>
                    <h3 style={{ marginTop: 10 }}>{c.name}</h3>
                    <span className="link-accent" style={{ fontSize: "0.85rem" }}>Voir la fiche →</span>
                  </div>
                ))}
              </div>
            )
          )}

          {tab === "Similaires" && (
            similar.length === 0 ? <EmptyState title="Aucun artiste similaire" hint="Enrichissement Deezer / Last.fm." /> : (
              <div className="grid grid-cards">
                {similar.map((s) => (
                  <div className="card artist-card" key={s.mbid} onClick={() => navigate(`/artists/${s.mbid}`)}>
                    <div className="row between">
                      {s.image_url ? <img className="artist-photo" style={{ width: 42, height: 42 }} src={s.image_url} alt="" />
                        : <div className="artist-avatar" style={{ width: 42, height: 42, fontSize: "1rem" }}>{initials(s.name)}</div>}
                      <span className="badge" style={{ borderColor: "rgba(167,139,250,0.35)", color: "#a78bfa" }}>
                        {s.source}{s.score ? ` · ${Math.round(s.score * 100)}%` : ""}
                      </span>
                    </div>
                    <h3 style={{ marginTop: 10 }}>{s.name}</h3>
                    <span className="link-accent" style={{ fontSize: "0.85rem" }}>Voir la fiche →</span>
                  </div>
                ))}
              </div>
            )
          )}

          {tab === "Graphe" && (
            graph && graph.nodes.length > 0
              ? <GraphView data={graph} height={560} />
              : <EmptyState title="Graphe vide" />
          )}
        </div>
      </div>
    </div>
  );
}

function formatCount(n) {
  if (n == null) return "—";
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(".0", "") + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1).replace(".0", "") + "k";
  return String(n);
}

function MiniStat({ value, label }) {
  return (
    <div className="stat-card" style={{ padding: 16 }}>
      <div className="stat-value gradient-text" style={{ fontSize: "1.8rem" }}>{value ?? 0}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
