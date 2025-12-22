# 📊 Wissenschaftliches Frontend

Ein spezialisiertes Frontend für statistische Analysen und wissenschaftliche Auswertungen von Experiment-Daten.

## 🚀 Schnellstart

```bash
# Im Hauptverzeichnis des Projekts
streamlit run frontend/scientific_frontend.py
```

Das Frontend öffnet sich automatisch im Browser unter `http://localhost:8501`.

## 📋 Features

### 1. **Experiment-Übersicht**
- Metriken-Karten mit wichtigen Kennzahlen
- Deskriptive Statistiken (Mittelwert, Median, Standardabweichung, etc.)
- Vollständige Rohdaten-Anzeige

### 2. **Statistische Tests**
- **t-Test**: Parametrischer Test für Mittelwertvergleiche
- **Mann-Whitney-U-Test**: Nicht-parametrischer Test für Medianvergleiche
- **Effektgrößen**: Cohen's d für praktische Signifikanz
- Automatische Signifikanz-Bestimmung (p < 0.05)

### 3. **Visualisierungen**
- Boxplots für Vergleich zwischen Legacy und Thesis Mode
- Mittelwerte mit Konfidenzintervallen
- Korrelationsmatrizen
- Zeitreihen-Plots für Experiment-Verlauf

### 4. **Hypothesen-Testing**
- Vordefinierte Hypothesen für häufige Fragestellungen
- Automatische Test-Ausführung
- Interpretation der Ergebnisse

### 5. **Export-Funktionen**
- **LaTeX**: Tabellen und statistische Ergebnisse für wissenschaftliche Publikationen
- **CSV**: Rohdaten und deskriptive Statistiken
- **JSON**: Vollständige Daten mit Metadaten

## 📊 Unterstützte Metriken

Das Frontend analysiert automatisch folgende Metriken (falls in den Daten vorhanden):

- `legacy_duration_seconds` / `thesis_duration_seconds`: Generierungsdauer
- `legacy_hallucinations` / `thesis_hallucinations`: Anzahl Halluzinationen
- `legacy_errors` / `thesis_errors`: Anzahl Fehler
- `legacy_warnings` / `thesis_warnings`: Anzahl Warnungen
- `hallucinations_prevented`: Verhinderte Halluzinationen
- `duration_difference_seconds`: Dauer-Differenz zwischen beiden Modi

## 🔬 Statistische Tests

### t-Test
- **Verwendung**: Vergleich von Mittelwerten zwischen zwei Gruppen (Legacy vs Thesis)
- **Voraussetzungen**: Normalverteilung, Varianzhomogenität
- **Ausgabe**: t-Statistik, p-Wert, Cohen's d, Effektgröße

### Mann-Whitney-U-Test
- **Verwendung**: Nicht-parametrischer Vergleich (keine Normalverteilung erforderlich)
- **Voraussetzungen**: Unabhängige Stichproben
- **Ausgabe**: U-Statistik, p-Wert

## 📈 Hypothesen

Das Frontend testet automatisch folgende Hypothesen:

1. **H1**: Thesis Mode verhindert signifikant mehr Halluzinationen als Legacy Mode
2. **H2**: Thesis Mode benötigt signifikant mehr Zeit als Legacy Mode
3. **H3**: Thesis Mode produziert weniger Fehler als Legacy Mode

## 💾 Datenformat

### Erwartetes CSV-Format

```csv
scenario_id,legacy_injects,legacy_errors,legacy_warnings,legacy_hallucinations,legacy_duration_seconds,thesis_injects,thesis_errors,thesis_warnings,thesis_hallucinations,thesis_duration_seconds,hallucinations_prevented,duration_difference_seconds
SCEN-001,18,0,0,0,333.15,18,0,0,0,617.46,0,284.31
SCEN-002,17,0,0,0,328.14,18,0,0,0,547.96,0,219.82
```

### Minimale Anforderungen

- Mindestens eine Spalte mit `legacy_` Präfix
- Mindestens eine Spalte mit `thesis_` Präfix
- `scenario_id` Spalte für Identifikation

