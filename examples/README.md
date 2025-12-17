# Examples

Dieses Verzeichnis enthält Beispiel-Szenarien und Demo-Code.

## Dateien

- **`demo_scenarios.py`** - Vordefinierte Demo-Szenarien
  - Schnellstart-Beispiele
  - Test-Szenarien
  - Vorkonfigurierte Konfigurationen

## Verwendung

```python
from examples.demo_scenarios import get_available_demo_scenarios, load_demo_scenario

# Verfügbare Demo-Szenarien abrufen
scenarios = get_available_demo_scenarios()

# Demo-Szenario laden
scenario = load_demo_scenario("ransomware_basic")
```

## Hinweis

Diese Beispiele sind für schnelles Testen und Demonstration gedacht.
