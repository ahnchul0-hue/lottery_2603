import { useState, useCallback } from 'react';
import { loadHistory, saveHistory } from '../lib/historyStorage';
import type { SavedPrediction } from '../types/history';

export function useHistoryStorage() {
  const [entries, setEntries] = useState<SavedPrediction[]>(() => loadHistory());

  const addEntry = useCallback((entry: SavedPrediction) => {
    setEntries(prev => {
      const next = [entry, ...prev];
      saveHistory(next);
      return next;
    });
  }, []);

  const updateEntry = useCallback((id: string, patch: Partial<SavedPrediction>) => {
    setEntries(prev => {
      const next = prev.map(e => e.id === id ? { ...e, ...patch } : e);
      saveHistory(next);
      return next;
    });
  }, []);

  const removeEntry = useCallback((id: string) => {
    setEntries(prev => {
      const next = prev.filter(e => e.id !== id);
      saveHistory(next);
      return next;
    });
  }, []);

  return { entries, addEntry, updateEntry, removeEntry };
}
