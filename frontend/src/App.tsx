import { useState } from 'react'
import { MachineSelector } from './components/MachineSelector'
import { PredictionResults } from './components/PredictionResults'
import { StatisticsDashboard } from './components/dashboard/StatisticsDashboard'
import { SavePredictionButton } from './components/history/SavePredictionButton'
import { HistorySection } from './components/history/HistorySection'
import { usePrediction } from './hooks/usePrediction'
import { useHistoryStorage } from './hooks/useHistoryStorage'
import type { SavedPrediction } from './types/history'

function App() {
  const [selectedMachine, setSelectedMachine] = useState<string | null>(null)
  const prediction = usePrediction()
  const { entries, addEntry, updateEntry } = useHistoryStorage()

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
        <h1 className="text-2xl font-bold text-text-primary mb-6">
          로또 예측기
        </h1>

        <MachineSelector
          selectedMachine={selectedMachine}
          onSelectMachine={setSelectedMachine}
        />

        <div className="my-6 text-center">
          <button
            onClick={handlePredict}
            disabled={!selectedMachine || prediction.isPending}
            className="px-8 py-3 bg-accent text-white font-bold rounded-lg hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {prediction.isPending ? '예측 중...' : '번호 예측'}
          </button>
        </div>

        {prediction.isError && (
          <p className="text-destructive text-center mb-4">
            예측 실패: 백엔드 서버를 확인하세요.
          </p>
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
          />
        </div>
      </div>
    </div>
  )
}

export default App
