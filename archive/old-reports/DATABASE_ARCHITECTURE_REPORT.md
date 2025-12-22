# Database Architecture & Data Model Report

**Erstellt:** 2025-12-15  
**Quelle:** `neo4j_client.py` und `state_models.py`  
**Zweck:** Technische Dokumentation der Datenbank-Schicht für Thesis

---

## 1. Cypher Queries

### 1.1 `update_entity_status` Query

**Methode:** `Neo4jClient.update_entity_status()`  
**Zeile:** 141-178 in `neo4j_client.py`

```cypher
MATCH (e {id: $entity_id})
SET e.status = $new_status,
    e.last_updated = datetime()
```

**Mit optionalem Inject-ID Tracking:**

```cypher
MATCH (e {id: $entity_id})
SET e.status = $new_status,
    e.last_updated = datetime(),
    e.last_updated_by_inject = $inject_id
```

**Parameter:**
- `entity_id`: String - ID der Entität (z.B. "SRV-001")
- `new_status`: String - Neuer Status (z.B. "offline", "compromised", "encrypted")
- `inject_id`: Optional String - ID des Injects, der die Änderung verursacht hat

**Python-Code (Zeilen 162-178):**
```python
query = """
MATCH (e {id: $entity_id})
SET e.status = $new_status,
    e.last_updated = datetime()
"""
if inject_id:
    query += ", e.last_updated_by_inject = $inject_id"

params = {
    "entity_id": entity_id,
    "new_status": new_status
}
if inject_id:
    params["inject_id"] = inject_id

session.run(query, **params)
```

---

### 1.2 `get_current_state` Query

**Methode:** `Neo4jClient.get_current_state()`  
**Zeile:** 70-117 in `neo4j_client.py`

**Ohne Entity-Type Filter:**

```cypher
MATCH (e)
OPTIONAL MATCH (e)-[r]->(related)
RETURN e, collect(r) as relationships, collect(related) as related_entities
LIMIT 100
```

**Mit Entity-Type Filter:**

```cypher
MATCH (e {type: $entity_type})
OPTIONAL MATCH (e)-[r]->(related)
RETURN e, collect(r) as relationships, collect(related) as related_entities
```

**Parameter:**
- `entity_type`: Optional String - Filter nach Entity-Typ (z.B. 'Server', 'Application')

**Python-Code (Zeilen 84-98):**
```python
if entity_type:
    query = """
    MATCH (e {type: $entity_type})
    OPTIONAL MATCH (e)-[r]->(related)
    RETURN e, collect(r) as relationships, collect(related) as related_entities
    """
    result = session.run(query, entity_type=entity_type)
else:
    query = """
    MATCH (e)
    OPTIONAL MATCH (e)-[r]->(related)
    RETURN e, collect(r) as relationships, collect(related) as related_entities
    LIMIT 100
    """
    result = session.run(query)
```

**Rückgabe-Format:**
```python
[
    {
        "entity_id": "SRV-001",
        "entity_type": "Server",
        "name": "Domain Controller DC-01",
        "status": "online",
        "properties": {...},
        "relationships": [
            {
                "target": "APP-001",
                "type": "RELATED_TO"
            }
        ]
    },
    ...
]
```

---

## 2. Seeding Logic: Enterprise Infrastructure (40 Assets)

**Methode:** `Neo4jClient.seed_enterprise_infrastructure()`  
**Zeile:** 507-646 in `neo4j_client.py`

### 2.1 Asset-Liste (Exakt 40 Assets)

#### Core Servers (5 Assets)
```python
SRV-CORE-001: "Core Server 001"
SRV-CORE-002: "Core Server 002"
SRV-CORE-003: "Core Server 003"
SRV-CORE-004: "Core Server 004"
SRV-CORE-005: "Core Server 005"
```

