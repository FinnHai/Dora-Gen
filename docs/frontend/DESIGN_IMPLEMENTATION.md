# CRUX Frontend - Design-System & Implementierungs-Dokumentation

## Übersicht

Diese Dokumentation beschreibt die vollständige Implementierung des CRUX Frontends gemäß dem Design-Konzept "The Glass Box". Das Frontend wurde als modernes Next.js-Projekt mit TypeScript, Tailwind CSS v4 und Shadcn/UI umgesetzt.

**Erstellt:** Dezember 2024  
**Status:** Implementiert und funktionsfähig

---

## 1. Design-Philosophie: "The Glass Box"

### Kern-Metapher

Im Gegensatz zu ChatGPT (Black Box) ist CRUX eine **"Glass Box"**. Das Designziel ist **epistemische Klarheit** - der Nutzer muss zu jedem Zeitpunkt visuell unterscheiden können zwischen:

1. **Generativem Vorschlag** (unsicher, probabilistisch, "Neuro")
   - Farbe: Neural Violet (#7E57C2)
   - Status: Generierend, noch ungeprüft

2. **Deterministischem Fakt** (sicher, verifiziert, "Symbolic")
   - Farbe: Verified Green (#2EA043)
   - Status: Verifiziert, validiert gegen Knowledge Graph

### Visuelle Sprache: "Critical Infrastructure Aesthetic"

Das Design orientiert sich an professionellen SOC (Security Operations Center) Dashboards und IDEs (Entwicklungsumgebungen), nicht an Consumer-Chatbots. Es vermittelt:
- Präzision
- Stabilität
- Kontrolle
- Transparenz

---

## 2. Design-System: Visuelle Spezifikationen

### 2.1 Farbpalette (Semantic Coloring)

Farben werden nicht zur Dekoration verwendet, sondern zur **semantischen Codierung der Informationsart**.

#### Background Layer
- `#090C10` (Void Black): Hintergrund für maximale Kontraste in dunklen Räumen
- `#161B22` (Panel Grey): Hintergrund für Module/Karten

#### The Neural Stream (LLM)
- `#7E57C2` (Neural Violet): Kennzeichnet vom LLM generierten, noch ungeprüften Text

#### The Symbolic Truth (Graph)
- `#2EA043` (Verified Green): Kennzeichnet validierte Fakten und existierende Assets im Digital Twin

#### The Intervention (Critic)
- `#D29922` (Warning Amber): Zeigt an, wo der Critic-Agent eingegriffen hat ("Soft Correction")
- `#F85149` (Critical Red): Zeigt blockierte Halluzinationen an ("Hard Rejection")

#### Neutrale Farben
- `#E6EDF3`: Primärer Text (hell für dunklen Hintergrund)
- `#8B949E`: Sekundärer Text (Labels, Metadaten)
- `#30363D`: Borders, Trennlinien

### 2.2 Typografie

#### Interface & Labels
- **Schriftart:** Inter (Variable Font)
- **Begründung:** Hohe Lesbarkeit bei kleinen Schriftgrößen
- **Gewichte:** 300, 400, 500, 600, 700

#### Daten, Logs & Injects
- **Schriftart:** JetBrains Mono (Monospace)
- **Begründung:** Zwingend erforderlich, um Tabellen und Zeitstempel (`T+00:15:00`) vertikal bündig darzustellen
- **Gewichte:** 400, 500, 600

**Implementierung:** Die Fonts werden über Next.js Fonts (`next/font/google`) geladen und als CSS-Variablen (`--font-inter`, `--font-jetbrains-mono`) bereitgestellt.

---

## 3. Informationsarchitektur: 3-Spalten-Layout

Das Layout bildet den Datenfluss von links nach rechts ab: **Input → Verarbeitung → Evidenz**

### Panel A: Scenario Composer (Links, 30% Breite)

**Funktion:** Hier entsteht das Narrativ.

**Darstellung:**
- Kein Chat-Verlauf, sondern eine **Timeline**
- Jeder Absatz des Szenarios ist eine eigene Karte ("Inject")

**UI-Element: "Inject Cards"**
- **Header:**
  - Inject ID (z.B. `#04`)
  - Zeitstempel (`T+02:00`)
  - Status-Indikator (kleiner Punkt rechts oben)
    - Violett = Generierend
    - Gelb = Validierend
    - Grün = Verifiziert
    - Rot = Abgelehnt

- **Body:**
  - Szenario-Text
  - Source → Target
  - Modality
  - Affected Assets (als Tags)

- **Refinement-History:**
  - Zeigt Korrekturen an (Original → Korrigiert)
  - Fehler-Details bei abgelehnten Injects

**Interaktion:**
- Klick auf Inject-Karte → Panel B und C fokussieren sich auf diesen Zeitschritt
- Hover über Asset-Tags → Graph zoomt auf entsprechendes Asset

**Komponente:** `components/ScenarioComposer.tsx`

### Panel B: Digital Twin / Knowledge Graph (Mitte, 50% Breite)

**Funktion:** Visuelle Darstellung der "Ground Truth"

**Technik:**
- Interaktiver WebGL-Graph (React Force Graph 2D)
- Force-Directed Layout für natürliche Netzwerkvisualisierung

**State-Awareness:**
- Der Graph ist nicht statisch
- **Time-Slider** Komponente am unteren Rand
- Funktion: Zieht man den Slider auf `T+00:30`, zeigt der Graph den Zustand des Netzwerks zu diesem Zeitpunkt

**Visualisierung:**
- **Node-Status:**
  - Grün (`#2EA043`): Online
  - Rot (`#F85149`): Kompromittiert
  - Gelb (`#D29922`): Degraded
  - Grau (`#8B949E`, transparent): Offline

- **Node-Highlighting:**
  - Selektierte Assets werden hervorgehoben (Neural Violet)
  - Automatisches Zoom bei Selektion

**Verbindung zum Text:**
- Wenn im Panel A der Text "Firewall FW-01" steht, wird der entsprechende Knoten im Panel B hervorgehoben
- Bidirektionale Verlinkung: Hover im Text → Graph zoomt, Hover im Graph → Text-Injects werden hervorgehoben

**Komponente:** `components/DigitalTwinGraph.tsx`

### Panel C: Forensic Trace & Critic Logs (Rechts, 20% Breite)

**Funktion:** Transparenz der Agenten-Entscheidungen ("Warum wurde das geändert?")

**Darstellung:**
- Terminal-ähnlicher Feed ("Log Stream")
- Monospace-Schriftart (JetBrains Mono)

**Inhalt:**
- JSON-Outputs des `Critic Agents`
- Event-Typen:
  - `[DRAFT]`: Rohe, abgelehnte Injects (Neural Violet)
  - `[CRITIC]`: Validierungsergebnisse (Warning Amber)
  - `[REFINED]`: Finale, akzeptierte Injects (Verified Green)

**Log-Format:**
```
[CRITIC] Scanning Inject #03...
[DETECTED] Asset 'SRV-Backup-99' not found in Graph.
[ACTION] Replacing with 'SRV-Backup-01' (Graph Match Score: 0.92).
[RESULT] Logic Constraint Satisfied.
```

**Komponente:** `components/ForensicTrace.tsx`

---

## 4. UX-Patterns & Interaktionen

### 4.1 Das "Refinement"-Pattern (Visualisierung der Korrektur)

Dies ist das wichtigste UX-Element, um den Mehrwert der Thesis zu zeigen. Wenn das LLM halluziniert und der Critic es korrigiert, darf der falsche Text nicht einfach verschwinden.

**4-Phasen-Animation:**

1. **Phase 1 (Ghosting):**
   - Das LLM schreibt den Text in violetter Farbe (`#7E57C2`)
   - Status: "Generierend"

2. **Phase 2 (Detection):**
   - Der halluzinierte Teil (z.B. eine falsche IP) wird rot unterstrichen (`#F85149`)
   - Status: "Validierend"

3. **Phase 3 (Correction):**
   - Animation streicht den falschen Begriff durch
   - Ersetzt ihn durch den korrekten Begriff aus dem Graphen (in Grün `#2EA043`)
   - Zeigt Fehler-Details an

4. **Phase 4 (Finalize):**
   - Der gesamte Text färbt sich weiß (neutral)
   - Ein grünes Checkmark-Icon erscheint am Rand
   - Status: "Verifiziert"

**Psychologischer Effekt:**
Der Nutzer sieht dem System beim "Denken" und "Korrigieren" zu. Das baut massives Vertrauen auf.

**Komponente:** `components/RefinementAnimation.tsx`

### 4.2 Semantic Hovering (Bidirektionale Verlinkung)

**Hover im Text:**
- Bewegt der Mauszeiger über ein Asset im Text ("Core Switch")
- Die Kamera im 3D-Graphen zoomt automatisch auf dieses Asset
- Der entsprechende Knoten wird hervorgehoben (Neural Violet)

**Hover im Graph:**
- Bewegt der Mauszeiger über einen Knoten im Graphen
- Alle Injects in der Timeline werden hervorgehoben, die dieses Asset betreffen
- Asset-Tags in den Inject-Cards werden ebenfalls hervorgehoben

**Implementierung:**
- Zustand wird über Zustand Store synchronisiert
- `hoveredAsset` und `highlightedNodeId` werden bidirektional aktualisiert

---

## 5. Technischer Stack

### 5.1 Frontend-Framework

**Next.js 15+ (React 19)**
- App Router für moderne Routing-Struktur
- Server-Side Rendering für schnelle Ladezeiten großer Reports
- TypeScript für Type-Safety

### 5.2 Styling

**Tailwind CSS v4**
- Utility-First CSS Framework
- Dark Theme Support
- Custom CSS-Variablen für Design-System

**Shadcn/UI**
- Professionelle UI-Komponenten
- Basiert auf Radix UI (Accessible)
- Tailwind CSS Integration
- Verwendete Komponenten:
  - Card
  - Accordion
  - Dialog
  - Button
  - Slider

### 5.3 Graph-Visualisierung

**React Force Graph 2D**
- Basierend auf Three.js
- Hochperformante Netzwerkvisualisierung im Browser
- Force-Directed Layout Algorithmus
- Interaktive Node/Link Manipulation

### 5.4 State Management

**Zustand**
- Leichtgewichtige State-Management-Lösung
- Notwendig für Sync zwischen Zeitleiste (Panel A) und Graph-Zustand (Panel B)
- Reaktive Updates ohne Verzögerung

### 5.5 Typografie

**Next.js Fonts (`next/font/google`)**
- Optimierte Font-Loading
- Automatische Font-Subsetting
- CSS-Variablen für Font-Familien

---

## 6. Projektstruktur

```
crux-frontend/
├── app/
│   ├── layout.tsx          # Root Layout mit Fonts
│   ├── page.tsx            # Hauptseite mit 3-Spalten-Layout
│   └── globals.css          # Design-System CSS
├── components/
│   ├── ScenarioComposer.tsx     # Panel A: Timeline mit Inject Cards
│   ├── DigitalTwinGraph.tsx     # Panel B: Knowledge Graph Visualisierung
│   ├── ForensicTrace.tsx        # Panel C: Critic Logs Stream
│   ├── RefinementAnimation.tsx  # Refinement-Pattern Animation
│   └── ui/                      # Shadcn/UI Komponenten
│       ├── card.tsx
│       ├── accordion.tsx
│       ├── dialog.tsx
│       ├── button.tsx
│       └── slider.tsx
├── lib/
│   ├── store.ts             # Zustand State Management
│   └── utils.ts              # Utility Functions (cn helper)
├── components.json           # Shadcn/UI Konfiguration
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript Konfiguration
├── README.md                # Projekt-README
└── DESIGN_IMPLEMENTATION.md # Diese Dokumentation
```

---

## 7. State Management: Zustand Store

### 7.1 Store-Struktur

**Datei:** `lib/store.ts`

**State-Interfaces:**

```typescript
interface Inject {
  inject_id: string;
  time_offset: string;
  content: string;
  status: 'generating' | 'validating' | 'verified' | 'rejected';
  phase: string;
  source: string;
  target: string;
  modality: string;
  mitre_id?: string;
  affected_assets: string[];
  refinement_history?: {
    original: string;
    corrected: string;
    errors: string[];
  }[];
}

interface GraphNode {
  id: string;
  label: string;
  type: 'server' | 'database' | 'network' | 'workstation';
  status: 'online' | 'offline' | 'compromised' | 'degraded';
  x?: number;
  y?: number;
  z?: number;
}

interface GraphLink {
  source: string;
  target: string;
  type: string;
}

interface CriticLog {
  timestamp: string;
  inject_id: string;
  event_type: 'DRAFT' | 'CRITIC' | 'REFINED';
  message: string;
  details?: {
    validation?: {
      is_valid: boolean;
      errors: string[];
      warnings: string[];
    };
  };
}
```

**Store-Actions:**
- `setInjects()`: Setzt alle Injects
- `addInject()`: Fügt neues Inject hinzu
- `updateInject()`: Aktualisiert bestehendes Inject
- `selectInject()`: Selektiert Inject (fokussiert Graph)
- `setGraphData()`: Setzt Graph-Nodes und Links
- `setGraphTimeOffset()`: Ändert Zeitpunkt im Graph
- `setHoveredAsset()`: Setzt gehoverte Asset-ID (für Semantic Hovering)
- `setHighlightedNode()`: Setzt hervorgehobenen Graph-Knoten
- `addCriticLog()`: Fügt Critic-Log hinzu
- `setCriticLogs()`: Setzt alle Critic-Logs

---

## 8. Komponenten-Details

### 8.1 ScenarioComposer

**Datei:** `components/ScenarioComposer.tsx`

**Funktionalität:**
- Rendert Timeline aller generierten Injects
- Inject Cards mit Status-Indikatoren
- Refinement-History Anzeige
- Asset-Highlighting bei Hover
- Selektion von Injects (fokussiert Graph)

**Props:** Keine (verwendet Zustand Store)

**Key Features:**
- Status-basierte Farbcodierung
- Klickbare Cards für Selektion
- Asset-Tags mit Hover-Effekt
- Leere State-Anzeige

### 8.2 DigitalTwinGraph

**Datei:** `components/DigitalTwinGraph.tsx`

**Funktionalität:**
- Rendert interaktiven Force-Directed Graph
- Time-Slider für State-Awareness
- Node-Status Visualisierung
- Automatisches Zoom auf selektierte Assets
- Hover-Handling für Semantic Hovering

**Props:** Keine (verwendet Zustand Store)

**Key Features:**
- Dynamisches Filtern von Nodes basierend auf Zeitpunkt
- Status-basierte Node-Farben
- Transparenz für offline Nodes
- Automatisches Zentrieren bei Selektion

**Technische Details:**
- Verwendet `react-force-graph-2d` (dynamisch importiert für SSR-Kompatibilität)
- Graph-Daten werden aus Store geladen
- Time-Offset wird in Minuten konvertiert für Slider

### 8.3 ForensicTrace

**Datei:** `components/ForensicTrace.tsx`

**Funktionalität:**
- Rendert Terminal-ähnlichen Log-Stream
- Event-Typ-basierte Farbcodierung
- Validierungsfehler und Warnungen Anzeige
- Timestamp-Formatierung

**Props:** Keine (verwendet Zustand Store)

**Key Features:**
- Monospace-Schriftart für Alignment
- Event-Typ Prefixes (`[DRAFT]`, `[CRITIC]`, `[REFINED]`)
- Fehler/Warnungen als strukturierte Liste
- Scrollbar für lange Log-Listen

### 8.4 RefinementAnimation

**Datei:** `components/RefinementAnimation.tsx`

**Funktionalität:**
- Animiert Refinement-Prozess in 4 Phasen
- Zeigt Original → Korrektur Übergang
- Fehler-Details Anzeige

**Props:**
- `original`: Originaler Text
- `corrected`: Korrigierter Text
- `errors`: Array von Fehler-Meldungen
- `onComplete`: Callback nach Animation

**Key Features:**
- Phasen-basierte Animation (Ghosting → Detection → Correction → Finalize)
- CSS-Transitions für smooth Übergänge
- Checkmark-Icon bei Finalisierung

---

## 9. Backend-Integration: REST API

### 9.1 API Server

**Datei:** `api_server.py` (im Hauptverzeichnis)

**Framework:** FastAPI

**Endpoints:**

#### `GET /`
Health check endpoint

#### `GET /api/graph/nodes`
Holt alle Nodes aus dem Knowledge Graph

**Response:**
```json
{
  "nodes": [
    {
      "id": "SRV-CORE-001",
      "label": "Core Server 001",
      "type": "server",
      "status": "online"
    }
  ]
}
```

#### `GET /api/graph/links`
Holt alle Relationships aus dem Knowledge Graph

**Response:**
```json
{
  "links": [
    {
      "source": "SRV-APP-001",
      "target": "DB-PROD-01",
      "type": "USES"
    }
  ]
}
```

#### `POST /api/scenario/generate`
Generiert ein neues Szenario

**Request:**
```json
{
  "scenario_type": "ransomware_double_extortion",
  "num_injects": 10
}
```

**Response:**
```json
{
  "scenario_id": "SCEN-001",
  "injects": [
    {
      "inject_id": "INJ-001",
      "time_offset": "T+00:00",
      "content": "...",
      "status": "verified",
      "phase": "SUSPICIOUS_ACTIVITY",
      "source": "Red Team",
      "target": "Blue Team",
      "modality": "SIEM Alert",
      "mitre_id": "T1078",
      "affected_assets": ["SRV-001"],
      "refinement_history": null
    }
  ]
}
```

#### `GET /api/scenario/{scenario_id}/logs`
Holt Critic-Logs für ein Szenario

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2025-12-20T10:33:00",
      "inject_id": "INJ-001",
      "event_type": "CRITIC",
      "message": "Scanning Inject #01...",
      "details": {
        "validation": {
          "is_valid": true,
          "errors": [],
          "warnings": []
        }
      }
    }
  ]
}
```

### 9.2 CORS-Konfiguration

Der API-Server ist für Frontend-Zugriff konfiguriert:
- Erlaubte Origins: `http://localhost:3000`, `http://localhost:3001`
- Credentials: Erlaubt
- Methods: Alle
- Headers: Alle

