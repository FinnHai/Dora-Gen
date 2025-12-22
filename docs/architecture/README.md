# System-Architektur - Wissenschaftliche Dokumentation

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2025-12-20  
**Status:** Produktiv

---

## Abstract

Diese Sektion enthält alle Architektur-Dokumentationen für die CRUX-Plattform. Die Dokumentationen beschreiben die Gesamtarchitektur, Komponenten und Datenflüsse des Systems.

---

## Inhaltsverzeichnis

### 1. [Architektur-Übersicht](ARCHITECTURE.md)
   - 1.1 High-Level Architektur
   - 1.2 Komponenten-Übersicht
   - 1.3 Datenfluss-Diagramme
   - 1.4 Technologie-Stack

### 2. [Architektur-Dokumentation](DOCUMENTATION.md)
   - 2.1 Detaillierte Komponenten
   - 2.2 Schnittstellen
   - 2.3 Abhängigkeiten

---

## Architektur-Prinzipien

### Neuro-Symbolische Architektur
- **Neuro-Komponente:** Generative LLMs für Inhaltsgenerierung
- **Symbolische Komponente:** FSM, Pydantic-Schemas, Neo4j

### Multi-Agenten-System
- **Hierarchische Agenten:** Manager → Intel → Generator → Critic
- **Orchestrierung:** LangGraph Workflow

### State Management
- **In-Memory:** LangGraph WorkflowState
- **Persistent:** Neo4j Knowledge Graph

---

## Dokumentations-Priorität

### 🔴 Kritisch (Muss-Have)

1. **[Architektur-Übersicht](ARCHITECTURE.md)** ⭐⭐⭐⭐⭐
   - High-Level Architektur
   - Komponenten-Übersicht

2. **[Architektur-Dokumentation](DOCUMENTATION.md)** ⭐⭐⭐⭐
   - Detaillierte Komponenten
   - Schnittstellen

---

## Schnellzugriff

### Architektur verstehen
→ [Architektur-Übersicht](ARCHITECTURE.md)

### Komponenten verstehen
→ [Architektur-Dokumentation](DOCUMENTATION.md)

---

**Letzte Aktualisierung:** 2025-12-20  
**Maintainer:** Architecture Team

