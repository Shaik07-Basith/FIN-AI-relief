import { useEffect, useState } from 'react'
import { api } from '../api'
import Pill from '../components/Pill'

export default function Settlements() {
  const [settlements, setSettlements] = useState([])
  const [priority, setPriority] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = (p) => {
    setLoading(true)
    api.getSettlements(p || undefined)
      .then(setSettlements)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load('') }, [])

  const currency = (n) => `₹${Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <div className="eyebrow">Settlements</div>
          <h1>Settlement predictions</h1>
          <p className="page-lede">Every loan update generates a fresh, rule-based settlement recommendation.</p>
        </div>
        <select
          value={priority}
          onChange={(e) => { setPriority(e.target.value); load(e.target.value) }}
          className="select"
        >
          <option value="">All priorities</option>
          <option value="High">High priority</option>
          <option value="Medium">Medium priority</option>
          <option value="Low">Low priority</option>
        </select>
      </header>

      <section className="card">
        {loading ? (
          <p className="empty-state">Loading settlements…</p>
        ) : error ? (
          <p className="form-error">{error}</p>
        ) : settlements.length === 0 ? (
          <p className="empty-state">No settlement predictions yet — add a loan to generate one.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Loan ID</th>
                <th>Prediction</th>
                <th>Recommended amount</th>
                <th>Risk</th>
                <th>Priority</th>
                <th>Generated</th>
              </tr>
            </thead>
            <tbody>
              {settlements.map((s) => (
                <tr key={s.settlement_id}>
                  <td>#{s.loan_id}</td>
                  <td><Pill value={s.settlement_prediction} /></td>
                  <td>{currency(s.recommended_amount)}</td>
                  <td>{s.risk_category}</td>
                  <td><Pill value={s.priority_level} /></td>
                  <td className="stat-hint">{new Date(s.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}
