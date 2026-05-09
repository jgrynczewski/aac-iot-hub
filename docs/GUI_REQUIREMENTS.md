# GUI Requirements & API Mapping

**Document Purpose:** Specyfikacja wymagań dla projektu GUI (scanning interface) oraz mapowanie funkcji GUI → AAC IoT Hub API endpoints.

**Target:** Accessibility-focused scanning interface dla kontroli inteligentnych żarówek Yeelight.

**Last Updated:** 2026-05-09

---

## 1. Overview - Koncepcja GUI

### 1.1 Typ Interfejsu
**Scanning Interface** - przyciski podświetlane automatycznie, użytkownik klika w momencie podświetlenia.

### 1.2 Interakcja
- **Pierwszy klik:** Preview efektu (żarówka pokazuje jak będzie wyglądać)
- **Drugi klik:** Zatwierdzenie i zastosowanie ustawienia

### 1.3 Skanowanie Hierarchiczne
```
┌─────────────────────────────────────────────┐
│ POZIOM 1: Grupy Funkcji                     │
│  [Podstawowa] → [Kolory] → [Barwa] →        │
│  → [Sceny] → [Efekty]                       │
└─────────────────────────────────────────────┘
              ↓ Wybrano "Kolory"
┌─────────────────────────────────────────────┐
│ POZIOM 2: Opcje w Grupie                    │
│  [⚪] → [🟡] → [🔴] → [🟢] → [🔵] →         │
│  → [🟣] → [🟠] → [🩷]                        │
└─────────────────────────────────────────────┘
```

---

## 2. GUI Layout - Kompletna Specyfikacja

### 2.1 Visual Mockup

```
╔══════════════════════════════════════════════════════════╗
║                  💡 LAMPA SALON                         ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  ┌────────────────────────────────────────────────────┐ ║
║  │         PODSTAWOWA KONTROLA                        │ ║
║  ├────────────────────────────────────────────────────┤ ║
║  │  [  ●  ]  [  ◐  ]  [  ◑  ]  [  ◕  ]  [  ○  ]    │ ║
║  │   OFF      25%      50%      75%     100%          │ ║
║  └────────────────────────────────────────────────────┘ ║
║                                                          ║
║  ┌────────────────────────────────────────────────────┐ ║
║  │         SZYBKIE KOLORY                             │ ║
║  ├────────────────────────────────────────────────────┤ ║
║  │  [⚪]  [🟡]  [🔴]  [🟢]  [🔵]  [🟣]  [🟠]  [🩷] │ ║
║  │  Biały Żółty Czerw Zielo Nieb Fiol Pomar Różo     │ ║
║  └────────────────────────────────────────────────────┘ ║
║                                                          ║
║  ┌────────────────────────────────────────────────────┐ ║
║  │         BARWA BIELI                                │ ║
║  ├────────────────────────────────────────────────────┤ ║
║  │      [  ❄️  ]    [  ☀️  ]    [  🔥  ]           │ ║
║  │      Zimne       Neutralne    Ciepłe              │ ║
║  │      6500K        4000K        2700K              │ ║
║  └────────────────────────────────────────────────────┘ ║
║                                                          ║
║  ┌────────────────────────────────────────────────────┐ ║
║  │         SCENY TEMATYCZNE                           │ ║
║  ├────────────────────────────────────────────────────┤ ║
║  │  [📖]  [🎬]  [😴]  [☕]  [🍽️]                    │ ║
║  │  Czyt  Film  Noc  Praca Kolac                      │ ║
║  └────────────────────────────────────────────────────┘ ║
║                                                          ║
║  ┌────────────────────────────────────────────────────┐ ║
║  │         EFEKTY WOW                                 │ ║
║  ├────────────────────────────────────────────────────┤ ║
║  │  [🚨]  [🌈]  [🎉]  [⚡]  [🕯️]  [💝]  [🔮]      │ ║
║  │  Police Rain Disco Strobe Candle Roman Magic       │ ║
║  └────────────────────────────────────────────────────┘ ║
║                                                          ║
║  ┌────────────────────────────────────────────────────┐ ║
║  │         ULUBIONE                                   │ ║
║  ├────────────────────────────────────────────────────┤ ║
║  │  [⭐ 1]  [⭐ 2]  [⭐ 3]    [💾 Zapisz]          │ ║
║  └────────────────────────────────────────────────────┘ ║
╚══════════════════════════════════════════════════════════╝
```

