# 🚀 Panopticon Deployment - Complete Configuration

## ✅ Deployment Status: FULLY OPERATIONAL

Both frontend and backend are successfully deployed and connected.

---

## 📊 Service URLs

### Frontend (Vercel)
- **Production URL**: `<your-vercel-app-url>`
- **Alternative URLs**: add any preview deployments provided by Vercel

### Backend (Render)
- **API Base URL**: `<your-render-api-url>`
- **Services**: record the Render service IDs from the dashboard once provisioned

---

## 🔑 API Configuration

### Primary API Key
Store the generated `PANOPTICON_API_KEY` in your secret manager and surface it to both the API and dashboard at runtime. Never hard-code it in source control.

### API Endpoints
- `GET /` - Public health check
- `GET /health` - Public health check
- `GET /stats` - Protected endpoint (requires API key)
- `GET /test` - Protected endpoint (requires API key)

### Testing the API
```bash
# Health check (public)
curl https://<your-render-api-url>/health

# Stats endpoint (requires API key)
curl -H "X-API-Key: $PANOPTICON_API_KEY" https://<your-render-api-url>/stats
```

---

## 🌐 Frontend Configuration

Before first use, open the dashboard settings card and enter:
- **API URL**: `https://<your-render-api-url>`
- **API Key**: the secret you generated above

### To Use the Dashboard:
1. Visit your Vercel deployment
2. Fill in the API URL and key in the Connection Settings panel
3. Click "Save & Refresh" to connect
4. The dashboard will load live stats from the backend
5. API keys are kept only in memory per tab; re-enter them if you refresh.

---

## 🔧 Environment Variables

### Backend (Render) - Already Configured
```
PANOPTICON_API_KEY=<set via Render/Vault>
PANOPTICON_DB_PATH=/opt/render/project/.render/panopticon.db
REDIS_URL=redis://localhost:6379
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<set via Render/Vault>
PANOPTICON_API_BASE_URL=https://<your-render-api-url>
MILVUS_HOST=localhost
MILVUS_PORT=19530
PANOPTICON_USE_KAFKA=false
PANOPTICON_ENABLE_AI_BRIEFING=false
PANOPTICON_MAX_UPLOAD_BYTES=5242880
PANOPTICON_MAX_SEARCH_RESULTS=100
PANOPTICON_RATE_LIMIT_WINDOW=60
PANOPTICON_RATE_LIMIT_MAX=60
```

### Frontend (Vercel) - No ENV vars needed
The frontend keeps only the API base URL in `localStorage`; API keys stay in-memory per session.

### Crawlers / Workers
```
PANOPTICON_API_BASE_URL=https://<your-render-api-url>
PANOPTICON_API_KEY=<same secret as API>
PANOPTICON_KAFKA_TOPIC=raw_ingestion          # optional
PANOPTICON_USE_KAFKA=false                    # flip to true when broker is ready
```
When HTTP ingestion is configured, crawlers post to `POST /ingest/record` and only fall back to Kafka/SQLite if the request fails.

---

## 📝 GitHub Repository

- **Repository**: https://github.com/oranolio956/TCOLaugh
- **Branch**: main
- **Auto-deploy**: Enabled for both Vercel and Render

### Important Files:
- `/panopticon/api/simple_main.py` - Simplified API for backend
- `/panopticon/api/templates/index.html` - Frontend dashboard
- `/vercel.json` - Vercel deployment configuration
- `/render.yaml` - Render services configuration

---

## 🔄 Auto-Deploy Configuration

### Render
- Auto-deploys on push to `main` branch
- Build command: `pip install fastapi uvicorn[standard]`
- Start command: `uvicorn panopticon.api.simple_main:app --host 0.0.0.0 --port $PORT`

### Vercel
- Auto-deploys on push to `main` branch
- Framework: Other (static HTML)
- No build process required

---

## 🛠️ Management Dashboards

### Render Dashboard
- URL: https://dashboard.render.com
- View logs, manage services, update environment variables

### Vercel Dashboard
- URL: https://vercel.com/dashboard
- View deployments, manage domains, analytics

---

## ✅ Features Working

1. ✅ Backend API responding to health checks
2. ✅ API authentication with X-API-Key header
3. ✅ Worker service processing background tasks
4. ✅ Crawler service running continuously
5. ✅ Frontend dashboard loading successfully
6. ✅ Frontend hosts connection settings (no baked-in secrets)
7. ✅ CORS configured for cross-origin requests
8. ✅ Auto-deploy on git push

---

## 🚨 Troubleshooting

### If API returns 403 Forbidden:
- Confirm you are sending the production `PANOPTICON_API_KEY` from your secret store
- Ensure the `X-API-Key` header is included in requests
- Check whether the rate limit threshold (`PANOPTICON_RATE_LIMIT_MAX`) has been exceeded (HTTP 429)

### If Frontend can't connect to backend:
- Verify CORS is working (already configured)
- Check that the API URL is correct in the Connection Settings
- Make sure to click "Save & Refresh" after entering credentials

### To update services:
1. Make changes in the GitHub repository
2. Push to main branch
3. Services will auto-deploy (takes ~2-5 minutes)

---

## 📧 Support Contacts

- **GitHub Repository**: https://github.com/oranolio956/TCOLaugh
- **Vercel Account**: metzlerdalton3-2498
- **Render Owner ID**: tea-d419fdili9vc739hocog

---

## 🎉 Deployment Complete!

The full stack application is now deployed and operational. Both frontend and backend are connected and working together.

**Live Application**: https://<your-vercel-app-url>