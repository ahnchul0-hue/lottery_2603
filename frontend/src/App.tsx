import { useState } from 'react'
import { MachineSelector } from './components/MachineSelector'
import { PredictionResults } from './components/PredictionResults'
import { ThemeToggle } from './components/ThemeToggle'
import { Disclaimer } from './components/Disclaimer'
import { StatisticsDashboard } from './components/dashboard/StatisticsDashboard'
import { SavePredictionButton } from './components/history/SavePredictionButton'
import { HistorySection } from './components/history/HistorySection'
import { usePrediction } from './hooks/usePrediction'
import { useHistoryStorage } from './hooks/useHistoryStorage'
import { useTheme } from './hooks/useTheme'
import type { SavedPrediction } from './types/history'

function App() {
  const [selectedMachine, setSelectedMachine] = useState<string | null>(null)
  const { cancelPrediction, ...prediction } = usePrediction()
  const { entries, addEntry, updateEntry, removeEntry } = useHistoryStorage()
  const { theme, toggle } = useTheme()

  const handleMachineChange = (machine: string) => {
    cancelPrediction()
    setSelectedMachine(machine)
  }

  const handlePredict = () => {
    if (selectedMachine) {
      prediction.mutate(selectedMachine)
    }
  }

  const handleSave = (roundNumber: number) => {
    if (!selectedMachine || !prediction.data) return
    const newEntry: SavedPrediction = {
      id: crypto.randomUUID(),
      roundNumber,
      machine: selectedMachine,
      date: new Date().toISOString().split('T')[0],
      predictions: prediction.data.map(r => ({
        strategy: r.strategy,
        games: r.games,
      })),
    }
    addEntry(newEntry)
  }

  return (
    <div className="min-h-screen bg-surface">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-text-primary">
            로또 예측기
          </h1>
          <ThemeToggle theme={theme} onToggle={toggle} />
        </div>

        <MachineSelector
          selectedMachine={selectedMachine}
          onSelectMachine={handleMachineChange}
        />

        <div className="my-6 text-center">
          <button
            onClick={handlePredict}
            disabled={!selectedMachine || prediction.isPending}
            className="px-8 py-3 bg-accent text-white font-bold rounded-lg hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors inline-flex items-center gap-2"
          >
            {prediction.isPending && (
              <svg className="animate-spin w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            )}
            {prediction.isPending ? '예측 중...' : '번호 예측'}
          </button>
        </div>

        {prediction.isError && (
          <p className="text-destructive text-center mb-4">
            예측 실패: 백엔드 서버를 확인하세요.
          </p>
        )}

        {prediction.isPending && (
          <div className="text-center py-12">
            <svg className="animate-spin w-8 h-8 mx-auto text-accent mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <p className="text-text-secondary font-bold">5가지 전략으로 예측 번호를 생성하고 있습니다...</p>
          </div>
        )}

        {prediction.data && <PredictionResults results={prediction.data} />}

        {prediction.data && selectedMachine && (
          <SavePredictionButton
            onSave={handleSave}
            disabled={!prediction.data}
          />
        )}

        {/* Dashboard section separator (per D-03) */}
        <div className="border-t border-border mt-8 pt-8">
          <h2 className="text-xl font-bold text-text-primary mb-4">
            통계 분석
          </h2>
          <StatisticsDashboard machine={selectedMachine} />
        </div>

        {/* History section separator */}
        <div className="border-t border-border mt-8 pt-8">
          <h2 className="text-xl font-bold text-text-primary mb-4">
            예측 이력
          </h2>
          <HistorySection
            entries={entries}
            onUpdateEntry={updateEntry}
            onRemoveEntry={removeEntry}
          />
        </div>

        <Disclaimer />
      </div>
    </div>
  )
}

export default App
