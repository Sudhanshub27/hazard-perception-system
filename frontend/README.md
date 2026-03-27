# Frontend Service

Next.js live dashboard for real-time hazard visualization.

## Structure

```
frontend/
├── Dockerfile
├── package.json
├── next.config.js
├── tailwind.config.js
├── src/
│   ├── app/
│   │   ├── page.tsx          # Home / Upload page
│   │   ├── dashboard/
│   │   │   └── page.tsx      # Live stream dashboard
│   │   └── analytics/
│   │       └── page.tsx      # Historical analytics
│   ├── components/
│   │   ├── VideoCanvas.tsx   # Renders annotated frames
│   │   ├── RiskGauge.tsx     # 0-100 animated gauge
│   │   ├── HazardLog.tsx     # Scrollable event log
│   │   └── ClassBreakdown.tsx# Per-class detection counts
│   └── hooks/
│       └── useWebSocket.ts   # WebSocket connection hook
```

## Development

```bash
cd frontend
npm install
npm run dev      # http://localhost:3000
```
