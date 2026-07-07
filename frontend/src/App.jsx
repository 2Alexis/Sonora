import { Routes, Route } from "react-router-dom";
import { PlayerProvider } from "./components/Player.jsx";
import Navbar from "./components/Navbar.jsx";
import Home from "./pages/Home.jsx";
import Search from "./pages/Search.jsx";
import Artists from "./pages/Artists.jsx";
import ArtistDetail from "./pages/ArtistDetail.jsx";
import Recordings from "./pages/Recordings.jsx";
import RecordingDetail from "./pages/RecordingDetail.jsx";
import Graph from "./pages/Graph.jsx";
import Stats from "./pages/Stats.jsx";

export default function App() {
  return (
    <PlayerProvider>
    <div className="layout">
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<Search />} />
        <Route path="/artists" element={<Artists />} />
        <Route path="/artists/:id" element={<ArtistDetail />} />
        <Route path="/recordings" element={<Recordings />} />
        <Route path="/recordings/:id" element={<RecordingDetail />} />
        <Route path="/graph" element={<Graph />} />
        <Route path="/stats" element={<Stats />} />
      </Routes>
      <footer className="footer">
        <div className="container">
          <svg className="footer-wave" width="120" height="20" viewBox="0 0 120 20" fill="none" aria-hidden="true">
            <path d="M2 10h10l4-6 5 12 4-9 4 5 5-8 4 10 5-5 4 3 6-4h48" stroke="url(#fw)" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
            <defs>
              <linearGradient id="fw" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0" stopColor="#FF6B4A" />
                <stop offset="0.6" stopColor="#FFB347" />
                <stop offset="1" stopColor="#2DD4BF" />
              </linearGradient>
            </defs>
          </svg>
          <div>
            <span className="brand-word" style={{ fontSize: "0.9rem" }}>SON<span className="brand-o">O</span>RA</span>
            {" · "}Explore le graphe du son — données{" "}
            <a className="link-accent" href="https://musicbrainz.org" target="_blank" rel="noreferrer">MusicBrainz</a>
            {" · "}enrichi{" "}
            <a className="link-accent" href="https://developers.deezer.com" target="_blank" rel="noreferrer">Deezer</a>
            {" · "}graphe Neo4j
          </div>
        </div>
      </footer>
    </div>
    </PlayerProvider>
  );
}
