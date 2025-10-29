# 🕷️ TCOLaugh - Command & Control Framework

> **Based on AdaptixC2 v0.9** - A powerful post-exploitation and adversarial emulation framework for authorized penetration testing.

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-red.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform](https://img.shields.io/badge/Platform-Cross--Platform-darkred.svg)](https://github.com/oranolio956/TCOLaugh)

---

## ⚠️ **LEGAL WARNING**

**This tool is designed for AUTHORIZED security testing and red team operations ONLY.**

Unauthorized use is strictly prohibited and may violate local and international laws. Use at your own risk.

---

## 🚀 Quick Start

### 1. Start the Server
```bash
cd dist
./adaptixserver -profile profile.json
```

Server starts on: `https://0.0.0.0:4321/tcolaugh`

### 2. Launch the Client
```bash
cd dist
./AdaptixClient
```

### 3. Connect
- **Server URL:** `https://YOUR_IP:10000/tcolaugh`
- **Password:** `TCOLaugh2025!Secure`

---

## 📦 What's Included

### ✅ Server (29MB)
- AdaptixServer binary
- Full database support
- JWT authentication
- Multi-operator support

### ✅ Client (17MB)
- Cross-platform Qt6 GUI
- Real-time agent monitoring
- Interactive file/process browsers
- Terminal access
- Scripting engine

### ✅ Extenders
- **Listeners:** HTTP/HTTPS, TCP, SMB, Gopher
- **Agents:** Beacon (Windows), Gopher (Cross-platform)
- **BOF Support:** Beacon Object Files
- **Tunneling:** SOCKS4/5, Port forwarding

---

## 🌟 Features

- ✅ Server/Client architecture for multiplayer
- ✅ Fully encrypted communications
- ✅ Plugin-based extenders
- ✅ Task and job storage
- ✅ Credentials manager
- ✅ Targets manager
- ✅ Remote terminal
- ✅ File/process browsers
- ✅ SOCKS proxies
- ✅ Port forwarding
- ✅ Agent linking
- ✅ Health checking
- ✅ Kill date & working time control
- ✅ Windows/Linux/macOS support

---

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[CREDENTIALS.md](CREDENTIALS.md)** - All credentials and access details
- **[Official Docs](https://adaptix-framework.gitbook.io/adaptix-framework)** - Full AdaptixC2 documentation

---

## ☁️ Cloud Deployment

### Render (C2 Server)
```bash
# Deploy via Render Dashboard
1. Go to render.com
2. New Web Service
3. Connect repo: oranolio956/TCOLaugh
4. Use Dockerfile.render
5. Deploy!
```

### Netlify (Phishing/Payload)
```bash
cd netlify-site
netlify deploy --prod
```

---

## 🔐 Default Credentials

**⚠️ CHANGE THESE BEFORE PRODUCTION USE**

### Server Access
- **Endpoint:** `/tcolaugh`
- **Port:** `4321`
- **Password:** `TCOLaugh2025!Secure`

### Operators
- **Admin:** `admin` / `Admin@TCO2025!`
- **Operator:** `operator` / `Operator@TCO2025!`

---

## 🛠️ Build from Source

### Prerequisites
- Go 1.24.4
- MinGW-w64
- Qt6
- CMake 3.28+

### Build All
```bash
make all
```

### Build Individual Components
```bash
make server      # Build server only
make client      # Build client only
make extenders   # Build extenders only
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│         Cloud Server (Render)           │
│    AdaptixServer + Extenders            │
└─────────────────────────────────────────┘
              ↑
              │ (Encrypted WebSocket)
              ↓
┌─────────────────────────────────────────┐
│      Local Machine (Client)             │
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

## 🎯 Use Cases

### Red Team Operations
- Penetration testing
- Social engineering
- Physical security testing
- Wireless testing

### Threat Hunting
- Advanced persistent threats
- Malware analysis
- Incident response
- Forensic analysis

### Security Training
- CTF competitions
- Security awareness
- Blue team training
- Red team training

---

## 🤝 Credits

- **Original Framework:** [AdaptixC2](https://github.com/Adaptix-Framework/AdaptixC2) by Adaptix Framework
- **TCOLaugh Edition:** Custom build with deployment automation
- **Contributors:** See [AdaptixC2 Contributors](https://github.com/Adaptix-Framework/AdaptixC2/graphs/contributors)

---

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **GitHub:** [https://github.com/oranolio956/TCOLaugh](https://github.com/oranolio956/TCOLaugh)
- **Original Repo:** [https://github.com/Adaptix-Framework/AdaptixC2](https://github.com/Adaptix-Framework/AdaptixC2)
- **Documentation:** [https://adaptix-framework.gitbook.io](https://adaptix-framework.gitbook.io/adaptix-framework)

---

## ⚖️ Final Warning

**TCOLaugh is a powerful tool that can cause significant damage if misused.**

- ✅ Always obtain written authorization before testing
- ✅ Follow ethical hacking principles
- ✅ Comply with local and international laws
- ✅ Report vulnerabilities responsibly

**The developers are not responsible for any misuse of this tool.**

---

<div align="center">

**🕷️ TCOLaugh - Where Digital Shadows Come to Life 🕷️**

*"For authorized security testing only"*

</div>