---

## 3. API Requirements - Mapowanie Funkcji

### 3.1 Podstawowa Kontrola

| GUI Przycisk | Funkcja | API Endpoint | Wymagane Parametry |
|--------------|---------|--------------|-------------------|
| ● OFF | Wyłącz | `PUT /devices/{id}/control` | `{"properties": {"power": "off"}}` |
| ◐ 25% | Jasność 25% | `PUT /devices/{id}/control` | `{"properties": {"power": "on", "brightness": 25}}` |
| ◑ 50% | Jasność 50% | `PUT /devices/{id}/control` | `{"properties": {"power": "on", "brightness": 50}}` |
| ◕ 75% | Jasność 75% | `PUT /devices/{id}/control` | `{"properties": {"power": "on", "brightness": 75}}` |
| ○ 100% | Jasność 100% | `PUT /devices/{id}/control` | `{"properties": {"power": "on", "brightness": 100}}` |

**API Requirement:**
```json
{
  "properties": {
    "power": "on|off",
    "brightness": 1-100
  }
}
```

---

### 3.2 Szybkie Kolory (RGB Presets)

| GUI | Kolor | RGB | API Call |
|-----|-------|-----|----------|
| ⚪ | Biały | (255, 255, 255) | `{"properties": {"rgb": [255, 255, 255], "brightness": 100}}` |
| 🟡 | Żółty | (255, 255, 0) | `{"properties": {"rgb": [255, 255, 0], "brightness": 100}}` |
| 🔴 | Czerwony | (255, 0, 0) | `{"properties": {"rgb": [255, 0, 0], "brightness": 100}}` |
| 🟢 | Zielony | (0, 255, 0) | `{"properties": {"rgb": [0, 255, 0], "brightness": 100}}` |
| 🔵 | Niebieski | (0, 0, 255) | `{"properties": {"rgb": [0, 0, 255], "brightness": 100}}` |
| 🟣 | Fioletowy | (128, 0, 128) | `{"properties": {"rgb": [128, 0, 128], "brightness": 100}}` |
| 🟠 | Pomarańczowy | (255, 165, 0) | `{"properties": {"rgb": [255, 165, 0], "brightness": 100}}` |
| 🩷 | Różowy | (255, 192, 203) | `{"properties": {"rgb": [255, 192, 203], "brightness": 100}}` |

**API Requirement:**
```json
{
  "properties": {
    "rgb": [red, green, blue],  // 0-255 each
    "brightness": 1-100          // optional
  }
}
```

---

### 3.3 Barwa Bieli (Color Temperature)

| GUI | Opis | Kelvin | API Call |
|-----|------|--------|----------|
| ❄️ | Zimne (chłodne białe) | 6500K | `{"properties": {"color_temp": 6500, "brightness": 100}}` |
| ☀️ | Neutralne (dzienne) | 4000K | `{"properties": {"color_temp": 4000, "brightness": 100}}` |
| 🔥 | Ciepłe (żółtawe) | 2700K | `{"properties": {"color_temp": 2700, "brightness": 100}}` |

**API Requirement:**
```json
{
  "properties": {
    "color_temp": 1700-6500,  // Kelvin
    "brightness": 1-100        // optional
  }
}
```

---

### 3.4 Sceny Tematyczne (Predefined Scenes)

| GUI | Scena | Ustawienia | API Call |
|-----|-------|------------|----------|
| 📖 | Czytanie | Jasne, neutralne | `{"properties": {"scene": "reading"}}` lub `{"color_temp": 5000, "brightness": 100}` |
| 🎬 | Film | Przyciemnione, ciepłe | `{"properties": {"scene": "movie"}}` lub `{"color_temp": 2700, "brightness": 20}` |
| 😴 | Noc | Bardzo ciemne, czerwone | `{"properties": {"scene": "night"}}` lub `{"rgb": [255, 0, 0], "brightness": 5}` |
| ☕ | Praca | Jasne, chłodne | `{"properties": {"scene": "work"}}` lub `{"color_temp": 6500, "brightness": 100}` |
| 🍽️ | Kolacja | Średnie, ciepłe | `{"properties": {"scene": "dinner"}}` lub `{"color_temp": 3000, "brightness": 60}` |

