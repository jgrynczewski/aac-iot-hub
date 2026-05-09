idzmitak# ADR 000: Wybór typu urządzenia IoT

## Status
Accepted

## Kontekst
AAC IoT Hub to lokalny hub do kontroli urządzeń IoT bez zależności od chmury. W fazie POC (Proof of Concept) przetestowano dwa typy urządzeń:
- **Yeelight**: Inteligentne żarówki WiFi (Yeelight Color Bulb, Yeelight Duo)
- **Shelly**: Inteligentne żarówki i urządzenia (Shelly Bulb Duo RGBW, Gen1 i Gen2+)

Oba typy urządzeń działają w sieci lokalnej i nie wymagają połączenia z chmurą, co jest zgodne z głównym założeniem projektu.

**Pytanie**: Który typ urządzenia wybrać jako podstawę dla pierwszej wersji serwisu? Czy wspierać jeden typ, czy oba od razu?

## Istniejące POC

### POC Yeelight (`yeelight_toggle.py`)
**Status**: Działa stabilnie
- **Kod**: 25 linii (bardzo prosty)
- **Biblioteka**: `yeelight` (oficjalna, dobrze utrzymywana)
- **Discovery**: SSDP (Simple Service Discovery Protocol) - UDP multicast
- **Konfiguracja urządzenia**: Wymaga włączenia "LAN Control" w aplikacji Yeelight Classic
- **Stabilność discovery**: 100% success rate
- **API komunikacji**: Wbudowane w bibliotekę `yeelight`
- **Dokumentacja**: Doskonała (oficjalna biblioteka + dokumentacja API)

**Przykład użycia:**
```python
from yeelight import discover_bulbs

bulbs = discover_bulbs()  # Auto-discovery przez SSDP
bulb = Bulb(bulbs[0]['ip'])
bulb.toggle()
```

### POC Shelly (`shelly_toggle.py`)
**Status**: Działa, ale z problemami
- **Kod**: 104 linie (złożony, custom discovery)
- **Biblioteka**: Custom implementacja (zeroconf + requests)
- **Discovery**: mDNS (Multicast DNS / Bonjour)
- **Konfiguracja urządzenia**: Factory reset może być wymagany
- **Stabilność discovery**: ~30% success rate dla Gen1 (działa 1 na 3-5 prób)
- **API komunikacji**: Bezpośrednie wywołania HTTP (różne dla Gen1 i Gen2+)
- **Dokumentacja**: Dobra, ale wymaga obsługi dwóch generacji

**Problemy zidentyfikowane w POC:**
- Shelly Gen1 mDNS discovery jest niestabilny (znany problem, udokumentowany w `docs/shelly.md:130`)
- Wymaga własnej implementacji discovery (brak dobrej biblioteki)
- Dwie generacje urządzeń (Gen1 i Gen2+) wymagają różnych API:
  - Gen1: REST API (`/color/0?turn=toggle`)
  - Gen2+: RPC API (`/rpc/Light.Toggle`)
- Discovery timeout 20 sekund (długi czas oczekiwania)

## Rozważane opcje

### Opcja 1: Tylko Yeelight (ZALECANA)

**Charakterystyka:**
- Fokus na jednym, stabilnym typie urządzenia
- Wykorzystanie gotowej, sprawdzonej biblioteki
- Szybszy czas do pierwszej działającej wersji
- Prostsze utrzymanie i testowanie

**Zalety:**
- ✅ **Prostota konfiguracji**: Jeden switch w aplikacji mobilnej ("LAN Control")
- ✅ **Stabilne discovery**: SSDP działa zawsze (100% success rate w testach)
- ✅ **Gotowa biblioteka**: `yeelight` jest oficjalna, dobrze utrzymywana, pełna funkcjonalność
- ✅ **Mniej kodu**: ~90% mniej kodu niż custom implementation dla Shelly
- ✅ **Jednorodne API**: Wszystkie urządzenia Yeelight używają tego samego protokołu
- ✅ **Szybszy development**: Możemy skupić się na architekturze serwisu, nie na discovery
- ✅ **Łatwiejsze testowanie**: Jeden typ urządzenia = prostsze testy
- ✅ **Lepsza dokumentacja**: Oficjalna biblioteka + API docs

**Wady:**
- ⚠️ Ograniczenie do jednego producenta (Yeelight/Xiaomi)
- ⚠️ Brak wsparcia dla urządzeń Shelly (na razie)
- ⚠️ Potencjalnie mniejsza baza użytkowników (tylko posiadacze Yeelight)

**Możliwość rozbudowy:**
- W przyszłości można dodać wsparcie dla Shelly jako drugi typ urządzenia
- Architektura serwisu (ADR-003) jest zaprojektowana tak, aby wspierać różne typy urządzeń
- Shelly może być dodany gdy:
  1. Problemy z discovery zostaną rozwiązane
  2. Pojawi się lepsza biblioteka
  3. Będzie rzeczywiste zapotrzebowanie od użytkowników