---

## 10. CSS-Architektur

### 10.1 Design-System Variablen

**Datei:** `app/globals.css`

**CSS-Variablen:**

```css
:root {
  /* CRUX Background Colors */
  --background: #090C10; /* Void Black */
  --foreground: #E6EDF3; /* Light text */
  
  /* CRUX Panel Colors */
  --card: #161B22; /* Panel Grey */
  
  /* CRUX Semantic Colors */
  --neural-violet: #7E57C2;
  --verified-green: #2EA043;
  --warning-amber: #D29922;
  --critical-red: #F85149;
  
  /* Typography */
  --font-inter: var(--font-inter);
  --font-jetbrains-mono: var(--font-jetbrains-mono);
}
```

### 10.2 Utility Classes

**Semantic Color Classes:**
- `.text-neural`: Neural Violet Text
- `.text-verified`: Verified Green Text
- `.text-warning`: Warning Amber Text
- `.text-critical`: Critical Red Text
- `.bg-panel`: Panel Grey Background
- `.bg-void`: Void Black Background

**Typography Classes:**
- `.font-ui`: Inter Font (für UI)
- `.font-data`: JetBrains Mono Font (für Daten)

### 10.3 Scrollbar Styling

Custom Scrollbar für Dark Theme:
- Track: Void Black
- Thumb: Panel Grey Border Color
- Hover: Lighter Grey

