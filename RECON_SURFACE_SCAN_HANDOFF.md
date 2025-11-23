# Recon & Surface Scan - Developer Handoff Documentation

## Executive Summary

**The Recon & Surface Scan feature is REAL and FUNCTIONAL**, but it's a **simplified implementation** compared to what a production-grade OSINT tool would offer. It performs actual HTTP requests to check if usernames exist on popular platforms, but uses basic status code checking rather than sophisticated detection methods.

---

## What It Does

The "Recon & Surface Scan" feature allows users to:
1. Enter a username (e.g., "shiftcipher")
2. Check if that username exists across multiple social media platforms
3. Receive results showing which platforms returned a 200 status code (indicating the profile likely exists)

---

## Architecture Overview

### Component Flow

```
User Input (Frontend)
    ↓
POST /recon/username (FastAPI endpoint)
    ↓
ActiveScanner.check_username() (async method)
    ↓
Concurrent HTTP requests to 4 platforms
    ↓
Results aggregated and persisted to database
    ↓
Response returned to user
```

---

## Detailed Component Breakdown

### 1. Frontend UI (`panopticon/api/templates/index.html`)

**Location:** Lines 81-100

**What it does:**
- Displays a form with a username input field
- Shows a "Live" badge indicating real-time operation
- Displays results in a JSON-formatted `<pre>` element
- Calls the JavaScript function `runRecon()` on form submission

**Key JavaScript Function:** `runRecon()` (lines 615-650)
- Validates API key is configured
- Extracts username from input field
- Makes authenticated POST request to `/recon/username`
- Displays results as formatted JSON
- Shows "Scanning surface web targets..." during operation

**User Experience:**
- User enters username → clicks "Scan Username" → sees "Scanning surface web targets..." → receives JSON results

---

### 2. API Endpoint (`panopticon/api/main.py`)

**Location:** Lines 272-282

**Endpoint:** `POST /recon/username`

**Request Format:**
```json
{
  "username": "shiftcipher"
}
```

**Response Format:**
```json
{
  "username": "shiftcipher",
  "found_on": [
    {
      "site": "Twitter",
      "url": "https://twitter.com/shiftcipher",
      "status": "found"
    },
    {
      "site": "GitHub",
      "url": "https://github.com/shiftcipher",
      "status": "found"
    }
  ]
}
```

**Security:**
- Protected by `SecurityMiddleware` - requires `X-API-Key` header
- Rate-limited per IP address (configurable via `PANOPTICON_RATE_LIMIT_MAX`)

**What happens:**
1. Validates request body contains `username` field
2. Calls `scanner.check_username(request.username)` (async)
3. Persists results to database as document type `"active_recon"`
4. Returns results to client

**Database Persistence:**
- Document ID format: `recon_{username}`
- Document type: `"active_recon"`
- Stores: `{"username": "...", "hits": [...]}`

---

### 3. Core Scanner (`panopticon/analysis/recon/active_scanner.py`)

**Class:** `ActiveScanner`

**Initialization:**
```python
scanner = ActiveScanner(timeout=None)
```
- `timeout` defaults to `PANOPTICON_RECON_TIMEOUT` env var (default: 6 seconds)

**Platforms Checked:**
Currently hardcoded to 4 platforms:
```python
self.sites = {
    "Twitter": "https://twitter.com/{}",
    "GitHub": "https://github.com/{}",
    "Instagram": "https://instagram.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
}
```

**Main Method: `check_username(username: str)`**

**How it works:**
1. Creates an `httpx.AsyncClient` with configured timeout
2. Builds a list of tasks (one per platform)
3. Executes all HTTP requests **concurrently** using `asyncio.gather()`
4. Each task calls `_fetch_site()` which:
   - Makes GET request to the platform URL
   - Uses User-Agent: `"panopticon-recon"`
   - Checks if `response.status_code == 200`
   - If 200, returns `{"site": "...", "url": "...", "status": "found"}`
   - If error or non-200, returns `None` (silently ignored)
5. Filters out `None` results and returns list of found platforms

**Key Implementation Details:**

**Concurrency:**
- Uses `asyncio.gather(*tasks, return_exceptions=True)`
- All 4 platforms checked simultaneously (not sequentially)
- Timeout applies to entire operation (6 seconds default)

**Detection Method:**
- **Simple status code checking** - if HTTP 200, assumes profile exists
- **No content analysis** - doesn't parse HTML to verify actual profile
- **No rate limiting** - makes requests as fast as possible
- **No proxy rotation** - direct requests from server IP

