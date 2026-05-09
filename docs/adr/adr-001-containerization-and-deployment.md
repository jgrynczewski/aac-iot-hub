# ADR 001: Konteneryzacja i Deployment

## Status
Proposed

## Kontekst
Projekt AAC IoT Hub wymaga uruchomienia jako serwis dostępny przez API. System musi być:
- Łatwy do wdrożenia na różnych platformach (w tym Ubuntu 18.04 LTS)
- Izolowany od środowiska hosta
- Portable między różnymi maszynami

## Rozważane opcje

### Opcja 1: Docker (ZALECANA)
**Zalety:**
- Najpopularniejsze rozwiązanie konteneryzacji (de facto standard)
- Oficjalne wsparcie dla Ubuntu 18.04 (Docker CE 20.10+)
- Prosty `docker run` do uruchomienia
- Docker Compose dla łatwej konfiguracji
- Ogromna społeczność i dokumentacja
- Multi-stage builds dla małych obrazów
- Docker Hub dla dystrybucji obrazów
- Networking out-of-the-box (bridge, host mode dla mDNS)

**Wady:**
- Ubuntu 18.04 wymaga manualnej instalacji Docker (nie ma w domyślnych repo)
- Większy footprint niż Podman

**Kompatybilność Ubuntu 18.04:**
- ✅ Oficjalnie wspierane przez Docker Inc.
- Wymaga instalacji z repozytorium Docker (nie apt default)
- Minimalna wersja: Docker CE 18.06+

### Opcja 2: Podman
**Zalety:**
- Daemonless (bezpieczniejsze)
- Rootless containers (lepsza security)
- Drop-in replacement dla Docker (kompatybilne CLI)
- Lepsze wsparcie dla systemd
- Oficjalnie przez Red Hat

**Wady:**
- ❌ **Brak oficjalnego wsparcia dla Ubuntu 18.04**
- Podman wymaga Ubuntu 20.10+ w oficjalnych repo
- Mniejsza popularność
- Problemy z networking w starszych wersjach

**Kompatybilność Ubuntu 18.04:**
- ❌ Brak w oficjalnych repo
- Możliwa kompilacja ze źródeł, ale skomplikowana
- **Nie spełnia wymagania "prosto uruchomić"**

### Opcja 3: LXC/LXD
**Zalety:**
- Natywne wsparcie Ubuntu (Canonical)
- Lekkie system containers
- Dostępne w Ubuntu 18.04

**Wady:**
- Bardziej system-centric niż application-centric
- Overengineering dla pojedynczej aplikacji
- Mniej portable (obrazy nie są tak standardowe jak Docker)
- Wymaga więcej konfiguracji networkingu

### Opcja 4: Python venv + systemd service
**Zalety:**
- Najprostsze (bez kontenerów)
- Najmniejszy overhead
- Bezpośredni dostęp do sieci (ważne dla mDNS/SSDP)

**Wady:**
- Brak izolacji
- Zależności od systemu hosta
- Trudniejszy deployment na różnych platformach
- Brak reprodukowalności środowiska
- Wymaga manualnej konfiguracji na każdym systemie

## Decyzja

**Wybrano: Docker (Opcja 1)**

### Uzasadnienie:
1. **Kompatybilność z Ubuntu 18.04**: Oficjalnie wspierane, sprawdzona instalacja
2. **Standardizacja**: Docker to standard branżowy - największa społeczność
3. **Prostota użycia**: `docker run -d --network=host aac-iot-hub`
4. **Network capabilities**: Zobacz **ADR-002** dla szczegółowej analizy konfiguracji sieciowej
5. **Reprodukowalność**: Ten sam obraz działa wszędzie
6. **Ekosystem**: Docker Compose, Docker Hub, CI/CD integration

**Wybór portu 8765**:
- Rzadko używany w standardowych aplikacjach
- Nie koliduje z popularnymi serwisami (8080, 8000, 8888, 3000, 5000, etc.)
- Łatwy do zapamiętania
- Konfigurowalny przez env var `API_PORT`
- Alternatywy jeśli zajęty: 9765, 9080, 8866

### Architektura rozwiązania:

```
┌─────────────────────────────────────────┐
│           Docker Container               │
│  ┌────────────────────────────────────┐ │
│  │     Python 3.12 Application        │ │
│  │  ┌──────────────────────────────┐  │ │
│  │  │      API Server (FastAPI)    │  │ │
│  │  │      Port: 8765              │  │ │
│  │  └──────────────────────────────┘  │ │
│  │  ┌──────────────────────────────┐  │ │
│  │  │   Yeelight Discovery Service │  │ │
│  │  │   (SSDP - UDP Multicast)     │  │ │
│  │  └──────────────────────────────┘  │ │
│  │  ┌──────────────────────────────┐  │ │
│  │  │   Device Control Logic       │  │ │
│  │  └──────────────────────────────┘  │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
         │                    │
         │ HTTP :8765         │ UDP Multicast (SSDP)
         │                    │ dla discovery
         ▼                    ▼
    Host Network      Local Network Devices
```

### Implementacja:

**Dockerfile (multi-stage):**
```dockerfile
FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .
EXPOSE 8765
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8765"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  aac-iot-hub:
    build: .
    network_mode: host  # Dla SSDP discovery - zobacz ADR-002
    restart: unless-stopped
    environment:
      - LOG_LEVEL=${LOG_LEVEL:-info}
      - API_PORT=${API_PORT:-8765}
```

### Network Mode:
Zobacz **ADR-002: Docker Network Configuration** dla szczegółowej analizy i uzasadnienia wyboru host mode dla multicast discovery.

### Ubuntu 18.04 - Instrukcje instalacji Docker:
```bash
# Usunięcie starych wersji
sudo apt-get remove docker docker-engine docker.io containerd runc

# Instalacja dependencies
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common

# Dodanie oficjalnego GPG key Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Dodanie repo Docker
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"

# Instalacja Docker CE
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Opcjonalnie: dodanie użytkownika do grupy docker
sudo usermod -aG docker $USER
```

## Konsekwencje

### Pozytywne:
- ✅ Portable deployment na wszystkie systemy z Docker
- ✅ Izolacja aplikacji od systemu hosta
- ✅ Łatwe wersjonowanie (image tags)
- ✅ Kompatybilność z Ubuntu 18.04+
- ✅ Możliwość dystrybucji przez Docker Hub
- ✅ CI/CD ready

### Negatywne:
- ⚠️ Wymaga instalacji Docker na Ubuntu 18.04 (nie jest preinstalowany)
- ⚠️ Network host mode zmniejsza izolację (zobacz ADR-002 dla uzasadnienia)
- ⚠️ Wymaga uprawnień do Docker (root lub docker group)

## Powiązane ADR
- ADR-000: Wybór typu urządzenia IoT (Yeelight)
- ADR-002: Docker Network Configuration
- ADR-003: HTTP API Protocol

### Alternatywny plan (fallback):
Jeśli Docker okaże się problematyczny, można łatwo wrócić do opcji 4 (venv + systemd), ponieważ aplikacja będzie zaprojektowana jako standalone Python service.

## Data
2026-04-25