---

## 11. Implementierungs-Highlights

### 11.1 Epistemische Klarheit

Das Frontend macht die Unterscheidung zwischen generativen Vorschlägen und deterministischen Fakten visuell explizit:

- **Violett** = Unsicher, probabilistisch (LLM-Output)
- **Grün** = Sicher, verifiziert (Graph-Validierung)
- **Gelb** = Warnung, Intervention (Critic-Korrektur)
- **Rot** = Fehler, Blockierung (Hard Rejection)

### 11.2 Transparenz durch Forensic Trace

Alle Agenten-Entscheidungen werden im Forensic Trace Panel sichtbar:
- Welche Injects wurden abgelehnt?
- Warum wurden sie abgelehnt?
- Wie wurden sie korrigiert?
- Welche Validierungsfehler traten auf?

### 11.3 State-Awareness im Graph

Der Graph ist nicht statisch, sondern zeigt den Systemzustand zu einem bestimmten Zeitpunkt:
- Time-Slider ermöglicht Navigation durch die Timeline
- Nodes ändern Status basierend auf Injects
- Kompromittierte Assets pulsieren rot
- Offline-Systeme werden transparent dargestellt

### 11.4 Bidirektionale Verlinkung

Semantic Hovering verbindet Text und Graph:
- Hover über Asset im Text → Graph zoomt
- Hover über Node im Graph → Text-Injects werden hervorgehoben
- Synchronisation über Zustand Store

