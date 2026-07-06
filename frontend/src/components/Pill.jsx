const toneMap = {
  High: 'pill-danger',
  Medium: 'pill-warm',
  Low: 'pill-accent',
  Likely: 'pill-accent',
  Possible: 'pill-warm',
  Unlikely: 'pill-danger',
}

export default function Pill({ value }) {
  const cls = toneMap[value] || 'pill-neutral'
  return <span className={`pill ${cls}`}>{value}</span>
}
