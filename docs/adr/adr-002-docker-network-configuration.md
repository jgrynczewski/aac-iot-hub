# ADR 002: Docker Network Configuration

## Status
Proposed

## Kontekst
AAC IoT Hub wymaga komunikacji z urządzeniami IoT w sieci lokalnej poprzez protokół SSDP (Simple Service Discovery Protocol). SSDP to protokół discovery używany przez Yeelight, który opiera się na UDP multicast (239.255.255.250:1900).

**Kluczowe wymaganie**: Kontener Docker musi mieć możliwość:
1. Wysyłania UDP multicast packets do lokalnej sieci
2. Odbierania odpowiedzi od urządzeń Yeelight w sieci
3. Komunikacji HTTP z urządzeniami (po discovery)

**Pytanie**: Czy discovery wymaga `--network=host` mode, czy można użyć standardowego bridge mode z większą izolacją?

## Rozważane opcje

### Opcja 1: Host Network Mode (ZALECANA)

**Konfiguracja:**
```yaml
services:
  aac-iot-hub:
    network_mode: host
    environment:
      - API_PORT=8765
```

**Jak działa:**
- Kontener dzieli cały network stack z hostem
- Nie ma izolacji sieciowej (kontener = host)
- Brak NAT, brak port mapping
- Multicast packets przechodzą bezpośrednio

**Zalety:**
- ✅ **Multicast działa out-of-the-box** - zero konfiguracji
- ✅ **100% pewności że SSDP zadziała** na wszystkich systemach
- ✅ Najprostsza konfiguracja (brak port mappingu)
- ✅ Najlepsza performance (brak overhead NAT)
- ✅ Kontener widzi wszystkie interfejsy sieciowe hosta
- ✅ Nie wymaga `CAP_NET_ADMIN` ani innych uprawnień
- ✅ Działa identycznie na Ubuntu 18.04, 20.04, 22.04+

**Wady:**
- ⚠️ **Brak izolacji sieciowej** - kontener ma dostęp do wszystkich portów hosta
- ⚠️ Port 8765 musi być wolny na hoście (konflikt jeśli zajęty)
- ⚠️ Kontener widzi cały network stack hosta (potentially security concern)
- ⚠️ Nie można używać `-p` flag (port mapping nie działa w host mode)

**Przypadki użycia:**
- ✅ Lokalne deployment w trusted network (dom, biuro)
- ✅ Gdy priorytetem jest prostota i pewność działania
- ✅ Single-service deployment (tylko AAC IoT Hub na hoście)

**Bezpieczeństwo:**
- **Akceptowalne** dla lokalnego IoT hub w domowej sieci
- Hub i tak musi być w tej samej sieci co urządzenia
- Brak exposu do internetu (tylko LAN)

### Opcja 2: Bridge Network Mode z multicast routing

**Konfiguracja:**
```yaml
services:
  aac-iot-hub:
    ports:
      - "8765:8765"
    cap_add:
      - NET_ADMIN
    sysctls:
      - net.ipv4.ip_forward=1
      - net.ipv4.conf.all.forwarding=1
    devices:
      - /dev/net/tun
```

**Dodatkowa konfiguracja na hoście:**
```bash
# Enable multicast routing
sudo sysctl -w net.ipv4.ip_forward=1

# Setup multicast route (może być wymagane)
sudo route add -net 239.0.0.0 netmask 255.0.0.0 dev docker0
```

**Jak działa:**
- Kontener ma własną sieć bridge (domyślnie `172.17.0.0/16`)
- Docker NAT forwaduje pakiety między bridge a hostem
- Multicast wymaga dodatkowego routingu

**Zalety:**
- ✅ Lepsza izolacja sieciowa
- ✅ Możliwość port mappingu (`-p 8765:8765`)
- ✅ Standardowy Docker networking

**Wady:**
- ❌ **Multicast może nie działać** - zależy od konfiguracji systemu
- ❌ Wymaga `CAP_NET_ADMIN` (większe uprawnienia)
- ❌ Wymaga dodatkowej konfiguracji systemu
- ❌ **Niestabilne na różnych wersjach Docker** (szczególnie starsze)
- ❌ **Może nie działać na Ubuntu 18.04** z Docker 19.x
- ❌ Wymaga manualnej konfiguracji routing tables
- ❌ Trudne do debugowania gdy nie działa
- ❌ Performance overhead (NAT dla każdego pakietu)

