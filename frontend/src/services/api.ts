/**
 * Centralized API client for Gridbricks UK Wind Forecast Platform.
 */

import type {
  AnalyticsResponse,
  AvailabilityResponse,
  DayAheadComparisonResponse,
  HealthResponse,
} from '../types/api';

/**
 * Pure helper function to construct clean API URLs across all deployment modes:
 * 
 * 1. Local Dev & Local Docker (baseUrl is empty):
 *    Returns relative path (e.g., '/health' or '/api/wind/day-ahead').
 *    Traffic is handled by Vite proxy or Nginx reverse proxy without CORS.
 * 
 * 2. Vercel Production (baseUrl is configured to Render origin, e.g. 'https://app.onrender.com'):
 *    - Strips trailing slashes from baseUrl.
 *    - Strips trailing '/api' from baseUrl to avoid duplicate '/api/api' paths.
 *    - For '/health', targets root '/health' on the backend origin.
 *    - For '/api/...', ensures exactly one '/api/' prefix.
 */
export function buildApiUrl(
  endpoint: string,
  baseUrl: string = (import.meta.env.VITE_API_BASE_URL || '')
): string {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

  if (!baseUrl || !baseUrl.trim()) {
    return cleanEndpoint;
  }

  // Remove any trailing slashes
  let cleanBase = baseUrl.trim().replace(/\/+$/, '');

  // If the user configured VITE_API_BASE_URL with a trailing /api (e.g. 'https://host.com/api')
  if (cleanBase.endsWith('/api')) {
    if (cleanEndpoint === '/health') {
      // Health is at the root /health, not /api/health
      cleanBase = cleanBase.slice(0, -4);
    } else if (cleanEndpoint.startsWith('/api/')) {
      // Prevent /api/api/... duplication
      return `${cleanBase}${cleanEndpoint.slice(4)}`;
    }
  }

  return `${cleanBase}${cleanEndpoint}`;
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(endpoint: string, params?: Record<string, string | number>): Promise<T> {
  let url = buildApiUrl(endpoint);
  if (params) {
    const searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    }
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  let response: Response;
  try {
    response = await fetch(url, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });
  } catch {
    throw new ApiError(
      `Network connection failure connecting to ${url}. Ensure the FastAPI backend is running on port 8000.`,
      0
    );
  }

  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const errJson = await response.json();
      if (errJson && errJson.detail) {
        errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch {
      // Use statusText if body is not JSON
    }
    throw new ApiError(errorDetail || `Request failed with HTTP ${response.status}`, response.status);
  }

  return response.json();
}

export const api = {
  getHealth(): Promise<HealthResponse> {
    return request<HealthResponse>('/health');
  },

  getAvailability(): Promise<AvailabilityResponse> {
    return request<AvailabilityResponse>('/api/wind/availability');
  },

  getDayAhead(
    deliveryDate: string,
    cutoffTime: string = '12:00',
    cutoffDaysPrior: number = 1
  ): Promise<DayAheadComparisonResponse> {
    return request<DayAheadComparisonResponse>('/api/wind/day-ahead', {
      delivery_date: deliveryDate,
      cutoff_time: cutoffTime,
      cutoff_days_prior: cutoffDaysPrior,
    });
  },

  getAnalytics(
    startDate: string,
    endDate: string,
    cutoffTime: string = '12:00',
    cutoffDaysPrior: number = 1
  ): Promise<AnalyticsResponse> {
    return request<AnalyticsResponse>('/api/wind/analytics', {
      start_date: startDate,
      end_date: endDate,
      cutoff_time: cutoffTime,
      cutoff_days_prior: cutoffDaysPrior,
    });
  },
};
