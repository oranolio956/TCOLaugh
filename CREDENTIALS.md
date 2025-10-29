# 🔐 TCOLaugh C2 - Credentials & Access

## ⚠️ SECURITY WARNING
**Keep this file secure! Contains sensitive credentials.**

---

## 🖥️ Server Access

### Local Server
- **URL:** `https://localhost:4321/tcolaugh`
- **Interface:** `0.0.0.0` (all interfaces)
- **Port:** `4321`
- **Endpoint:** `/tcolaugh`

### Cloud Server (Render)
- **URL:** `https://tcolaugh-c2.onrender.com:4321/tcolaugh`
- **Status:** Ready for deployment
- **Plan:** Free tier (spins down after 15min inactivity)

---

## 👤 Operator Accounts

### Admin Account
- **Username:** `admin`
- **Password:** `Admin@TCO2025!`
- **Permissions:** Full access

### Operator Account
- **Username:** `operator`
- **Password:** `Operator@TCO2025!`
- **Permissions:** Standard operator

### Server Password (Quick Connect)
- **Password:** `TCOLaugh2025!Secure`
- **Mode:** `only_password: true`

---

## 🔑 API Keys

### Render API
```
rnd_8k1otMACNZ6I1mmr2Wj5Km1Sq11L
```
**Usage:**
```bash
curl -H "Authorization: Bearer rnd_8k1otMACNZ6I1mmr2Wj5Km1Sq11L" \
  https://api.render.com/v1/services
```

### Netlify API
```
nfp_ipxfC11Ujv9gD1TmM6mMsmy8jg5dpoeg7f5f
```
**Usage:**
```bash
netlify deploy --auth nfp_ipxfC11Ujv9gD1TmM6mMsmy8jg5dpoeg7f5f
```

---

## 🔒 SSL Certificates

### Location
```
dist/server.rsa.crt
dist/server.rsa.key
```

### Details
- **Type:** RSA 2048-bit
- **Validity:** 3650 days (10 years)
- **Subject:** `/C=US/ST=State/L=City/O=TCOLaugh/CN=tcolaugh.local`

### Regenerate (if needed)
```bash
cd dist
openssl req -x509 -nodes -newkey rsa:2048 \
  -keyout server.rsa.key -out server.rsa.crt \
  -days 3650 -subj "/C=US/ST=State/L=City/O=TCOLaugh/CN=tcolaugh.local"
```

---

## 📦 Built Artifacts

### Server
- **Binary:** `dist/adaptixserver` (29MB)
- **Platform:** Linux x86_64
- **Go Version:** 1.24.4

### Client
- **Binary:** `dist/AdaptixClient` (17MB)
- **Platform:** Linux x86_64
- **Qt Version:** 6.4.2

### Extenders
```
dist/extenders/
├── agent_beacon/          # Windows/Linux beacon agent
├── agent_gopher/          # Cross-platform gopher agent
├── listener_beacon_http/  # HTTP/HTTPS listener
├── listener_beacon_smb/   # SMB listener
├── listener_beacon_tcp/   # TCP listener
└── listener_gopher_tcp/   # Gopher TCP listener
```

---

## 🌐 Deployment URLs

### GitHub Repository
```
https://github.com/oranolio956/TCOLaugh
```

### Render Service (After Deployment)
```
https://tcolaugh-c2.onrender.com
```

### Netlify Site (After Deployment)
```
https://tcolaugh-phishing.netlify.app
```

---

## 🔧 Configuration Files

### Server Profile
**File:** `dist/profile.json`

**Key Settings:**
- Interface: `0.0.0.0`
- Port: `4321`
- Endpoint: `/tcolaugh`
- SSL Cert: `server.rsa.crt`
- SSL Key: `server.rsa.key`

### Token Lifetimes
- **Access Token:** 12 hours
- **Refresh Token:** 168 hours (7 days)

---

## 📊 Quick Reference

### Start Server
```bash
cd dist
./adaptixserver -profile profile.json
```

### Start Client
```bash
cd dist
./AdaptixClient
```

### Connect Client to Server
1. Launch AdaptixClient
2. Enter server URL: `https://YOUR_SERVER:4321/tcolaugh`
3. Enter password: `TCOLaugh2025!Secure`
4. Or use operator credentials

---

## 🛡️ Security Best Practices

1. **Change Default Passwords**
   - Update all passwords in `profile.json`
   - Use strong, unique passwords

2. **Regenerate SSL Certificates**
   - Create new certificates for production
   - Use proper domain names

3. **Restrict Access**
   - Use firewall rules
   - Limit IP ranges
   - Enable VPN access only

4. **Rotate API Keys**
   - Regularly rotate Render/Netlify keys
   - Revoke unused keys

5. **Monitor Access**
   - Review operator logs
   - Track agent connections
   - Monitor for anomalies

---

## 📝 Notes

- All passwords are for **authorized testing only**
- Change credentials before production use
- Keep this file in a secure location
- Never commit real credentials to public repos

---

**Last Updated:** October 29, 2024
**Framework Version:** AdaptixC2 v0.9
**Build:** TCOLaugh Edition
