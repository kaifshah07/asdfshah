/**
 * Automated test runner for buildApiUrl logic.
 * Tests edge cases across Local Dev, Local Docker, and Vercel/Render Production.
 */

import assert from 'node:assert';

// Pure implementation mirroring frontend/src/services/api.ts
function buildApiUrl(endpoint, baseUrl = '') {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

  if (!baseUrl || !baseUrl.trim()) {
    return cleanEndpoint;
  }

  let cleanBase = baseUrl.trim().replace(/\/+$/, '');

  if (cleanBase.endsWith('/api')) {
    if (cleanEndpoint === '/health') {
      cleanBase = cleanBase.slice(0, -4);
    } else if (cleanEndpoint.startsWith('/api/')) {
      return `${cleanBase}${cleanEndpoint.slice(4)}`;
    }
  }

  return `${cleanBase}${cleanEndpoint}`;
}

console.log('Running buildApiUrl compatibility unit tests...');

// Case 1: Empty or whitespace base URL (Local Vite Dev or Local Docker Nginx)
assert.strictEqual(buildApiUrl('/health', ''), '/health');
assert.strictEqual(buildApiUrl('/api/wind/availability', ''), '/api/wind/availability');
assert.strictEqual(buildApiUrl('/api/wind/day-ahead', '   '), '/api/wind/day-ahead');
assert.strictEqual(buildApiUrl('/api/wind/analytics', undefined), '/api/wind/analytics');
assert.strictEqual(buildApiUrl('api/wind/analytics', ''), '/api/wind/analytics');

// Case 2: Configured base URL without trailing slash (Standard Vercel -> Render)
const RENDER_ORIGIN = 'https://gridbricks-backend.onrender.com';
assert.strictEqual(buildApiUrl('/health', RENDER_ORIGIN), `${RENDER_ORIGIN}/health`);
assert.strictEqual(buildApiUrl('/api/wind/availability', RENDER_ORIGIN), `${RENDER_ORIGIN}/api/wind/availability`);
assert.strictEqual(buildApiUrl('/api/wind/day-ahead', RENDER_ORIGIN), `${RENDER_ORIGIN}/api/wind/day-ahead`);
assert.strictEqual(buildApiUrl('/api/wind/analytics', RENDER_ORIGIN), `${RENDER_ORIGIN}/api/wind/analytics`);

// Case 3: Configured base URL with trailing slash (User typo in Vercel env var)
const RENDER_WITH_SLASH = 'https://gridbricks-backend.onrender.com/';
assert.strictEqual(buildApiUrl('/health', RENDER_WITH_SLASH), `${RENDER_ORIGIN}/health`);
assert.strictEqual(buildApiUrl('/api/wind/day-ahead', RENDER_WITH_SLASH), `${RENDER_ORIGIN}/api/wind/day-ahead`);

// Case 4: Configured base URL with trailing /api or /api/ (User accidentally added /api)
const RENDER_WITH_API = 'https://gridbricks-backend.onrender.com/api';
const RENDER_WITH_API_SLASH = 'https://gridbricks-backend.onrender.com/api/';
assert.strictEqual(buildApiUrl('/health', RENDER_WITH_API), `${RENDER_ORIGIN}/health`, 'Should target root /health');
assert.strictEqual(buildApiUrl('/health', RENDER_WITH_API_SLASH), `${RENDER_ORIGIN}/health`, 'Should target root /health');
assert.strictEqual(
  buildApiUrl('/api/wind/day-ahead', RENDER_WITH_API),
  `${RENDER_ORIGIN}/api/wind/day-ahead`,
  'Should prevent /api/api duplication'
);
assert.strictEqual(
  buildApiUrl('/api/wind/day-ahead', RENDER_WITH_API_SLASH),
  `${RENDER_ORIGIN}/api/wind/day-ahead`,
  'Should prevent /api/api duplication with trailing slash'
);

console.log('✓ All 12 buildApiUrl test cases passed successfully!');
