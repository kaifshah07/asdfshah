# Gridbricks UK Wind Forecast Platform — Frontend

## Overview
A high-performance, institutional-grade energy trading decision-support dashboard built with **React**, **TypeScript**, **Vite**, **Tailwind CSS v4**, and **Recharts**.

The dashboard connects to the Gridbricks FastAPI backend to analyze pre-auction Day-Ahead wind generation forecasts against outturn actuals across all 48 UK settlement periods in January 2026.

---

## Key Views & Features

### 1. Day-Ahead Decision View
- **Settlement Period Time-Series:** Visual comparison of actual wind generation (FUELHH) and Day-Ahead forecast (WINDFOR) across all 48 half-hour settlement periods.
- **Decision Cutoff Scrubber:** Enforces pre-auction decision cutoff timing (default: $D-1$ `12:00 UTC`), filtering out subsequent forecast revisions to prevent lookahead bias.
- **Signed Variance Breakdown:** Settlement-by-settlement bar chart displaying over-forecasting (short deficit risk) and under-forecasting (surplus spill).
- **Day KPI Cards:** MAE, RMSE, Mean Bias Error, WAPE, observation counts, and P10/P50/P90 risk bounds.

### 2. Multi-Day Forecast Analytics View
- **Aggregated Performance:** Multi-day/full-month evaluation across January 2026.
- **Peak vs. Off-Peak Comparison:** Side-by-side performance audit for Peak hours (07:00–19:00 UTC, SP 15–38) vs. Off-Peak hours.
- **Diurnal Error Profile:** 48-period hourly breakdown revealing systemic diurnal biases.
- **Daily Error Progression:** Trendline of daily MAE and WAPE across January dates.

### 3. Technical Methodology Modal
- Explains Elexon datasets, gate-closure logic, hourly-to-half-hourly settlement mapping, and statistical error formulas.

---

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── AnalyticsView.tsx           # Multi-day, peak/off-peak, & diurnal analytics
│   │   ├── ErrorDistributionChart.tsx  # Signed half-hourly error bar chart
│   │   ├── FilterControls.tsx          # Date pickers & cutoff controls
│   │   ├── ForecastChart.tsx           # 48-period time-series Recharts chart
│   │   ├── Header.tsx                  # Header, metadata badges, & tab navigation
│   │   ├── KpiCards.tsx                # Institutional KPI metrics cards
│   │   ├── MethodologyModal.tsx        # Calculation & data source methodology
│   │   └── StatusStates.tsx            # Loading, Error, and Empty state displays
│   ├── services/
│   │   └── api.ts                      # Centralized typed API client
│   ├── types/
│   │   └── api.ts                      # TypeScript contracts matching backend schemas
│   ├── App.tsx                         # Main dashboard layout & state management
│   ├── index.css                       # Tailwind CSS v4 styling & typography
│   └── main.tsx                        # Application mount
├── .env.example                        # Environment variables template
├── package.json                        # Frontend dependencies & scripts
├── tsconfig.json                       # TypeScript strict configuration
└── vite.config.ts                      # Vite configuration & dev proxy
```

---

## Local Development

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Create `.env` (or copy from `.env.example`):
```bash
cp .env.example .env
```
Default:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 3. Start Development Server
```bash
npm run dev
```
The dashboard will run at: **`http://localhost:5173`**

### 4. Build Production Bundle
```bash
npm run build
```
Build output is generated in `dist/`.
