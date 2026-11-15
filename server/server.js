/**
 * CLEO Server-Side NASA FIRMS Proxy & Static Application Server (`server/server.js`)
 *
 * Responsibilities (Section 8):
 * 1. Reads NASA_FIRMS_MAP_KEY exclusively from server environment variables.
 * 2. Never exposes credentials to the browser.
 * 3. Checks NASA FIRMS data availability and transaction status (/mapserver/mapkey_status/).
 * 4. Caches upstream CSV responses in-memory with configurable TTL to respect the
 *    5,000 transactions / 10-minute rate limit.
 * 5. Serves the CLEO platform and exposes /api/firms/status, /api/firms/availability, and /api/firms/area.
 */

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const url = require('url');

// Auto-load .env file from project root if present (Zero-dependency)
const envPath = path.join(__dirname, '..', '.env');
if (fs.existsSync(envPath)) {
  try {
    const envLines = fs.readFileSync(envPath, 'utf8').split(/\r?\n/);
    for (const line of envLines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const eqIdx = trimmed.indexOf('=');
      if (eqIdx !== -1) {
        const k = trimmed.slice(0, eqIdx).trim();
        const v = trimmed.slice(eqIdx + 1).trim().replace(/^['"]|['"]$/g, '');
        if (k && !process.env[k]) {
          process.env[k] = v;
        }
      }
    }
  } catch (err) {
    // Fail silently on read error
  }
}

const PORT = Number(process.env.PORT || 8080);
const MAP_KEY = (process.env.NASA_FIRMS_MAP_KEY || '').trim();
const CACHE_TTL_MS = Number(process.env.CACHE_TTL_SECONDS || 900) * 1000;

const VALID_SOURCES = new Set([
  'MODIS_NRT',
  'MODIS_SP',
  'VIIRS_SNPP_NRT',
  'VIIRS_SNPP_SP',
  'VIIRS_NOAA20_NRT',
  'VIIRS_NOAA20_SP',
  'VIIRS_NOAA21_NRT',
  'VIIRS_NOAA21_SP',
]);

const responseCache = new Map();

function isValidMapKey(key) {
  return Boolean(
    key &&
    key.length === 32 &&
    /^[a-zA-Z0-9]+$/.test(key) &&
    key !== 'your_32_character_nasa_firms_map_key_here'
  );
}

function fetchHttpsText(targetUrl) {
  return new Promise((resolve, reject) => {
    const req = https.get(targetUrl, { timeout: 15000 }, (res) => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => { body += chunk; });
      res.on('end', () => {
        if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
          resolve(body);
        } else {
          reject(new Error(`Upstream NASA FIRMS HTTP ${res.statusCode}: ${body.slice(0, 200)}`));
        }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy(new Error('NASA FIRMS upstream request timed out after 15s'));
    });
  });
}

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  });
  res.end(JSON.stringify(payload, null, 2));
}

const server = http.createServer(async (req, res) => {
  const parsed = url.parse(req.url || '/', true);
  const pathname = parsed.pathname || '/';

  // Handle CORS Preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    });
    return res.end();
  }

  if (pathname === '/api/firms/status') {
    const configured = isValidMapKey(MAP_KEY);
    if (!configured) {
      return sendJson(res, 200, {
        configured: false,
        mode: 'VERIFIED_NASA_ARCHIVE',
        message: 'NASA_FIRMS_MAP_KEY not configured on server. Serving verified NASA FIRMS reference archive.',
        transaction_limit: 5000,
        transaction_interval: '10 minutes',
      });
    }
    try {
      const statusRaw = await fetchHttpsText(
        `https://firms.modaps.eosdis.nasa.gov/mapserver/mapkey_status/?MAP_KEY=${MAP_KEY}`
      );
      const statusJson = JSON.parse(statusRaw);
      return sendJson(res, 200, {
        configured: true,
        mode: 'LIVE_NASA_API',
        status: statusJson,
      });
    } catch (err) {
      return sendJson(res, 502, {
        configured: true,
        mode: 'FALLBACK_ON_UPSTREAM_ERROR',
        error: err.message,
      });
    }
  }

  if (pathname === '/api/firms/availability') {
    if (!isValidMapKey(MAP_KEY)) {
      return sendJson(res, 503, {
        error: 'NASA_FIRMS_MAP_KEY not configured.',
      });
    }
    try {
      const availRaw = await fetchHttpsText(
        `https://firms.modaps.eosdis.nasa.gov/api/data_availability/csv/${MAP_KEY}/all`
      );
      res.writeHead(200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'Cache-Control': 'public, max-age=3600',
        'Access-Control-Allow-Origin': '*',
      });
      return res.end(availRaw);
    } catch (err) {
      return sendJson(res, 502, { error: err.message });
    }
  }

  if (pathname === '/api/firms/area') {
    if (!isValidMapKey(MAP_KEY)) {
      return sendJson(res, 503, {
        error: 'Server NASA_FIRMS_MAP_KEY is not configured. Use Verified NASA Archive mode or upload NASA FIRMS CSV archives.',
      });
    }
    const source = String(parsed.query.source || 'VIIRS_NOAA20_NRT').trim();
    const bbox = String(parsed.query.bbox || 'world').trim();
    const dayRange = Math.min(10, Math.max(1, Number(parsed.query.days || 1)));
    const dateParam = parsed.query.date ? String(parsed.query.date).trim() : '';

    if (!VALID_SOURCES.has(source)) {
      return sendJson(res, 400, { error: `Invalid FIRMS sensor source: ${source}` });
    }
    const cacheKey = `${source}:${bbox}:${dayRange}:${dateParam}`;
    const cached = responseCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
      res.writeHead(200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'X-CLEO-Cache': 'HIT',
        'Access-Control-Allow-Origin': '*',
      });
      return res.end(cached.csv);
    }

    const firmsUrl =
      `https://firms.modaps.eosdis.nasa.gov/api/area/csv/${MAP_KEY}/${source}/${bbox}/${dayRange}` +
      (dateParam ? `/${dateParam}` : '');

    try {
      const csvData = await fetchHttpsText(firmsUrl);
      responseCache.set(cacheKey, { timestamp: Date.now(), csv: csvData });
      res.writeHead(200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'X-CLEO-Cache': 'MISS',
        'Access-Control-Allow-Origin': '*',
      });
      return res.end(csvData);
    } catch (err) {
      return sendJson(res, 502, { error: `Failed to retrieve NASA FIRMS data: ${err.message}` });
    }
  }

  // Serve CLEO single-page web application
  const primaryHtmlPath = path.join(__dirname, '..', 'public', 'cleo_platform.html');
  const legacyHtmlPath = path.join(__dirname, '..', 'artifacts', 'file_generation', 'ttl=63d', 'output', 'cleo_platform.html');
  const htmlPath = fs.existsSync(primaryHtmlPath) ? primaryHtmlPath : legacyHtmlPath;
  if (pathname === '/' || pathname === '/index.html' || pathname === '/cleo_platform.html') {
    if (fs.existsSync(htmlPath)) {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      return fs.createReadStream(htmlPath).pipe(res);
    }
  }

  return sendJson(res, 404, { error: 'Not found' });
});

if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`CLEO Geospatial Fire Intelligence Server listening on http://localhost:${PORT}`);
  });
}

module.exports = { server, isValidMapKey };
