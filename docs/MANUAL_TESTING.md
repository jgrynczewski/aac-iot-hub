# Manual Testing Guide - AAC IoT Hub

**Phase 1 Testing - Project Setup Verification**

This document provides step-by-step manual testing procedures for Phase 1 of the AAC IoT Hub implementation.

---

## Prerequisites

- Docker installed and running
- Docker Compose plugin installed (or standalone docker-compose)
- Terminal access
- Web browser
- Port 8765 available (not used by other services)

---

## Phase 1: Setup Testing

### ✅ Test 1: Build and Run Container

**Command (Docker Compose V2 - Recommended):**
```bash
docker compose up
```

**Alternative (older standalone docker-compose):**
```bash
docker-compose up
```

**Note:** Modern Docker uses `docker compose` (V2 plugin). All examples use V2 syntax.

**Expected Output:**
```
[+] Building ...
[+] Running 1/1
 ✔ Container aac-iot-hub  Created
Attaching to aac-iot-hub
aac-iot-hub  | INFO:     Started server process [1]
aac-iot-hub  | INFO:     Waiting for application startup.
aac-iot-hub  | INFO:     Application startup complete.
aac-iot-hub  | INFO:     Uvicorn running on http://0.0.0.0:8765 (Press CTRL+C to quit)
```

**Success Criteria:**
- ✅ Container builds without errors (first build may take 1-2 minutes)
- ✅ FastAPI server starts successfully
- ✅ Logs show "Application startup complete"
- ✅ Server runs on port 8765

**Common Issues:**
- **"port is already allocated"**: Port 8765 is in use. Stop other services or change AAC_API_PORT in .env
- **"permission denied"**: Run with `sudo` or add your user to docker group
- **Build fails**: Check requirements.txt exists and is readable

---

### ✅ Test 2: Swagger UI (Interactive API Documentation)

**Action:**
Open in web browser:
```
http://localhost:8765/docs
```

**Expected Result:**
- ✅ Swagger UI page loads
- ✅ Title shows "AAC IoT Hub"
- ✅ API version shows "0.1.0"
- ✅ Two endpoints visible:
  - `GET /` - Root endpoint
  - `GET /api/health` - Health check endpoint

**Interactive Test:**
1. Click on `GET /api/health`
2. Click "Try it out"
3. Click "Execute"
4. Verify response shows:
   ```json
   {
     "status": "ok",
     "version": "0.1.0"
   }
   ```

**Screenshot Location:**
Browser should show Swagger UI interface with expandable endpoint documentation.

**Common Issues:**
- **Cannot reach page**: Check if container is running (`docker ps`)
- **Connection refused**: Verify port 8765 is correct
- **404 error**: Check if you're using http:// (not https://)

---

### ✅ Test 3: Health Endpoint (curl)

**Prerequisites:**
- Container must be running
- Open new terminal window (keep container running in first terminal)

**Command:**
```bash
curl http://localhost:8765/api/health
```

**Expected Output:**
```json
{"status":"ok","version":"0.1.0","timestamp":"2026-04-29T10:30:00.000000"}
```

**Success Criteria:**
- ✅ HTTP 200 status code (implicit if JSON returned)
- ✅ JSON response contains `"status": "ok"`
- ✅ JSON response contains `"version": "0.1.0"`
- ✅ Timestamp is present and valid ISO format

**Pretty Print (Optional):**
```bash
curl http://localhost:8765/api/health | jq
```

**Common Issues:**
- **"curl: command not found"**: Install curl: `sudo apt install curl`
- **"Connection refused"**: Container not running or wrong port
- **Empty response**: Check container logs for errors

---

### ✅ Test 4: Root Endpoint

**Command:**
```bash
curl http://localhost:8765/
```

**Expected Output:**
```json
{"name":"AAC IoT Hub","version":"0.1.0","status":"running"}
```

**Success Criteria:**
- ✅ HTTP 200 status code
- ✅ JSON contains `"name": "AAC IoT Hub"`
- ✅ JSON contains `"version": "0.1.0"`
- ✅ JSON contains `"status": "running"`

**Alternative Test (Browser):**
Open in browser: `http://localhost:8765/`

You should see the JSON response rendered in the browser.

---

### 🔧 Test 5: Container Status Check

**Command:**
```bash
docker ps
```

**Expected Output:**
```
CONTAINER ID   IMAGE              COMMAND                  STATUS         PORTS     NAMES
abc123def456   aac-iot-hub-...    "uvicorn app.main:..."   Up 2 minutes             aac-iot-hub
```

**Success Criteria:**
- ✅ Container `aac-iot-hub` is listed
- ✅ Status shows "Up X minutes/seconds"
- ✅ No restart loop (status should not show "Restarting")

