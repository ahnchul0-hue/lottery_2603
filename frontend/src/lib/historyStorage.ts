import type { SavedPrediction } from '../types/history';

export const STORAGE_KEY = 'lottery-prediction-history';

export function loadHistory(): SavedPrediction[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as SavedPrediction[]) : [];
  } catch {
    return [];
  }
}

export function saveHistory(entries: SavedPrediction[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
  } catch (e) {
    console.error('Failed to save history to localStorage:', e);
  }
}
