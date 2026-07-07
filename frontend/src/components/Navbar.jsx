import { NavLink } from "react-router-dom";
import Logo from "./Logo.jsx";
import { IconHome, IconSearch, IconNodes, IconWave, IconGraph, IconStats } from "./Icons.jsx";

const LINKS = [
  { to: "/", label: "Accueil", end: true, Icon: IconHome },
  { to: "/search", label: "Recherche", Icon: IconSearch },
  { to: "/artists", label: "Artistes", Icon: IconNodes },
  { to: "/recordings", label: "Morceaux", Icon: IconWave },
  { to: "/graph", label: "Graphe", Icon: IconGraph },
  { to: "/stats", label: "Stats", Icon: IconStats },
];

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <NavLink to="/">
          <Logo />
        </NavLink>
        <div className="nav-links">
          {LINKS.map(({ to, label, end, Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
            >
              <Icon width={16} height={16} />
              {label}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  );
}
