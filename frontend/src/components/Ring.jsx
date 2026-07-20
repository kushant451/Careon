export default function Ring({ value, max = 100, size = 100, color = "#E8896A", sub = "" }) {
  const pct = max ? value / max : 0;
  const r = size * 0.42;
  const circ = 2 * Math.PI * r;
  const dash = pct * circ;
  const cx = size / 2;
  const cy = size / 2;
  const fs = size * 0.22;

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#F0DDD0" strokeWidth={size * 0.08} />
      <circle
        cx={cx}
        cy={cy}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth={size * 0.08}
        strokeDasharray={`${dash.toFixed(1)} ${circ.toFixed(1)}`}
        strokeLinecap="round"
        transform={`rotate(-90 ${cx} ${cy})`}
      />
      <text
        x={cx}
        y={cy - 0.04 * size}
        textAnchor="middle"
        dominantBaseline="central"
        fill={color}
        fontSize={fs}
        fontWeight="700"
      >
        {value}
      </text>
      {sub && (
        <text x={cx} y={cy + size * 0.2} textAnchor="middle" fill="#9C7A6B" fontSize={size * 0.1}>
          {sub}
        </text>
      )}
    </svg>
  );
}
