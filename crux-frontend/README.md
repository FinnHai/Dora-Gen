# CRUX Frontend - The Glass Box

Modernes Next.js Frontend für den Neuro-Symbolic Crisis Scenario Generator.

## Design-Konzept

CRUX implementiert das **"Glass Box"** Design-Prinzip: Im Gegensatz zu ChatGPT (Black Box) bietet CRUX **epistemische Klarheit**. Der Nutzer kann zu jedem Zeitpunkt visuell unterscheiden zwischen:

1. **Generativem Vorschlag** (unsicher, probabilistisch, "Neuro") - Farbe: Neural Violet (#7E57C2)
2. **Deterministischem Fakt** (sicher, verifiziert, "Symbolic") - Farbe: Verified Green (#2EA043)

## Technischer Stack

- **Framework:** Next.js 15+ (React 19)
- **Styling:** Tailwind CSS v4
- **UI Components:** Shadcn/UI
- **Graph Visualization:** React Force Graph 2D
- **State Management:** Zustand
- **Typografie:** 
  - Inter (UI & Labels)
  - JetBrains Mono (Daten, Logs, Zeitstempel)

## Design-System

### Farbpalette (Semantic Coloring)

- **Background Layer:**
  - `#090C10` (Void Black): Hintergrund
  - `#161B22` (Panel Grey): Module/Karten

- **The Neural Stream (LLM):**
  - `#7E57C2` (Neural Violet): Vom LLM generierter, noch ungeprüfter Text

- **The Symbolic Truth (Graph):**
  - `#2EA043` (Verified Green): Validierte Fakten und existierende Assets

- **The Intervention (Critic):**
  - `#D29922` (Warning Amber): Critic-Agent Eingriffe ("Soft Correction")
  - `#F85149` (Critical Red): Blockierte Halluzinationen ("Hard Rejection")

## Projektstruktur

```
crux-frontend/
├── app/
│   ├── layout.tsx          # Root Layout mit Fonts
│   ├── page.tsx            # Hauptseite mit 3-Spalten-Layout
│   └── globals.css          # Design-System CSS
├── components/
│   ├── ScenarioComposer.tsx # Panel A: Timeline mit Inject Cards
│   ├── DigitalTwinGraph.tsx # Panel B: Knowledge Graph Visualisierung
│   ├── ForensicTrace.tsx    # Panel C: Critic Logs Stream
│   └── RefinementAnimation.tsx # Refinement-Pattern Animation
├── lib/
│   ├── store.ts             # Zustand State Management
│   └── utils.ts             # Utility Functions
└── components/ui/           # Shadcn/UI Komponenten
```

## Features

### Panel A: Scenario Composer (30% Breite)

- Timeline-Darstellung aller generierten Injects
- Inject Cards mit Status-Indikatoren:
  - Violett: Generierend
  - Gelb: Validierend
  - Grün: Verifiziert
  - Rot: Abgelehnt
- Refinement-History Anzeige
- Asset-Highlighting bei Hover

### Panel B: Digital Twin / Knowledge Graph (50% Breite)

- Interaktiver Force-Directed Graph (WebGL)
- Time-Slider für State-Awareness
- Node-Status Visualisierung:
  - Grün: Online
  - Rot: Kompromittiert
  - Gelb: Degraded
  - Grau (transparent): Offline
- Automatisches Zoom auf selektierte Assets

### Panel C: Forensic Trace & Critic Logs (20% Breite)

- Terminal-ähnlicher Log-Stream
- JSON-Outputs des Critic Agents
- Event-Typen:
  - `[DRAFT]`: Rohe, abgelehnte Injects
  - `[CRITIC]`: Validierungsergebnisse
  - `[REFINED]`: Finale, akzeptierte Injects

## UX-Patterns

### Refinement-Pattern

Visualisierung der Korrektur in 4 Phasen:

1. **Phase 1 (Ghosting):** Text in violetter Farbe
2. **Phase 2 (Detection):** Halluzinierter Teil rot unterstrichen
3. **Phase 3 (Correction):** Falscher Begriff durchgestrichen, korrekter Begriff in Grün
4. **Phase 4 (Finalize):** Text wird weiß, grünes Checkmark-Icon

### Semantic Hovering

- **Hover im Text:** Asset-Namen im Text → Graph zoomt automatisch auf Asset
- **Hover im Graph:** Knoten im Graph → Alle betroffenen Injects werden hervorgehoben

## Setup & Entwicklung

### Voraussetzungen

- Node.js 18+
- npm oder yarn

### Installation

```bash
cd crux-frontend
npm install
```

### Entwicklung

```bash
npm run dev
```

Die App läuft auf `http://localhost:3000`

### Build für Production

```bash
npm run build
npm start
```

## Backend-Integration

Das Frontend kommuniziert mit dem FastAPI Backend (`api_server.py`):

- **API Base URL:** `http://localhost:8000`
- **Endpoints:**
  - `GET /api/graph/nodes` - Graph Nodes
  - `GET /api/graph/links` - Graph Relationships
  - `POST /api/scenario/generate` - Szenario generieren
  - `GET /api/scenario/{scenario_id}/logs` - Critic Logs

## Nächste Schritte

- [ ] DORA-Compliance Dashboard implementieren
- [ ] Export-Funktionalität (PDF mit Zertifikat)
- [ ] Reality Score Berechnung
- [ ] TTP Coverage Matrix (MITRE ATT&CK Heatmap)
- [ ] WebSocket für Live-Updates während Generierung

## Lizenz

[Zu definieren]