---

## 12. Setup & Entwicklung

### 12.1 Voraussetzungen

- Node.js 18+
- npm oder yarn

### 12.2 Installation

```bash
cd crux-frontend
npm install
```

### 12.3 Entwicklung

```bash
npm run dev
```

Die App läuft auf `http://localhost:3000`

### 12.4 Build für Production

```bash
npm run build
npm start
```

### 12.5 Backend starten

```bash
# Im Hauptverzeichnis
python api_server.py
```

Die API läuft auf `http://localhost:8000`

---

## 13. Bekannte Probleme & Lösungen

### 13.1 CSS @import Fehler

**Problem:** `@import` Regeln müssen am Anfang der CSS-Datei stehen.

**Lösung:** Google Fonts werden über Next.js Fonts geladen, nicht über CSS `@import`. Die redundanten `@import`-Regeln wurden entfernt.

### 13.2 SSR-Kompatibilität für React Force Graph

**Problem:** React Force Graph verwendet WebGL, das nur im Browser verfügbar ist.

**Lösung:** Dynamischer Import mit `dynamic(() => import('react-force-graph-2d'), { ssr: false })`

### 13.3 FastAPI nicht installiert

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Lösung:** FastAPI muss installiert werden:
```bash
pip install fastapi uvicorn[standard]
```

