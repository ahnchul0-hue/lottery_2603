import { useQuery } from '@tanstack/react-query'
import type { MachineInfo } from '../types/lottery'
import { fetchMachineData } from '../lib/api'

export function useMachineInfo(machine: string) {
  return useQuery<MachineInfo>({
    queryKey: ['machineInfo', machine],
    queryFn: async () => {
      const data = await fetchMachineData(machine)
      return {
        machine: data.machine,
        totalDraws: data.total_draws,
        latestRound:
          data.draws[data.draws.length - 1]?.round_number ?? 0,
      }
    },
    staleTime: Infinity,
    enabled: machine.length > 0,
  })
}