**API Requirement (Option A - Scene Presets):**
```json
{
  "properties": {
    "scene": "reading|movie|night|work|dinner"
  }
}
```

**API Requirement (Option B - Manual Values):**
GUI oblicza wartości i wysyła kombinację brightness + color_temp/rgb

**Rekomendacja:** Option B (prostsze API, logika w GUI)

---

### 3.5 Efekty WOW (Animated Flows)

| GUI | Efekt | Opis | API Call |
|-----|-------|------|----------|
| 🚨 | Police | Niebiesko-czerwony migający | `{"properties": {"flow": "police"}}` |
| 🌈 | Rainbow | Tęczowy gradient płynny | `{"properties": {"flow": "rainbow"}}` |
| 🎉 | Disco | Losowe kolory szybkie | `{"properties": {"flow": "disco"}}` |
| ⚡ | Strobe | Stroboskop biały | `{"properties": {"flow": "strobe"}}` |
| 🕯️ | Candle | Symulacja płomienia świecy | `{"properties": {"flow": "candle"}}` |
| 💝 | Romantic | Ciepłe kolory płynne | `{"properties": {"flow": "romantic"}}` |
| 🔮 | Magic | Losowy mix kolorów wolny | `{"properties": {"flow": "magic"}}` |

**API Requirement:**
```json
{
  "properties": {
    "flow": "police|rainbow|disco|strobe|candle|romantic|magic|...",
    "flow_action": "start|stop"  // optional, default: start
  }
}
```

**Stop Flow:**
```json
{
  "properties": {
    "flow_action": "stop"
  }
}
```

---

### 3.6 Ulubione (Favorites)

| GUI | Funkcja | API Call |
|-----|---------|----------|
| ⭐ 1 | Przywróć ulubiony #1 | `PUT /devices/{id}/favorites/1` |
| ⭐ 2 | Przywróć ulubiony #2 | `PUT /devices/{id}/favorites/2` |
| ⭐ 3 | Przywróć ulubiony #3 | `PUT /devices/{id}/favorites/3` |
| 💾 | Zapisz obecny stan | `POST /devices/{id}/favorites` body: `{"slot": 1-3}` |

**API Requirements:**

**Zapisz favorite:**
```
POST /devices/{id}/favorites
{
  "slot": 1-3,
  "name": "Mój ulubiony" // optional
}
```

**Przywróć favorite:**
```
PUT /devices/{id}/favorites/{slot}
```

**Pobierz listę favorites:**
```
GET /devices/{id}/favorites
```

**Response:**
```json
{
  "favorites": [
    {
      "slot": 1,
      "name": "Wieczorne czytanie",
      "settings": {
        "brightness": 75,
        "color_temp": 4000
      }
    },
    ...
  ]
}
```

---

## 4. Complete API Endpoint Summary

### 4.1 Wymagane Endpointy dla GUI

| Endpoint | Method | Purpose | Priority |
|----------|--------|---------|----------|
| `/devices/{id}/control` | PUT | Podstawowa kontrola + kolory + barwa | **MUST** |
| `/devices/{id}/flow` | PUT | Start/stop animacji | **MUST** |
| `/devices/{id}/favorites` | GET | Lista ulubionych | **SHOULD** |
| `/devices/{id}/favorites` | POST | Zapisz ulubiony | **SHOULD** |
| `/devices/{id}/favorites/{slot}` | PUT | Przywróć ulubiony | **SHOULD** |
| `/devices/{id}/status` | GET | Obecny stan żarówki | **MUST** |

### 4.2 Nowe Capabilities do Dodania

Obecne API wspiera tylko:
- ✅ `power` (on/off/toggle)

