import React from 'react';
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { SettlementPeriodForecast } from '../types/api';

interface ForecastChartProps {
  periods: SettlementPeriodForecast[];
  deliveryDate: string;
}

export const ForecastChart: React.FC<ForecastChartProps> = ({ periods, deliveryDate }) => {
  // Format data for Recharts
  const chartData = periods.map((p) => {
    const time = new Date(p.start_time);
    const timeLabel = time.toISOString().substring(11, 16);
    return {
      sp: p.settlement_period,
      timeLabel: `SP${p.settlement_period} (${timeLabel})`,
      shortTime: timeLabel,
      actual: p.actual_generation_mw,
      forecast: p.forecast_generation_mw,
      error: p.error_mw,
      publishTime: p.forecast_publish_time
        ? new Date(p.forecast_publish_time).toISOString().substring(11, 16) + ' UTC'
        : 'N/A',
    };
  });

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
        <div>
          <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
            <span>Day-Ahead Wind Generation vs Actual Outturn</span>
            <span className="text-xs font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
              {deliveryDate} (48 Half-Hour Settlement Periods)
            </span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Hourly ESO forecast (mapped to constituent 30-min settlement periods) compared with FUELHH actual generation
          </p>
        </div>

        <div className="flex items-center gap-4 text-xs font-medium">
          <div className="flex items-center gap-1.5">
            <span className="h-3 w-3 rounded-full bg-cyan-400"></span>
            <span className="text-slate-300">Actual Outturn (FUELHH)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-3 w-3 rounded-full bg-amber-400"></span>
            <span className="text-slate-300">Day-Ahead Forecast (WINDFOR)</span>
          </div>
        </div>
      </div>

      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
            <defs>
              <linearGradient id="actualGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />

            <XAxis
              dataKey="sp"
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              tickFormatter={(sp) => {
                // Show labels every 4 settlement periods (every 2 hours)
                if (sp === 1 || sp % 4 === 0 || sp === 48) {
                  const h = Math.floor((sp - 1) / 2);
                  const m = sp % 2 === 0 ? '30' : '00';
                  return `${h.toString().padStart(2, '0')}:${m}`;
                }
                return '';
              }}
            />

            <YAxis
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              tickFormatter={(val) => `${(val / 1000).toFixed(0)} GW`}
              domain={['auto', 'auto']}
            />

            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || !payload.length) return null;
                const d = payload[0].payload;
                const error = d.error;
                const isOver = error !== null && error > 0;
                return (
                  <div className="bg-slate-950 border border-slate-700 rounded-lg p-3 shadow-xl text-xs font-mono">
                    <div className="font-semibold text-slate-200 border-b border-slate-800 pb-1 mb-2 font-sans flex justify-between gap-4">
                      <span>{d.timeLabel}</span>
                      <span className="text-slate-400">Published: {d.publishTime}</span>
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between gap-4">
                        <span className="text-cyan-400 font-sans">Actual Generation:</span>
                        <span className="font-bold text-slate-100">
                          {d.actual !== null ? `${d.actual.toLocaleString()} MW` : 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between gap-4">
                        <span className="text-amber-400 font-sans">Day-Ahead Forecast:</span>
                        <span className="font-bold text-slate-100">
                          {d.forecast !== null ? `${d.forecast.toLocaleString()} MW` : 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between gap-4 pt-1 border-t border-slate-800/80">
                        <span className="text-slate-400 font-sans">Forecast Variance:</span>
                        <span
                          className={`font-bold ${
                            isOver ? 'text-amber-400' : 'text-cyan-400'
                          }`}
                        >
                          {error !== null ? `${error > 0 ? '+' : ''}${error.toLocaleString()} MW` : 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              }}
            />

            <Area
              type="monotone"
              dataKey="actual"
              stroke="#06b6d4"
              strokeWidth={2}
              fill="url(#actualGradient)"
              name="Actual Outturn"
              dot={false}
              activeDot={{ r: 4, stroke: '#06b6d4', strokeWidth: 2, fill: '#0891b2' }}
            />

            <Line
              type="stepAfter"
              dataKey="forecast"
              stroke="#f59e0b"
              strokeWidth={2}
              strokeDasharray="4 2"
              name="Day-Ahead Forecast"
              dot={false}
              activeDot={{ r: 4, stroke: '#f59e0b', strokeWidth: 2, fill: '#d97706' }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2 px-2">
        <span>Settlement Period 1 (00:00 UTC)</span>
        <span>Peak Window: SP 15–38 (07:00–19:00 UTC)</span>
        <span>Settlement Period 48 (23:30 UTC)</span>
      </div>
    </div>
  );
};
