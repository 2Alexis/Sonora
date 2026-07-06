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
          SONORA · Explore le graphe du son — données{" "}
          <a className="link-accent" href="https://musicbrainz.org" target="_blank" rel="noreferrer">
            MusicBrainz
          </a>{" "}
          · graphe Neo4j
        </div>
      </footer>
    </div>
    </PlayerProvider>
  );
}
