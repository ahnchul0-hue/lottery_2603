import { useEffect, useState } from 'react'

const API_BASE = 'http://localhost:8000/api'

function App() {
  const [health, setHealth] = useState<{
    status: string
    data_loaded: boolean
    total_records: number
  } | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(setHealth)
      .catch((err) => setError(err.message))
  }, [])

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center">
      <div className="max-w-[400px] w-full mx-4 bg-card p-8 rounded-xl shadow-md border border-border">
        <h1 className="text-2xl font-bold leading-tight text-text-primary mb-6">
          Lottery Predictor
        </h1>
        <div className="space-y-3 text-left">
          {health === null && error === null && (
            <p className="text-text-secondary">Connecting to backend...</p>
          )}
          {health !== null && (
            <>
              <p className="text-text-primary">
                <span className="inline-block w-2 h-2 rounded-full bg-success mr-2"></span>
                Status: Connected
              </p>
              <p className="text-text-primary">
                Data loaded: {health.total_records} records
              </p>
            </>
          )}
          {error !== null && (
            <>
              <p className="text-destructive font-bold">
                Backend Connection Failed
              </p>
              <p className="text-text-secondary">
                Could not reach the backend server. Make sure FastAPI is running on port 8000.
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
