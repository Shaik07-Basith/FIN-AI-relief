import { useEffect, useState } from 'react'
import { api } from '../api'

export default function Negotiations() {
  const [negotiations, setNegotiations] = useState([])
  const [history, setHistory] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getNegotiations(), api.getAiHistory()])
      .then(([n, h]) => { setNegotiations(n); setHistory(h) })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="page-loading">Loading AI history…</div>

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <div className="eyebrow">AI negotiations</div>
          <h1>Negotiation letters &amp; activity log</h1>
          <p className="page-lede">
            Every generated strategy and letter is saved here, along with a log of AI-assisted actions.
          </p>
        </div>
      </header>

      {error && <p className="form-error">{error}</p>}

      <section className="card">
        <h2>Generated letters</h2>
        {negotiations.length === 0 ? (
          <p className="empty-state">No negotiation letters generated yet — go to Loans and click "Negotiate".</p>
        ) : (
          negotiations.map((n) => (
            <div key={n.ai_id} className="negotiation-item">
              <div className="negotiation-meta">
                <strong>Loan #{n.loan_id}</strong>
                <span className="stat-hint">{new Date(n.generated_at).toLocaleString()}</span>
              </div>
              <pre className="ai-block">{n.negotiation_strategy}</pre>
              <pre className="ai-block">{n.negotiation_letter}</pre>
            </div>
          ))
        )}
      </section>

      <section className="card">
        <h2>Activity log</h2>
        {history.length === 0 ? (
          <p className="empty-state">No AI activity recorded yet.</p>
        ) : (
          <ul className="history-list">
            {history.map((h) => (
              <li key={h.history_id}>
                <span className="stat-hint">{new Date(h.timestamp).toLocaleString()}</span>
                <span className="history-type">{h.query_type}</span>
                <span>{h.generated_content}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