---

## 14. Nächste Schritte / Offene TODOs

### 14.1 DORA-Compliance Dashboard

**Status:** Noch nicht implementiert

**Geplante Features:**
- Reality Score Tachometer (0-100%)
- TTP Coverage Matrix (MITRE ATT&CK Heatmap)
- Export-Funktionalität mit kryptografisch signiertem Zertifikat

### 14.2 API-Integration

**Status:** Backend vorhanden, Frontend-Integration noch ausstehend

**Geplante Features:**
- Fetch von Graph-Daten beim Laden
- Szenario-Generierung über API
- Live-Updates während Generierung (WebSocket)

### 14.3 Refinement-Animation Integration

**Status:** Komponente vorhanden, noch nicht in Inject Cards integriert

**Geplante Features:**
- Automatische Animation bei Refinement-Events
- Integration in ScenarioComposer

---

## 15. Design-Entscheidungen & Begründungen

### 15.1 Warum Next.js statt Streamlit?

**Begründung:**
- Modernes, professionelles Frontend-Framework
- Bessere Performance für große Datenmengen
- Flexibleres Design-System
- Server-Side Rendering für schnelle Ladezeiten
- Besser für Production-Deployment

### 15.2 Warum React Force Graph statt D3.js?

**Begründung:**
- Einfacheres API für React-Integration
- Automatisches Force-Directed Layout
- WebGL-Performance für große Graphen
- Gute Dokumentation und Community

