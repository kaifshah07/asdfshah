import React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { SettlementPeriodForecast } from '../types/api';

interface ErrorDistributionChartProps {
  periods: SettlementPeriodForecast[];
}

export const ErrorDistributionChart: React.FC<ErrorDistributionChartProps> = ({ periods }) => {
  const chartData = periods.map((p) => {
    const time = new Date(p.start_time);
    const timeLabel = time.toISOString().substring(11, 16);
    return {
      sp: p.settlement_period,
      timeLabel: `SP${p.settlement_period} (${timeLabel})`,
      error: p.error_mw,
      absError: p.abs_error_mw,
    };
  });

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
        <div>
          <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
            <span>Half-Hourly Forecast Variance (Error = Forecast − Actual)</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Signed half-hourly error: Positive indicates over-forecast (shortage risk), Negative indicates under-forecast (spill)
          </p>
        </div>

        <div className="flex items-center gap-4 text-xs font-medium">
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded bg-amber-400"></span>
            <span className="text-slate-300">Over-Forecast (+MW)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded bg-cyan-400"></span>
            <span className="text-slate-300">Under-Forecast (−MW)</span>
          </div>
        </div>
      </div>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />

            <XAxis
              dataKey="sp"
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              tickFormatter={(sp) => {
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
              tickFormatter={(val) => `${val > 0 ? '+' : ''}${(val / 1000).toFixed(1)}k`}
            />

            <ReferenceLine y={0} stroke="#475569" strokeWidth={1.5} />

            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || !payload.length) return null;
                const d = payload[0].payload;
                const error = d.error;
                const isOver = error !== null && error > 0;
                return (
                  <div className="bg-slate-950 border border-slate-700 rounded-lg p-2.5 shadow-xl text-xs font-mono">
                    <div className="font-semibold text-slate-200 border-b border-slate-800 pb-1 mb-1 font-sans">
                      {d.timeLabel}
                    </div>
                    <div className="flex justify-between gap-4">
                      <span className="text-slate-400 font-sans">Forecast Variance:</span>
                      <span className={`font-bold ${isOver ? 'text-amber-400' : 'text-cyan-400'}`}>
                        {error !== null ? `${error > 0 ? '+' : ''}${error.toLocaleString()} MW` : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between gap-4 text-slate-400 text-[11px] mt-0.5">
                      <span className="font-sans">Classification:</span>
                      <span>{isOver ? 'Over-Forecast (Deficit)' : error < 0 ? 'Under-Forecast (Surplus)' : 'Exact'}</span>
                    </div>
                  </div>
                );
              }}
            />

            <Bar dataKey="error" maxBarSize={16}>
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.error !== null && entry.error >= 0 ? '#f59e0b' : '#06b6d4'}
                  fillOpacity={0.85}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
