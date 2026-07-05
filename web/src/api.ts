export type SearchResult = {
  kind: string;
  title?: string;
  link?: string;
  description?: string;
  id?: string;
  url?: string;
  organisation?: string;
  payload?: unknown;
  detail?: string;
};

export type Region = {
  id: string;
  name: string;
  type: string;
  sample_postcode: string;
  lat: number;
  lng: number;
};

export type ExplorerTopic = {
  id: string;
  title: string;
  summary: string;
  tools: string[];
};

const API = "/api";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API}${path}`);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export function searchAll(q: string) {
  return getJson<{ query: string; count: number; results: SearchResult[] }>(
    `/search?q=${encodeURIComponent(q)}`,
  );
}

export function fetchTopics() {
  return getJson<{ topics: ExplorerTopic[]; count: number }>("/explorer/topics");
}

export function fetchRegions() {
  return getJson<{ regions: Region[]; count: number }>("/geo/regions");
}

export function fetchPostcode(postcode: string) {
  return getJson<Record<string, unknown>>(`/postcode/${encodeURIComponent(postcode)}`);
}

export function fetchCarbon() {
  return getJson<Record<string, unknown>>("/carbon");
}

export function fetchFloods() {
  return getJson<Record<string, unknown>>("/floods?limit=8");
}

export function fetchCpih() {
  return getJson<Record<string, unknown>>("/inflation/cpih");
}

export function fetchCrimeByPostcode(postcode: string) {
  return getJson<Record<string, unknown>>(
    `/crime/by-postcode/${encodeURIComponent(postcode)}?limit=8`,
  );
}

export function fetchMpByPostcode(postcode: string) {
  return getJson<Record<string, unknown>>(`/parliament/mp?postcode=${encodeURIComponent(postcode)}`);
}

export function fetchWeatherByPostcode(postcode: string) {
  return getJson<Record<string, unknown>>(
    `/weather/by-postcode/${encodeURIComponent(postcode)}?resolution=hourly`,
  );
}