### 15.3 Warum Zustand statt Redux?

**Begründung:**
- Leichtgewichtiger (weniger Boilerplate)
- Einfacheres API
- Ausreichend für diese Anwendung
- Bessere Developer Experience

### 15.4 Warum Shadcn/UI statt Material-UI?

**Begründung:**
- Professionelleres Design (passt zu SOC/IDE-Ästhetik)
- Tailwind CSS Integration
- Accessible (Radix UI Basis)
- Copy-Paste Komponenten (keine Runtime-Dependencies)

---

## 16. Code-Qualität & Best Practices

### 16.1 TypeScript

- Alle Komponenten sind typisiert
- Interfaces für alle Datenstrukturen
- Type-Safety für Store-Actions

### 16.2 Komponenten-Struktur

- Funktionale Komponenten mit Hooks
- Separation of Concerns (jedes Panel eigene Komponente)
- Wiederverwendbare UI-Komponenten

### 16.3 State Management

- Zentrale State-Verwaltung über Zustand
- Reaktive Updates
- Keine Prop-Drilling

### 16.4 Performance

- Dynamische Imports für große Bibliotheken
- Lazy Loading wo möglich
- Optimierte Font-Loading über Next.js

---

## 17. Testing & Qualitätssicherung

### 17.1 Linter

