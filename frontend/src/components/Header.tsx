import React from 'react';
import { Activity, Calendar, Clock, Database, HelpCircle, ShieldCheck } from 'lucide-react';
import type { AvailabilityResponse } from '../types/api';

interface HeaderProps {
  activeTab: 'day-ahead' | 'analytics';
  onTabChange: (tab: 'day-ahead' | 'analytics') => void;
  availability: AvailabilityResponse | null;
  cutoffTime: string;
  cutoffDaysPrior: number;
  onOpenMethodology: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onTabChange,
  availability,
  cutoffTime,
  cutoffDaysPrior,
  onOpenMethodology,
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-30 px-4 py-3 sm:px-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        {/* Brand & Title */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold">
            <Activity className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-slate-100 tracking-tight text-lg">Gridbricks</span>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 font-mono">
                UK Day-Ahead Market
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Wind Generation Forecast Decision-Support & Accuracy Evaluation
            </p>
          </div>
        </div>

        {/* Status Indicators & Metadata */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-xs">
          {availability && (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700/60 text-slate-300">
              <Database className="h-3.5 w-3.5 text-cyan-400" />
              <span>
                Coverage: <span className="font-mono text-cyan-300">{availability.min_date}</span> to{' '}
                <span className="font-mono text-cyan-300">{availability.max_date}</span>
              </span>
            </div>
          )}

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700/60 text-slate-300">
            <Clock className="h-3.5 w-3.5 text-amber-400" />
            <span>
              Decision Cutoff: <span className="font-mono text-amber-300">D-{cutoffDaysPrior} {cutoffTime} UTC</span>
            </span>
          </div>

          <button
            onClick={onOpenMethodology}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 transition-colors"
            title="View calculation methodology and source data details"
          >
            <HelpCircle className="h-3.5 w-3.5 text-indigo-400" />
            <span>Methodology</span>
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto mt-3 flex items-center border-t border-slate-800/80 pt-2 gap-4">
        <button
          onClick={() => onTabChange('day-ahead')}
          className={`flex items-center gap-2 text-sm font-medium py-1.5 px-3 rounded-md transition-colors ${
            activeTab === 'day-ahead'
              ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
          }`}
        >
          <Calendar className="h-4 w-4" />
          <span>Day-Ahead Decision View</span>
        </button>

        <button
          onClick={() => onTabChange('analytics')}
          className={`flex items-center gap-2 text-sm font-medium py-1.5 px-3 rounded-md transition-colors ${
            activeTab === 'analytics'
              ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
          }`}
        >
          <ShieldCheck className="h-4 w-4" />
          <span>Forecast Accuracy Analytics</span>
        </button>
      </div>
    </header>
  );
};
