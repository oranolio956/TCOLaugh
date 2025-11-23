# TLS Fingerprint Evasion

## Overview

TLS fingerprint evasion helps bypass advanced detection systems like Cloudflare that use JA3 fingerprinting to identify automated tools.

## Current Implementation

The current implementation uses standard httpx, which has a known TLS fingerprint. For production use with Cloudflare-protected sites, consider:

### Option 1: curl-impersonate (Recommended)

**curl-impersonate** is a curl build that impersonates real browsers' TLS fingerprints.

**Installation:**
```bash
# Download curl-impersonate binary
wget https://github.com/lwthiker/curl-impersonate/releases/download/v0.6.2/curl-impersonate-v0.6.2.x86_64-linux-gnu.tar.gz
tar -xzf curl-impersonate-v0.6.2.x86_64-linux-gnu.tar.gz
```

**Usage:**
- Use as subprocess wrapper around httpx
- Or use `curl_cffi` Python library (wrapper around curl-impersonate)

### Option 2: CycleTLS (Node.js/Go)

**CycleTLS** is a TLS fingerprint spoofing library.

**Installation:**
```bash
npm install @puppeteer/browsers
# Or use Go version
```

**Integration:**
- Run as separate service
- Proxy requests through CycleTLS service

### Option 3: uTLS (Golang)

**uTLS** provides granular control over TLS handshake.

**Usage:**
- Build Go service that wraps httpx requests
- Use uTLS to customize ClientHello packet

## Implementation Status

**Current:** Standard httpx (detectable fingerprint)  
**Future:** Integrate curl-impersonate or CycleTLS for TLS evasion

## Configuration

To enable TLS evasion (when implemented):

```python
scanner = ActiveScanner(
    enable_tls_evasion=True,
    tls_fingerprint="chrome_120_windows"  # or "firefox_121", etc.
)
```

## Notes

- TLS evasion requires external tools (curl-impersonate, CycleTLS, or uTLS)
- Not implemented yet - using standard httpx
- Will be added in future enhancement
