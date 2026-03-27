import { useMutation } from '@tanstack/react-query';
import { fetchReflection } from '../lib/api';

export type ReflectRequest = {
  machine: string;
  roundNumber: number;
  comparisonData: object;
  pastReflections?: string[];
};

export function useReflection() {
  return useMutation<string, Error, ReflectRequest>({
    mutationFn: fetchReflection,
  });
}
