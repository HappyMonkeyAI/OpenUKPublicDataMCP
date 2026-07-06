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
  fetchMpByPostcode,
  fetchPostcode,
  fetchRegions,
  fetchTopics,
  fetchWeatherByPostcode,
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

// -------------------------------------------------------------
// Beautiful Componentized Cards for Details Panel
// -------------------------------------------------------------

function LocationDetails({ place }: { place: any }) {
  const data = place?.data;
  if (!data) return null;
  return (
    <div className="detail-card location-card">
      <div className="card-header">
        <h3>📍 Location: {data.postcode}</h3>
        <span className="source-badge" title={place.source?.licence || "Public Data"}>
          {place.source?.id || "postcodes.io"}
        </span>
      </div>
      <div className="card-grid">
        <div className="card-item">
          <span className="label">Country</span>
          <span className="val">{data.country || "N/A"}</span>
        </div>
        <div className="card-item">
          <span className="label">Region</span>
          <span className="val">{data.region || "N/A"}</span>
        </div>
        <div className="card-item">
          <span className="label">District</span>
          <span className="val">{data.admin_district || "N/A"}</span>
        </div>
        <div className="card-item">
          <span className="label">Constituency</span>
          <span className="val">{data.parliamentary_constituency || "N/A"}</span>
        </div>
        <div className="card-item double-col">
          <span className="label">Coordinates</span>
          <span className="val font-mono">
            {Number(data.latitude).toFixed(5)}° N, {Number(data.longitude).toFixed(5)}° E
          </span>
        </div>
      </div>
    </div>
  );
}