**Przypadki użycia:**
- ⚠️ Gdy **NAPRAWDĘ** potrzebujesz izolacji sieciowej
- ⚠️ Multi-service deployment z konfliktami portów
- ⚠️ Deployment w środowisku gdzie host mode jest zabroniony

**Problemy w praktyce:**
Docker bridge domyślnie **nie forwarduje multicast packets**. Wymagane są:
1. IP forwarding w kernelu
2. Multicast routing rules
3. iptables rules dla multicast
4. Może wymagać `smcroute` (multicast routing daemon)

**Kompatybilność:**
- Ubuntu 22.04+: Może działać z odpowiednią konfiguracją
- Ubuntu 20.04: Niestabilne, wymaga testowania
- Ubuntu 18.04: **Prawdopodobnie nie zadziała** - stary kernel + Docker

### Opcja 3: Macvlan Network Mode

**Konfiguracja:**
```yaml
services:
  aac-iot-hub:
    networks:
      - macvlan_net

networks:
  macvlan_net:
    driver: macvlan
    driver_opts:
      parent: eth0  # lub wlan0, enp3s0 - zależy od systemu!
    ipam:
      config:
        - subnet: 192.168.1.0/24
          gateway: 192.168.1.1
          ip_range: 192.168.1.192/27  # Kontener dostanie IP z tego zakresu
```

**Jak działa:**
- Kontener dostaje **własny MAC address** w sieci fizycznej
- Kontener jest "równorzędnym" urządzeniem w sieci LAN
- Multicast działa jak dla fizycznego urządzenia
- Routery/switch'e widzą kontener jako osobne urządzenie

**Zalety:**
- ✅ **Multicast działa perfekcyjnie** (kontener = fizyczne urządzenie w sieci)
- ✅ Pełna izolacja od hosta
- ✅ Kontener ma własny IP z puli DHCP/statyczny
- ✅ Najbardziej "native" networking dla IoT

**Wady:**
- ❌ **Wymaga konfiguracji specyficznej dla hosta** (`parent: eth0` vs `wlan0` vs `enp3s0`)
- ❌ Nazwa interfejsu sieciowego różni się między systemami
- ❌ **Nie działa na WiFi** (większość kart WiFi blokuje multiple MAC addresses)
- ❌ Wymaga znajomości architektury sieci lokalnej (subnet, gateway, IP range)
- ❌ **Host nie może komunikować się z kontenerem** (macvlan isolation)
- ❌ Może wymagać uprawnień na routerze (allow multiple MACs per port)
- ❌ Trudne dla nietechnicznych użytkowników

**Przypadki użycia:**
- ⚠️ Advanced users z przewodowym Ethernet
- ⚠️ Deployment w środowisku korporacyjnym z IT supportem
- ⚠️ Gdy kontener ma być "równorzędnym" urządzeniem w sieci

**Deal-breaker**: Nie działa na WiFi, wymaga per-host configuration

### Opcja 4: IPvlan (L3) Mode

**Konfiguracja:**
```yaml
services:
  aac-iot-hub:
    networks:
      - ipvlan_net

networks:
  ipvlan_net:
    driver: ipvlan
    driver_opts:
      parent: eth0
      ipvlan_mode: l3
```

**Jak działa:**
- Podobnie do macvlan, ale na warstwie IP (nie MAC)
- Kontener dzieli MAC address z hostem, ale ma własny IP

**Zalety:**
- ✅ Mniej problematyczny niż macvlan (single MAC)
- ✅ Działa na większej liczbie kart sieciowych

**Wady:**
- ❌ **Multicast może nie działać** (IPvlan L3 mode blokuje broadcast/multicast)
- ❌ IPvlan L2 mode ma te same problemy co macvlan
- ❌ Wymaga kernel 4.2+ (OK dla Ubuntu 18.04, ale edge cases)

**Przypadki użycia:**
- ❌ **NIE dla SSDP/multicast** - nie będzie działać

