import React from 'react';
import { Calendar, ChevronLeft, ChevronRight, Clock, RefreshCw, SlidersHorizontal } from 'lucide-react';

interface FilterControlsProps {
  activeTab: 'day-ahead' | 'analytics';
  deliveryDate: string;
  onDeliveryDateChange: (date: string) => void;
  startDate: string;
  onStartDateChange: (date: string) => void;
  endDate: string;
  onEndDateChange: (date: string) => void;
  cutoffTime: string;
  onCutoffTimeChange: (time: string) => void;
  cutoffDaysPrior: number;
  onCutoffDaysPriorChange: (days: number) => void;
  onApply: () => void;
  isLoading: boolean;
  minDate?: string;
  maxDate?: string;
}

export const FilterControls: React.FC<FilterControlsProps> = ({
  activeTab,
  deliveryDate,
  onDeliveryDateChange,
  startDate,
  onStartDateChange,
  endDate,
  onEndDateChange,
  cutoffTime,
  onCutoffTimeChange,
  cutoffDaysPrior,
  onCutoffDaysPriorChange,
  onApply,
  isLoading,
  minDate = '2026-01-01',
  maxDate = '2026-01-31',
}) => {
  // Helpers for step prev/next day
  const shiftDay = (delta: number) => {
    try {
      const current = new Date(deliveryDate);
      current.setDate(current.getDate() + delta);
      const nextStr = current.toISOString().split('T')[0];
      if (nextStr >= minDate && nextStr <= maxDate) {
        onDeliveryDateChange(nextStr);
      }
    } catch {
      // ignore
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 mb-6 shadow-sm">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        {/* Left Side: Date Selectors */}
        <div className="flex flex-wrap items-center gap-3">
          {activeTab === 'day-ahead' ? (
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                Delivery Date:
              </span>
              <div className="flex items-center gap-1 bg-slate-950 border border-slate-700 rounded-lg p-1">
                <button
                  type="button"
                  onClick={() => shiftDay(-1)}
                  disabled={deliveryDate <= minDate || isLoading}
                  className="p-1 hover:bg-slate-800 rounded text-slate-300 disabled:opacity-30 disabled:cursor-not-allowed"
                  title="Previous Day"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <input
                  type="date"
                  value={deliveryDate}
                  min={minDate}
                  max={maxDate}
                  onChange={(e) => onDeliveryDateChange(e.target.value)}
                  className="bg-transparent text-sm text-slate-200 font-mono focus:outline-none px-2"
                />
                <button
                  type="button"
                  onClick={() => shiftDay(1)}
                  disabled={deliveryDate >= maxDate || isLoading}
                  className="p-1 hover:bg-slate-800 rounded text-slate-300 disabled:opacity-30 disabled:cursor-not-allowed"
                  title="Next Day"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>

              {/* Quick Jump Buttons */}
              <div className="hidden sm:flex items-center gap-1 ml-2 text-xs">
                {['2026-01-01', '2026-01-15', '2026-01-31'].map((d) => (
                  <button
                    key={d}
                    type="button"
                    onClick={() => onDeliveryDateChange(d)}
                    className={`px-2 py-1 rounded text-xs font-mono transition-colors ${
                      deliveryDate === d
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                        : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Jan {d.slice(8)}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Range:
                </span>
                <div className="flex items-center gap-2 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1">
                  <Calendar className="h-3.5 w-3.5 text-slate-400" />
                  <input
                    type="date"
                    value={startDate}
                    min={minDate}
                    max={endDate}
                    onChange={(e) => onStartDateChange(e.target.value)}
                    className="bg-transparent text-sm text-slate-200 font-mono focus:outline-none"
                  />
                  <span className="text-slate-500">to</span>
                  <input
                    type="date"
                    value={endDate}
                    min={startDate}
                    max={maxDate}
                    onChange={(e) => onEndDateChange(e.target.value)}
                    className="bg-transparent text-sm text-slate-200 font-mono focus:outline-none"
                  />
                </div>
              </div>

              {/* Quick Range Presets */}
              <div className="flex items-center gap-1 text-xs">
                <button
                  type="button"
                  onClick={() => {
                    onStartDateChange('2026-01-01');
                    onEndDateChange('2026-01-07');
                  }}
                  className="px-2 py-1 rounded bg-slate-800 text-slate-400 hover:text-slate-200"
                >
                  Wk 1
                </button>
                <button
                  type="button"
                  onClick={() => {
                    onStartDateChange('2026-01-08');
                    onEndDateChange('2026-01-14');
                  }}
                  className="px-2 py-1 rounded bg-slate-800 text-slate-400 hover:text-slate-200"
                >
                  Wk 2
                </button>
                <button
                  type="button"
                  onClick={() => {
                    onStartDateChange('2026-01-01');
                    onEndDateChange('2026-01-31');
                  }}
                  className="px-2 py-1 rounded bg-slate-800 text-slate-400 hover:text-slate-200"
                >
                  Full Month
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Cutoff Settings & Apply Button */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Decision Cutoff Selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Clock className="h-3 w-3 text-amber-400" />
              Decision Cutoff:
            </span>
            <div className="flex items-center gap-1 bg-slate-950 border border-slate-700 rounded-lg px-2 py-1">
              <span className="text-xs text-slate-400">D-</span>
              <select
                value={cutoffDaysPrior}
                onChange={(e) => onCutoffDaysPriorChange(Number(e.target.value))}
                className="bg-transparent text-xs text-slate-200 font-mono focus:outline-none cursor-pointer"
                title="Number of days prior to delivery day when decision is made"
              >
                <option value={1} className="bg-slate-900 text-slate-200">1 (Day-Ahead)</option>
                <option value={0} className="bg-slate-900 text-slate-200">0 (Within-Day)</option>
                <option value={2} className="bg-slate-900 text-slate-200">2 (Two-Days-Ahead)</option>
              </select>

              <span className="text-slate-600">|</span>

              <select
                value={cutoffTime}
                onChange={(e) => onCutoffTimeChange(e.target.value)}
                className="bg-transparent text-xs text-slate-200 font-mono focus:outline-none cursor-pointer"
                title="UTC cutoff time on decision day"
              >
                <option value="09:00" className="bg-slate-900 text-slate-200">09:00 UTC</option>
                <option value="11:00" className="bg-slate-900 text-slate-200">11:00 UTC</option>
                <option value="11:30" className="bg-slate-900 text-slate-200">11:30 UTC</option>
                <option value="12:00" className="bg-slate-900 text-slate-200">12:00 UTC (Default)</option>
                <option value="14:00" className="bg-slate-900 text-slate-200">14:00 UTC</option>
                <option value="17:00" className="bg-slate-900 text-slate-200">17:00 UTC</option>
              </select>
            </div>
          </div>

          {/* Apply Button */}
          <button
            type="button"
            onClick={onApply}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 text-white rounded-lg text-xs font-semibold shadow transition-all cursor-pointer disabled:cursor-not-allowed"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>{isLoading ? 'Updating...' : 'Apply Filters'}</span>
          </button>
        </div>
      </div>
      
      <div className="mt-2 text-[11px] text-slate-500 flex items-center gap-1.5">
        <SlidersHorizontal className="h-3 w-3" />
        <span>
          Cutoff rule: Forecasts published strictly on or before D-{cutoffDaysPrior} {cutoffTime} UTC are selected. Later revisions are excluded to prevent lookahead bias.
        </span>
      </div>
    </div>
  );
};