**Check All Containers (including stopped):**
```bash
docker ps -a
```

---

### 🔧 Test 6: View Container Logs

**Command (follow mode - live logs):**
```bash
docker-compose logs -f
```

**Alternative:**
```bash
docker logs -f aac-iot-hub
```

**Expected Output:**
```
aac-iot-hub  | INFO:     Started server process [1]
aac-iot-hub  | INFO:     Waiting for application startup.
aac-iot-hub  | INFO:     Application startup complete.
aac-iot-hub  | INFO:     Uvicorn running on http://0.0.0.0:8765
```

**Success Criteria:**
- ✅ No error messages (ERROR, CRITICAL)
- ✅ Server started successfully
- ✅ Logs show API requests when you hit endpoints

**Exit:** Press `Ctrl+C` to stop following logs (container keeps running)

---

### 🔧 Test 7: Stop and Restart

**Stop Container:**
```bash
docker-compose down
```

**Expected Output:**
```
[+] Running 1/1
 ✔ Container aac-iot-hub  Removed
```

**Restart in Detached Mode (background):**
```bash
docker-compose up -d
```

**Expected Output:**
```
[+] Running 1/1
 ✔ Container aac-iot-hub  Started
```

**Verify Running:**
```bash
curl http://localhost:8765/api/health
```

**Success Criteria:**
- ✅ Container stops cleanly (no errors)
- ✅ Container restarts successfully
- ✅ Health endpoint responds after restart

---

### 🔧 Test 8: ReDoc Documentation (Alternative Docs)

**Action:**
Open in browser:
```
http://localhost:8765/redoc
```

**Expected Result:**
- ✅ ReDoc UI loads
- ✅ Shows same API documentation as Swagger
- ✅ Cleaner, three-column layout

---

### 🔧 Test 9: OpenAPI Schema

**Command:**
```bash
curl http://localhost:8765/openapi.json | jq
```

**Expected Result:**
- ✅ Valid JSON schema returned
- ✅ Contains API title, version, paths, schemas
- ✅ FastAPI auto-generated OpenAPI 3.0 spec

---

## Testing Checklist - Phase 1

~~Mark each test as you complete it:~~

**Status: ✅ ALL TESTS COMPLETED (2026-04-29)**

- [x] Test 1: Build and run container (`docker compose up`) ✅
- [x] Test 2: Swagger UI accessible at `/docs` ✅
- [x] Test 3: Health endpoint returns 200 OK ✅
- [x] Test 4: Root endpoint returns correct JSON ✅
- [x] Test 5: Container shows as "Up" in `docker ps` ✅
- [x] Test 6: Logs show no errors ✅
- [x] Test 7: Container stops and restarts cleanly ✅
- [x] Test 8: ReDoc accessible at `/redoc` ✅
- [x] Test 9: OpenAPI schema accessible ✅

**✅ Phase 1 is complete and verified!**

---

## Troubleshooting

### Issue: "docker-compose: command not found"

**Solution 1 (Recommended):** Use Docker Compose V2 (built into Docker)
```bash
docker compose up
```

**Solution 2:** Install docker-compose plugin
```bash
sudo apt install docker-compose-plugin
```

**Solution 3:** Install standalone docker-compose
```bash
sudo apt install docker-compose
```

### Issue: "Cannot connect to Docker daemon"

**Solution:**
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

Add user to docker group (logout/login required):
```bash
sudo usermod -aG docker $USER
```

### Issue: Port 8765 already in use

**Find what's using the port:**
```bash
sudo lsof -i :8765
```

**Kill the process or change port:**
Create `.env` file:
```env
AAC_API_PORT=9765
```

Then rebuild:
```bash
docker compose down
docker compose up -d
```

### Issue: Container keeps restarting

**Check logs:**
```bash
docker logs aac-iot-hub
```

Common causes:
- Python import errors
- Missing dependencies
- Port conflict

### Issue: Swagger UI shows 404

**Verify container is running:**
```bash
docker ps
```

**Check if FastAPI started:**
```bash
docker logs aac-iot-hub | grep "Application startup complete"
```

---

## Next Steps

~~After Phase 1 tests pass:~~
**Phase 1 tests completed ✅ (2026-04-29)**

Next steps:
1. Stop container: `docker compose down`
2. Proceed to **Phase 2: Data Models** (see docs/IMPLEMENTATION_PLAN.md)
3. Keep this testing guide for reference in future phases

---

## Test Environment Info

**OS:** Linux (Ubuntu/Debian-based)
**Docker:** 20.10+
**Docker Compose:** V2 (recommended)
**Python:** 3.12 (in container)
**FastAPI:** 0.110.0+

---

**Last Updated:** 2026-04-29