### Opcja 2: Tylko Shelly

**Charakterystyka:**
- Fokus na urządzeniach Shelly
- Custom implementacja discovery i komunikacji
- Wsparcie dla dwóch generacji (Gen1 i Gen2+)

**Zalety:**
- ✅ Shelly to popularny producent w EU
- ✅ Większa gama urządzeń (nie tylko żarówki)
- ✅ Open source firmware (możliwość customizacji)

**Wady:**
- ❌ **Niestabilne discovery**: Gen1 mDNS działa w ~30% prób
- ❌ **Brak dobrej biblioteki**: Trzeba implementować wszystko ręcznie
- ❌ **Dwie generacje**: Gen1 (ESP8266) i Gen2+ (ESP32) mają różne API
- ❌ **Więcej kodu**: 4x więcej kodu niż Yeelight (104 vs 25 linii)
- ❌ **Trudniejsze utrzymanie**: Custom kod wymaga większego wysiłku
- ❌ **Dłuższy time-to-market**: Więcej czasu na debugging discovery
- ❌ **Gorsza UX**: 20s timeout + retry logic dla discovery

**Analiza bibliotek dla Shelly:**
Z dokumentacji POC (`docs/shelly.md`):
- **pyShelly**: Przestarzałe, nie wspiera Gen2+
- **aioshelly**: Async, ale wymaga Home Assistant dependencies
- **ShellyPy**: Podstawowe, brak discovery

**Konkluzja**: Brak jednoznacznie dobrej biblioteki dla Shelly

### Opcja 3: Yeelight i Shelly (wsparcie dla obu)

**Charakterystyka:**
- Wsparcie dla dwóch typów urządzeń od początku
- Bardziej uniwersalny hub
- Abstrakcja nad różnicami w protokołach

**Zalety:**
- ✅ Większa baza potencjalnych użytkowników
- ✅ Bardziej uniwersalny hub
- ✅ Możliwość mieszania urządzeń w jednej sieci

**Wady:**
- ❌ **Zwiększona złożoność**: Dwa różne discovery protocols (SSDP + mDNS)
- ❌ **Niestabilność**: Problemy Shelly wpływają na cały system
- ❌ **Więcej kodu do utrzymania**: Custom Shelly + library Yeelight
- ❌ **Trudniejsze testowanie**: Kombinacje urządzeń, edge cases
- ❌ **Dłuższy development**: Trzeba obsłużyć oba typy od początku
- ❌ **Discovery timeout**: Musi czekać na oba protokoły (SSDP + mDNS)
- ❌ **Abstrakcja**: Potrzebna warstwa abstrakcji nad różnicami
- ❌ **Premature generalization**: Over-engineering na początku projektu

**Problemy architektoniczne:**
```python
# Trzeba będzie obsłużyć:
class Device(ABC):
    @abstractmethod
    async def toggle(self): pass

class YeelightDevice(Device):
    # Używa biblioteki yeelight

class ShellyDevice(Device):
    # Custom implementation
    # Różne API dla Gen1 vs Gen2+

# Discovery musi obsłużyć:
- SSDP (Yeelight) - multicast 239.255.255.250:1900
- mDNS (Shelly Gen1) - _http._tcp.local.
- mDNS (Shelly Gen2+) - _shelly._tcp.local.
```

## Decyzja

**Wybrano: Opcja 1 - Tylko Yeelight**

## Uzasadnienie szczegółowe

### 1. Prostota jako główny priorytet

Projekt jest w fazie MVP (Minimum Viable Product). Kluczowe jest:
- Szybkie dostarczenie działającego rozwiązania
- Minimalizacja ryzyka technicznego
- Skupienie na architekturze serwisu, nie na quirks discovery

**Yeelight spełnia wszystkie wymagania** z minimalną złożonością.

### 2. Analiza porównawcza POC

| Kryterium | Yeelight | Shelly |
|-----------|----------|---------|
| Linie kodu POC | 25 | 104 (4x więcej) |
| Discovery success rate | 100% | ~30% (Gen1) |
| Biblioteka | Oficjalna, pełna | Brak / Custom |
| Setup urządzenia | 1 switch w apce | Factory reset może być potrzebny |
| API consistency | Jednolite | Gen1 ≠ Gen2+ |
| Discovery timeout | ~3s | 20s |
| Dokumentacja | Doskonała | Dobra, ale fragmentaryczna |
| Stabilność | Wysoka | Średnia (Gen1 issues) |

**Konkluzja**: Yeelight wygrywa w każdym kryterium technicznym.

### 3. Time-to-market