**Error Handling:**
- Exceptions are caught and logged as warnings
- Failed checks return `None` and are filtered out
- No retry logic
- No exponential backoff

**Limitations:**
1. **False Positives:** Some platforms return 200 for non-existent profiles (e.g., redirects, error pages)
2. **False Negatives:** Private profiles, rate limiting, or network issues may cause misses
3. **No Verification:** Doesn't verify the profile actually belongs to the username
4. **Limited Platforms:** Only checks 4 platforms (Sherlock-style tools check 100+)
5. **No Rate Limiting:** Could get IP banned if used heavily
6. **No Proxy Support:** All requests come from same IP

---

### 4. HLR Lookup Method (NOT CURRENTLY USED)

**Location:** Lines 51-64 in `active_scanner.py`

**Status:** **IMPLEMENTED BUT NOT CALLED**

The `hlr_lookup()` method exists but:
- Is never called by any endpoint
- Returns **hardcoded mock data**
- Comment says "In reality, this calls a paid API like Twilio or HLR-Lookups.com"

**Current Implementation:**
```python
def hlr_lookup(self, phone_number: str) -> Dict[str, Any]:
    # Mock response:
    return {
        "number": phone_number,
        "status": "active",
        "carrier": "Verizon Wireless",
        "country_code": "US",
        "roaming": False,
    }
```

**To make it real:**
- Would need to integrate with Twilio HLR API or similar service
- Requires API credentials and payment
- Would need to add endpoint: `POST /recon/phone`

---

## Configuration

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `PANOPTICON_RECON_TIMEOUT` | `6` | Timeout in seconds for all concurrent HTTP requests |

**Example:**
```bash
export PANOPTICON_RECON_TIMEOUT=10  # 10 second timeout
```

---

## Testing

### Unit Test (`tests/test_ingestion_and_recon.py`)

**Test:** `test_active_scanner_runs_concurrently()`

**What it tests:**
- Verifies concurrent execution works
- Mocks `_fetch_site()` to return fake results
- Confirms all sites are checked and results aggregated

**How to run:**
```bash
PYTHONPATH=$(pwd) pytest tests/test_ingestion_and_recon.py::test_active_scanner_runs_concurrently -v
```

### Manual Testing

**Via API:**
```bash
curl -X POST http://localhost:8000/recon/username \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"username": "shiftcipher"}'
```

**Via Frontend:**
1. Navigate to `http://localhost:8000`
2. Configure API key in Connection Settings
3. Enter username in "Recon & Surface Scan" section
4. Click "Scan Username"

---

## Integration Points

### Database Persistence

**Where:** `panopticon/api/main.py` line 279-281

**What gets stored:**
- Document ID: `recon_{username}`
- Source type: `"active_recon"`
- Timestamp: `0.0` (should be `time.time()`)
- Raw data: `{"username": "...", "hits": [...]}`

**Query example:**
```python
from panopticon.persistence.sqlite_manager import db_instance
docs = db_instance.search_documents("username", "shiftcipher")
# Returns all documents containing that username, including recon results
```

### Simulation Suite Usage

**Location:** `panopticon/simulation_suite.py` lines 71-78

**How it's used:**
- Simulated user agents call `/recon/username` endpoint
- 30% probability of running recon per session
- Used for load testing and integration verification

---

## Current Limitations & Future Improvements

### Current Limitations

1. **Only 4 platforms** - Should expand to 50+ like Sherlock
2. **Basic detection** - Status code only, no content analysis
3. **No rate limiting** - Could get IP banned
4. **No proxy support** - All requests from same IP
5. **No retry logic** - Single attempt per platform
6. **No verification** - Doesn't confirm profile actually exists
7. **HLR lookup is fake** - Returns hardcoded data

### Recommended Improvements

1. **Expand Platform List:**
   ```python
   # Load from external config file or database
   self.sites = load_platforms_from_config()
   ```

2. **Better Detection:**
   ```python
   # Parse HTML for profile-specific elements
   if "Profile not found" in response.text:
       return None
   ```

3. **Add Rate Limiting:**
   ```python
   # Use asyncio.Semaphore to limit concurrent requests
   async with self.rate_limiter:
       response = await client.get(url)
   ```

4. **Proxy Rotation:**
   ```python
   # Rotate through proxy list
   proxy = self.proxy_pool.get_next()
   response = await client.get(url, proxies=proxy)
   ```

