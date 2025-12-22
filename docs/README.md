# CRUX Platform - Wissenschaftliche Dokumentation

**Version:** 2.0.0  
**Letzte Aktualisierung:** 2025-12-20  
**Status:** Produktiv

---

## Abstract

Diese Dokumentation beschreibt die CRUX-Plattform, ein neuro-symbolisches Multi-Agenten-System zur Generierung von DORA-konformen Krisenszenarien für Finanzunternehmen. Die Plattform kombiniert Generative KI (LLMs), Knowledge Graphs (Neo4j) und Vektor-Datenbanken (ChromaDB) zur Erstellung realistischer, logisch konsistenter MSELs (Master Scenario Event Lists).

---

## Inhaltsverzeichnis

### 1. [Einführung & Setup](getting-started/README.md)
   - 1.1 [Installation & Konfiguration](getting-started/SETUP.md)
   - 1.2 [Schnellstart-Anleitung](getting-started/QUICK_START.md)

### 2. [System-Architektur](architecture/README.md)
   - 2.1 [Architektur-Übersicht](architecture/ARCHITECTURE.md)
   - 2.2 [Komponenten-Dokumentation](architecture/DOCUMENTATION.md)

### 3. [Backend-System](backend/README.md)
   - 3.1 [Agenten-Architektur](backend/AGENTEN_DOKUMENTATION.md)
   - 3.2 [Workflow & State Management](backend/BACKEND_WORKFLOW_DOKUMENTATION.md)
   - 3.3 [Backend-API Übersicht](backend/BACKEND_DOKUMENTATION.md)

### 4. [Frontend-System](frontend/README.md)
   - 4.1 [Design-System & UX-Konzept](frontend/DESIGN_IMPLEMENTATION.md)
   - 4.2 [Implementation Summary](frontend/IMPLEMENTATION_SUMMARY.md)
   - 4.3 [Backend-Integration](frontend/BACKEND_INTEGRATION.md)
   - 4.4 [Graph-Visualisierung](frontend/GRAPH_IMPROVEMENTS.md)

### 5. [API & Integration](api/README.md)
   - 5.1 [REST API Dokumentation](api/BACKEND_CONNECTION_COMPLETE.md)

### 6. [Evaluation & Validierung](evaluation/README.md)
   - 6.1 [Evaluations-Methodik](evaluation/EVALUATION_METHODOLOGY.md)
   - 6.2 [Evaluations-Ergebnisse](evaluation/EVALUATION_SUMMARY.md)

### 7. [Benutzer-Anleitungen](user-guides/README.md)
   - 7.1 [Hauptanleitung](user-guides/ANWENDUNGSANLEITUNG.md)
   - 7.2 [Frontend-Bedienung](user-guides/FRONTEND.md)
   - 7.3 [Crisis Cockpit](user-guides/CRISIS_COCKPIT_README.md)

### 8. [Thesis-Dokumentation](thesis/THESIS_DOCUMENTATION.md)

---

## Dokumentations-Struktur

### Kategorisierung

Die Dokumentation ist nach folgenden Kategorien strukturiert:

#### **Theoretische Grundlagen**
- Architektur-Dokumentationen
- Design-Prinzipien
- Konzeptuelle Modelle

#### **Technische Implementierung**
- Backend-System (Agenten, Workflow, State Management)
- Frontend-System (Design, Implementation, Integration)
- API & Integration

#### **Praktische Anwendung**
- Setup & Installation
- Benutzer-Anleitungen
- Troubleshooting

#### **Wissenschaftliche Evaluation**
- Evaluations-Methodik
- Evaluations-Ergebnisse
- Metriken & Analysen

---

## Dokumentations-Standards

### Formatierung

- **Sprache:** Deutsch (wissenschaftlich)
- **Struktur:** Hierarchisch, nummeriert
- **Referenzen:** Vollständige Quellenangaben
- **Code-Beispiele:** Vollständig, kommentiert
- **Diagramme:** Aktuell, beschriftet

### Metadaten

Jede Dokumentation enthält:
- **Version:** Versionsnummer
- **Letzte Aktualisierung:** Datum
- **Autor:** Verantwortlicher
- **Status:** Entwicklungsstatus

### Qualitätskriterien

- ✅ Vollständigkeit: Alle relevanten Aspekte dokumentiert
- ✅ Aktualität: Dokumentation entspricht Code-Stand
- ✅ Verständlichkeit: Klare Sprache, strukturiert
- ✅ Nachvollziehbarkeit: Code-Beispiele, Diagramme
- ✅ Wissenschaftlichkeit: Theoretische Fundierung, Methodik

---

## Schnellzugriff nach Zielgruppe

