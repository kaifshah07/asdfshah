import React from 'react';
import { BookOpen, Clock, Database, Info, Scale, X } from 'lucide-react';

interface MethodologyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MethodologyModal: React.FC<MethodologyModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-2.5">
            <BookOpen className="h-5 w-5 text-emerald-400" />
            <h2 className="text-base font-semibold text-slate-100">
              Methodology & Technical Specifications
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 overflow-y-auto space-y-6 text-sm text-slate-300">
          {/* 1. Datasets */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2 mb-2">
              <Database className="h-4 w-4" />
              1. Official Elexon BMRS Datasets
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-2">
              All data is sourced exclusively from Elexon BMRS open APIs for wholesale UK power settlement:
            </p>
            <ul className="list-disc list-inside space-y-1 text-xs text-slate-300 ml-1">
              <li>
                <strong className="text-slate-100 font-mono">FUELHH (Actuals):</strong> Half-hourly generation outturn for Great Britain by fuel type category (<span className="font-mono text-cyan-300">fuelType = "WIND"</span>). Updated every 30 minutes, 48 settlement periods per day.
              </li>
              <li>
                <strong className="text-slate-100 font-mono">WINDFOR (Forecasts):</strong> National Grid ESO wind generation forecasts published at approximately 3-hour intervals (8 daily publication runs) with horizons up to ~73 hours ahead.
              </li>
            </ul>
          </div>

          {/* 2. Gate Closure Cutoff */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2 mb-2">
              <Clock className="h-4 w-4" />
              2. Pre-Auction Decision Cutoff Logic
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-2">
              Day-ahead wholesale electricity procurement auctions in the UK (EPEX SPOT and Nord Pool) close in the morning/noon on day <span className="font-mono text-slate-200">D-1</span> (proposed analysis default: <span className="font-mono text-amber-300">12:00:00 UTC</span>).
            </p>
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs space-y-1 font-mono">
              <div className="text-emerald-400">Decision Cutoff Timestamp = D - 1 at 12:00:00 UTC</div>
              <div className="text-slate-400">Strict Lookahead Rule: publishTime &le; Cutoff Timestamp</div>
            </div>
            <p className="text-[11px] text-slate-500 mt-2">
              Note: 12:00 UTC is the configured analysis cutoff for evaluating pre-auction visibility, not a rigid statutory market rule. Traders may adjust the cutoff in the filter panel.
            </p>
          </div>

          {/* 3. Alignment Rule */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-2 mb-2">
              <Scale className="h-4 w-4" />
              3. Hourly Forecast to Half-Hourly Settlement Alignment
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-2">
              In Great Britain, actual generation is measured on 30-minute settlement periods ($p \in [1, 48]$), whereas National Grid ESO publishes wind forecasts at 60-minute resolution ($H \in [0, 23]$).
            </p>
            <p className="text-xs text-slate-400 leading-relaxed mb-2">
              Since power (MW) is an instantaneous rate of energy transfer, an expected average rate of $G$ MW throughout hour $[H:00, H+1:00)$ applies directly as the expected average rate for both constituent 30-minute settlement periods ($2H+1$ and $2H+2$):
            </p>
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs font-mono text-slate-300">
              Period $p$ maps to Hour $H = \lfloor(p - 1) / 2\rfloor$<br />
              SP1 (00:00-00:30 UTC) &rarr; Hour 00:00 forecast<br />
              SP2 (00:30-01:00 UTC) &rarr; Hour 00:00 forecast
            </div>
          </div>

          {/* 4. Metric Formulas */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2 mb-2">
              <Info className="h-4 w-4" />
              4. Error Metrics & Mathematical Formulations
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <div className="font-semibold text-slate-200">Signed Error ($e_i$)</div>
                <div className="font-mono text-amber-300 mt-1">Error = Forecast − Actual (MW)</div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Positive = Over-forecast (short deficit). Negative = Under-forecast (spill).
                </p>
              </div>

              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <div className="font-semibold text-slate-200">MAE (Mean Absolute Error)</div>
                <div className="font-mono text-cyan-300 mt-1">MAE = (1/N) &Sigma; |Forecast − Actual|</div>
                <p className="text-[11px] text-slate-400 mt-1">Average absolute magnitude of forecast error in MW.</p>
              </div>

              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <div className="font-semibold text-slate-200">RMSE</div>
                <div className="font-mono text-indigo-300 mt-1">RMSE = &radic;((1/N) &Sigma; (Forecast − Actual)&sup2;)</div>
                <p className="text-[11px] text-slate-400 mt-1">Penalizes large outlier forecast misses heavily.</p>
              </div>

              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <div className="font-semibold text-slate-200">WAPE (%)</div>
                <div className="font-mono text-emerald-300 mt-1">WAPE = (&Sigma; |Error| / &Sigma; Actual) &times; 100</div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Weighted percentage error, safe against low/zero generation periods.
                </p>
              </div>
            </div>
          </div>

          {/* 5. Missing Data Policy */}
          <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 text-xs">
            <span className="font-semibold text-slate-200">Missing Data Policy: </span>
            <span className="text-slate-400">
              Observations with missing forecasts or actuals are strictly excluded from mathematical metric formulas and reported in <span className="font-mono text-slate-200">missing_count</span>. Missing values are never silently coerced to zero.
            </span>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/60 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
