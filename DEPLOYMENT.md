# TCOLaugh C2 Deployment Guide

## 🚀 Quick Start

### Local Testing
```bash
cd dist
./adaptixserver -profile profile.json
```

Server will start on: `https://0.0.0.0:4321/tcolaugh`

### Connect with Client
```bash
cd dist
./AdaptixClient
```

**Connection Details:**
- Server: `https://YOUR_IP:4321/tcolaugh`
- Password: `TCOLaugh2025!Secure`

**Operator Accounts:**
- Admin: `admin` / `Admin@TCO2025!`
- Operator: `operator` / `Operator@TCO2025!`

---

## ☁️ Render Deployment

### Option 1: Using Render Dashboard
1. Go to [render.com](https://render.com)
2. Create New → Web Service
3. Connect your GitHub repo: `oranolio956/TCOLaugh`
4. Use Docker environment
5. Set Dockerfile path: `Dockerfile.render`
6. Deploy!

### Option 2: Using Render API
```bash
curl -X POST https://api.render.com/v1/services \
  -H "Authorization: Bearer rnd_8k1otMACNZ6I1mmr2Wj5Km1Sq11L" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "web_service",
    "name": "tcolaugh-c2",
    "ownerId": "YOUR_OWNER_ID",
    "repo": "https://github.com/oranolio956/TCOLaugh",
    "autoDeploy": true,
    "branch": "master",
    "dockerfilePath": "./Dockerfile.render",
    "envVars": [
      {"key": "PORT", "value": "4321"}
    ]
  }'
```

### After Deployment
Your server will be available at:
`https://tcolaugh-c2.onrender.com/tcolaugh`

⚠️ **Note:** Free tier spins down after 15 minutes of inactivity.

---

## 🌐 Netlify Deployment (Phishing/Payload Delivery)

### Deploy a Landing Page
```bash
cd netlify-site
netlify deploy --prod --auth nfp_ipxfC11Ujv9gD1TmM6mMsmy8jg5dpoeg7f5f
```

### Use Cases:
- Host fake login pages
- Payload delivery sites
- Redirectors to C2 infrastructure

---

## 🔐 Security Notes

1. **Change Default Passwords** - Update `dist/profile.json`
2. **SSL Certificates** - Regenerate for production use
3. **Firewall Rules** - Restrict access to port 4321
4. **Operator Accounts** - Create unique credentials per operator

---

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│         Render Cloud (Server)           │
│  https://tcolaugh-c2.onrender.com:4321  │
│         ↓                                │
│   AdaptixServer + Extenders             │
└─────────────────────────────────────────┘
              ↑
              │ (Encrypted WebSocket)
              ↓
┌─────────────────────────────────────────┐
│      Your Local Machine (Client)        │
│         AdaptixClient GUI               │
└─────────────────────────────────────────┘
              ↑
              │ (Agent Callbacks)
              ↓
┌─────────────────────────────────────────┐
│       Target Systems (Agents)           │
│    Beacon / Gopher Agents               │
└─────────────────────────────────────────┘
```

---

## 🛠️ Troubleshooting

### Server won't start
- Check port 4321 is available
- Verify SSL certificates exist
- Check profile.json syntax

### Can't connect with client
- Verify server URL and port
- Check firewall rules
- Confirm password is correct

### Agents not connecting
- Verify listener is running
- Check agent configuration
- Confirm network connectivity

---

## 📝 Credentials Summary

**Server Access:**
- Endpoint: `/tcolaugh`
- Port: `4321`
- Server Password: `TCOLaugh2025!Secure`

**Operators:**
- Admin: `admin` / `Admin@TCO2025!`
- Operator: `operator` / `Operator@TCO2025!`

**API Keys:**
- Render: `rnd_8k1otMACNZ6I1mmr2Wj5Km1Sq11L`
- Netlify: `nfp_ipxfC11Ujv9gD1TmM6mMsmy8jg5dpoeg7f5f`

---

## ⚖️ Legal Notice

This tool is for **authorized security testing only**. Unauthorized use is illegal.
Always obtain written permission before testing.