**Code (Zeilen 522-529):**
```python
for i in range(1, 6):
    enterprise_assets.append({
        "id": f"SRV-CORE-{i:03d}",
        "type": "Server",
        "name": f"Core Server {i:03d}",
        "status": "normal"
    })
```

#### Application Servers (15 Assets)
```python
SRV-APP-001: "Application Server 001"
SRV-APP-002: "Application Server 002"
SRV-APP-003: "Application Server 003"
SRV-APP-004: "Application Server 004"
SRV-APP-005: "Application Server 005"
SRV-APP-006: "Application Server 006"
SRV-APP-007: "Application Server 007"
SRV-APP-008: "Application Server 008"
SRV-APP-009: "Application Server 009"
SRV-APP-010: "Application Server 010"
SRV-APP-011: "Application Server 011"
SRV-APP-012: "Application Server 012"
SRV-APP-013: "Application Server 013"
SRV-APP-014: "Application Server 014"
SRV-APP-015: "Application Server 015"
```

**Code (Zeilen 531-538):**
```python
for i in range(1, 16):
    enterprise_assets.append({
        "id": f"SRV-APP-{i:03d}",
        "type": "Server",
        "name": f"Application Server {i:03d}",
        "status": "normal"
    })
```

#### Production Databases (5 Assets)
```python
DB-PROD-01: "Production Database 01"
DB-PROD-02: "Production Database 02"
DB-PROD-03: "Production Database 03"
DB-PROD-04: "Production Database 04"
DB-PROD-05: "Production Database 05"
```

**Code (Zeilen 541-548):**
```python
for i in range(1, 6):
    enterprise_assets.append({
        "id": f"DB-PROD-{i:02d}",
        "type": "Database",
        "name": f"Production Database {i:02d}",
        "status": "normal"
    })
```

#### Development Databases (5 Assets)
**Hinweis:** Diese können leicht mit PROD-Datenbanken verwechselt werden!

```python
DB-DEV-01: "Development Database 01"
DB-DEV-02: "Development Database 02"
DB-DEV-03: "Development Database 03"
DB-DEV-04: "Development Database 04"
DB-DEV-05: "Development Database 05"
```

**Code (Zeilen 549-556):**
```python
for i in range(1, 6):
    enterprise_assets.append({
        "id": f"DB-DEV-{i:02d}",
        "type": "Database",
        "name": f"Development Database {i:02d}",
        "status": "normal"
    })
```

#### Finance Workstations (10 Assets)
```python
WS-FINANCE-01: "Finance Workstation 01"
WS-FINANCE-02: "Finance Workstation 02"
WS-FINANCE-03: "Finance Workstation 03"
WS-FINANCE-04: "Finance Workstation 04"
WS-FINANCE-05: "Finance Workstation 05"
WS-FINANCE-06: "Finance Workstation 06"
WS-FINANCE-07: "Finance Workstation 07"
WS-FINANCE-08: "Finance Workstation 08"
WS-FINANCE-09: "Finance Workstation 09"
WS-FINANCE-10: "Finance Workstation 10"
```

**Code (Zeilen 558-565):**
```python
for i in range(1, 11):
    enterprise_assets.append({
        "id": f"WS-FINANCE-{i:02d}",
        "type": "Workstation",
        "name": f"Finance Workstation {i:02d}",
        "status": "normal"
    })
```

### 2.2 Gesamtübersicht

| Kategorie | Anzahl | Asset-IDs | Status |
|-----------|--------|-----------|--------|
| Core Servers | 5 | SRV-CORE-001 bis 005 | normal |
| Application Servers | 15 | SRV-APP-001 bis 015 | normal |
| Production Databases | 5 | DB-PROD-01 bis 05 | normal |
| Development Databases | 5 | DB-DEV-01 bis 05 | normal |
| Finance Workstations | 10 | WS-FINANCE-01 bis 10 | normal |
| **GESAMT** | **40** | - | - |

### 2.3 Relationships (Beziehungen)

