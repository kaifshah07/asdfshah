# Gridbricks Deployment & Environment Guide

**Document Version:** 1.0.0  
**Target Environments:** Local Development, Local Docker Compose, Cloud (Vercel + Render)  

---

## 1. Environment Compatibility Matrix

| Setting / Variable | Local Dev (`npm run dev`) | Local Docker (`compose.yaml`) | Cloud Vercel + Render |
| :--- | :--- | :--- | :--- |
| **Frontend Port** | `5173` | `3000` (host mapped to container :80) | Port 443 (HTTPS) |
| **Backend Port** | `8000` | `8000` (host mapped to container :8000)| Dynamic `$PORT` |
| **`VITE_API_BASE_URL`** | Empty string `""` | Empty string `""` | `https://<render-service>.onrender.com` |
| **API Proxy** | Vite dev proxy (`localhost:5173/api`) | Nginx reverse proxy (`localhost:3000/api`) | Direct cross-origin `fetch()` to Render |
| **`CORS_ALLOWED_ORIGINS`**| Default localhost origins | Default localhost origins | `*` or `https://<vercel-app>.vercel.app` |
| **Health Check Path** | `http://127.0.0.1:8000/health` | `http://localhost:3000/health` | `https://<render-service>.onrender.com/health` |

---

## 2. Docker Compose Deployment

Docker Compose orchestrates both services on a private virtual bridge network (`gridbricks-net`):

```bash
# Start all containers in the background
docker compose up -d

# Inspect health status and port mappings
docker compose ps

# View container logs
docker compose logs -f

# Stop containers cleanly
docker compose down
```

### Container Layout
- **`backend`:** Runs `python:3.11-slim`, exposes port 8000, runs container healthcheck (`curl -f http://localhost:8000/health`).
- **`frontend`:** Multi-stage build (Node 22 builder + Nginx Alpine runner), exposes container port 80 mapped to host 3000, proxies `/api/` to `http://backend:8000/api/`.

---

## 3. Render Deployment (Backend Web Service)

1. Connect your repository on [Render](https://dashboard.render.com/).
2. Select **Web Service** with runtime **Python 3**.
3. Configure:
   - **Build Command:** `pip install --no-cache-dir -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
4. Set Environment Variables:
   - `PYTHONPATH`: `.`
   - `PYTHON_VERSION`: `3.11.9`
   - `CORS_ALLOWED_ORIGINS`: `*` (or your specific Vercel URL once known)
5. Verify live endpoint: `https://<your-service>.onrender.com/health`.

---

## 4. Vercel Deployment (Frontend Static SPA)

1. Import your repository on [Vercel](https://vercel.com/new).
2. Configure:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Select `frontend` (or leave root)
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
3. Environment Variables:
   - **`VITE_API_BASE_URL`**: `https://<your-service>.onrender.com`
   > **Note on Vite Build-Time Variables:** Vite embeds `import.meta.env.VITE_*` into the compiled JavaScript chunks at build time. If you change `VITE_API_BASE_URL` in Vercel settings, you must trigger a new deployment to rebuild the static assets.
4. Deploy and verify the live dashboard in an incognito window.
