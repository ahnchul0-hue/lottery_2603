import type { MachineDataResponse, PredictResponse } from '../types/lottery';

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
): Promise<PredictResponse> {
  const res = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ machine, strategy }),
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch prediction: HTTP ${res.status}`);
  }
  return res.json() as Promise<PredictResponse>;
}
