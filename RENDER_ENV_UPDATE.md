# Render Environment Variables Update

## ✅ **Changes Needed for Render**

### **1. Updated Timeout** ✅
**Change:** `PANOPTICON_RECON_TIMEOUT` from `"6"` to `"3"`

**Reason:** Optimized timeout for faster results (most requests complete in <200ms)

**Files Updated:**
- `render.yaml` ✅
- `deploy_render_services.py` ✅

---

### **2. New Environment Variables (Optional)** ✅

#### **Proxy Configuration (Phase 3)**
These are **optional** - proxies are disabled by default.

**To Enable Proxies:**
```yaml
# In render.yaml, add:
- key: PANOPTICON_ENABLE_PROXY
  value: "true"
- key: SMARTPROXY_ENDPOINT
  value: "http://gate.smartproxy.com:10000"
- key: SMARTPROXY_USERNAME
  value: "your_username"
- key: SMARTPROXY_PASSWORD
  value: "your_password"  # Use Render Secrets
```

**Or for IPRoyal:**
```yaml
- key: PANOPTICON_ENABLE_PROXY
  value: "true"
- key: IPROYAL_ENDPOINT
  value: "http://gate.iproyal.com:12321"
- key: IPROYAL_USERNAME
  value: "your_username"
- key: IPROYAL_PASSWORD
  value: "your_password"  # Use Render Secrets
```

**Or for Bright Data:**
```yaml
- key: PANOPTICON_ENABLE_PROXY
  value: "true"
- key: BRIGHTDATA_ENDPOINT
  value: "http://zproxy.lum-superproxy.io:22225"
- key: BRIGHTDATA_USERNAME
  value: "your_username"
- key: BRIGHTDATA_PASSWORD
  value: "your_password"  # Use Render Secrets
```

---

## 📋 **Current Render Configuration**

### **Required Variables (Already Set):**
- ✅ `PANOPTICON_API_KEY` - API authentication
- ✅ `PANOPTICON_RECON_TIMEOUT` - Request timeout (updated to 3s)
- ✅ `PANOPTICON_DB_PATH` - Database location
- ✅ All other existing variables

### **New Optional Variables (Phase 3):**
- ⚠️ `PANOPTICON_ENABLE_PROXY` - Enable proxy rotation (default: false)
- ⚠️ `SMARTPROXY_*` - Smartproxy configuration (if using)
- ⚠️ `IPROYAL_*` - IPRoyal configuration (if using)
- ⚠️ `BRIGHTDATA_*` - Bright Data configuration (if using)

---

## 🎯 **What's Already Working**

**No changes required** - the system works without proxy configuration:
- ✅ 473 platforms working
- ✅ Enhanced detection working
- ✅ User-Agent rotation working (automatic)
- ✅ Rate limiting working (automatic)
- ✅ All features functional

**Proxies are optional** - only needed if:
- You want to avoid IP bans
- You're scanning heavily
- You need to bypass Cloudflare

---

## 🔧 **How to Add Proxy Support (Optional)**

### **Option 1: Via Render Dashboard**
1. Go to Render Dashboard
2. Select your service
3. Go to "Environment" tab
4. Add these variables:
   - `PANOPTICON_ENABLE_PROXY` = `true`
   - `SMARTPROXY_ENDPOINT` = `http://gate.smartproxy.com:10000`
   - `SMARTPROXY_USERNAME` = `your_username`
   - `SMARTPROXY_PASSWORD` = `your_password` (use Secrets)

### **Option 2: Via render.yaml**
Uncomment the proxy configuration lines in `render.yaml` and set values.

### **Option 3: Via deploy_render_services.py**
Uncomment proxy configuration and update values.

---

## ✅ **Summary**

**Required Changes:**
- ✅ `PANOPTICON_RECON_TIMEOUT`: `6` → `3` (already updated in files)

**Optional Changes:**
- ⚠️ Add proxy configuration if you want proxy support
- ⚠️ Otherwise, system works fine without proxies

**Status:** ✅ Ready to deploy - no breaking changes required!