**Do zaimplementowania:**
- ❌ `brightness` (1-100)
- ❌ `rgb` ([r, g, b])
- ❌ `color_temp` (1700-6500K)
- ❌ `flow` (police, rainbow, disco, etc.)
- ❌ `scene` (opcjonalnie - można zastąpić kombinacjami powyższych)
- ❌ `favorites` (persistence wymagana)

---

## 5. Yeelight Flow Definitions

### 5.1 Dostępne Efekty w Bibliotece `yeelight`

**Proste (built-in transitions):**
```python
from yeelight import Flow, RGBTransition, HSVTransition,
                      TemperatureTransition, SleepTransition

# Police
police = Flow(
    count=0,  # infinite
    transitions=[
        RGBTransition(0, 0, 255, duration=500, brightness=100),
        SleepTransition(500),
        RGBTransition(255, 0, 0, duration=500, brightness=100),
        SleepTransition(500),
    ]
)

# Rainbow
rainbow = Flow(
    count=0,
    transitions=[
        HSVTransition(0, 100, duration=1000),    # Red
        HSVTransition(60, 100, duration=1000),   # Yellow
        HSVTransition(120, 100, duration=1000),  # Green
        HSVTransition(180, 100, duration=1000),  # Cyan
        HSVTransition(240, 100, duration=1000),  # Blue
        HSVTransition(300, 100, duration=1000),  # Magenta
    ]
)

# Strobe
strobe = Flow(
    count=0,
    transitions=[
        RGBTransition(255, 255, 255, duration=50, brightness=100),
        SleepTransition(50),
        RGBTransition(0, 0, 0, duration=50, brightness=1),
        SleepTransition(50),
    ]
)

# Candle (flicker simulation)
candle = Flow(
    count=0,
    transitions=[
        TemperatureTransition(2700, duration=random(800, 1200), brightness=random(70, 90)),
        TemperatureTransition(2500, duration=random(800, 1200), brightness=random(60, 80)),
    ]
)
```

### 5.2 API Serialization

**Problem:** Flow objects nie są JSON-serializable

**Rozwiązanie:** API przyjmuje nazwę flow, backend tworzy Flow object:

```python
PREDEFINED_FLOWS = {
    "police": police_flow,
    "rainbow": rainbow_flow,
    "disco": disco_flow,
    "strobe": strobe_flow,
    "candle": candle_flow,
    "romantic": romantic_flow,
}

# API endpoint:
flow_name = request.properties.get("flow")
flow_obj = PREDEFINED_FLOWS[flow_name]
await adapter.start_flow(flow_obj)
```

---

## 6. Preview Mode (dla GUI)

### 6.1 Koncept
Pierwszy klik → API stosuje zmianę **temporary** (np. 2 sekundy), potem wraca do poprzedniego stanu.

### 6.2 API Support Options

**Option A - GUI Timer:**
- GUI wysyła normalną komendę
- GUI czeka 2s
- GUI wysyła komendę przywrócenia stanu
- **Pros:** Proste API
- **Cons:** GUI musi pamiętać poprzedni stan

**Option B - API Preview Mode:**
```json
{
  "properties": {
    "rgb": [255, 0, 0],
    "preview": true,
    "preview_duration": 2000  // ms
  }
}
```
- API automatycznie wraca po timeout
- **Pros:** GUI prostsza, API pamięta stan
- **Cons:** Bardziej złożone API

**Rekomendacja:** Option A dla MVP (prostota), Option B dla v2

---

## 7. Hierarchia Grup - Szczegóły Skanowania

### 7.1 Struktura Nawigacji

