# Jak uruchomić sterowanie żarówką Yeelight

## Krok 1: Zainstaluj bibliotekę

```bash
pip install yeelight
```

## Krok 2: Włącz tryb LAN Control w żarówce

⚠️ **WAŻNE: Musisz używać aplikacji Yeelight Classic!**

Opcja **LAN Control** jest dostępna **TYLKO** w aplikacji **[Yeelight Classic](https://home.yeelight.de/en/support/lan-control/)**.

**W aplikacji Xiaomi Home NIE MA tej opcji!** Jeśli masz żarówkę dodaną w Xiaomi Home, musisz zainstalować osobno aplikację Yeelight Classic.

**Kroki:**
1. Pobierz i zainstaluj aplikację **Yeelight Classic** na telefonie (Android/iOS)
2. Dodaj swoją żarówkę do aplikacji Yeelight Classic
3. Kliknij na swoją żarówkę
4. Wejdź w ustawienia żarówki (ikona w prawym dolnym rogu)
5. Znajdź opcję **"Sterowanie poprzez LAN"**
6. **WŁĄCZ** tę opcję! Bez tego skrypt nie zadziała.

## Krok 3: Uruchom skrypt

```bash
python yeelight_toggle.py
```

Skrypt automatycznie znajdzie żarówki w sieci i przełączy stan pierwszej znalezionej.

Żarówka powinna się przełączyć (włączona → wyłączona lub wyłączona → włączona).

## Rozwiązywanie problemów

- **"W sieci nie ma żarówek"** - Upewnij się że:
  - Żarówka jest włączona (podłączona do prądu)
  - Opcja **Sterowanie poprzez LAN** jest włączona w aplikacji Yeelight Classic
  - Komputer i żarówka są w tej samej sieci WiFi

- **"BulbException: Can't connect"** - Tryb LAN Control nie jest włączony lub żarówka nie odpowiada

- **Skrypt nic nie znajduje mimo włączonego LAN Control** - Sprawdź firewall na komputerze (może blokować broadcast UDP)

## Dokumentacja

- [Dokumentacja biblioteki python-yeelight](https://yeelight.readthedocs.io/en/latest/) - pełna dokumentacja z opisem wszystkich dostępnych metod i funkcji