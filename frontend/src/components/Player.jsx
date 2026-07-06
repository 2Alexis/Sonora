import { createContext, useContext, useEffect, useRef, useState } from "react";
import { previewUrl } from "../api/client.js";

// Lecteur audio global : un seul extrait joue à la fois (previews Deezer 30s).
const PlayerContext = createContext(null);

export function PlayerProvider({ children }) {
  const audioRef = useRef(null);
  const [current, setCurrent] = useState(null); // { id, url, title }

  useEffect(() => {
    if (!audioRef.current) audioRef.current = new Audio();
    const audio = audioRef.current;
    const onEnd = () => setCurrent(null);
    audio.addEventListener("ended", onEnd);
    return () => audio.removeEventListener("ended", onEnd);
  }, []);

  function toggle(track) {
    const audio = audioRef.current;
    if (current?.id === track.id) {
      audio.pause();
      setCurrent(null);
      return;
    }
    audio.src = track.url;
    audio.play().catch(() => {});
    setCurrent(track);
  }

  return (
    <PlayerContext.Provider value={{ current, toggle }}>
      {children}
      {current && (
        <div className="now-playing">
          <span className="np-eq"><i /><i /><i /></span>
          <div className="np-text">
            <strong>{current.title}</strong>
            <span className="dim">extrait 30s · Deezer</span>
          </div>
          <button className="btn btn-sm" onClick={() => toggle(current)}>⏸ Stop</button>
        </div>
      )}
    </PlayerContext.Provider>
  );
}

export const usePlayer = () => useContext(PlayerContext);

// Bouton play/pause pour un morceau (désactivé si pas d'extrait Deezer).
export function PlayButton({ track }) {
  const { current, toggle } = usePlayer();
  if (!track.deezer_track_id) {
    return <span className="dim" title="Extrait indisponible" style={{ opacity: 0.4 }}>—</span>;
  }
  const active = current?.id === track.mbid;
  return (
    <button
      className={"play-btn" + (active ? " active" : "")}
      onClick={() => toggle({ id: track.mbid, url: previewUrl(track.mbid), title: track.title })}
      title={active ? "Pause" : "Écouter l'extrait"}
    >
      {active ? "⏸" : "▶"}
    </button>
  );
}