## Decyzja

**Wybrano: Host Network Mode (Opcja 1)**

## Uzasadnienie szczegółowe

### 1. Wymagania projektu vs opcje:

| Kryterium | Host Mode | Bridge + routing | Macvlan | Ipvlan |
|-----------|-----------|------------------|---------|--------|
| Multicast działa | ✅ 100% | ⚠️ Może | ✅ Tak | ❌ Nie |
| Zero config | ✅ Tak | ❌ Wymaga setup | ❌ Per-host config | ❌ Wymaga setup |
| Ubuntu 18.04 | ✅ Działa | ❌ Problemy | ⚠️ Zależy od HW | ⚠️ Kernel issues |
| WiFi support | ✅ Tak | ✅ Tak | ❌ Nie | ⚠️ Limited |
| Prostota użycia | ✅ Trivial | ❌ Advanced | ❌ Expert | ❌ Advanced |
| Izolacja | ❌ Brak | ✅ Dobra | ✅ Pełna | ✅ Dobra |

### 2. Analiza bezpieczeństwa:

**Host mode - ryzyka:**
- Kontener ma dostęp do wszystkich portów hosta
- Kontener widzi wszystkie interfejsy sieciowe
- Brak firewall między kontenerem a hostem

**Mitigacje:**
- ✅ IoT Hub działa w **trusted local network** (dom, biuro)
- ✅ Brak exposu do internetu (tylko LAN)
- ✅ Aplikacja nie wymaga sudo/root w kontenerze
- ✅ Readonly filesystem możliwy (security hardening)
- ✅ Hub **musi** być w tej samej sieci co urządzenia (wymaganie funkcjonalne)

**Konkluzja**: Dla lokalnego IoT hub w domowej sieci, brak izolacji sieciowej jest **akceptowalny trade-off** za prostotę i pewność działania.

### 3. Praktyczne argumenty:

**Dlaczego NIE bridge mode:**
```bash
# To jest to co użytkownik musiałby zrobić:
sudo sysctl -w net.ipv4.ip_forward=1
sudo apt-get install smcroute
sudo smcroute -d
sudo iptables -A INPUT -p udp -d 239.255.255.250 --dport 1900 -j ACCEPT
# ...i to może NIE działać na Ubuntu 18.04
```

vs

**Host mode:**
```bash
docker compose up -d  # That's it.
```

**Które użytkownik wybierze?**

### 4. Kompatybilność:

SSDP (Yeelight discovery) używa:
- **Multicast IP**: 239.255.255.250
- **Port**: UDP 1900
- **TTL**: 1-4 (local network only)

Host mode:
- ✅ Multicast routing działa automatycznie
- ✅ TTL jest zachowany
- ✅ Packets wychodzą z interfejsu hosta (tak jak aplikacja natywna)

### 5. User Experience:

Typowy użytkownik AAC IoT Hub to:
- Hobbista automatyki domowej
- Developer testujący lokalne IoT
- Osoba bez zaawansowanej wiedzy o networkingu

**Host mode**: `docker compose up` i działa

**Note:** Modern Docker uses `docker compose` (V2 plugin). For older standalone version, use `docker-compose`.
**Bridge mode**: 30 minut debugowania dlaczego discovery nie działa

### 6. Przyszłościowość:

Jeśli w przyszłości potrzebujemy izolacji, możemy:
1. Dodać opcję env var: `NETWORK_MODE=bridge|host`
2. Dokumentować obie opcje
3. Domyślnie host mode (dla prostoty)

Lub:

```yaml
# Advanced users mogą override
services:
  aac-iot-hub:
    network_mode: "${NETWORK_MODE:-host}"
```

## Implementacja

### docker-compose.yml (finalna wersja):
```yaml
version: '3.8'

services:
  aac-iot-hub:
    build: .
    network_mode: host
    restart: unless-stopped
    environment:
      - LOG_LEVEL=${LOG_LEVEL:-info}
      - API_PORT=${API_PORT:-8765}
    volumes:
      - ./config:/app/config:ro
```

### Dockerfile (networking perspective):
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Kopiowanie dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie aplikacji
COPY . .

