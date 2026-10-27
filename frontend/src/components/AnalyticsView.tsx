import React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { AnalyticsResponse } from '../types/api';
import { KpiCards } from './KpiCards';
import { Clock, ShieldAlert, Sun, Moon } from 'lucide-react';

interface AnalyticsViewProps {
  analytics: AnalyticsResponse;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ analytics }) => {
  // Format diurnal data for Recharts
  const diurnalData = analytics.diurnal_profile.map((d) => ({
    sp: d.settlement_period,
    time: d.time_label,
    label: `SP${d.settlement_period} (${d.time_label})`,
    meanActual: d.mean_actual_mw,
    meanForecast: d.mean_forecast_mw,
    meanBias: d.mean_bias_mw,
    mae: d.mae_mw,
  }));

  // Format daily metrics
  const dailyData = analytics.daily_metrics.map((d) => ({
    date: d.date,
    dayLabel: `Jan ${d.date.slice(8)}`,
    mae: d.mae_mw,
    bias: d.mean_bias_mw,
    rmse: d.rmse_mw,
    wape: d.wape_percent,
  }));

  return (
    <div className="space-y-6">
      {/* 1. Range Overview KPIs */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-slate-100 uppercase tracking-wider flex items-center gap-2">
            <span>Aggregated Portfolio Accuracy</span>
            <span className="text-xs font-mono text-cyan-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700 font-normal">
              {analytics.start_date} to {analytics.end_date} ({analytics.cutoff_time_utc})
            </span>
          </h2>
        </div>
        <KpiCards metrics={analytics.overall_metrics} />
      </div>

      {/* 2. Peak vs Off-Peak Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Peak Period Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
            <div className="flex items-center gap-2">
              <Sun className="h-4 w-4 text-amber-400" />
              <h3 className="text-sm font-semibold text-slate-100">Peak Window (07:00 – 19:00 UTC)</h3>
            </div>
            <span className="text-xs text-slate-400 font-mono">SP 15 to SP 38 (24 HH/day)</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
              <div className="text-slate-400 text-[11px]">Peak MAE</div>
              <div className="text-base font-bold font-mono text-slate-100 mt-0.5">
                {analytics.peak_metrics.mae_mw?.toLocaleString()} <span className="text-xs text-slate-500">MW</span>
              </div>
            </div>

            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
              <div className="text-slate-400 text-[11px]">Peak RMSE</div>
              <div className="text-base font-bold font-mono text-slate-100 mt-0.5">
                {analytics.peak_metrics.rmse_mw?.toLocaleString()} <span className="text-xs text-slate-500">MW</span>
              </div>
            </div>

            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
              <div className="text-slate-400 text-[11px]">Peak Bias</div>
              <div
                className={`text-base font-bold font-mono mt-0.5 ${
                  (analytics.peak_metrics.mean_bias_mw || 0) > 0 ? 'text-amber-400' : 'text-cyan-400'
                }`}
              >
                {(analytics.peak_metrics.mean_bias_mw || 0) > 0 ? '+' : ''}
                {analytics.peak_metrics.mean_bias_mw?.toLocaleString()}{' '}
                <span className="text-xs text-slate-500">MW</span>
              </div>
            </div>

            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
              <div className="text-slate-400 text-[11px]">Peak WAPE</div>
              <div className="text-base font-bold font-mono text-emerald-400 mt-0.5">
                {analytics.peak_metrics.wape_percent?.toFixed(2)}%
              </div>
            </div>
          </div>
          <p className="text-[11px] text-slate-400 mt-3 leading-relaxed">
            Critical procurement hours when consumer demand and power prices are highest. Systemic over-forecasting during peak hours creates substantial cash-out imbalance exposure.
          </p>
        </div>

        {/* Off-Peak Period Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
            <div className="flex items-center gap-2">
              <Moon className="h-4 w-4 text-indigo-400" />
              <h3 className="text-sm font-semibold text-slate-100">Off-Peak Window (Night & Evening)</h3>
            </div>
            <span className="text-xs text-slate-400 font-mono">SP 1–14 & 39–48 (24 HH/day)</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
              <div className="text-slate-400 text-[11px]">Off-Peak MAE</div>
              <div className="text-base font-bold font-mono text-slate-100 mt-0.5">
                {analytics.off_peak_metrics.mae_mw?.toLocaleString()}{' '}
                <span className="text-xs text-slate-500">MW</span>
              </div>
            </div>

            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
              <div className="text-slate-400 text-[11px]">Off-Peak RMSE</div>
              <div className="text-base font-bold font-mono text-slate-100 mt-0.5">
                {analytics.off_peak_metrics.rmse_mw?.toLocaleString()}{' '}
                <span className="text-xs text-slate-500">MW</span>
              </div>
            </div>

            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
              <div className="text-slate-400 text-[11px]">Off-Peak Bias</div>
              <div
                className={`text-base font-bold font-mono mt-0.5 ${
                  (analytics.off_peak_metrics.mean_bias_mw || 0) > 0 ? 'text-amber-400' : 'text-cyan-400'
                }`}
              >
                {(analytics.off_peak_metrics.mean_bias_mw || 0) > 0 ? '+' : ''}
                {analytics.off_peak_metrics.mean_bias_mw?.toLocaleString()}{' '}
                <span className="text-xs text-slate-500">MW</span>
              </div>
            </div>

            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
              <div className="text-slate-400 text-[11px]">Off-Peak WAPE</div>
              <div className="text-base font-bold font-mono text-emerald-400 mt-0.5">
                {analytics.off_peak_metrics.wape_percent?.toFixed(2)}%
              </div>
            </div>
          </div>
          <p className="text-[11px] text-slate-400 mt-3 leading-relaxed">
            Low-demand nighttime periods. Higher nighttime wind output can trigger negative power pricing if wind is significantly under-forecasted.
          </p>
        </div>
      </div>

      {/* 3. Diurnal 48-Period Profile Chart */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              <Clock className="h-4 w-4 text-cyan-400" />
              <span>Diurnal Error Profile (Settlement Periods 1 to 48)</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Average Mean Bias and MAE by half-hour of the day across all {analytics.daily_metrics.length} selected days
            </p>
          </div>

          <div className="flex items-center gap-4 text-xs font-medium">
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded bg-amber-400"></span>
              <span className="text-slate-300">Mean Bias (Forecast − Actual)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded bg-cyan-400"></span>
              <span className="text-slate-300">MAE (Error Magnitude)</span>
            </div>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={diurnalData} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
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
                tickFormatter={(val) => `${(val / 1000).toFixed(1)}k`}
              />

              <ReferenceLine y={0} stroke="#475569" />

              <Tooltip
                content={({ active, payload }) => {
                  if (!active || !payload || !payload.length) return null;
                  const d = payload[0].payload;
                  return (
                    <div className="bg-slate-950 border border-slate-700 rounded-lg p-2.5 shadow-xl text-xs font-mono">
                      <div className="font-semibold text-slate-200 border-b border-slate-800 pb-1 mb-1 font-sans">
                        {d.label}
                      </div>
                      <div className="space-y-1">
                        <div className="flex justify-between gap-4">
                          <span className="text-slate-400 font-sans">Mean Forecast:</span>
                          <span className="text-slate-200">{d.meanForecast?.toLocaleString()} MW</span>
                        </div>
                        <div className="flex justify-between gap-4">
                          <span className="text-slate-400 font-sans">Mean Actual:</span>
                          <span className="text-slate-200">{d.meanActual?.toLocaleString()} MW</span>
                        </div>
                        <div className="flex justify-between gap-4 pt-1 border-t border-slate-800">
                          <span className="text-amber-400 font-sans">Mean Bias:</span>
                          <span className="font-bold text-amber-300">
                            {d.meanBias !== null ? `${d.meanBias > 0 ? '+' : ''}${d.meanBias.toLocaleString()} MW` : 'N/A'}
                          </span>
                        </div>
                        <div className="flex justify-between gap-4">
                          <span className="text-cyan-400 font-sans">MAE:</span>
                          <span className="font-bold text-cyan-300">{d.mae?.toLocaleString()} MW</span>
                        </div>
                      </div>
                    </div>
                  );
                }}
              />

              <Bar dataKey="meanBias" fill="#f59e0b" fillOpacity={0.8} name="Mean Bias" />
              <Bar dataKey="mae" fill="#06b6d4" fillOpacity={0.6} name="MAE" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 4. Daily Error Trend Chart */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-purple-400" />
              <span>Day-by-Day Forecast Error Progression</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Daily MAE and WAPE across selected January dates
            </p>
          </div>

          <div className="flex items-center gap-4 text-xs font-medium">
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-cyan-400"></span>
              <span className="text-slate-300">Daily MAE (MW)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-400"></span>
              <span className="text-slate-300">Daily WAPE (%)</span>
            </div>
          </div>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={dailyData} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />

              <XAxis dataKey="dayLabel" stroke="#64748b" fontSize={11} tickLine={false} />

              <YAxis
                yAxisId="left"
                stroke="#64748b"
                fontSize={11}
                tickLine={false}
                tickFormatter={(val) => `${(val / 1000).toFixed(0)}k`}
              />

              <YAxis
                yAxisId="right"
                orientation="right"
                stroke="#64748b"
                fontSize={11}
                tickLine={false}
                tickFormatter={(val) => `${val}%`}
              />

              <Tooltip
                content={({ active, payload }) => {
                  if (!active || !payload || !payload.length) return null;
                  const d = payload[0].payload;
                  return (
                    <div className="bg-slate-950 border border-slate-700 rounded-lg p-2.5 shadow-xl text-xs font-mono">
                      <div className="font-semibold text-slate-200 border-b border-slate-800 pb-1 mb-1 font-sans">
                        {d.date}
                      </div>
                      <div className="space-y-1">
                        <div className="flex justify-between gap-4">
                          <span className="text-cyan-400 font-sans">Daily MAE:</span>
                          <span className="font-bold text-slate-100">{d.mae?.toLocaleString()} MW</span>
                        </div>
                        <div className="flex justify-between gap-4">
                          <span className="text-slate-400 font-sans">Daily Bias:</span>
                          <span className="font-bold text-slate-100">
                            {d.bias > 0 ? '+' : ''}{d.bias?.toLocaleString()} MW
                          </span>
                        </div>
                        <div className="flex justify-between gap-4">
                          <span className="text-emerald-400 font-sans">Daily WAPE:</span>
                          <span className="font-bold text-emerald-300">{d.wape?.toFixed(2)}%</span>
                        </div>
                      </div>
                    </div>
                  );
                }}
              />

              <Line
                yAxisId="left"
                type="monotone"
                dataKey="mae"
                stroke="#06b6d4"
                strokeWidth={2}
                dot={{ r: 3, fill: '#06b6d4' }}
                activeDot={{ r: 5 }}
                name="MAE"
              />

              <Line
                yAxisId="right"
                type="monotone"
                dataKey="wape"
                stroke="#10b981"
                strokeWidth={2}
                strokeDasharray="3 3"
                dot={{ r: 3, fill: '#10b981' }}
                activeDot={{ r: 5 }}
                name="WAPE"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