```
ROOT
│
├─ PODSTAWOWA KONTROLA
│  ├─ OFF (wyłącz)
│  ├─ 25% (jasność)
│  ├─ 50% (jasność)
│  ├─ 75% (jasność)
│  └─ 100% (jasność)
│
├─ SZYBKIE KOLORY
│  ├─ ⚪ Biały
│  ├─ 🟡 Żółty
│  ├─ 🔴 Czerwony
│  ├─ 🟢 Zielony
│  ├─ 🔵 Niebieski
│  ├─ 🟣 Fioletowy
│  ├─ 🟠 Pomarańczowy
│  └─ 🩷 Różowy
│
├─ BARWA BIELI
│  ├─ ❄️ Zimne (6500K)
│  ├─ ☀️ Neutralne (4000K)
│  └─ 🔥 Ciepłe (2700K)
│
├─ SCENY TEMATYCZNE
│  ├─ 📖 Czytanie
│  ├─ 🎬 Film
│  ├─ 😴 Noc
│  ├─ ☕ Praca
│  └─ 🍽️ Kolacja
│
├─ EFEKTY WOW
│  ├─ 🚨 Police
│  ├─ 🌈 Rainbow
│  ├─ 🎉 Disco
│  ├─ ⚡ Strobe
│  ├─ 🕯️ Candle
│  ├─ 💝 Romantic
│  └─ 🔮 Magic
│
└─ ULUBIONE
   ├─ ⭐ Slot 1
   ├─ ⭐ Slot 2
   ├─ ⭐ Slot 3
   └─ 💾 Zapisz obecny
```

**Liczba przycisków:**
- Grupy: 6
- Opcje: 5 + 8 + 3 + 5 + 7 + 4 = **32 przyciski**
- **Total:** 6 grup + 32 opcje = 38 elementów

---

## 8. RGB Color Reference

### 8.1 Dokładne Wartości RGB

```python
PRESET_COLORS = {
    "white":   (255, 255, 255),  # ⚪ Czysty biały
    "yellow":  (255, 255, 0),    # 🟡 Jasny żółty
    "red":     (255, 0, 0),      # 🔴 Czysty czerwony
    "green":   (0, 255, 0),      # 🟢 Czysty zielony
    "blue":    (0, 0, 255),      # 🔵 Czysty niebieski
    "purple":  (128, 0, 128),    # 🟣 Fiolet
    "orange":  (255, 165, 0),    # 🟠 Pomarańczowy
    "pink":    (255, 192, 203),  # 🩷 Różowy pastelowy
}
```

### 8.2 Color Temperature Reference

```python
COLOR_TEMPS = {
    "warm":    2700,  # 🔥 Ciepłe (świeca, zachód słońca)
    "neutral": 4000,  # ☀️ Neutralne (dzienne światło)
    "cool":    6500,  # ❄️ Zimne (pochmurny dzień, czysty biały)
}
```

---

## 9. Implementation Priority

### 9.1 Phase 1 - MVP (Minimalny Zestaw)
**Deadline:** Najbliższe 2-3 dni

**API Endpoints:**
- ✅ `PUT /devices/{id}/control` - rozszerzyć o:
  - `brightness` (1-100)
  - `rgb` ([r, g, b])
  - `color_temp` (1700-6500)

**Funkcje GUI:**
- OFF + 4 poziomy jasności (5 przycisków)
- 8 kolorów RGB (8 przycisków)
- 3 temperatury (3 przyciski)
- **Total: 16 przycisków**

### 9.2 Phase 2 - Extended
**Deadline:** 1 tydzień

**API Endpoints:**
- `PUT /devices/{id}/flow` - animacje
  - Implement 3-4 podstawowe flows

**Funkcje GUI:**
- 3-4 efekty WOW (police, rainbow, disco)
- **Total: +4 przyciski = 20 przycisków**

### 9.3 Phase 3 - Full Featured
**Deadline:** 2 tygodnie

**API Endpoints:**
- `GET/POST/PUT /devices/{id}/favorites` - ulubione

**Funkcje GUI:**
- 5 scen tematycznych
- 3 sloty ulubionych + zapisz
- **Total: +9 przycisków = 29 przycisków**

---

## 10. Testing Strategy

### 10.1 GUI Testing (Inny Projekt)
- Accessibility testing z screen readers
- Timing tests (scan speed)
- Click detection accuracy
- Visual contrast (WCAG compliance)

### 10.2 API Testing (Ten Projekt)
- Unit tests dla każdej nowej capability
- Integration tests z mock Yeelight bulb
- Rate limiting tests (60 req/min)
- Flow animation tests

### 10.3 End-to-End Testing
- GUI → API → Real Yeelight bulb
- Wszystkie kombinacje parametrów
- Preview mode workflow
- Error handling (bulb offline, invalid params)

---

