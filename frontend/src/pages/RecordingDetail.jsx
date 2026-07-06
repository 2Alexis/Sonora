import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { api, errMessage } from "../api/client.js";
import { Loader, ErrorState, EmptyState } from "../components/States.jsx";
import { PlayButton } from "../components/Player.jsx";
import { formatDuration, year } from "../utils/format.js";

export default function RecordingDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [rec, setRec] = useState(null);
  const [artists, setArtists] = useState([]);
  const [releases, setReleases] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    setError(null);
    setRec(null);
    Promise.all([
      api.getRecording(id),
      api.getRecordingArtists(id),
      api.getRecordingReleases(id),
    ])
      .then(([r, a, rel]) => {
        setRec(r);
        setArtists(a);
        setReleases(rel);
      })
      .catch((e) => setError(errMessage(e)));
  }, [id]);

  if (error) return <div className="page"><div className="container"><ErrorState message={error} /></div></div>;
  if (!rec) return <div className="page"><div className="container"><Loader /></div></div>;

  return (
    <div className="page">
      <div className="container">
        <Link to="/recordings" className="link-accent" style={{ fontSize: "0.85rem" }}>← Tous les morceaux</Link>

        {/* En-tête morceau */}
        <div className="card mt" style={{ padding: 28 }}>
          <div className="row" style={{ gap: 22 }}>
            {rec.cover_url ? (
              <img src={rec.cover_url} alt="" style={{ width: 120, height: 120, borderRadius: 16, objectFit: "cover", boxShadow: "var(--shadow)" }} />
            ) : (
              <div className="artist-avatar" style={{ width: 120, height: 120, fontSize: "3rem", borderRadius: 16 }}>♪</div>
            )}
            <div style={{ flex: 1 }}>
              <span className="badge accent">Morceau</span>
              <h1 style={{ fontSize: "2.2rem", margin: "10px 0" }}>{rec.title}</h1>
              <div className="meta-row">
                <span className="badge">⏱ {formatDuration(rec.length)}</span>
                {rec.first_release_date && <span className="badge">1ère sortie {year(rec.first_release_date)}</span>}
                {rec.deezer_rank != null && <span className="badge teal">rang Deezer {rec.deezer_rank.toLocaleString("fr-FR")}</span>}
              </div>
              <div className="row mt">
                {rec.deezer_track_id ? (
                  <div className="row">
                    <PlayButton track={rec} />
                    <span className="muted" style={{ fontSize: "0.85rem" }}>Écouter l'extrait 30s</span>
                  </div>
                ) : (
                  <span className="dim" style={{ fontSize: "0.85rem" }}>Aucun extrait disponible pour ce morceau</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Artistes crédités */}
        <h2 className="section-title"><span className="dot" />Artistes crédités</h2>
        {artists.length === 0 ? <EmptyState title="Aucun artiste" /> : (
          <div className="grid grid-cards">
            {artists.map((a) => (
              <div className="card artist-card" key={a.mbid} onClick={() => navigate(`/artists/${a.mbid}`)}>
                <div className="row between">
                  <h3>{a.name}</h3>
                  {a.role === "FEATURED_ON" ? <span className="badge teal">feat.</span> : <span className="badge">principal</span>}
                </div>
                <span className="link-accent" style={{ fontSize: "0.85rem" }}>Voir la fiche →</span>
              </div>
            ))}
          </div>
        )}

        {/* Albums contenant ce morceau */}
        <h2 className="section-title"><span className="dot" />Présent sur</h2>
        {releases.length === 0 ? <EmptyState title="Aucun album" /> : (
          <table className="table">
            <thead><tr><th>Album</th><th>Année</th><th>Pays</th><th>Type</th></tr></thead>
            <tbody>
              {releases.map((r) => (
                <tr key={r.mbid}>
                  <td>{r.title}</td>
                  <td className="muted">{year(r.date)}</td>
                  <td className="muted">{r.country || "—"}</td>
                  <td>{r.release_type ? <span className="badge">{r.release_type}</span> : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
