# Tools für Forensic-Trace-Analyse

Diese Dokumentation beschreibt verschiedene Tools und Frameworks, die für die Analyse von `forensic_trace.jsonl`-Daten verwendet werden können.

## 1. Streamlit (Empfohlen für Custom Tools) ⭐

**Status:** ✅ **Aktuell implementiert** (`scientific_frontend.py`)

Das beste Tool, um aus Python-Skripten eine echte Web-App zu machen.

* **Beschreibung:** Open-Source Python-Framework. Der Analyse-Code wird in eine Datei (`scientific_frontend.py`) integriert, und Streamlit erstellt automatisch ein interaktives Dashboard mit File-Uploader.
* **Warum hier:** Die spezifische "Refine-Loop"-Logik (z.B. *Zähle nur, wenn `refine_count > 0*`) kann direkt programmiert werden. Interaktive Filterung möglich (z.B. "Zeige nur Szenario 3").
* **Implementierte Algorithmen:** 
  - Refinement-Heatmaps
  - Text-Mining der Warnungen
  - Fehler-Klassifizierung
  - 30 verschiedene Analysen (Zeitanalyse, NLP, Performance-Metriken)

**Start:** `streamlit run frontend/scientific_frontend.py`

---

## 2. Google Colab / JupyterLab (Analysten-Standard)

Die direkte Umgebung für Data Science Code.

* **Beschreibung:** Interaktives Notizbuch im Browser. Datei hochladen und Code-Blöcke nacheinander ausführen.
* **Warum hier:** Perfekt für explorative Deep-Dives. Algorithmen können "on the fly" geändert werden (z.B. "Jetzt filtere mal nach MITRE-Fehlern") mit sofortigem Ergebnis.
* **Mögliche Algorithmen:** 
  - Zeitreihenanalyse (Fatigue)
  - Statistische Tests (Acceptance Rate)
  - Komplexe Plots (Seaborn/Matplotlib)

**Vorteil:** Keine Installation, läuft im Browser

---

## 3. ELK Stack (Elasticsearch, Logstash, Kibana) (Log-Profi)

Der Industriestandard für Log-Analyse, wenn es "Enterprise" sein soll.

* **Beschreibung:** JSONL-Datei in Elasticsearch importieren und Dashboards in Kibana erstellen.
* **Warum hier:** Extrem stark bei großen Datenmengen und Volltextsuche. Sofortige Suche nach "Hallucination" in Millionen von Zeilen möglich.
* **Mögliche Algorithmen:** 
  - Anomalie-Erkennung (Machine Learning Features von Elastic)
  - Zeitreihen-Visualisierung
  - Geo-Mapping (falls relevant)

**Vorteil:** Skalierbar für große Datenmengen

---

## 4. KNIME (Visueller "No-Code" Ansatz)

Wenn du nicht programmieren, aber komplexe Workflows bauen willst.

* **Beschreibung:** Knoten (z.B. "File Reader" -> "JSON Path" -> "Group By" -> "Bar Chart") auf eine Leinwand ziehen und verbinden.
* **Warum hier:** Sehr gut nachvollziehbar. Der "Refine-Algorithmus" kann visuell nachgebaut werden (filtern, joinen, aggregieren) ohne Code.
* **Mögliche Algorithmen:** 
  - Clustering (K-Means auf Fehler-Vektoren)
  - Decision Trees (Was führt zum Abbruch?)
  - Korrelationsmatrizen

**Vorteil:** Visueller Workflow-Builder

---

## 5. Julius AI / ChatGPT Advanced Data Analysis (KI-Assistent)

Der schnellste Weg ohne Setup.

* **Beschreibung:** Datei hochladen und dem Bot in natürlicher Sprache Anweisungen geben: "Visualisiere die Refine-Loops als Heatmap".
* **Warum hier:** Kein Setup nötig. Die KI schreibt und führt den Python-Code für die Algorithmen selbstständig aus.
* **Mögliche Algorithmen:** Alles, was beschrieben werden kann (z.B. "Finde Muster in den Ablehnungen").

**Vorteil:** Schnell, keine Installation

---

## Empfehlung

**Für wiederverwendbare Tools:** **Streamlit** (bereits implementiert)  
**Für explorative Analysen:** **JupyterLab / Google Colab**  
**Für Enterprise-Skalierung:** **ELK Stack**  
**Für visuelle Workflows:** **KNIME**  
**Für schnelle Prototypen:** **Julius AI / ChatGPT**

---

## Aktuelle Implementierung

Das aktuelle `scientific_frontend.py` verwendet **Streamlit** und bietet:

- ✅ File-Upload für JSONL-Dateien
- ✅ 30 verschiedene Analysen in 3 Kategorien
- ✅ Interaktive Visualisierungen (Plotly)
- ✅ Tab-basierte Navigation
- ✅ Dashboard-Übersicht mit Key Metrics
- ✅ Grid-Layout für bessere Übersichtlichkeit

**Nächste Schritte:**
- Weitere Analysen hinzufügen
- Export-Funktionen für Ergebnisse
- Vergleich zwischen verschiedenen Datensätzen
- Automatische Report-Generierung