function MPDetails({ mp }: { mp: any }) {
  const data = mp?.data;
  const members = data?.members || [];
  if (!members.length) {
    return (
      <div className="detail-card mp-card">
        <div className="card-header">
          <h3>🏛️ Parliamentary MP</h3>
          <span className="source-badge">parliament_uk</span>
        </div>
        <p className="no-data">No active MPs returned for this constituency.</p>
      </div>
    );
  }
  return (
    <div className="detail-card mp-card">
      <div className="card-header">
        <h3>🏛️ Parliamentary MP</h3>
        <span className="source-badge">{mp.source?.id || "parliament_uk"}</span>
      </div>
      {members.map((member: any) => (
        <div key={member.id} className="mp-member">
          {member.thumbnail_url ? (
            <img src={member.thumbnail_url} alt={member.name} className="mp-thumb" />
          ) : (
            <div className="mp-thumb-placeholder">👤</div>
          )}
          <div className="mp-info">
            <h4 className="mp-name">{member.name}</h4>
            <p className="mp-meta">
              <span className="mp-party-badge">{member.party || "Independent"}</span>
            </p>
            <p className="mp-const">
              Constituency: <strong>{member.constituency}</strong>
            </p>
            <p className="mp-house text-small">House: {member.house || "Commons"}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

function WeatherDetails({ weather }: { weather: any }) {
  const wxEnvelope = weather?.forecast || weather;
  const data = wxEnvelope?.data;
  if (!data) return null;
  if (data.status === "auth_required") {
    return (
      <div className="detail-card weather-card auth-warning">
        <div className="card-header">
          <h3>🌦️ Weather (Met Office)</h3>
          <span className="source-badge">met_office</span>
        </div>
        <div className="auth-alert">
          <div className="auth-alert-title">🔑 Optional API Key Needed</div>
          <p className="auth-alert-desc">{data.message}</p>
        </div>
      </div>
    );
  }
  const forecast = data.forecast || [];
  const locationName = data.location_name || "Resolved Location";
  return (
    <div className="detail-card weather-card">
      <div className="card-header">
        <h3>🌦️ Weather Forecast: {locationName}</h3>
        <span className="source-badge">{wxEnvelope.source?.id || "met_office_datahub"}</span>
      </div>
      {forecast.length > 0 ? (
        <div className="forecast-scroll">
          <table className="forecast-table">
            <thead>
              <tr>
                <th>Time (UTC)</th>
                <th>Temp</th>
                <th>Rain</th>
                <th>Wind</th>
              </tr>
            </thead>
            <tbody>
              {forecast.slice(0, 8).map((f: any, idx: number) => {
                const timeStr = f.time
                  ? new Date(f.time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                  : `Point ${idx + 1}`;
                return (
                  <tr key={idx}>
                    <td className="font-mono">{timeStr}</td>
                    <td className="font-mono text-accent">{f.screenTemperature ?? f.temp ?? "N/A"}°C</td>
                    <td className="font-mono">{f.probabilityOfPrecipitation ?? f.rain ?? "N/A"}%</td>
                    <td className="font-mono">{f.windSpeed10m ?? f.windSpeed ?? f.wind ?? "N/A"} mph</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="no-data">No forecast timeseries data returned.</p>
      )}
    </div>
  );
}

function CrimeDetails({ crime }: { crime: any }) {
  const crimeEnvelope = crime?.crime || crime;
  const data = crimeEnvelope?.data;
  const crimes = data?.crimes || [];
  if (!data) return null;
  return (
    <div className="detail-card crime-card">
      <div className="card-header">
        <h3>🚨 Street-Level Crime</h3>
        <span className="source-badge">{crimeEnvelope.source?.id || "police_uk"}</span>
      </div>
      <div className="crime-summary-box">
        <span className="crime-count">{data.count ?? crimes.length}</span>
        <span className="crime-count-label">Recorded crimes near location</span>
      </div>
      {crimes.length > 0 ? (
        <div className="crime-list">
          {crimes.slice(0, 8).map((c: any, idx: number) => (
            <div key={idx} className="crime-item">
              <span className="crime-cat">{c.category?.replace(/-/g, " ")}</span>
              <span className="crime-month font-mono">{c.month}</span>
            </div>
          ))}
        </div>
      ) : (
        <p className="no-data">No recent street crime incidents reported.</p>
      )}
    </div>
  );
}

function CarbonIntensityDetails({ carbon }: { carbon: any }) {
  const data = carbon?.data;
  const item = Array.isArray(data) ? data[0] : data;
  if (!item) return null;
  const intensity = item.intensity;
  return (
    <div className="detail-card carbon-card">
      <div className="card-header">
        <h3>⚡ Grid Carbon Intensity</h3>
        <span className="source-badge">{carbon.source?.id || "national_grid_eso"}</span>
      </div>
      <div className="carbon-grid">
        <div className="carbon-value-box">
          <span className="carbon-value">{intensity?.actual ?? intensity?.forecast ?? "N/A"}</span>
          <span className="carbon-unit">gCO₂/kWh</span>
        </div>
        <div className="carbon-meta">
          <p>
            Grid Index:{" "}
            <span className={`carbon-index-badge index-${intensity?.index}`}>
              {intensity?.index || "unknown"}
            </span>
          </p>
          <p className="text-small muted text-time">
            Active: {item.from ? new Date(item.from).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "Now"}
          </p>
        </div>
      </div>
    </div>
  );
}

function FloodWarningsDetails({ floods }: { floods: any }) {
  const data = floods?.data;
  const warnings = data?.warnings || [];
  if (!data) return null;
  return (
    <div className="detail-card flood-card">
      <div className="card-header">
        <h3>🌊 Active Flood Warnings</h3>
        <span className="source-badge">{floods.source?.id || "ea_flood_monitoring"}</span>
      </div>
      <div className="flood-summary-box">
        <span className="flood-count">{data.count ?? warnings.length}</span>
        <span className="flood-count-label">Warnings in England</span>
      </div>
      {warnings.length > 0 ? (
        <div className="flood-list">
          {warnings.slice(0, 4).map((w: any, idx: number) => (
            <div key={idx} className="flood-item">
              <span className={`flood-severity severity-${w.severity_level || 3}`}>
                {w.severity || "Flood Alert"}
              </span>
              <h4 className="flood-area">{w.description}</h4>
              {w.message && <p className="flood-desc text-small">{w.message}</p>}
            </div>
          ))}
        </div>
      ) : (
        <p className="no-data">No active flood warnings reported.</p>
      )}
    </div>
  );
}

function CpihDetails({ cpih }: { cpih: any }) {
  const data = cpih?.data;
  if (!data) return null;
  return (
    <div className="detail-card economy-card">
      <div className="card-header">
        <h3>📈 Inflation Headline (CPIH)</h3>
        <span className="source-badge">{cpih.source?.id || "ons_beta_api"}</span>
      </div>
      <div className="economy-grid">
        <div className="economy-value-box">
          <span className="economy-value">{data.month_on_month_percent ?? "N/A"}%</span>
          <span className="economy-label">Month-on-Month Change</span>
        </div>
        <div className="economy-meta">
          <p>
            Latest Period: <strong>{data.latest_period || "N/A"}</strong>
          </p>
          <p className="text-small muted">Aggregated index slice from the ONS Beta API.</p>
        </div>
      </div>
    </div>
  );
}

// Reusable Helper to fetch topic facts for a postcode
async function getTopicData(topicId: string, postcode: string): Promise<Record<string, unknown>> {
  const bundle: Record<string, unknown> = {};
  if (topicId === "energy") {
    bundle.carbon = await fetchCarbon();
  } else if (topicId === "environment") {
    bundle.floods = await fetchFloods();
  } else if (topicId === "economy") {
    bundle.cpih = await fetchCpih();
  } else if (topicId === "safety") {
    bundle.crime = await fetchCrimeByPostcode(postcode);
  } else if (topicId === "democracy") {
    bundle.mp = await fetchMpByPostcode(postcode);
  } else if (topicId === "weather") {
    bundle.weather = await fetchWeatherByPostcode(postcode);
  }
  return bundle;
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
  const [showRawJson, setShowRawJson] = useState(false);

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
          const matchedPostcode = String(place.postcode || query);
          const newRegion: Region = {
            id: "search",
            name: String(place.parliamentary_constituency || place.region || "Location"),
            type: "constituency",
            sample_postcode: matchedPostcode,
            lat: Number(place.latitude),
            lng: Number(place.longitude),
          };
          setSelectedRegion(newRegion);
          setConstituency(String(place.parliamentary_constituency || ""));
          
          const bundle: Record<string, unknown> = { place: payload };
          if (selectedTopic) {
            const topicData = await getTopicData(selectedTopic.id, matchedPostcode);
            Object.assign(bundle, topicData);
          }
          setDetail(bundle);
        }
      } else {
        // If it's not a postcode but normal dataset search, clear location details
        setSelectedRegion(null);
        setConstituency(null);
        setDetail(null);
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
      
      if (selectedTopic) {
        const topicData = await getTopicData(selectedTopic.id, region.sample_postcode);
        Object.assign(bundle, topicData);
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
      if (selectedRegion) {
        const place = await fetchPostcode(selectedRegion.sample_postcode);
        bundle.place = place;
        const topicData = await getTopicData(topic.id, selectedRegion.sample_postcode);
        Object.assign(bundle, topicData);
      } else {
        if (topic.id === "energy") bundle.carbon = await fetchCarbon();
        else if (topic.id === "environment") bundle.floods = await fetchFloods();
        else if (topic.id === "economy") bundle.cpih = await fetchCpih();
      }
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
        <div className="brand-section">
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
          <button type="submit" disabled={loading} className="search-btn">
            {loading ? "..." : "Search"}
          </button>
        </form>
      </header>

      {error ? <div className="banner error">{error}</div> : null}

      <main className="layout">
        <aside className="panel">
          <div className="panel-section">
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
          </div>

          <div className="panel-section">
            <h2>Regions</h2>
            <ul className="region-list">
              {regions.map((region) => (
                <li key={region.id}>
                  <button
                    type="button"
                    className={selectedRegion?.id === region.id ? "active" : ""}
                    onClick={() => void drillRegion(region)}
                  >
                    <span className="region-name">{region.name}</span>
                    <small className="region-pc">{region.sample_postcode}</small>
                  </button>
                </li>
              ))}
            </ul>
          </div>
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
                  color: selectedRegion?.id === region.id ? "#6366f1" : "#334155",
                  fillColor: selectedRegion?.id === region.id ? "#818cf8" : "#475569",
                  fillOpacity: 0.65,
                  weight: selectedRegion?.id === region.id ? 3 : 1.5,
                }}
                eventHandlers={{ click: () => void drillRegion(region) }}
              >
                <Popup>
                  <strong className="popup-title">{region.name}</strong>
                  <br />
                  Sample Postcode: <code className="popup-code">{region.sample_postcode}</code>
                </Popup>
              </CircleMarker>
            ))}

            {/* Custom Marker for Searched Postcode */}
            {selectedRegion && selectedRegion.id === "search" && (
              <CircleMarker
                key="search-result-marker"
                center={[selectedRegion.lat, selectedRegion.lng]}
                radius={16}
                pathOptions={{
                  color: "#f43f5e",
                  fillColor: "#fda4af",
                  fillOpacity: 0.75,
                  weight: 3,
                }}
                eventHandlers={{ click: () => void drillRegion(selectedRegion) }}
              >
                <Popup>
                  <strong className="popup-title">{selectedRegion.name}</strong>
                  <br />
                  Postcode: <code className="popup-code">{selectedRegion.sample_postcode}</code> (Searched)
                </Popup>
              </CircleMarker>
            )}

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
          <div className="panel-header">
            <h2>Details</h2>
            {loading && <span className="loader">⌛ Loading...</span>}
          </div>

          {searchResults.length > 0 ? (
            <div className="search-results-box">
              <h3>Search results</h3>
              <ul className="results">
                {searchResults.map((row, index) => (
                  <li key={`${row.kind}-${index}`} className="search-result-item">
                    <span className="pill">{row.kind}</span>
                    {row.link || row.url ? (
                      <a href={row.link || row.url} target="_blank" rel="noreferrer" className="result-link">
                        {row.title}
                      </a>
                    ) : (
                      <strong>{row.title}</strong>
                    )}
                    {row.description ? <p className="result-desc">{row.description}</p> : null}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {detail ? (
            <div className="details-container">
              {detail.place && <LocationDetails place={detail.place} />}
              {detail.mp && <MPDetails mp={detail.mp} />}
              {detail.weather && <WeatherDetails weather={detail.weather} />}
              {detail.crime && <CrimeDetails crime={detail.crime} />}
              {detail.carbon && <CarbonIntensityDetails carbon={detail.carbon} />}
              {detail.floods && <FloodWarningsDetails floods={detail.floods} />}
              {detail.cpih && <CpihDetails cpih={detail.cpih} />}

              {/* Informative Placeholders for Active Topics without location context */}
              {!detail.place && selectedTopic?.id === "democracy" && (
                <div className="detail-card info-card">
                  <p className="muted-msg">🏛️ Select a region on the left or search a postcode above to view Parliamentary constituency representation facts.</p>
                </div>
              )}
              {!detail.place && selectedTopic?.id === "weather" && (
                <div className="detail-card info-card">
                  <p className="muted-msg">🌦️ Select a region on the left or search a postcode above to retrieve weather forecasts.</p>
                </div>
              )}
              {!detail.place && selectedTopic?.id === "safety" && (
                <div className="detail-card info-card">
                  <p className="muted-msg">🚨 Select a region on the left or search a postcode above to pull local street-level crime logs.</p>
                </div>
              )}

              <div className="raw-json-section">
                <button
                  type="button"
                  className="raw-json-btn"
                  onClick={() => setShowRawJson(!showRawJson)}
                >
                  {showRawJson ? "▲ Hide Raw JSON Payload" : "▼ Inspect Raw JSON Payload"}
                </button>
                {showRawJson && (
                  <pre className="json">{JSON.stringify(detail, null, 2)}</pre>
                )}
              </div>
            </div>
          ) : (
            <div className="empty-details">
              <p className="muted">Pick a topic on the left or select a region/postcode to fetch live UK public data.</p>
            </div>
          )}
        </aside>
      </main>
    </div>
  );
}