## 11. Accessibility Notes (dla GUI projektu)

### 11.1 Wymagania WCAG
- **Kontrast:** Minimum 4.5:1 dla tekstu
- **Rozmiar przycisków:** Extra large (120x120px minimum)
- **Spacje między przyciskami:** Minimum 8px
- **Focus indicators:** Wyraźne podświetlenie (3px border minimum)

### 11.2 Screen Reader Support
- Każdy przycisk ma `aria-label`
- Aktualny stan czytany automatycznie
- Grupy mają `role="group"` i `aria-labelledby`

### 11.3 Keyboard Navigation
- Tab/Shift+Tab - nawigacja między grupami
- Arrow keys - nawigacja wewnątrz grupy
- Space/Enter - aktywacja
- Escape - anuluj/wróć

---

## 12. Future Enhancements (Post-MVP)

### 12.1 Advanced Features
- **Gradient colors** - płynne przejścia między kolorami
- **Custom flows** - użytkownik tworzy własne animacje
- **Schedules** - zaplanowane sceny (timer, sunrise/sunset)
- **Multi-device control** - kontrola wielu żarówek naraz
- **Rooms/Groups** - grupowanie żarówek

### 12.2 Integration Ideas
- **Voice control** - integracja z TTS/STT
- **MQTT support** - Home Assistant, OpenHAB
- **Webhook triggers** - IFTTT, Zapier
- **API webhooks** - powiadomienia o zmianach stanu

---

## 13. Technical Notes

### 13.1 Yeelight Library Limits
- **Rate limiting:** 60 commands/minute
- **Music mode:** Removes rate limit (for flows)
- **Connection timeout:** 5 seconds default
- **Retry logic:** 3 retries recommended

### 13.2 Network Requirements
- **LAN Control:** Must be enabled in Yeelight app
- **Port:** 55443 (Yeelight default)
- **Protocol:** TCP for commands, UDP for discovery
- **Same network:** GUI device, API server, bulb must be on same LAN

### 13.3 Performance Considerations
- **Response time:** < 200ms for basic commands
- **Flow start:** < 500ms
- **Discovery:** 2-5 seconds
- **Batch operations:** Use music mode for rapid commands

---

## 14. Summary - Action Items for API Project

### 14.1 Implement New Capabilities

**In `YeelightAdapter`:**
```python
async def set_brightness(self, value: int) -> bool
async def set_rgb(self, red: int, green: int, blue: int) -> bool
async def set_color_temp(self, degrees: int) -> bool
async def start_flow(self, flow_name: str) -> bool
async def stop_flow(self) -> bool
```

**In API `/devices/{id}/control`:**
- Accept `brightness`, `rgb`, `color_temp`, `flow` properties
- Validate ranges
- Handle errors gracefully

### 14.2 Create Flow Library

**In `app/services/flows.py`:**
```python
PREDEFINED_FLOWS = {
    "police": create_police_flow(),
    "rainbow": create_rainbow_flow(),
    "disco": create_disco_flow(),
    "strobe": create_strobe_flow(),
    "candle": create_candle_flow(),
    "romantic": create_romantic_flow(),
}
```

### 14.3 Optional: Favorites System

**Requires:**
- Persistence layer (SQLite, file-based)
- New endpoints for CRUD operations
- Device state snapshot mechanism

**Can defer to Phase 3**

---

## 15. Questions & Decisions

### 15.1 Resolved
- ✅ Jasność: 4 poziomy (25%, 50%, 75%, 100%)
- ✅ Skanowanie: Hierarchiczne
- ✅ Animacje: Jak najwięcej
- ✅ Preview: Klik → preview → klik → apply

### 15.2 Remaining Questions
- ⚠️ Persistence: SQLite, JSON file, or in-memory only?
- ⚠️ Multiple devices: One API instance for all bulbs?
- ⚠️ Auto-discovery: Periodic background scan?
- ⚠️ Websocket: Real-time state updates for GUI?

**Rekomendacja:** Defer to next discussion, focus on core functionality first.

---

**Document Version:** 1.0
**Created:** 2026-05-09
**Author:** AAC IoT Hub Team
**For:** GUI Scanning Interface Project
