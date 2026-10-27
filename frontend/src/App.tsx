import React, { useEffect, useRef, useState } from 'react';
import { Header } from './components/Header';
import { FilterControls } from './components/FilterControls';
import { KpiCards } from './components/KpiCards';
import { ForecastChart } from './components/ForecastChart';
import { ErrorDistributionChart } from './components/ErrorDistributionChart';
import { AnalyticsView } from './components/AnalyticsView';
import { MethodologyModal } from './components/MethodologyModal';
import { EmptyState, ErrorState, LoadingState } from './components/StatusStates';
import { api, ApiError } from './services/api';
import type {
  AnalyticsResponse,
  AvailabilityResponse,
  DayAheadComparisonResponse,
} from './types/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'day-ahead' | 'analytics'>('day-ahead');

  // Filter Parameters
  const [deliveryDate, setDeliveryDate] = useState<string>('2026-01-15');
  const [startDate, setStartDate] = useState<string>('2026-01-01');
  const [endDate, setEndDate] = useState<string>('2026-01-31');
  const [cutoffTime, setCutoffTime] = useState<string>('12:00');
  const [cutoffDaysPrior, setCutoffDaysPrior] = useState<number>(1);

  // Data States
  const [availability, setAvailability] = useState<AvailabilityResponse | null>(null);
  const [dayAheadData, setDayAheadData] = useState<DayAheadComparisonResponse | null>(null);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsResponse | null>(null);

  // Status States
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isMethodologyOpen, setIsMethodologyOpen] = useState<boolean>(false);

  // Sequence token to prevent out-of-order response races
  const requestIdRef = useRef<number>(0);

  // Initial load
  useEffect(() => {
    const currentReq = ++requestIdRef.current;
    async function initData() {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const avail = await api.getAvailability();
        if (currentReq !== requestIdRef.current) return;
        setAvailability(avail);

        const da = await api.getDayAhead('2026-01-15', '12:00', 1);
        if (currentReq !== requestIdRef.current) return;
        setDayAheadData(da);

        const an = await api.getAnalytics('2026-01-01', '2026-01-31', '12:00', 1);
        if (currentReq !== requestIdRef.current) return;
        setAnalyticsData(an);
      } catch (err) {
        if (currentReq === requestIdRef.current) {
          if (err instanceof ApiError) {
            setErrorMessage(err.message);
          } else {
            setErrorMessage('Failed to connect to the backend API service.');
          }
        }
      } finally {
        if (currentReq === requestIdRef.current) {
          setIsLoading(false);
        }
      }
    }

    initData();
  }, []);

  // Handler for Applying Filters
  const handleApplyFilters = async () => {
    const currentReq = ++requestIdRef.current;
    setIsLoading(true);
    setErrorMessage(null);

    // Clear stale dataset to prevent displaying previous date data if request fails
    if (activeTab === 'day-ahead') {
      setDayAheadData(null);
    } else {
      setAnalyticsData(null);
    }

    try {
      if (activeTab === 'day-ahead') {
        const da = await api.getDayAhead(deliveryDate, cutoffTime, cutoffDaysPrior);
        if (currentReq === requestIdRef.current) {
          setDayAheadData(da);
        }
      } else {
        const an = await api.getAnalytics(startDate, endDate, cutoffTime, cutoffDaysPrior);
        if (currentReq === requestIdRef.current) {
          setAnalyticsData(an);
        }
      }
    } catch (err) {
      if (currentReq === requestIdRef.current) {
        if (err instanceof ApiError) {
          setErrorMessage(err.message);
        } else {
          setErrorMessage('An unexpected error occurred while fetching data.');
        }
      }
    } finally {
      if (currentReq === requestIdRef.current) {
        setIsLoading(false);
      }
    }
  };

  // If user switches tab and data is missing, fetch it
  const handleTabChange = async (tab: 'day-ahead' | 'analytics') => {
    setActiveTab(tab);
    setErrorMessage(null);
    const currentReq = ++requestIdRef.current;

    if (tab === 'analytics' && !analyticsData) {
      setIsLoading(true);
      try {
        const an = await api.getAnalytics(startDate, endDate, cutoffTime, cutoffDaysPrior);
        if (currentReq === requestIdRef.current) {
          setAnalyticsData(an);
        }
      } catch (err) {
        if (currentReq === requestIdRef.current) {
          if (err instanceof ApiError) setErrorMessage(err.message);
        }
      } finally {
        if (currentReq === requestIdRef.current) {
          setIsLoading(false);
        }
      }
    } else if (tab === 'day-ahead' && !dayAheadData) {
      setIsLoading(true);
      try {
        const da = await api.getDayAhead(deliveryDate, cutoffTime, cutoffDaysPrior);
        if (currentReq === requestIdRef.current) {
          setDayAheadData(da);
        }
      } catch (err) {
        if (currentReq === requestIdRef.current) {
          if (err instanceof ApiError) setErrorMessage(err.message);
        }
      } finally {
        if (currentReq === requestIdRef.current) {
          setIsLoading(false);
        }
      }
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* 1. Header */}
      <Header
        activeTab={activeTab}
        onTabChange={handleTabChange}
        availability={availability}
        cutoffTime={cutoffTime}
        cutoffDaysPrior={cutoffDaysPrior}
        onOpenMethodology={() => setIsMethodologyOpen(true)}
      />

      {/* 2. Main Content Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6 sm:px-6">
        {/* Filters and Controls */}
        <FilterControls
          activeTab={activeTab}
          deliveryDate={deliveryDate}
          onDeliveryDateChange={setDeliveryDate}
          startDate={startDate}
          onStartDateChange={setStartDate}
          endDate={endDate}
          onEndDateChange={setEndDate}
          cutoffTime={cutoffTime}
          onCutoffTimeChange={setCutoffTime}
          cutoffDaysPrior={cutoffDaysPrior}
          onCutoffDaysPriorChange={setCutoffDaysPrior}
          onApply={handleApplyFilters}
          isLoading={isLoading}
          minDate={availability?.min_date}
          maxDate={availability?.max_date}
        />

        {/* Error Banner */}
        {errorMessage && (
          <ErrorState
            message={errorMessage}
            onRetry={handleApplyFilters}
          />
        )}

        {/* Loading State */}
        {isLoading && !errorMessage && (
          <LoadingState
            message={
              activeTab === 'day-ahead'
                ? `Reconstructing Day-Ahead forecast for ${deliveryDate} (Cutoff: D-${cutoffDaysPrior} ${cutoffTime} UTC)...`
                : `Computing multi-day forecast analytics from ${startDate} to ${endDate}...`
            }
          />
        )}

        {/* Content: Day-Ahead Tab */}
        {!isLoading && !errorMessage && activeTab === 'day-ahead' && (
          <div>
            {dayAheadData ? (
              <>
                <KpiCards metrics={dayAheadData.metrics} />
                <ForecastChart
                  periods={dayAheadData.periods}
                  deliveryDate={dayAheadData.delivery_date}
                />
                <ErrorDistributionChart periods={dayAheadData.periods} />
              </>
            ) : (
              <EmptyState />
            )}
          </div>
        )}

        {/* Content: Analytics Tab */}
        {!isLoading && !errorMessage && activeTab === 'analytics' && (
          <div>
            {analyticsData ? (
              <AnalyticsView analytics={analyticsData} />
            ) : (
              <EmptyState />
            )}
          </div>
        )}
      </main>

      {/* 3. Institutional Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 px-4 py-4 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            <span className="font-semibold text-slate-400">Gridbricks Decision Platform</span> — UK Wholesale Power Day-Ahead Forecasting
          </div>
          <div className="flex items-center gap-4 text-[11px]">
            <span>Data: Elexon BMRS (FUELHH & WINDFOR)</span>
            <span>•</span>
            <span>Target Period: January 2026</span>
            <span>•</span>
            <span>Resolution: Half-Hourly (48 SP/Day)</span>
          </div>
        </div>
      </footer>

      {/* 4. Methodology Modal */}
      <MethodologyModal
        isOpen={isMethodologyOpen}
        onClose={() => setIsMethodologyOpen(false)}
      />
    </div>
  );
};

export default App;