**Yeelight**:
- POC działa → serwis może być zbudowany w dni/tygodnie
- Biblioteka dostarcza wszystko out-of-the-box
- Fokus na architekturze REST API

**Shelly**:
- Wymaga debugging discovery (może zająć tygodnie)
- Custom implementation discovery + kontroli
- Obsługa dwóch generacji = więcej edge cases
- Fokus na rozwiązywaniu problemów z urządzeniami

**Oszacowanie czasu**:
- Yeelight: 2-3 tygodnie do MVP
- Shelly: 4-6 tygodni do MVP (debugging discovery)
- Oba: 6-8 tygodni (abstrakcja + testing)

### 4. Jakość kodu i utrzymanie

**Yeelight**:
```python
# Cały discovery to:
from yeelight import discover_bulbs
bulbs = discover_bulbs()
```

**Shelly**:
```python
# Discovery wymaga:
- Klasa ShellyListener (ServiceListener)
- Obsługa zeroconf
- Parsing mDNS responses
- Obsługa Gen1 vs Gen2+
- Retry logic
- Timeout handling
```

**Maintainability**: Yeelight wygrywa zdecydowanie.

### 5. User Experience

**Yeelight setup**:
1. Zainstaluj Yeelight Classic app
2. Podłącz żarówkę
3. Włącz "LAN Control" w ustawieniach
4. Gotowe

**Shelly setup**:
1. Podłącz urządzenie
2. Sprawdź generację (Gen1 vs Gen2+)
3. Factory reset jeśli discovery nie działa
4. Czekaj 20s na discovery
5. Retry jeśli nie znalazło (Gen1)
6. Gotowe (może)

**UX winner**: Yeelight

### 6. Risk Analysis

**Ryzyka dla Yeelight**:
- ✅ Biblioteka może przestać być utrzymywana
  - **Mitigation**: API Yeelight jest proste, można fork'nąć
- ✅ Ograniczenie do jednego producenta
  - **Mitigation**: Yeelight/Xiaomi to duży gracz, stabilny

**Ryzyka dla Shelly**:
- ❌ Discovery może nie działać w niektórych sieciach
  - **Trudne do mitigation**: Problem na poziomie firmware/hardware
- ❌ Custom kod wymaga utrzymania
  - **Mitigation**: Więcej czasu na maintenance
- ❌ Dwie generacje urządzeń komplikują kod
  - **Mitigation**: Więcej testów, więcej kodu

**Risk assessment**: Yeelight ma niższe ryzyko.

### 7. Strategia przyszłościowa: Shelly jako drugi typ urządzenia

Decyzja **NIE wyklucza** Shelly w przyszłości. Plan:

**Faza 1: MVP z Yeelight (obecna)**
- Implementacja REST API (ADR-003)
- Discovery dla Yeelight
- Podstawowe funkcje (power, brightness, color)
- Docker deployment (ADR-001, ADR-002)

**Faza 2: Stabilizacja (następna)**
- Więcej funkcji Yeelight (efekty, scenes)
- Testy integracyjne
- Dokumentacja użytkownika
- Feedback od użytkowników

**Faza 3: Rozszerzenie o Shelly (przyszłość - JEŚLI)**
Warunki dodania Shelly:
1. **Rozwiązane problemy discovery** (Gen1 stabilne lub porzucone)
2. **Pojawienie się lepszej biblioteki** dla Shelly
3. **Rzeczywiste zapotrzebowanie** od użytkowników
4. **Architektura wspiera** abstrakcję urządzeń (będzie)

**Architektura przygotowana na rozszerzenie**:
```python
# Abstrakcja już zaprojektowana w ADR-003
class DeviceService(ABC):
    @abstractmethod
    async def discover(self) -> List[Device]: pass
    @abstractmethod
    async def control(self, device_id, action): pass

class YeelightService(DeviceService):
    # Implementacja dla Yeelight

# W przyszłości:
class ShellyService(DeviceService):
    # Implementacja dla Shelly (gdy będzie stabilna)
```

### 8. Feedback z POC

Z dokumentacji POC (`docs/shelly.md:130`):
> **Known Issues:**
> - Shelly Gen1 mDNS discovery can be unreliable (works ~1 in 3-5 runs)
> - Requires factory reset sometimes

Versus `docs/yeelight.md`:
> **Setup is straightforward:**
> - Enable "LAN Control" in Yeelight Classic app
> - Discovery works reliably

**Empiryczne dane**: Yeelight po prostu działa.

## Implementacja

### Struktura projektu dla Yeelight

```
aac-iot-hub/
├── app/
│   ├── services/
│   │   ├── yeelight_service.py  # Discovery + control dla Yeelight
│   │   └── device_service.py    # Abstract base (dla przyszłych typów)
│   └── models/
│       ├── device.py             # Abstract Device model
│       └── yeelight_device.py    # Yeelight-specific model
```

