import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    monthly_income: '',
    monthly_expenses: '',
  })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await register({
        ...form,
        monthly_income: Number(form.monthly_income) || 0,
        monthly_expenses: Number(form.monthly_expenses) || 0,
      })
      navigate('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-screen">
      <div className="auth-panel">
        <div className="auth-mark">FR</div>
        <h1>Start your recovery plan</h1>
        <p className="auth-sub">Set up your borrower profile in a couple of minutes.</p>

        <form onSubmit={handleSubmit} className="auth-form">
          <label>
            Full name
            <input value={form.name} onChange={update('name')} required />
          </label>
          <label>
            Email
            <input type="email" value={form.email} onChange={update('email')} required />
          </label>
          <label>
            Password
            <input type="password" value={form.password} onChange={update('password')} required minLength={6} />
          </label>
          <div className="form-row">
            <label>
              Monthly income
              <input type="number" min="0" value={form.monthly_income} onChange={update('monthly_income')} />
            </label>
            <label>
              Monthly expenses
              <input type="number" min="0" value={form.monthly_expenses} onChange={update('monthly_expenses')} />
            </label>
          </div>

          {error && <div className="form-error">{error}</div>}

          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p className="auth-switch">
          Already registered? <Link to="/login">Sign in</Link>
        </p>
      </div>
      <div className="auth-side">
        <blockquote>
          "Structured data in, a clear settlement plan out."
        </blockquote>
      </div>
    </div>
  )
}
