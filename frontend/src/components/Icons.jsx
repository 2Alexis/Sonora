// Jeu d'icônes SVG maison — trait 1.7, style cohérent, thème son/graphe/musique.
// Évite les emojis (rendu incohérent selon l'OS) pour une vraie identité.

const base = {
  width: 20,
  height: 20,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.7,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

export function IconHome(p) {
  return (
    <svg {...base} {...p}>
      <path d="M4 11.5 12 4l8 7.5" />
      <path d="M6 10.5V20h12v-9.5" />
      <path d="M10 20v-5h4v5" />
    </svg>
  );
}

export function IconSearch(p) {
  return (
    <svg {...base} {...p}>
      <circle cx="11" cy="11" r="6.5" />
      <path d="M20 20l-3.8-3.8" />
    </svg>
  );
}

// Nœuds reliés = artistes / graphe
export function IconNodes(p) {
  return (
    <svg {...base} {...p}>
      <circle cx="6" cy="7" r="2.4" />
      <circle cx="18" cy="6" r="2.4" />
      <circle cx="12" cy="17" r="2.4" />
      <path d="M7.9 8.4 10.4 15M16.4 7.6 13.4 15.4M8.3 7 15.7 6.3" />
    </svg>
  );
}

// Onde sonore = morceaux
export function IconWave(p) {
  return (
    <svg {...base} {...p}>
      <path d="M3 12h2M19 12h2" />
      <path d="M7 8v8M11 4v16M15 7v10" />
    </svg>
  );
}

// Graphe/réseau (page graphe)
export function IconGraph(p) {
  return (
    <svg {...base} {...p}>
      <circle cx="5" cy="6" r="2" />
      <circle cx="19" cy="8" r="2" />
      <circle cx="9" cy="18" r="2" />
      <circle cx="17" cy="17" r="2" />
      <path d="M6.7 7 7.6 16M10.9 17.3 15.1 16.7M10.7 17 17.2 9.2M7 6.4 17 7.6" />
    </svg>
  );
}

// Barres de stats / égaliseur
export function IconStats(p) {
  return (
    <svg {...base} {...p}>
      <path d="M5 20V11M12 20V4M19 20v-6" />
    </svg>
  );
}

export function IconPlay(p) {
  return (
    <svg {...base} {...p}>
      <path d="M8 5.5v13l11-6.5z" />
    </svg>
  );
}

// Disque vinyle = collaboration / release
export function IconDisc(p) {
  return (
    <svg {...base} {...p}>
      <circle cx="12" cy="12" r="8.5" />
      <circle cx="12" cy="12" r="2.2" />
    </svg>
  );
}

// Micro = artiste / featuring
export function IconMic(p) {
  return (
    <svg {...base} {...p}>
      <rect x="9" y="3" width="6" height="11" rx="3" />
      <path d="M6 11a6 6 0 0 0 12 0M12 17v3M9 20h6" />
    </svg>
  );
}
