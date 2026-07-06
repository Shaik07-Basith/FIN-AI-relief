import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import RecoveryGauge from '../components/RecoveryGauge'
import Pill from '../components/Pill'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [loans, setLoans] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true

    Promise.all([api.getDashboard(), api.getLoans()])
      .then(([dashboard, loanList]) => {
        console.log("Dashboard API Response:", dashboard)
        console.log("Loans API Response:", loanList)

        if (!mounted) return

        setSummary(dashboard)
        setLoans(loanList)
      })
      .catch((err) => {
        console.error(err)
        setError(err.message)
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })

    return () => {
      mounted = false
    }
  }, [])

  if (loading)
    return <div className="page-loading">Loading your recovery overview...</div>

  if (error)
    return <div className="page-error">{error}</div>

  if (!summary)
    return (
      <div className="page-error">
        Dashboard data not found. Please add your financial details or check the backend.
      </div>
    )

  const currency = (n) =>
    `₹${Number(n || 0).toLocaleString('en-IN', {
      maximumFractionDigits: 0,
    })}`

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <div className="eyebrow">Overview</div>
          <h1>Your recovery snapshot</h1>
          <p className="page-lede">
            A live read on your debt load, stress level, and where the platform
            recommends focusing first.
          </p>
        </div>
        <Link to="/loans" className="btn btn-primary">
          Add a loan
        </Link>
      </header>

      <section className="grid-summary">
        <div className="card card-gauge">
          <RecoveryGauge
            score={summary.financial_health_score ?? 0}
            label="Financial health score"
          />
          <div className="pill-row">
            <span className="stat-label">Stress level</span>
            <Pill value={summary.stress_level ?? "Low"} />
          </div>
        </div>

        <div className="card stat-card">
          <div className="stat-label">Total outstanding</div>
          <div className="stat-value">
            {currency(summary.total_outstanding)}
          </div>
          <div className="stat-hint">
            Across {summary.total_loans ?? 0} loan
            {(summary.total_loans ?? 0) === 1 ? "" : "s"}
          </div>
        </div>

        <div className="card stat-card">
          <div className="stat-label">Monthly EMI outflow</div>
          <div className="stat-value">{currency(summary.total_emi)}</div>
          <div className="stat-hint">
            EMI ratio {summary.emi_ratio ?? 0}% of income
          </div>
        </div>

        <div className="card stat-card">
          <div
            className={
              "stat-value" +
              ((summary.monthly_surplus ?? 0) < 0 ? " stat-negative" : "")
            }
          >
            {currency(summary.monthly_surplus)}
          </div>
          <div className="stat-label">Monthly surplus</div>
          <div className="stat-hint">
            DTI ratio {summary.dti_ratio ?? 0}% of annual income
          </div>
        </div>
      </section>

      <section className="card">
        <div className="card-header">
          <h2>Loans needing attention</h2>
          <span className="stat-hint">
            {summary.high_priority_loans ?? 0} flagged high priority
          </span>
        </div>

        {loans.length === 0 ? (
          <p className="empty-state">
            No loans yet.{" "}
            <Link to="/loans">Add your first loan</Link> to get a settlement
            recommendation.
          </p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Lender</th>
                <th>Type</th>
                <th>Outstanding</th>
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
                  <td>
                    <Pill
                      value={
                        loan.overdue_months >= 6
                          ? "High"
                          : loan.overdue_months >= 3
                          ? "Medium"
                          : "Low"
                      }
                    />
                    <span className="stat-hint" style={{ marginLeft: 8 }}>
                      {loan.overdue_months} mo
                    </span>
                  </td>
                  <td>
                    <Link to="/loans" className="link">
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}