**Code (Zeilen 615-630):**
```python
relationships = [
    # Core Server Dependencies
    ("SRV-APP-001", "RUNS_ON", "SRV-CORE-001"),
    ("SRV-APP-002", "RUNS_ON", "SRV-CORE-002"),
    ("SRV-APP-003", "RUNS_ON", "SRV-CORE-003"),
    
    # Database Dependencies (verwirrend: PROD vs DEV)
    ("SRV-APP-001", "USES", "DB-PROD-01"),
    ("SRV-APP-002", "USES", "DB-PROD-02"),
    ("SRV-APP-003", "USES", "DB-DEV-01"),  # Kann mit PROD verwechselt werden!
    ("SRV-APP-004", "USES", "DB-DEV-02"),
    
    # Workstation Dependencies
    ("WS-FINANCE-01", "CONNECTS_TO", "SRV-APP-001"),
    ("WS-FINANCE-02", "CONNECTS_TO", "SRV-APP-002"),
]
```

**Cypher Query für Relationship-Erstellung (Zeilen 632-637):**
```cypher
MATCH (source {id: $source_id}), (target {id: $target_id})
CREATE (source)-[r:{rel_type}]->(target)
```

**Relationship-Typen:**
- `RUNS_ON`: Application Server läuft auf Core Server
- `USES`: Application verwendet Database
- `CONNECTS_TO`: Workstation verbindet sich mit Application Server

### 2.4 Seeding-Prozess

**Code (Zeilen 567-583):**
```python
with self.driver.session(database=self.database) as session:
    # Lösche ALLE bestehenden Entities (inklusive Szenarien und Injects)
    print("🗑️  Lösche bestehende Datenbank-Inhalte...")
    session.run("MATCH (n) DETACH DELETE n")
    
    # Erstelle alle Enterprise Assets
    print(f"🏢 Erstelle {len(enterprise_assets)} Enterprise Assets...")
    for asset in enterprise_assets:
        query = """
        CREATE (e:Entity {
            id: $id,
            type: $type,
            name: $name,
            status: $status
        })
        """
        session.run(query, **asset)
```

---

## 3. Pydantic Models

### 3.1 `Inject` Model

**Datei:** `state_models.py`  
**Zeile:** 91-152

**Vollständige Definition:**

```python
class Inject(BaseModel):
    """
    MSEL-Inject Modell gemäß DORA-Anforderungen.
    
    Jeder Inject repräsentiert einen einzelnen "Einwurf" in einem
    Krisenszenario und muss logisch konsistent und DORA-konform sein.
    """
    inject_id: str = Field(
        ...,
        description="Eindeutige Inject-ID (z.B. INJ-005)",
        pattern=r"^INJ-\d{3,}$"
    )
    time_offset: str = Field(
        ...,
        description="Zeitversatz vom Szenario-Start (z.B. T+02:00 oder T+00:02:30)",
        pattern=r"^T\+(\d{2}):(\d{2})(?::(\d{2}))?$"
    )
    phase: CrisisPhase = Field(
        ...,
        description="Aktuelle Phase im FSM"
    )
    source: str = Field(
        ...,
        description="Quelle des Injects (z.B. 'Red Team / Attacker', 'Blue Team / SOC')"
    )
    target: str = Field(
        ...,
        description="Empfänger des Injects (z.B. 'Blue Team / SOC', 'Management')"
    )
    modality: InjectModality = Field(
        ...,
        description="Kommunikationsmodalität"
    )
    content: str = Field(
        ...,
        description="Inhalt des Injects (Text)",
        min_length=10
    )
    technical_metadata: TechnicalMetadata = Field(
        ...,
        description="Technische Metadaten (MITRE, IOCs, etc.)"
    )
    dora_compliance_tag: Optional[str] = Field(
        None,
        description="DORA Compliance Tag (z.B. 'Art25_VulnScan', 'Art25_IncidentResponse')"
    )
    business_impact: Optional[str] = Field(
        None,
        description="Geschäftliche Auswirkung (z.B. 'Zahlungsverkehr gestoppt')"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Erstellungszeitpunkt"
    )

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validiert, dass der Content nicht leer ist."""
        if not v or len(v.strip()) < 10:
            raise ValueError("Content muss mindestens 10 Zeichen lang sein")
        return v.strip()
```