## 🔧 Abhängigkeiten

### Erforderlich
- `streamlit`
- `pandas`
- `numpy`
- `plotly`

### Optional (für statistische Tests)
- `scipy` (wird automatisch verwendet, falls verfügbar)

Installation:
```bash
pip install streamlit pandas numpy plotly scipy
```

## 📝 Verwendung

### Schritt 1: Daten laden

1. **Option A**: CSV-Datei hochladen
   - Klicke auf "Experiment-Daten hochladen" in der Sidebar
   - Wähle eine CSV-Datei mit Experiment-Ergebnissen

2. **Option B**: Standard-Datei laden
   - Klicke auf "Standard-Datei laden"
   - Lädt automatisch `experiment_results.csv` aus dem Hauptverzeichnis

### Schritt 2: Analysen durchführen

- **Übersicht**: Sieh dir die Metriken und deskriptiven Statistiken an
- **Statistische Tests**: Führe t-Tests und Mann-Whitney-U-Tests durch
- **Visualisierungen**: Erstelle Boxplots und Korrelationsmatrizen
- **Hypothesen-Testing**: Teste vordefinierte Hypothesen

### Schritt 3: Ergebnisse exportieren

- **LaTeX**: Für wissenschaftliche Publikationen
- **CSV**: Für weitere Analysen in anderen Tools
- **JSON**: Für programmatische Weiterverarbeitung

## 🎨 Anpassungen

### Eigene Hypothesen hinzufügen

Bearbeite die `hypotheses` Liste in `scientific_frontend.py`:

```python
hypotheses = [
    {
        "id": "H4",
        "text": "Deine Hypothese hier",
        "metric": "deine_metrik",
        "test": "test_typ"
    }
]
```

### Zusätzliche Metriken analysieren

Füge neue Metriken zur `metrics_to_analyze` Liste hinzu:

```python
metrics_to_analyze = [
    ("deine_metrik", "Deine Metrik Label"),
    # ...
]
```

## 📊 Beispiel-Ausgabe

### Deskriptive Statistiken

| Metrik | Mittelwert | Median | Std. Abw. | Min | Max | N |
|--------|------------|--------|-----------|-----|-----|---|
| Legacy Dauer (s) | 345.23 | 333.15 | 25.67 | 323.09 | 389.02 | 6 |
| Thesis Dauer (s) | 631.58 | 617.46 | 120.45 | 521.41 | 826.13 | 6 |

### Statistische Tests

**t-Test:**
- t(10) = -5.234, p = 0.0003 (signifikant, p < 0.05)
- Cohen's d = 1.234 (large effect)

## 🐛 Fehlerbehebung

### "scipy nicht verfügbar"
- Installiere scipy: `pip install scipy`
- Statistische Tests sind ohne scipy nicht verfügbar

### "Nicht genug Datenpunkte"
- Stelle sicher, dass mindestens 2 Datenpunkte pro Gruppe vorhanden sind
- Prüfe, ob die CSV-Datei korrekt geladen wurde

### Visualisierungen werden nicht angezeigt
- Prüfe, ob die erwarteten Spalten in den Daten vorhanden sind
- Stelle sicher, dass plotly installiert ist: `pip install plotly`

## 📚 Wissenschaftliche Best Practices

1. **Signifikanzniveau**: Standardmäßig wird p < 0.05 als signifikant betrachtet
2. **Effektgrößen**: Cohen's d wird automatisch berechnet (small: <0.2, medium: <0.5, large: ≥0.5)
3. **Test-Auswahl**: 
   - Verwende t-Test bei Normalverteilung
   - Verwende Mann-Whitney-U-Test bei nicht-normalverteilten Daten
4. **Multiple Comparisons**: Bei mehreren Tests sollte eine Bonferroni-Korrektur erwogen werden

## 🔗 Weitere Ressourcen

- [Streamlit Dokumentation](https://docs.streamlit.io/)
- [scipy.stats Dokumentation](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Plotly Dokumentation](https://plotly.com/python/)

## 📝 Lizenz

Teil des DORA Scenario Generator Projekts.
