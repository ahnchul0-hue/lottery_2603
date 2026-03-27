import type { MachineDataResponse, PredictResponse } from '../types/lottery';
import type { HeatmapData } from '../types/statistics';

export const API_BASE = 'http://localhost:8000/api';

export async function fetchMachineData(
  machine: string,
): Promise<MachineDataResponse> {
  const res = await fetch(
    `${API_BASE}/data?machine=${encodeURIComponent(machine)}`,
  );
  if (!res.ok) {
    throw new Error(`Failed to fetch machine data: HTTP ${res.status}`);
  }
  return res.json() as Promise<MachineDataResponse>;
}

export async function fetchPrediction(
  machine: string,
  strategy: string,
  signal?: AbortSignal,
): Promise<PredictResponse> {
  const res = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ machine, strategy }),
    signal,
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch prediction: HTTP ${res.status}`);
  }
  return res.json() as Promise<PredictResponse>;
}

export async function fetchHeatmapData(): Promise<HeatmapData> {
  const res = await fetch(`${API_BASE}/statistics/heatmap`);
  if (!res.ok) {
    throw new Error(`Failed to fetch heatmap data: HTTP ${res.status}`);
  }
  return res.json() as Promise<HeatmapData>;
}

export async function fetchReflection(req: {
  machine: string;
  roundNumber: number;
  comparisonData: object;
  pastReflections?: string[];
}): Promise<string> {
  const res = await fetch(`${API_BASE}/reflect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      machine: req.machine,
      round_number: req.roundNumber,
      comparison_data: req.comparisonData,
      past_reflections: req.pastReflections,
    }),
  });
  if (!res.ok) throw new Error(`Reflection failed: HTTP ${res.status}`);
  const data = (await res.json()) as { reflection: string };
  return data.reflection;
}
