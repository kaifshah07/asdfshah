import React from 'react';
import { AlertTriangle, ArrowDownRight, ArrowUpRight, CheckCircle2, Gauge, Scale, TrendingUp } from 'lucide-react';
import type { ErrorMetrics } from '../types/api';

interface KpiCardsProps {
  metrics: ErrorMetrics;
}

export const KpiCards: React.FC<KpiCardsProps> = ({ metrics }) => {
  const isOverForecasting = metrics.mean_bias_mw !== null && metrics.mean_bias_mw > 0;
  const isUnderForecasting = metrics.mean_bias_mw !== null && metrics.mean_bias_mw < 0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
      {/* 1. MAE */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between shadow-sm">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium uppercase tracking-wider">MAE</span>
          <Scale className="h-4 w-4 text-cyan-400" />
        </div>
        <div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {metrics.mae_mw !== null ? `${metrics.mae_mw.toLocaleString()} ` : '— '}
            <span className="text-xs font-normal text-slate-400 font-sans">MW</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1 leading-tight">
            Mean Absolute Error magnitude
          </p>
        </div>
      </div>

      {/* 2. RMSE */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between shadow-sm">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium uppercase tracking-wider">RMSE</span>
          <Gauge className="h-4 w-4 text-indigo-400" />
        </div>
        <div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {metrics.rmse_mw !== null ? `${metrics.rmse_mw.toLocaleString()} ` : '— '}
            <span className="text-xs font-normal text-slate-400 font-sans">MW</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1 leading-tight">
            Penalizes large forecast swings
          </p>
        </div>
      </div>

      {/* 3. Mean Bias Error */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between shadow-sm">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium uppercase tracking-wider">Mean Bias</span>
          {isOverForecasting ? (
            <ArrowUpRight className="h-4 w-4 text-amber-400" />
          ) : isUnderForecasting ? (
            <ArrowDownRight className="h-4 w-4 text-cyan-400" />
          ) : (
            <TrendingUp className="h-4 w-4 text-slate-400" />
          )}
        </div>
        <div>
          <div
            className={`text-xl font-bold font-mono ${
              isOverForecasting ? 'text-amber-300' : isUnderForecasting ? 'text-cyan-300' : 'text-slate-100'
            }`}
          >
            {metrics.mean_bias_mw !== null
              ? `${metrics.mean_bias_mw > 0 ? '+' : ''}${metrics.mean_bias_mw.toLocaleString()} `
              : '— '}
            <span className="text-xs font-normal text-slate-400 font-sans">MW</span>
          </div>
          <div className="flex items-center gap-1 mt-1">
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                isOverForecasting
                  ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                  : isUnderForecasting
                  ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20'
                  : 'bg-slate-800 text-slate-400'
              }`}
            >
              {isOverForecasting ? 'Over-Forecast' : isUnderForecasting ? 'Under-Forecast' : 'Neutral'}
            </span>
          </div>
        </div>
      </div>

      {/* 4. WAPE */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between shadow-sm">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium uppercase tracking-wider">WAPE</span>
          <TrendingUp className="h-4 w-4 text-emerald-400" />
        </div>
        <div>
          <div className="text-xl font-bold font-mono text-emerald-400">
            {metrics.wape_percent !== null ? `${metrics.wape_percent.toFixed(2)}` : '—'}
            <span className="text-sm font-normal text-slate-400 font-sans">%</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1 leading-tight">
            Σ|Error| / ΣActual Outturn
          </p>
        </div>
      </div>

      {/* 5. Error Bounds (P10 / P90) */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between shadow-sm">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium uppercase tracking-wider">Risk Bands</span>
          <AlertTriangle className="h-4 w-4 text-purple-400" />
        </div>
        <div className="text-xs font-mono">
          <div className="flex justify-between py-0.5 text-slate-300">
            <span className="text-slate-500">P90:</span>
            <span>{metrics.p90_error_mw !== null ? `${metrics.p90_error_mw > 0 ? '+' : ''}${metrics.p90_error_mw} MW` : '—'}</span>
          </div>
          <div className="flex justify-between py-0.5 text-slate-300">
            <span className="text-slate-500">P50:</span>
            <span>{metrics.p50_error_mw !== null ? `${metrics.p50_error_mw > 0 ? '+' : ''}${metrics.p50_error_mw} MW` : '—'}</span>
          </div>
          <div className="flex justify-between py-0.5 text-slate-300">
            <span className="text-slate-500">P10:</span>
            <span>{metrics.p10_error_mw !== null ? `${metrics.p10_error_mw > 0 ? '+' : ''}${metrics.p10_error_mw} MW` : '—'}</span>
          </div>
        </div>
      </div>

      {/* 6. Observations */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between shadow-sm">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium uppercase tracking-wider">Coverage</span>
          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
        </div>
        <div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {metrics.observations_count}
            <span className="text-xs font-normal text-slate-400 font-sans"> slots</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1 leading-tight">
            {metrics.missing_count === 0 ? (
              <span className="text-emerald-400">100% complete (0 missing)</span>
            ) : (
              <span className="text-amber-400">{metrics.missing_count} missing intervals</span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
};
