import { useEffect, useState } from 'react'
import { api } from '../api'
import RecoveryGauge from '../components/RecoveryGauge'
import Pill from '../components/Pill'

export default function FinancialProfile() {
  const [profile, setProfile] = useState(null)
  const [form, setForm] = useState({ monthly_income: '', monthly_expenses: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const load = async () => {
    const data = await api.getFinancialProfile()
    setProfile(data)
    setForm({ monthly_income: data.monthly_income, monthly_expenses: data.monthly_expenses })
  }

  useEffect(() => {
    load().catch((err) => setError(err.message)).finally(() => setLoading(false))
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      const updated = await api.updateFinancialProfile({
        monthly_income: Number(form.monthly_income),
        monthly_expenses: Number(form.monthly_expenses),
      })
      setProfile(updated)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="page-loading">Loading financial profile…</div>

  const currency = (n) => `₹${Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <div className="eyebrow">Financial profile</div>
          <h1>Track your financial health</h1>
          <p className="page-lede">
            Update your income and expenses any time — every loan you add automatically recalculates these numbers.
          </p>
        </div>
      </header>

      <section className="grid-summary">
        <div className="card card-gauge">
          <RecoveryGauge score={profile.financial_health_score} label="Financial health score" />
          <div className="pill-row">
            <span className="stat-label">Stress level</span>
            <Pill value={profile.stress_level} />
          </div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">EMI ratio</div>
          <div className="stat-value">{profile.emi_ratio}%</div>
          <div className="stat-hint">of monthly income</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">DTI ratio</div>
          <div className="stat-value">{profile.dti_ratio}%</div>
          <div className="stat-hint">of annual income</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">Monthly surplus</div>
          <div className={'stat-value' + (profile.monthly_surplus < 0 ? ' stat-negative' : '')}>
            {currency(profile.monthly_surplus)}
          </div>
          <div className="stat-hint">income − expenses − EMI</div>
        </div>
      </section>

      <section className="card">
        <h2>Update income &amp; expenses</h2>
        <form onSubmit={handleSubmit} className="form-row">
          <label>
            Monthly income
            <input
              type="number" min="0"
              value={form.monthly_income}
              onChange={(e) => setForm({ ...form, monthly_income: e.target.value })}
            />
          </label>
          <label>
            Monthly expenses
            <input
              type="number" min="0"
              value={form.monthly_expenses}
              onChange={(e) => setForm({ ...form, monthly_expenses: e.target.value })}
            />
          </label>
          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving ? 'Saving…' : 'Save changes'}
          </button>
        </form>
        {error && <div className="form-error">{error}</div>}
      </section>
    </div>
  )
}
