import React from 'react';
import { AlertCircle, Loader2, SearchX } from 'lucide-react';

export const LoadingState: React.FC<{ message?: string }> = ({
  message = 'Loading day-ahead forecasts & actuals...',
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-16 text-slate-400 bg-slate-900/50 border border-slate-800 rounded-2xl my-8">
      <Loader2 className="h-8 w-8 text-emerald-400 animate-spin mb-3" />
      <div className="text-sm font-medium text-slate-200">{message}</div>
      <p className="text-xs text-slate-500 mt-1">Reconstructing pre-auction decision state from cached Elexon data</p>
    </div>
  );
};

export const ErrorState: React.FC<{
  title?: string;
  message: string;
  onRetry?: () => void;
}> = ({ title = 'Failed to Load Market Data', message, onRetry }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-rose-950/20 border border-rose-900/50 rounded-2xl my-8 max-w-xl mx-auto">
      <div className="h-12 w-12 rounded-full bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mb-3">
        <AlertCircle className="h-6 w-6" />
      </div>
      <h3 className="text-base font-semibold text-rose-200">{title}</h3>
      <p className="text-xs text-rose-300/80 mt-1.5 max-w-md leading-relaxed">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 px-4 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold transition-colors cursor-pointer"
        >
          Retry Request
        </button>
      )}
    </div>
  );
};

export const EmptyState: React.FC<{
  title?: string;
  message?: string;
}> = ({
  title = 'No Aligned Observations Found',
  message = 'No forecast or actual generation observations were found matching the selected filter criteria.',
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-14 text-center bg-slate-900/40 border border-slate-800 rounded-2xl my-8 max-w-lg mx-auto">
      <SearchX className="h-10 w-10 text-slate-600 mb-3" />
      <h3 className="text-sm font-semibold text-slate-300">{title}</h3>
      <p className="text-xs text-slate-500 mt-1 max-w-sm">{message}</p>
    </div>
  );
};
