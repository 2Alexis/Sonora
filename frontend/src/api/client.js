import axios from "axios";

// En dev, Vite proxifie /api -> http://localhost:8000 (voir vite.config.js).
// En prod (build), on peut surcharger via VITE_API_URL.
const baseURL = import.meta.env.VITE_API_URL || "/api";

const http = axios.create({ baseURL, timeout: 30000 });

// URL de l'extrait audio d'un morceau (le backend résout une URL Deezer fraîche).
export const previewUrl = (mbid) => `${baseURL}/recordings/${mbid}/preview`;

export const api = {
  // --- Recherche & import ---
  searchArtists: (q, limit = 10) =>
    http.get("/search/artists", { params: { q, limit } }).then((r) => r.data),
  importArtist: (mbid) =>
    http.post("/import/artists", { mbid }).then((r) => r.data),

  // --- Artistes ---
  listArtists: (params = {}) => http.get("/artists", { params }).then((r) => r.data),
  getArtist: (id) => http.get(`/artists/${id}`).then((r) => r.data),
  getArtistRecordings: (id) => http.get(`/artists/${id}/recordings`).then((r) => r.data),
  getArtistReleases: (id) => http.get(`/artists/${id}/releases`).then((r) => r.data),
  getArtistCollaborations: (id) =>
    http.get(`/artists/${id}/collaborations`).then((r) => r.data),
  getArtistSimilar: (id) => http.get(`/artists/${id}/similar`).then((r) => r.data),

  // --- Morceaux ---
  listRecordings: (params = {}) => http.get("/recordings", { params }).then((r) => r.data),
  getRecording: (id) => http.get(`/recordings/${id}`).then((r) => r.data),
  getRecordingArtists: (id) => http.get(`/recordings/${id}/artists`).then((r) => r.data),
  getRecordingReleases: (id) => http.get(`/recordings/${id}/releases`).then((r) => r.data),

  // --- Graphe ---
  getGraph: (limit = 150) => http.get("/graph", { params: { limit } }).then((r) => r.data),
  getArtistGraph: (id) => http.get(`/graph/artists/${id}`).then((r) => r.data),

  // --- Stats ---
  statsOverview: () => http.get("/stats/overview").then((r) => r.data),
  topArtists: (limit = 10) =>
    http.get("/stats/top-artists", { params: { limit } }).then((r) => r.data),
  topCollaborations: (limit = 10) =>
    http.get("/stats/top-collaborations", { params: { limit } }).then((r) => r.data),
  topGenres: (limit = 10) =>
    http.get("/stats/top-genres", { params: { limit } }).then((r) => r.data),
  topRecordings: (limit = 10) =>
    http.get("/stats/top-recordings", { params: { limit } }).then((r) => r.data),
};

// Extrait un message d'erreur lisible depuis une erreur axios.
export function errMessage(e) {
  return e?.response?.data?.detail || e?.message || "Une erreur est survenue.";
}