### Entwickler
1. [Setup](getting-started/SETUP.md) → Projekt einrichten
2. [Architektur](architecture/ARCHITECTURE.md) → System verstehen
3. [Backend Workflow](backend/BACKEND_WORKFLOW_DOKUMENTATION.md) → Workflow verstehen
4. [Agenten](backend/AGENTEN_DOKUMENTATION.md) → Agenten verstehen

### Wissenschaftler / Thesis
1. [Thesis-Dokumentation](thesis/THESIS_DOCUMENTATION.md) → Thesis-relevante Infos
2. [Architektur](architecture/ARCHITECTURE.md) → System-Architektur
3. [Evaluation](evaluation/EVALUATION_SUMMARY.md) → Evaluations-Ergebnisse
4. [Agenten-System](backend/AGENTEN_DOKUMENTATION.md) → Multi-Agenten-Architektur

### Benutzer
1. [Quick Start](getting-started/QUICK_START.md) → Schnellstart
2. [Anwendungsanleitung](user-guides/ANWENDUNGSANLEITUNG.md) → Vollständige Anleitung
3. [Frontend](user-guides/FRONTEND.md) → Frontend-Bedienung

### System-Administratoren
1. [Setup](getting-started/SETUP.md) → Installation
2. [API-Dokumentation](api/BACKEND_CONNECTION_COMPLETE.md) → API-Endpunkte
3. [Troubleshooting](frontend/TROUBLESHOOTING.md) → Problembehebung

---

## Dokumentations-Hierarchie

```
docs/
├── README.md (Diese Datei)
├── getting-started/          # Setup & Installation
│   ├── README.md
│   ├── SETUP.md
│   └── QUICK_START.md
├── architecture/             # System-Architektur
│   ├── README.md
│   ├── ARCHITECTURE.md
│   └── DOCUMENTATION.md
├── backend/                  # Backend-System
│   ├── README.md
│   ├── AGENTEN_DOKUMENTATION.md
│   ├── BACKEND_WORKFLOW_DOKUMENTATION.md
│   └── BACKEND_DOKUMENTATION.md
├── frontend/                 # Frontend-System
│   ├── README.md
│   ├── DESIGN_IMPLEMENTATION.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── BACKEND_INTEGRATION.md
│   ├── GRAPH_IMPROVEMENTS.md
│   ├── QUICK_START.md
│   └── TROUBLESHOOTING.md
├── api/                     # API & Integration
│   ├── README.md
│   └── BACKEND_CONNECTION_COMPLETE.md
├── evaluation/              # Evaluation & Validierung
│   ├── README.md
│   ├── EVALUATION_METHODOLOGY.md
│   └── EVALUATION_SUMMARY.md
├── user-guides/             # Benutzer-Anleitungen
│   ├── README.md
│   ├── ANWENDUNGSANLEITUNG.md
│   ├── FRONTEND.md
│   └── CRISIS_COCKPIT_README.md
├── thesis/                  # Thesis-Dokumentation
│   └── THESIS_DOCUMENTATION.md
└── development/             # Entwicklung & Deployment
    └── DEPLOY_TO_GITHUB.md
```

---

## Wissenschaftliche Referenzen

### Konzepte

- **Neuro-Symbolische KI:** Kombination von generativen LLMs mit symbolischen Validierungsregeln
- **Multi-Agenten-Systeme:** Orchestrierung spezialisierter Agenten (LangGraph)
- **Knowledge Graphs:** Neo4j für State Management und Abhängigkeitsmodellierung
- **DORA Compliance:** Digital Operational Resilience Act (EU-Verordnung)

### Technologien

- **LangGraph:** Workflow-Orchestrierung
- **OpenAI GPT-4o:** Generative KI für Inhaltsgenerierung
- **Neo4j:** Graph-Datenbank für State Management
- **ChromaDB:** Vektor-Datenbank für TTP-Retrieval
- **Next.js:** Frontend-Framework (React)
- **FastAPI:** REST API Framework

---

## Versionshistorie

### Version 2.0.0 (2025-12-20)
- Umstrukturierung der Dokumentation
- Wissenschaftliche Formatierung
- Vollständige Kategorisierung
- Erweiterte Metadaten

### Version 1.0.0 (Initial)
- Erste Dokumentations-Version
- Basis-Struktur

---

## Kontakt & Support

Bei Fragen zur Dokumentation oder technischen Problemen:
- **Projekt-Repository:** Siehe Haupt-README.md
- **Issues:** GitHub Issues (falls verfügbar)
- **Dokumentation:** Diese Datei und Unterkategorien

---

**Dokumentations-Maintainer:** CRUX Development Team  
**Lizenz:** Siehe Haupt-README.md  
**Stand:** 2025-12-20
