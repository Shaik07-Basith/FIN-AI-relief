import { useEffect, useState } from 'react'
import { api } from '../api'
import Pill from '../components/Pill'

const emptyForm = {
  lender_name: '',
  loan_type: '',
  loan_amount: '',
  outstanding_amount: '',
  interest_rate: '',
  emi: '',
  overdue_months: '',
}

export default function Loans() {
  const [loans, setLoans] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [selectedLoanId, setSelectedLoanId] = useState(null)
  const [settlements, setSettlements] = useState([])
  const [negotiating, setNegotiating] = useState(false)
  const [negotiation, setNegotiation] = useState(null)

  const loadLoans = async () => {
    const data = await api.getLoans()
    setLoans(data)
    return data
  }

  useEffect(() => {
    loadLoans()
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const payload = {
        lender_name: form.lender_name,
        loan_type: form.loan_type,
        loan_amount: Number(form.loan_amount),
        outstanding_amount: Number(form.outstanding_amount),
        interest_rate: Number(form.interest_rate) || 0,
        emi: Number(form.emi) || 0,
        overdue_months: Number(form.overdue_months) || 0,
      }
      await api.createLoan(payload)
      setForm(emptyForm)
      await loadLoans()
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (loanId) => {
    await api.deleteLoan(loanId)
    if (selectedLoanId === loanId) {
      setSelectedLoanId(null)
      setSettlements([])
      setNegotiation(null)
    }
    await loadLoans()
  }

  const handleViewSettlements = async (loanId) => {
    setSelectedLoanId(loanId)
    setNegotiation(null)
    const data = await api.getLoanSettlements(loanId)
    setSettlements(data)
  }

  const handleNegotiate = async (loanId) => {
    setNegotiating(true)
    setError('')
    try {
      const result = await api.generateNegotiation(loanId, 'professional')
      setNegotiation(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setNegotiating(false)
    }
  }

  const currency = (n) => `₹${Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <div className="eyebrow">Loans</div>
          <h1>Manage your loan accounts</h1>
          <p className="page-lede">
            Add a loan to get an automatic financial health update and settlement recommendation.
          </p>
        </div>
      </header>

      <section className="card">
        <h2>Add a loan</h2>
        <form onSubmit={handleSubmit} className="loan-form">
          <label>
            Lender name
            <input value={form.lender_name} onChange={update('lender_name')} required />
          </label>
          <label>
            Loan type
            <input value={form.loan_type} onChange={update('loan_type')} placeholder="Personal, Credit card, Auto…" required />
          </label>
          <label>
            Loan amount
            <input type="number" min="0" value={form.loan_amount} onChange={update('loan_amount')} required />
          </label>
          <label>
            Outstanding amount
            <input type="number" min="0" value={form.outstanding_amount} onChange={update('outstanding_amount')} required />
          </label>
          <label>
            Interest rate (%)
            <input type="number" min="0" step="0.1" value={form.interest_rate} onChange={update('interest_rate')} />
          </label>
          <label>
            Monthly EMI
            <input type="number" min="0" value={form.emi} onChange={update('emi')} />
          </label>
          <label>
            Overdue months
            <input type="number" min="0" value={form.overdue_months} onChange={update('overdue_months')} />
          </label>

          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? 'Saving…' : 'Add loan'}
          </button>
        </form>
        {error && <div className="form-error">{error}</div>}
      </section>

      <section className="card">
        <h2>Your loans</h2>
        {loading ? (
          <p className="empty-state">Loading loans…</p>
        ) : loans.length === 0 ? (
          <p className="empty-state">No loans added yet.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Lender</th>
                <th>Type</th>
                <th>Outstanding</th>
                <th>EMI</th>
                <th>Overdue</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {loans.map((loan) => (
                <tr key={loan.loan_id}>
                  <td>{loan.lender_name}</td>
                  <td>{loan.loan_type}</td>
                  <td>{currency(loan.outstanding_amount)}</td>
                  <td>{currency(loan.emi)}</td>
                  <td>{loan.overdue_months} mo</td>
                  <td className="table-actions">
                    <button className="btn btn-ghost btn-sm" onClick={() => handleViewSettlements(loan.loan_id)}>
                      Settlement
                    </button>
                    <button className="btn btn-ghost btn-sm" onClick={() => handleNegotiate(loan.loan_id)} disabled={negotiating}>
                      Negotiate
                    </button>
                    <button className="btn btn-ghost btn-sm btn-danger" onClick={() => handleDelete(loan.loan_id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {selectedLoanId && settlements.length > 0 && (
        <section className="card">
          <h2>Settlement predictions</h2>
          {settlements.map((s) => (
            <div key={s.settlement_id} className="settlement-row">
              <Pill value={s.settlement_prediction} />
              <span>Recommended amount: <strong>{currency(s.recommended_amount)}</strong></span>
              <span className="stat-hint">Risk: {s.risk_category} · Priority: {s.priority_level}</span>
            </div>
          ))}
        </section>
      )}

      {negotiating && <p className="empty-state">Generating negotiation strategy…</p>}

      {negotiation && (
        <section className="card">
          <h2>AI negotiation strategy</h2>
          <pre className="ai-block">{negotiation.negotiation_strategy}</pre>
          <h2>Draft settlement letter</h2>
          <pre className="ai-block">{negotiation.negotiation_letter}</pre>
        </section>
      )}
    </div>
  )
}
