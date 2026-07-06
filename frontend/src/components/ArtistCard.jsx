import { useNavigate } from "react-router-dom";
import { initials } from "../utils/format.js";

export default function ArtistCard({ artist }) {
  const navigate = useNavigate();
  const tracks = artist.tracks ?? artist.recording_count;

  return (
    <div className="card artist-card" onClick={() => navigate(`/artists/${artist.mbid}`)}>
      {artist.image_url ? (
        <img className="artist-photo" src={artist.image_url} alt={artist.name} loading="lazy" />
      ) : (
        <div className="artist-avatar">{initials(artist.name)}</div>
      )}
      <h3>{artist.name}</h3>
      {artist.disambiguation && <span className="dim" style={{ fontSize: "0.8rem" }}>{artist.disambiguation}</span>}
      <div className="meta-row">
        {artist.type && <span className="badge">{artist.type}</span>}
        {artist.country && <span className="badge">📍 {artist.country}</span>}
        {artist.begin_date && <span className="badge">{String(artist.begin_date).slice(0, 4)}</span>}
      </div>
      {tracks != null && (
        <div className="row between mt">
          <span className="badge teal">{tracks} morceaux</span>
          <span className="link-accent" style={{ fontSize: "0.85rem" }}>Voir la fiche →</span>
        </div>
      )}
    </div>
  );
}