#### Feld-Details mit Regex-Patterns

| Feld | Typ | Required | Regex Pattern | Beschreibung |
|------|-----|----------|---------------|--------------|
| `inject_id` | `str` | ✅ | `^INJ-\d{3,}$` | Eindeutige Inject-ID (z.B. "INJ-005", "INJ-123") |
| `time_offset` | `str` | ✅ | `^T\+(\d{2}):(\d{2})(?::(\d{2}))?$` | Zeitversatz (z.B. "T+02:00" oder "T+00:02:30") |
| `phase` | `CrisisPhase` | ✅ | - | Enum: NORMAL_OPERATION, SUSPICIOUS_ACTIVITY, etc. |
| `source` | `str` | ✅ | - | Quelle des Injects |
| `target` | `str` | ✅ | - | Empfänger des Injects |
| `modality` | `InjectModality` | ✅ | - | Enum: SIEM_ALERT, EMAIL, etc. |
| `content` | `str` | ✅ | - | Mindestens 10 Zeichen (validiert) |
| `technical_metadata` | `TechnicalMetadata` | ✅ | - | Pydantic Model (siehe unten) |
| `dora_compliance_tag` | `Optional[str]` | ❌ | - | DORA Compliance Tag |
| `business_impact` | `Optional[str]` | ❌ | - | Geschäftliche Auswirkung |
| `created_at` | `Optional[datetime]` | ❌ | - | Erstellungszeitpunkt (auto) |

#### Regex-Pattern Erklärungen

**`inject_id` Pattern: `^INJ-\d{3,}$`**
- `^` - Start der Zeichenkette
- `INJ-` - Literal "INJ-"
- `\d{3,}` - Mindestens 3 Ziffern
- `$` - Ende der Zeichenkette
- **Beispiele:** ✅ "INJ-005", ✅ "INJ-123", ❌ "INJ-12" (nur 2 Ziffern)

**`time_offset` Pattern: `^T\+(\d{2}):(\d{2})(?::(\d{2}))?$`**
- `^` - Start der Zeichenkette
- `T\+` - Literal "T+"
- `(\d{2})` - Capture Group 1: 2 Ziffern (Tage)
- `:` - Literal ":"
- `(\d{2})` - Capture Group 2: 2 Ziffern (Stunden)
- `(?::(\d{2}))?` - Optional: ":" gefolgt von 2 Ziffern (Minuten)
- `$` - Ende der Zeichenkette
- **Beispiele:** ✅ "T+02:00", ✅ "T+00:02:30", ❌ "T+2:00" (nur 1 Ziffer)

#### `TechnicalMetadata` Model

**Zeile:** 63-88 in `state_models.py`

```python
class TechnicalMetadata(BaseModel):
    """Technische Metadaten für einen Inject."""
    mitre_id: Optional[str] = Field(
        None,
        description="MITRE ATT&CK Technique ID (z.B. T1110)"
    )
    affected_assets: List[str] = Field(
        default_factory=list,
        description="Liste betroffener Assets (Server, Applikationen, etc.)"
    )
    ioc_hash: Optional[str] = Field(
        None,
        description="Indikator of Compromise Hash"
    )
    ioc_ip: Optional[str] = Field(
        None,
        description="Indikator of Compromise IP-Adresse"
    )
    ioc_domain: Optional[str] = Field(
        None,
        description="Indikator of Compromise Domain"
    )
    severity: Optional[str] = Field(
        None,
        description="Schweregrad (Low, Medium, High, Critical)"
    )
```

