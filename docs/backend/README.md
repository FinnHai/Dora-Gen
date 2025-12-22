# Backend-System - Wissenschaftliche Dokumentation

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2025-12-20  
**Status:** Produktiv

---

## Abstract

Das Backend-System der CRUX-Plattform implementiert ein neuro-symbolisches Multi-Agenten-System zur Generierung von DORA-konformen Krisenszenarien. Die Architektur basiert auf LangGraph für Workflow-Orchestrierung, Neo4j für State Management und spezialisierten Agenten für verschiedene Aufgaben.

---

## Inhaltsverzeichnis

### 1. [Agenten-System](AGENTEN_DOKUMENTATION.md)
   - 1.1 Architektur-Übersicht
   - 1.2 Manager Agent
   - 1.3 Intel Agent
   - 1.4 Generator Agent
   - 1.5 Critic Agent
   - 1.6 Performance-Metriken

### 2. [Workflow & State Management](BACKEND_WORKFLOW_DOKUMENTATION.md)
   - 2.1 LangGraph Workflow
   - 2.2 WorkflowState Schema
   - 2.3 Neo4j State Management
   - 2.4 State-Übergänge
   - 2.5 Second-Order Effects

### 3. [Backend-API Übersicht](BACKEND_DOKUMENTATION.md)
   - 3.1 API-Endpunkte
   - 3.2 Neo4j Integration
   - 3.3 Scenario Management
   - 3.4 Error-Handling

---

## System-Architektur

### Komponenten-Übersicht

```
Backend-System
├── Orchestration Layer
│   └── LangGraph Workflow (scenario_workflow.py)
├── Agent Layer
│   ├── Manager Agent (Storyline-Planung)
│   ├── Intel Agent (TTP-Retrieval)
│   ├── Generator Agent (Inject-Generierung)
│   └── Critic Agent (Validierung)
├── Data Layer
│   ├── Neo4j (Knowledge Graph)
│   ├── ChromaDB (Vektor-Datenbank)
│   └── OpenAI GPT-4o (LLM)
└── API Layer
    └── FastAPI REST API
```

### Datenfluss

```
User Request
    ↓
FastAPI Endpoint
    ↓
LangGraph Workflow
    ↓
Agenten (sequenziell)
    ↓
Neo4j State Update
    ↓
Response (Injects, Logs)
```

---

## Dokumentations-Priorität

### 🔴 Kritisch (Muss-Have)

1. **[Agenten-System](AGENTEN_DOKUMENTATION.md)** ⭐⭐⭐⭐⭐
   - Vollständige Dokumentation aller Agenten
   - Input/Output-Spezifikationen
   - LLM-Konfigurationen
   - Performance-Metriken

2. **[Workflow & State Management](BACKEND_WORKFLOW_DOKUMENTATION.md)** ⭐⭐⭐⭐⭐
   - LangGraph Workflow-Details
   - Neo4j State Management
   - State-Übergänge
   - Second-Order Effects

### 🟠 Wichtig (Sollte-Have)

3. **[Backend-API Übersicht](BACKEND_DOKUMENTATION.md)** ⭐⭐⭐⭐
   - API-Endpunkte
   - Integration-Details
   - Error-Handling

---

## Wissenschaftliche Grundlagen

### Multi-Agenten-Systeme

Das System implementiert ein **hierarchisches Multi-Agenten-System** mit spezialisierten Agenten:

- **Manager Agent:** Strategische Planung (Top-Down)
- **Intel Agent:** Informationsbeschaffung (RAG)
- **Generator Agent:** Inhaltsgenerierung (LLM)
- **Critic Agent:** Validierung & Refinement (Reflect-Refine Loop)

### Neuro-Symbolische Architektur

**Neuro-Komponente:**
- Generative LLMs (GPT-4o) für Inhaltsgenerierung
- Semantische Suche (ChromaDB) für TTP-Retrieval

**Symbolische Komponente:**
- FSM (Finite State Machine) für Phasen-Übergänge
- Pydantic-Schemas für Datenvalidierung
- Neo4j für logische Abhängigkeiten

### State Management

**In-Memory State:**
- LangGraph WorkflowState (TypedDict)
- Pro Iteration aktualisiert

**Persistent State:**
- Neo4j Knowledge Graph
- Entity-Status, Relationships
- Temporal State (Timestamps)

---

## Technische Spezifikationen

### LLM-Konfigurationen

| Agent | Modell | Temperature | Zweck |
|-------|--------|-------------|-------|
| Manager | GPT-4o | 0.7 | Storyline-Planung |
| Generator | GPT-4o | 0.8 | Inject-Generierung |
| Critic | GPT-4o | 0.3 | Validierung |

### Datenbanken

| Datenbank | Typ | Verwendung |
|-----------|-----|------------|
| Neo4j | Graph-DB | State Management, Abhängigkeiten |
| ChromaDB | Vektor-DB | TTP-Retrieval (semantische Suche) |

### Performance-Metriken

- **Durchschnittliche Generierungszeit:** ~3-5 Sekunden pro Inject
- **LLM-Call-Zeit:** ~1-2 Sekunden
- **Validierungszeit:** ~0.5-1 Sekunde (symbolisch), ~1-2 Sekunden (LLM)
- **Kosten pro Inject:** ~$0.04-0.06 (mit Refinement)

---

## Schnellzugriff

### Agenten verstehen
→ [Agenten-Dokumentation](AGENTEN_DOKUMENTATION.md)

### Workflow verstehen
→ [Workflow-Dokumentation](BACKEND_WORKFLOW_DOKUMENTATION.md)

### API-Endpunkte
→ [Backend-API Übersicht](BACKEND_DOKUMENTATION.md)

---

## Referenzen

- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- Neo4j Documentation: https://neo4j.com/docs/
- OpenAI API Documentation: https://platform.openai.com/docs/
- ChromaDB Documentation: https://docs.trychroma.com/

---

**Letzte Aktualisierung:** 2025-12-20  
**Maintainer:** Backend Development Team
