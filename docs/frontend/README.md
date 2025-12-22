# Frontend-System - Wissenschaftliche Dokumentation

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2025-12-20  
**Status:** Produktiv

---

## Abstract

Das Frontend-System der CRUX-Plattform implementiert eine Next.js-basierte Web-Anwendung zur Visualisierung und Interaktion mit generierten Krisenszenarien. Das Design-System basiert auf der "Glass Box" Metapher zur epistemischen Klarheit zwischen generativen Vorschlägen (Neuro) und verifizierten Fakten (Symbolic).

---

## Inhaltsverzeichnis

### 1. [Design-System & UX-Konzept](DESIGN_IMPLEMENTATION.md)
   - 1.1 Design-DNA & Philosophie
   - 1.2 Visuelle Sprache
   - 1.3 Semantic Coloring
   - 1.4 Typografie & Layout
   - 1.5 UX-Patterns

### 2. [Implementation Summary](IMPLEMENTATION_SUMMARY.md)
   - 2.1 Technischer Stack
   - 2.2 Komponenten-Architektur
   - 2.3 State Management

### 3. [Backend-Integration](BACKEND_INTEGRATION.md)
   - 3.1 API-Client
   - 3.2 Datenfluss
   - 3.3 Error-Handling

### 4. [Graph-Visualisierung](GRAPH_IMPROVEMENTS.md)
   - 4.1 Graph-Features
   - 4.2 Interaktivität
   - 4.3 Performance-Optimierungen

### 5. [Quick Start](QUICK_START.md)
   - 5.1 Installation
   - 5.2 Entwicklung
   - 5.3 Production Build

### 6. [Troubleshooting](TROUBLESHOOTING.md)
   - 6.1 Häufige Probleme
   - 6.2 Lösungen
   - 6.3 Debugging

---

## System-Architektur

### Komponenten-Übersicht

```
Frontend-System
├── Layout Layer
│   ├── 3-Column Grid
│   └── Responsive Design
├── Component Layer
│   ├── ScenarioComposer (Panel A)
│   ├── DigitalTwinGraph (Panel B)
│   └── ForensicTrace (Panel C)
├── State Management
│   └── Zustand Store
├── API Layer
│   └── CruxAPI Client
└── Styling Layer
    ├── Tailwind CSS
    └── Shadcn/UI Components
```

### Datenfluss

```
User Interaction
    ↓
Component Event
    ↓
Zustand Store Update
    ↓
API Call (optional)
    ↓
UI Update
```

---

## Design-System

### Philosophie: "The Glass Box"

**Epistemische Klarheit:**
- **Neuro (Violett):** Generative Vorschläge, unsicher, probabilistisch
- **Symbolic (Grün):** Verifizierte Fakten, deterministisch
- **Intervention (Rot/Gelb):** Kritik-Agent Korrekturen

### Semantic Coloring

| Kategorie | Hex-Code | Verwendung |
|-----------|----------|------------|
| Neuro | `#7F5AF0` | Generative Inhalte |
| Symbolic | `#2CB67D` | Verifizierte Fakten |
| Intervention | `#E53170` | Kritik-Korrekturen |
| Void Black | `#090C10` | Hintergrund |
| Panel Grey | `#161B22` | Panels |

### Typografie

- **Interface:** Inter (Google Fonts)
- **Data/Logs:** JetBrains Mono (Monospace)

---

## Technischer Stack

### Frontend-Framework
- **Next.js 16.1.0** (React, SSR)
- **TypeScript** (Type Safety)
- **Tailwind CSS v4** (Styling)
- **Shadcn/UI** (Component Library)

### Visualisierung
- **React Force Graph** (Three.js)
- **D3.js** (Graph Physics)

### State Management
- **Zustand** (Lightweight Store)

### API
- **Fetch API** (REST Calls)
- **FastAPI Backend** (Python)

---

## Dokumentations-Priorität

### 🔴 Kritisch (Muss-Have)

1. **[Design-System & UX-Konzept](DESIGN_IMPLEMENTATION.md)** ⭐⭐⭐⭐⭐
   - Design-DNA & Philosophie
   - Visuelle Sprache
   - UX-Patterns

2. **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** ⭐⭐⭐⭐
   - Technischer Stack
   - Komponenten-Architektur

### 🟠 Wichtig (Sollte-Have)

3. **[Backend-Integration](BACKEND_INTEGRATION.md)** ⭐⭐⭐⭐
   - API-Client
   - Datenfluss

4. **[Graph-Visualisierung](GRAPH_IMPROVEMENTS.md)** ⭐⭐⭐
   - Graph-Features
   - Interaktivität

### 🟡 Optional (Nice-to-Have)

5. **[Quick Start](QUICK_START.md)** ⭐⭐⭐⭐⭐
   - Installation & Entwicklung

6. **[Troubleshooting](TROUBLESHOOTING.md)** ⭐⭐⭐
   - Problembehebung

---

## Wissenschaftliche Grundlagen

### UX-Patterns

**Refinement-Pattern:**
- 4-Phasen-Animation zur Visualisierung von Korrekturen
- Violett → Rot Underline → Strikethrough + Grün → Weiß + Grün Shield

**Semantic Hovering:**
- Bidirektionale Verknüpfung zwischen Text-Assets und Graph-Nodes
- Hover über Text → Graph-Highlight
- Hover über Graph → Text-Highlight

### Information Architecture

**3-Column Layout:**
- **Panel A (30%):** Scenario Composer (Timeline)
- **Panel B (50%):** Digital Twin Graph (Knowledge Graph)
- **Panel C (20%):** Forensic Trace (Logs)

---

## Schnellzugriff

### Design-System verstehen
→ [Design-Implementierung](DESIGN_IMPLEMENTATION.md)

### Frontend starten
→ [Quick Start](QUICK_START.md)

### Backend verbinden
→ [Backend-Integration](BACKEND_INTEGRATION.md)

### Probleme lösen
→ [Troubleshooting](TROUBLESHOOTING.md)

---

## Referenzen

- Next.js Documentation: https://nextjs.org/docs
- Tailwind CSS Documentation: https://tailwindcss.com/docs
- Shadcn/UI Documentation: https://ui.shadcn.com/
- React Force Graph: https://github.com/vasturiano/react-force-graph

---

**Letzte Aktualisierung:** 2025-12-20  
**Maintainer:** Frontend Development Team