#### `InjectModality` Enum

**Zeile:** 53-61 in `state_models.py`

```python
class InjectModality(str, Enum):
    """Kommunikationsmodalität für Injects."""
    SIEM_ALERT = "SIEM Alert"
    EMAIL = "Email"
    PHONE_CALL = "Phone Call"
    PHYSICAL_EVENT = "Physical Event"
    NEWS_REPORT = "News Report"
    INTERNAL_REPORT = "Internal Report"
```

#### `CrisisPhase` Enum

**Zeile:** 17-25 in `state_models.py`

```python
class CrisisPhase(str, Enum):
    """Finite State Machine Phasen für Krisenszenarien."""
    NORMAL_OPERATION = "NORMAL_OPERATION"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    INITIAL_INCIDENT = "INITIAL_INCIDENT"
    ESCALATION_CRISIS = "ESCALATION_CRISIS"
    CONTAINMENT = "CONTAINMENT"
    RECOVERY = "RECOVERY"
```

---

### 3.2 `WorkflowState` TypedDict

**Datei:** `workflows/state_schema.py`  
**Zeile:** 19-74

**Vollständige Definition:**

```python
class WorkflowState(TypedDict):
    """
    State für den LangGraph Workflow.
    
    Wird zwischen den Nodes (Agenten) übergeben und enthält
    alle relevanten Informationen für die Szenario-Generierung.
    """
    # Szenario-Metadaten
    scenario_id: str
    scenario_type: ScenarioType
    current_phase: CrisisPhase
    
    # Generierte Injects
    injects: List[Inject]
    
    # Aktueller Systemzustand (aus Neo4j)
    system_state: Dict[str, Any]  # Entitäten und deren Status
    
    # Workflow-Kontrolle
    iteration: int  # Aktuelle Iteration
    max_iterations: int  # Maximale Anzahl Injects
    
    # Agenten-Outputs
    manager_plan: Optional[Dict[str, Any]]  # Storyline vom Manager Agent
    selected_action: Optional[Dict[str, Any]]  # Ausgewählte Aktion (MITRE TTP)
    draft_inject: Optional[Inject]  # Roher Inject vom Generator
    validation_result: Optional[ValidationResult]  # Validierung vom Critic
    
    # Intel & Kontext
    available_ttps: List[Dict[str, Any]]  # Verfügbare TTPs vom Intel Agent
    historical_context: List[Dict[str, Any]]  # Vorherige Injects für Konsistenz
    
    # Fehlerbehandlung
    errors: List[str]
    warnings: List[str]
    
    # Metadaten
    start_time: datetime
    metadata: Dict[str, Any]
    
    # Workflow-Logs für Dashboard
    workflow_logs: List[Dict[str, Any]]  # Logs von jedem Node
    agent_decisions: List[Dict[str, Any]]  # Entscheidungen der Agenten
    
    # Interaktive Entscheidungen
    pending_decision: Optional[Dict[str, Any]]  # Aktuell ausstehende Benutzer-Entscheidung
    user_decisions: List[Dict[str, Any]]  # Alle getroffenen Benutzer-Entscheidungen
    end_condition: Optional[str]  # Aktuelle End-Bedingung (FATAL, VICTORY, NORMAL_END, CONTINUE)
    interactive_mode: bool  # Ob interaktiver Modus aktiviert ist
    
    # Mode für A/B Testing
    mode: Literal['legacy', 'thesis']  # 'legacy' = Skip Validation, 'thesis' = Full Validation (Default)
    
    # Human-in-the-Loop Feedback
    user_feedback: Optional[str]  # Letzte Response Action vom Benutzer (z.B. "Shutdown SRV-001")
```

#### Feld-Kategorien

