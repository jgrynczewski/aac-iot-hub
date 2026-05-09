# AAC IoT Hub - Documentation Index

**Quick Navigation:** Wszystkie dokumenty w jednym miejscu

**Last Updated:** 2026-05-09

---

## 📚 Start Here

### **For First-Time Users:**
1. **[../README.md](../README.md)** - Quick Start, instalacja, podstawowe użycie
2. **[API_EXAMPLES.md](API_EXAMPLES.md)** - Przykłady curl dla wszystkich endpointów
3. **[yeelight.md](yeelight.md)** - Jak skonfigurować żarówkę Yeelight

### **For Developers Resuming Work:**
1. **[../NEXT_STEPS.md](../NEXT_STEPS.md)** ⭐ **START HERE** - Pełny kontekst + roadmap
2. **[STATUS.md](STATUS.md)** - Obecny status implementacji (100%)
3. **[GUI_REQUIREMENTS.md](GUI_REQUIREMENTS.md)** - Specyfikacja dla GUI projektu

---

## 📖 Documentation Structure

### **Main Documents**

| File | Purpose | Status | Last Updated |
|------|---------|--------|--------------|
| [../README.md](../README.md) | Main documentation | ✅ Current | 2026-05-09 |
| [../NEXT_STEPS.md](../NEXT_STEPS.md) | Development roadmap | ✅ Current | 2026-05-09 |
| [STATUS.md](STATUS.md) | Implementation status | ✅ 100% | 2026-05-09 |

### **API Documentation**

| File | Purpose | Audience |
|------|---------|----------|
| [API_EXAMPLES.md](API_EXAMPLES.md) | curl examples, endpoint docs | Users, Testers |
| [GUI_REQUIREMENTS.md](GUI_REQUIREMENTS.md) | GUI spec + API mapping | GUI Developers |

### **Implementation Plans**

| File | Purpose | Status |
|------|---------|--------|
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | Original 7-phase plan | ✅ Complete |
| [MANUAL_TESTING.md](MANUAL_TESTING.md) | Manual test procedures | ✅ Tested |

### **Architecture Decisions (ADR)**

| File | Topic | Decision |
|------|-------|----------|
| [adr/adr-000-device-type-selection.md](adr/adr-000-device-type-selection.md) | Device choice | Yeelight (SSDP, proven) |
| [adr/adr-001-containerization-and-deployment.md](adr/adr-001-containerization-and-deployment.md) | Deployment | Docker + Compose |
| [adr/adr-002-docker-network-configuration.md](adr/adr-002-docker-network-configuration.md) | Networking | Host mode (SSDP) |
| [adr/adr-003-http-api-protocol.md](adr/adr-003-http-api-protocol.md) | API protocol | REST + FastAPI |

### **Research Documents**

| File | Purpose | Status |
|------|---------|--------|
| [yeelight.md](yeelight.md) | Yeelight POC & setup | ✅ Working |
| [shelly.md](shelly.md) | Shelly research | ⏸️ Future |
| [future-devices.md](future-devices.md) | Other device research | 📝 Research |

---

## 🎯 Documentation by Use Case

### **"I want to use the API"**
1. Read [../README.md](../README.md) - Quick start
2. Check [API_EXAMPLES.md](API_EXAMPLES.md) - How to call endpoints
3. Enable LAN Control on Yeelight: [yeelight.md](yeelight.md)

### **"I'm building the GUI project"**
1. Read [GUI_REQUIREMENTS.md](GUI_REQUIREMENTS.md) - Complete spec
2. Check [API_EXAMPLES.md](API_EXAMPLES.md) - Current endpoints
3. Use [../NEXT_STEPS.md](../NEXT_STEPS.md) - For future features

### **"I'm resuming development"**
1. **Start:** [../NEXT_STEPS.md](../NEXT_STEPS.md) - Full context + roadmap ⭐
2. Check [STATUS.md](STATUS.md) - What's done (100%)
3. Review [GUI_REQUIREMENTS.md](GUI_REQUIREMENTS.md) - What to build next

### **"I want to understand the architecture"**
1. Read ADR documents in [adr/](adr/) folder
2. Check [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Original design
3. Review [STATUS.md](STATUS.md) - Implementation details

### **"I want to test manually"**
1. Follow [MANUAL_TESTING.md](MANUAL_TESTING.md) - Test procedures
2. Use [API_EXAMPLES.md](API_EXAMPLES.md) - curl commands
3. Check [yeelight.md](yeelight.md) - Device setup

---

## 📊 Project Status Overview

**Current Version:** MVP v1.0 ✅ (100% Complete)

**What Works:**
- ✅ REST API for power control (on/off/toggle)
- ✅ SSDP discovery for Yeelight devices
- ✅ Docker deployment (host network mode)
- ✅ 39 integration tests passing
- ✅ Manual testing with real devices passed

**What's Next (MVP v2.0):**
- ⏳ Brightness control (1-100)
- ⏳ RGB color control
- ⏳ Color temperature control (1700-6500K)
- ⏳ Flow animations (7 effects)
- ⏳ Scenes & presets

See [../NEXT_STEPS.md](../NEXT_STEPS.md) for detailed roadmap.

---

## 🔍 Quick Search

**Looking for:**
- **API endpoint examples** → [API_EXAMPLES.md](API_EXAMPLES.md)
- **Current capabilities** → [STATUS.md](STATUS.md) or [../README.md](../README.md)
- **Future features** → [../NEXT_STEPS.md](../NEXT_STEPS.md) or [GUI_REQUIREMENTS.md](GUI_REQUIREMENTS.md)
- **Setup instructions** → [../README.md](../README.md) or [yeelight.md](yeelight.md)
- **Architecture decisions** → [adr/](adr/) folder
- **Test procedures** → [MANUAL_TESTING.md](MANUAL_TESTING.md)
- **Development context** → [../NEXT_STEPS.md](../NEXT_STEPS.md) ⭐

---

## 📝 Document Relationships

```
README.md (Entry point for users)
    │
    ├─→ docs/STATUS.md (Implementation details)
    │       │
    │       └─→ docs/IMPLEMENTATION_PLAN.md (Original plan)
    │
    ├─→ docs/API_EXAMPLES.md (API usage)
    │
    └─→ NEXT_STEPS.md ⭐ (Development roadmap)
            │
            ├─→ docs/GUI_REQUIREMENTS.md (GUI spec)
            │
            └─→ docs/adr/* (Architecture decisions)
```

---

## 🎬 Quick Start Commands

### **Read Documentation:**
```bash
# Main README
cat README.md

# Development roadmap (if resuming)
cat NEXT_STEPS.md

# API examples
cat docs/API_EXAMPLES.md

# Full status
cat docs/STATUS.md
```

### **Start Using:**
```bash
# Start API
docker compose up -d

# Test health
curl http://localhost:8765/api/health

# Discover devices
curl -X POST http://localhost:8765/api/v1/devices/discover
```

---

## 💡 Tips

- **First time here?** Start with [../README.md](../README.md)
- **Returning developer?** Go directly to [../NEXT_STEPS.md](../NEXT_STEPS.md)
- **Building GUI?** Check [GUI_REQUIREMENTS.md](GUI_REQUIREMENTS.md)
- **Need examples?** See [API_EXAMPLES.md](API_EXAMPLES.md)
- **Want history?** Read [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) + [STATUS.md](STATUS.md)

---

**Last Updated:** 2026-05-09
**Maintained by:** AAC IoT Hub Team
**Questions?** Check [../README.md](../README.md) or [../NEXT_STEPS.md](../NEXT_STEPS.md)