# Port jest dokumentacyjny (host mode ignoruje EXPOSE)
# Ale zostawiamy dla clarity
EXPOSE 8765

# Non-root user (security best practice)
RUN useradd -m -u 1000 aac && chown -R aac:aac /app
USER aac

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8765"]
```

### Użycie:

**Prosty start:**
```bash
docker-compose up -d
```

**Custom port (jeśli 8765 zajęty):**
```bash
API_PORT=9765 docker-compose up -d
```

**Sprawdzenie discovery:**
```bash
# API dostępne na hoście
curl http://localhost:8765/api/v1/devices/discover

# Logi discovery
docker-compose logs -f
```

## Konsekwencje

### Pozytywne:
- ✅ **Gwarancja działania multicast** na wszystkich systemach
- ✅ **Zero konfiguracji** sieciowej
- ✅ **Najlepsza kompatybilność** (Ubuntu 18.04+)
- ✅ **Prosty debugging** (kontener = host)
- ✅ **Najlepsza performance** (brak NAT overhead)
- ✅ **WiFi support** out-of-the-box
- ✅ **User-friendly** (działa od razu)

### Negatywne:
- ⚠️ **Brak izolacji sieciowej**
  - **Akceptowalne**: IoT hub w trusted LAN
- ⚠️ **Port 8765 musi być wolny**
  - **Mitigation**: Env var `API_PORT` do zmiany portu
  - **Mitigation**: Dokumentacja alternatywnych portów (9765, 9080)
- ⚠️ **Kontener widzi cały network stack**
  - **Mitigation**: Non-root user w kontenerze
  - **Mitigation**: Readonly filesystem gdzie możliwe

### Ryzyka i mitigacje:

**Ryzyko**: Port conflict (8765 zajęty)
**Mitigation**:
```bash
API_PORT=9765 docker compose up -d
# lub w .env:
API_PORT=9765
```

**Ryzyko**: Security concerns w shared hosting
**Mitigation**:
- Dokumentacja: "NIE używać host mode w shared/untrusted environments"
- Opcjonalna konfiguracja bridge mode dla advanced users
- Security hardening w kontenerze (non-root, readonly FS)

**Ryzyko**: Przyszłe wymaganie izolacji
**Mitigation**:
- Env var switch: `NETWORK_MODE=${NETWORK_MODE:-host}`
- Dokumentacja obu trybów
- Default: host (prostota), optional: bridge (advanced)

## Alternatywna konfiguracja (dla advanced users)

Jeśli użytkownik naprawdę potrzebuje bridge mode (np. multi-service deployment):

```yaml
# docker-compose.bridge.yml
services:
  aac-iot-hub:
    ports:
      - "8765:8765"
    cap_add:
      - NET_ADMIN
    sysctls:
      - net.ipv4.ip_forward=1
```

**WARNING w dokumentacji**:
> Bridge mode może wymagać dodatkowej konfiguracji systemu dla multicast routing.
> Zalecamy host mode dla najprostszego setup. Bridge mode jest przeznaczony dla
> advanced users z specyficznymi wymaganiami bezpieczeństwa.

## Testy

Aby zweryfikować że discovery działa:

```python
# tests/test_discovery.py
import socket
import struct

def test_multicast_send():
    """Test czy możemy wysłać multicast packet"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    message = b"M-SEARCH * HTTP/1.1\r\n..."
    sock.sendto(message, ("239.255.255.250", 1900))
    # Jeśli nie ma exception = multicast działa
```

## Dokumentacja dla użytkowników

### Quick Start:
```bash
docker compose up -d
curl http://localhost:8765/api/v1/devices/discover
```

### Port zajęty?
```bash
API_PORT=9765 docker compose up -d
```

### Debugging:
```bash
# Sprawdź czy kontener działa w host mode
docker inspect aac-iot-hub | grep NetworkMode
# Output: "NetworkMode": "host"

# Sprawdź discovery logs
docker compose logs -f | grep -i discovery
```

## Data
2026-04-25

## Powiązane ADR
- ADR-000: Wybór typu urządzenia IoT (Yeelight + SSDP)
- ADR-001: Konteneryzacja i Deployment
- ADR-003: HTTP API Protocol