5. **Retry Logic:**
   ```python
   # Exponential backoff retry
   for attempt in range(3):
       try:
           response = await client.get(url)
           break
       except Exception:
           await asyncio.sleep(2 ** attempt)
   ```

6. **Real HLR Integration:**
   ```python
   # Integrate with Twilio HLR API
   async def hlr_lookup(self, phone: str):
       async with httpx.AsyncClient() as client:
           response = await client.post(
               "https://api.twilio.com/...",
               auth=(self.twilio_sid, self.twilio_token),
               data={"phone": phone}
           )
           return response.json()
   ```

---

## Security Considerations

### Current Security

✅ **Protected by API key** - Requires `X-API-Key` header  
✅ **Rate limited** - Per-IP throttling via middleware  
✅ **No sensitive data exposure** - Only returns public URLs  
✅ **Async execution** - Doesn't block event loop  

### Security Concerns

⚠️ **User-Agent identification** - Uses `"panopticon-recon"` which identifies the tool  
⚠️ **No request obfuscation** - Easy to detect automated requests  
⚠️ **IP exposure** - Server IP visible to platforms  
⚠️ **No request throttling** - Could trigger anti-bot measures  

### Recommendations

1. **Rotate User-Agents:**
   ```python
   user_agents = [
       "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
   ]
   headers = {"User-Agent": random.choice(user_agents)}
   ```

2. **Add Delays:**
   ```python
   # Random delay between requests
   await asyncio.sleep(random.uniform(0.5, 2.0))
   ```

3. **Use Proxies:**
   - Rotate through proxy pool
   - Distribute requests across IPs

---

## Monitoring & Observability

### Logging

**Location:** `panopticon/analysis/recon/active_scanner.py`

**Log Levels:**
- `INFO`: "Starting username scan for '{username}'..."
- `WARNING`: "Error checking {site}: {exception}"

**Example logs:**
```
INFO: Starting username scan for 'shiftcipher'...
WARNING: Error checking Instagram: Connection timeout
```

### Metrics to Track

1. **Request count** - Total recon requests per day
2. **Success rate** - Percentage of platforms returning 200
3. **Response times** - Average time per platform check
4. **Error rate** - Percentage of failed requests
5. **Database writes** - Number of recon results persisted

---

## Deployment Considerations

### Render Deployment

**Configuration:** `render.yaml` and `deploy_render_services.py`

**Environment Variable:**
```yaml
envVars:
  - key: PANOPTICON_RECON_TIMEOUT
    value: "6"
```

### Docker Deployment

**Configuration:** `panopticon/infrastructure/docker-compose.yml`

**Environment Variable:**
```yaml
environment:
  PANOPTICON_RECON_TIMEOUT: "6"
```

---

## Code Dependencies

### Required Packages

- `httpx` - Async HTTP client for concurrent requests
- `asyncio` - Python async/await support (stdlib)

### Import Chain

```
panopticon/api/main.py
  → from panopticon.analysis.recon.active_scanner import ActiveScanner
    → import httpx
    → import asyncio
```

---

## Summary

**Is it real?** ✅ **YES** - It makes actual HTTP requests to real platforms.

**Is it production-ready?** ⚠️ **PARTIALLY** - It works but has limitations:
- Basic detection method (status codes only)
- Limited platform coverage (4 platforms)
- No advanced features (proxies, retries, content analysis)
- HLR lookup is mocked

**What it does well:**
- Concurrent execution (fast)
- Async/await (doesn't block)
- Results persistence
- API security (key-protected)

**What needs improvement:**
- More platforms
- Better detection logic
- Proxy support
- Retry mechanisms
- Real HLR integration

---

## Quick Reference

**File Locations:**
- Frontend UI: `panopticon/api/templates/index.html` (lines 81-100, 615-650)
- API Endpoint: `panopticon/api/main.py` (lines 272-282)
- Core Logic: `panopticon/analysis/recon/active_scanner.py` (entire file)
- Tests: `tests/test_ingestion_and_recon.py` (lines 51-68)

**Key Methods:**
- `ActiveScanner.check_username(username)` - Main entry point
- `ActiveScanner._fetch_site(client, site, url, label)` - Per-platform check
- `POST /recon/username` - API endpoint

**Configuration:**
- `PANOPTICON_RECON_TIMEOUT` - Timeout in seconds (default: 6)

**Database:**
- Document type: `"active_recon"`
- Document ID format: `recon_{username}`
