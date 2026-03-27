import { MACHINE_IDS } from '../types/lottery'
import { useMachineInfo } from '../hooks/useMachineInfo'
import { MachineCard } from './MachineCard'

export function MachineSelector({
  selectedMachine,
  onSelectMachine,
}: {
  selectedMachine: string | null
  onSelectMachine: (machine: string) => void
}) {
  const machine1 = useMachineInfo(MACHINE_IDS[0])
  const machine2 = useMachineInfo(MACHINE_IDS[1])
  const machine3 = useMachineInfo(MACHINE_IDS[2])

  const machines = [machine1, machine2, machine3]

  return (
    <section>
      <h2 className="text-lg font-bold text-text-primary mb-3">호기 선택</h2>
      <div className="flex gap-4">
        {MACHINE_IDS.map((machineId, i) => {
          const query = machines[i]
          return (
            <MachineCard
              key={machineId}
              machineId={machineId}
              totalDraws={query.data?.totalDraws ?? 0}
              latestRound={query.data?.latestRound ?? 0}
              isSelected={machineId === selectedMachine}
              onSelect={() => onSelectMachine(machineId)}
              isLoading={query.isLoading}
            />
          )
        })}
      </div>
    </section>
  )
}