- ESLint konfiguriert
- TypeScript Type-Checking
- CSS-Linting über Tailwind

### 17.2 Browser-Kompatibilität

- Moderne Browser (Chrome, Firefox, Safari, Edge)
- WebGL-Unterstützung erforderlich für Graph

---

## 18. Deployment

### 18.1 Production Build

```bash
npm run build
npm start
```

### 18.2 Environment Variables

Keine erforderlich (Backend-URL könnte konfigurierbar gemacht werden)

### 18.3 Docker (Optional)

Dockerfile könnte erstellt werden für Container-Deployment.

---

## 19. Zusammenfassung

Das CRUX Frontend implementiert erfolgreich das "Glass Box" Design-Konzept:

✅ **Design-System:** Vollständig umgesetzt mit semantischen Farben und Typografie  
✅ **3-Spalten-Layout:** Panel A (Scenario Composer), Panel B (Digital Twin Graph), Panel C (Forensic Trace)  
✅ **UX-Patterns:** Refinement-Animation und Semantic Hovering implementiert  
✅ **State Management:** Zustand Store für zentrale State-Verwaltung  
✅ **Backend-Integration:** FastAPI Server bereit für Frontend-Kommunikation  
✅ **TypeScript:** Vollständig typisiert  
✅ **Performance:** Optimiert für große Datenmengen  

**Status:** Funktionsfähig und bereit für weitere Entwicklung

---

## 20. Referenzen

- **Design-Konzept:** Siehe ursprüngliche Design-Spezifikation
- **Next.js Dokumentation:** https://nextjs.org/docs
- **Tailwind CSS v4:** https://tailwindcss.com/docs
- **Shadcn/UI:** https://ui.shadcn.com
- **React Force Graph:** https://github.com/vasturiano/react-force-graph
- **Zustand:** https://github.com/pmndrs/zustand

---

**Dokumentation erstellt:** Dezember 2024  
**Version:** 1.0  
**Autor:** CRUX Development Team