### Dependencies

```txt
# requirements.txt
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
pydantic>=2.6.0
yeelight>=0.7.14  # Jedyna device-specific dependency
```

### Migration path do Shelly (przyszłość)

Jeśli w przyszłości dodamy Shelly:
1. Dodaj `shelly_service.py` obok `yeelight_service.py`
2. Implementuj `DeviceService` interface
3. Discovery agreguje wyniki z obu serwisów
4. API pozostaje niezmienione (dzięki abstrakcji)

## Konsekwencje

### Pozytywne:
- ✅ **Szybszy time-to-market**: MVP w 2-3 tygodnie vs 6-8 tygodni
- ✅ **Stabilność**: 100% success rate discovery
- ✅ **Prostota kodu**: 25 linii POC vs 104 linii
- ✅ **Mniejsze ryzyko techniczne**: Sprawdzona biblioteka
- ✅ **Łatwiejsze utrzymanie**: Mniej kodu, mniej bugs
- ✅ **Lepsze UX**: Prosty setup, szybkie discovery
- ✅ **Fokus na architekturze**: Czas na REST API, Docker, itp.
- ✅ **Gotowość na rozszerzenie**: Architektura wspiera wiele typów urządzeń

### Negatywne:
- ⚠️ **Ograniczenie do Yeelight**: Tylko posiadacze Yeelight mogą używać (na razie)
- ⚠️ **Mniejsza baza użytkowników**: Potencjalnie mniej userów niż gdyby oba typy
- ⚠️ **Vendor lock-in**: Zależność od Xiaomi/Yeelight ecosystem

### Mitigacje negatywnych konsekwencji:

**Mitigation dla vendor lock-in**:
- Abstrakcja `DeviceService` pozwala dodać inne typy w przyszłości
- Yeelight API jest proste i można je zreplikować w razie potrzeby
- Xiaomi/Yeelight to stabilny, duży gracz na rynku

**Mitigation dla mniejszej bazy użytkowników**:
- Fokus na jakości, nie ilości
- Stabilny produkt dla Yeelight > niestabilny dla obu typów
- Shelly może być dodany później gdy będzie stabilny

### Warunki rewizji decyzji:

Decyzja powinna być zrewidowana jeśli:
1. ❌ Biblioteka `yeelight` przestanie być utrzymywana (>12 miesięcy bez update)
2. ❌ Pojawi się major bug w Yeelight discovery nie do obejścia
3. ✅ Shelly Gen1 discovery stanie się stabilne (>90% success rate)
4. ✅ Pojawi się oficjalna, dobra biblioteka dla Shelly
5. ✅ Większość użytkowników będzie prosić o Shelly support

## Alternatywy odrzucone

### "Czemu nie Zigbee/Z-Wave/Matter?"

Te protokoły wymagają **hardware bridge/gateway**:
- Zigbee: Wymaga Zigbee coordinator (USB dongle)
- Z-Wave: Wymaga Z-Wave controller
- Matter: Jeszcze w fazie adopcji

**AAC IoT Hub** to **software-only** rozwiązanie:
- Działa na każdym komputerze z Dockerem
- Nie wymaga dodatkowego hardware
- WiFi-based devices (Yeelight, Shelly) są self-contained

### "Czemu nie Home Assistant integration?"

Home Assistant to pełny home automation system. AAC IoT Hub to:
- **Lightweight**: Minimalistyczny hub dla podstawowej kontroli
- **Simple**: Prosty REST API, nie full automation platform
- **Focused**: Kontrola urządzeń, nie automacje/scenes/dashboards

Różne use cases, różne rozwiązania.

## Podsumowanie

**Yeelight jako pierwszy (i na razie jedyny) typ urządzenia** to najlepsza decyzja dla MVP:
- Prostota > złożoność
- Stabilność > feature completeness
- Time-to-market > uniwersalność

Shelly pozostaje jako **potencjalne rozszerzenie** gdy:
- Problemy discovery zostaną rozwiązane
- Pojawi się lepsza biblioteka
- Będzie realne zapotrzebowanie

**"Make it work, make it right, make it fast" - Kent Beck**

Zaczynamy od "make it work" z Yeelight. Shelly może być "make it right" w przyszłości.

## Powiązane ADR
- ADR-001: Konteneryzacja i Deployment
- ADR-002: Docker Network Configuration (SSDP dla Yeelight)
- ADR-003: HTTP API Protocol (abstrakcja wspiera wiele typów urządzeń)

## Data
2026-04-25

## Status Log
- 2026-04-25: **Accepted** - Wybrano Yeelight jako pierwszy typ urządzenia
- 2026-04-25: Proposed - Initial draft