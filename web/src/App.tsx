import { useEffect, useMemo, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import type { LatLngExpression } from "leaflet";
import {
  ExplorerTopic,
  Region,
  SearchResult,
  fetchCarbon,
  fetchCpih,
  fetchCrimeByPostcode,
  fetchFloods,
  fetchPostcode,
  fetchRegions,
  fetchTopics,
  searchAll,
} from "./api";

const UK_CENTER: LatLngExpression = [54.5, -3.5];

function MapFocus({ lat, lng }: { lat: number; lng: number }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo([lat, lng], 8, { duration: 0.8 });
  }, [lat, lng, map]);
  return null;
}

export default function App() {
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [topics, setTopics] = useState<ExplorerTopic[]>([]);
  const [regions, setRegions] = useState<Region[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<ExplorerTopic | null>(null);
  const [selectedRegion, setSelectedRegion] = useState<Region | null>(null);
  const [detail, setDetail] = useState<Record<string, unknown> | null>(null);
  const [constituency, setConstituency] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const [t, r] = await Promise.all([fetchTopics(), fetchRegions()]);
        setTopics(t.topics);
        setRegions(r.regions);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load explorer metadata");
      }
    })();
  }, []);

  const mapFocus = useMemo(() => {
    if (selectedRegion) {
      return { lat: selectedRegion.lat, lng: selectedRegion.lng };
    }
    return null;
  }, [selectedRegion]);

  async function runSearch(event?: React.FormEvent) {
    event?.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await searchAll(query.trim());
      setSearchResults(data.results);
      const postcodeHit = data.results.find((r) => r.kind === "postcode");
      if (postcodeHit?.payload && typeof postcodeHit.payload === "object") {
        const payload = postcodeHit.payload as { data?: Record<string, unknown> };
        const place = payload.data;
        if (place?.latitude && place?.longitude) {
          setSelectedRegion({
            id: "search",
            name: String(place.parliamentary_constituency || place.region || "Location"),
            type: "constituency",
            sample_postcode: String(place.postcode || query),
            lat: Number(place.latitude),
            lng: Number(place.longitude),
          });
          setConstituency(String(place.parliamentary_constituency || ""));
          setDetail({ place: payload });
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  async function drillRegion(region: Region) {
    setSelectedRegion(region);
    setConstituency(null);
    setLoading(true);
    setError(null);
    try {
      const place = await fetchPostcode(region.sample_postcode);
      const data = place.data as Record<string, unknown> | undefined;
      setConstituency(String(data?.parliamentary_constituency || ""));
      const bundle: Record<string, unknown> = { place };
      if (selectedTopic?.id === "energy") {
        bundle.carbon = await fetchCarbon();
      } else if (selectedTopic?.id === "environment") {
        bundle.floods = await fetchFloods();
      } else if (selectedTopic?.id === "economy") {
        bundle.cpih = await fetchCpih();
      } else if (selectedTopic?.id === "safety") {
        bundle.crime = await fetchCrimeByPostcode(region.sample_postcode);
      }
      setDetail(bundle);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Drill-down failed");
    } finally {
      setLoading(false);
    }
  }

  async function loadTopicFacts(topic: ExplorerTopic) {
    setSelectedTopic(topic);
    setLoading(true);
    setError(null);
    try {
      const bundle: Record<string, unknown> = { topic: topic.id };
      if (topic.id === "energy") bundle.carbon = await fetchCarbon();
      if (topic.id === "environment") bundle.floods = await fetchFloods();
      if (topic.id === "economy") bundle.cpih = await fetchCpih();
      setDetail(bundle);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load topic");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>OpenUK Public Data Explorer</h1>
          <p className="subtitle">
            No-key-first UK data — search facts, browse topics, drill from regions to constituencies.
          </p>
        </div>
        <form className="search" onSubmit={runSearch}>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search GOV.UK, ONS, datasets, or postcode (e.g. SW1A 1AA)"
            aria-label="Search"
          />
          <button type="submit" disabled={loading}>
            {loading ? "…" : "Search"}
          </button>
        </form>
      </header>

      {error ? <div className="banner error">{error}</div> : null}

      <main className="layout">
        <aside className="panel">
          <h2>Topics</h2>
          <ul className="topic-list">
            {topics.map((topic) => (
              <li key={topic.id}>
                <button
                  type="button"
                  className={selectedTopic?.id === topic.id ? "active" : ""}
                  onClick={() => void loadTopicFacts(topic)}
                >
                  <strong>{topic.title}</strong>
                  <span>{topic.summary}</span>
                </button>
              </li>
            ))}
          </ul>

          <h2>Regions</h2>
          <ul className="region-list">
            {regions.map((region) => (
              <li key={region.id}>
                <button type="button" onClick={() => void drillRegion(region)}>
                  {region.name}
                  <small>{region.sample_postcode}</small>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <section className="map-panel">
          <MapContainer center={UK_CENTER} zoom={6} className="map" scrollWheelZoom>
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {regions.map((region) => (
              <CircleMarker
                key={region.id}
                center={[region.lat, region.lng]}
                radius={selectedRegion?.id === region.id ? 14 : 8}
                pathOptions={{
                  color: selectedRegion?.id === region.id ? "#0b5fff" : "#334155",
                  fillOpacity: 0.55,
                }}
                eventHandlers={{ click: () => void drillRegion(region) }}
              >
                <Popup>
                  <strong>{region.name}</strong>
                  <br />
                  Sample: {region.sample_postcode}
                </Popup>
              </CircleMarker>
            ))}
            {mapFocus ? <MapFocus lat={mapFocus.lat} lng={mapFocus.lng} /> : null}
          </MapContainer>
          {constituency ? (
            <p className="constituency">
              Parliamentary constituency (2024): <strong>{constituency}</strong>
            </p>
          ) : (
            <p className="constituency muted">
              Select a region or search a postcode to resolve constituency-level context.
            </p>
          )}
        </section>

        <aside className="panel detail">
          <h2>Details</h2>
          {searchResults.length > 0 ? (
            <>
              <h3>Search results</h3>
              <ul className="results">
                {searchResults.map((row, index) => (
                  <li key={`${row.kind}-${index}`}>
                    <span className="pill">{row.kind}</span>
                    {row.link || row.url ? (
                      <a href={row.link || row.url} target="_blank" rel="noreferrer">
                        {row.title}
                      </a>
                    ) : (
                      <strong>{row.title}</strong>
                    )}
                    {row.description ? <p>{row.description}</p> : null}
                  </li>
                ))}
              </ul>
            </>
          ) : null}
          {detail ? (
            <pre className="json">{JSON.stringify(detail, null, 2)}</pre>
          ) : (
            <p className="muted">Pick a topic or region to load live MCP-backed facts.</p>
          )}
        </aside>
      </main>
    </div>
  );
}