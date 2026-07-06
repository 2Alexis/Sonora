import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Accueil", end: true },
  { to: "/search", label: "Recherche" },
  { to: "/artists", label: "Artistes" },
  { to: "/recordings", label: "Morceaux" },
  { to: "/graph", label: "Graphe" },
  { to: "/stats", label: "Stats" },
];

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <NavLink to="/" className="brand">
          <img src="/favicon.svg" alt="SONORA" className="brand-logo" />
          <span>SONORA</span>
        </NavLink>
        <div className="nav-links">
          {LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
            >
              {l.label}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  );
}