| Kategorie | Felder | Typ |
|-----------|--------|-----|
| **Szenario-Metadaten** | `scenario_id`, `scenario_type`, `current_phase` | `str`, `ScenarioType`, `CrisisPhase` |
| **Generierte Injects** | `injects` | `List[Inject]` |
| **Systemzustand** | `system_state` | `Dict[str, Any]` |
| **Workflow-Kontrolle** | `iteration`, `max_iterations` | `int`, `int` |
| **Agenten-Outputs** | `manager_plan`, `selected_action`, `draft_inject`, `validation_result` | `Optional[Dict]`, `Optional[Dict]`, `Optional[Inject]`, `Optional[ValidationResult]` |
| **Intel & Kontext** | `available_ttps`, `historical_context` | `List[Dict]`, `List[Dict]` |
| **Fehlerbehandlung** | `errors`, `warnings` | `List[str]`, `List[str]` |
| **Metadaten** | `start_time`, `metadata` | `datetime`, `Dict[str, Any]` |
| **Workflow-Logs** | `workflow_logs`, `agent_decisions` | `List[Dict]`, `List[Dict]` |
| **Interaktive Entscheidungen** | `pending_decision`, `user_decisions`, `end_condition`, `interactive_mode` | `Optional[Dict]`, `List[Dict]`, `Optional[str]`, `bool` |
| **A/B Testing Mode** | `mode` | `Literal['legacy', 'thesis']` |
| **Human-in-the-Loop** | `user_feedback` | `Optional[str]` |

#### Typ-Imports

```python
from typing import TypedDict, List, Optional, Dict, Any, Literal
from datetime import datetime
from state_models import (
    Inject,
    ScenarioState,
    CrisisPhase,
    ScenarioType,
    ValidationResult
)
```

---

## 4. Weitere Relevante Models

### 4.1 `ScenarioState` Model

**Zeile:** 155-184 in `state_models.py`

```python
class ScenarioState(BaseModel):
    """
    Zustand eines laufenden Szenarios.
    
    Wird von LangGraph für State Management verwendet.
    """
    scenario_id: str = Field(
        ...,
        description="Eindeutige Szenario-ID"
    )
    scenario_type: ScenarioType = Field(
        ...,
        description="Typ des Szenarios"
    )
    current_phase: CrisisPhase = Field(
        default=CrisisPhase.NORMAL_OPERATION,
        description="Aktuelle FSM-Phase"
    )
    injects: List[Inject] = Field(
        default_factory=list,
        description="Liste aller generierten Injects"
    )
    start_time: datetime = Field(
        default_factory=datetime.now,
        description="Startzeitpunkt des Szenarios"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Zusätzliche Metadaten"
    )
```

### 4.2 `ValidationResult` Model

**Zeile:** 247-272 in `state_models.py`

```python
class ValidationResult(BaseModel):
    """Ergebnis der Validierung durch den Critic-Agent."""
    is_valid: bool = Field(
        ...,
        description="Ist der Inject valide?"
    )
    logical_consistency: bool = Field(
        ...,
        description="Ist der Inject logisch konsistent mit der Historie?"
    )
    dora_compliance: bool = Field(
        ...,
        description="Erfüllt der Inject DORA-Anforderungen?"
    )
    causal_validity: bool = Field(
        ...,
        description="Ist der Inject kausal valide (MITRE ATT&CK Graph)?"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Liste von Fehlermeldungen"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Liste von Warnungen"
    )
```

---

## Zusammenfassung

### Datenbank-Schicht (`neo4j_client.py`)
- ✅ Cypher Queries für State-Management dokumentiert
- ✅ Seeding-Logik mit exakt 40 Assets dokumentiert
- ✅ Relationship-Typen dokumentiert

### Datenmodelle (`state_models.py` & `state_schema.py`)
- ✅ `Inject` Pydantic Model mit allen Regex-Patterns dokumentiert
- ✅ `WorkflowState` TypedDict vollständig dokumentiert
- ✅ Alle unterstützenden Models dokumentiert

**Ende des Berichts**
