// Signature visual: a "recovery gauge" -- an arc that fills from rust (distress)
// through gold (caution) to moss green (recovered), used to represent the
// borrower's financial health score wherever it appears in the app.
export default function RecoveryGauge({ score = 0, label = 'Financial health', size = 180 }) {
  const clamped = Math.max(0, Math.min(100, score))
  const radius = size / 2 - 14
  const circumference = Math.PI * radius // half-circle arc
  const offset = circumference - (clamped / 100) * circumference

  const tone =
    clamped >= 70 ? 'var(--color-accent)' : clamped >= 40 ? 'var(--color-accent-warm)' : 'var(--color-danger)'

  const cx = size / 2
  const cy = size / 2

  return (
    <div className="gauge">
      <svg width={size} height={size / 2 + 20} viewBox={`0 0 ${size} ${size / 2 + 20}`}>
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke="var(--color-border)"
          strokeWidth="12"
          strokeLinecap="round"
        />
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke={tone}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.6s ease, stroke 0.6s ease' }}
        />
        <text x={cx} y={cy - 6} textAnchor="middle" className="gauge-number">
          {Math.round(clamped)}
        </text>
      </svg>
      <div className="gauge-label">{label}</div>
    </div>
  )
}
