# 🏗️ Architektur-Dokumentation

Detaillierte Architektur-Diagramme und Beschreibungen des DORA-Szenariengenerators.

## 📊 Übersicht

### High-Level Architektur

```mermaid
graph TB
    subgraph "Frontend Layer"
        ST[Streamlit UI]
    end
    
    subgraph "Orchestration Layer"
        LG[LangGraph Workflow]
    end
    
    subgraph "Agent Layer"
        MA[Manager Agent]
        GA[Generator Agent]
        CA[Critic Agent]
        IA[Intel Agent]
    end
    
    subgraph "Data Layer"
        NEO[Neo4j<br/>Knowledge Graph]
        CHROMA[ChromaDB<br/>Vector DB]
        LLM[OpenAI GPT-4o]
    end
    
    ST --> LG
    LG --> MA
    LG --> GA
    LG --> CA
    LG --> IA
    
    MA --> LLM
    GA --> LLM
    CA --> LLM
    
    IA --> CHROMA
    LG --> NEO
    GA --> NEO
    CA --> NEO
    
    style ST fill:#1f77b4
    style LG fill:#ff7f0e
    style MA fill:#2ca02c
    style GA fill:#2ca02c
    style CA fill:#2ca02c
    style IA fill:#2ca02c
    style NEO fill:#d62728
    style CHROMA fill:#9467bd
    style LLM fill:#8c564b
```

## 🔄 Workflow-Architektur

### LangGraph Workflow Flow

```mermaid
stateDiagram-v2
    [*] --> StateCheck
    
    StateCheck --> Manager: System State
    Manager --> Intel: Storyline Plan
    Intel --> ActionSelection: TTPs
    ActionSelection --> Generator: Selected TTP
    Generator --> Critic: Draft Inject
    Critic --> StateUpdate: Valid
    Critic --> Generator: Invalid (Refine)
    StateUpdate --> StateCheck: Continue
    StateUpdate --> [*]: End
    
    note right of Critic
        Max 2 Refine Attempts
        per Inject
    end note
    
    note right of StateUpdate
        Updates Neo4j
        Tracks Second-Order Effects
    end note
```

### Detaillierter Workflow

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Streamlit UI
    participant Workflow as LangGraph Workflow
    participant Manager as Manager Agent
    participant Intel as Intel Agent
    participant Generator as Generator Agent
    participant Critic as Critic Agent
    participant Neo4j
    participant ChromaDB
    participant OpenAI
    
    User->>Frontend: Configure Scenario
    Frontend->>Workflow: Start Generation
    
    loop For each Inject
        Workflow->>Neo4j: Get Current State
        Neo4j-->>Workflow: System Entities
        
        Workflow->>Manager: Create Storyline
        Manager->>OpenAI: Generate Plan
        OpenAI-->>Manager: Storyline Plan
        Manager-->>Workflow: Plan
        
        Workflow->>Intel: Get Relevant TTPs
        Intel->>ChromaDB: Query TTPs
        ChromaDB-->>Intel: TTP List
        Intel-->>Workflow: TTPs
        
        Workflow->>Workflow: Select Action
        
        Workflow->>Generator: Generate Inject
        Generator->>OpenAI: Create Inject
        OpenAI-->>Generator: Draft Inject
        Generator-->>Workflow: Inject
        
        Workflow->>Critic: Validate Inject
        Critic->>OpenAI: Validate
        OpenAI-->>Critic: Validation Result
        Critic-->>Workflow: Result
        
        alt Valid
            Workflow->>Neo4j: Update State
            Neo4j-->>Workflow: Updated
        else Invalid
            Workflow->>Generator: Refine (max 2x)
        end
    end
    
    Workflow-->>Frontend: Scenario Result
    Frontend-->>User: Display Results
```

## 🧩 Komponenten-Architektur

### Agent-Architektur

```mermaid
graph LR
    subgraph "Manager Agent"
        M1[Storyline Planning]
        M2[Phase Transition Logic]
        M3[LLM Integration]
    end
    
    subgraph "Generator Agent"
        G1[Inject Creation]
        G2[Content Generation]
        G3[Metadata Assignment]
    end
    
    subgraph "Critic Agent"
        C1[Logical Consistency]
        C2[DORA Compliance]
        C3[Causal Validity]
    end
    
    subgraph "Intel Agent"
        I1[TTP Retrieval]
        I2[Vector Search]
        I3[Phase Filtering]
    end
    
    M1 --> M2
    M2 --> M3
    
    G1 --> G2
    G2 --> G3
    
    C1 --> C2
    C2 --> C3
    
    I1 --> I2
    I2 --> I3
    
    style M1 fill:#2ca02c
    style G1 fill:#2ca02c
    style C1 fill:#2ca02c
    style I1 fill:#2ca02c
```

### State Management Architektur

```mermaid
graph TB
    subgraph "State Models"
        SM[Pydantic Models]
        INJ[Inject Schema]
        SCEN[Scenario State]
        ENT[Graph Entities]
    end
    
    subgraph "Neo4j Knowledge Graph"
        N1[Entities<br/>Server, Apps, Depts]
        N2[Relationships<br/>RUNS_ON, USES]
        N3[Status Tracking<br/>online, offline, compromised]
    end
    
    subgraph "FSM"
        F1[Phase States]
        F2[Transition Rules]
        F3[Validation Logic]
    end
    
    SM --> INJ
    SM --> SCEN
    SM --> ENT
    
    ENT --> N1
    ENT --> N2
    ENT --> N3
    
    SCEN --> F1
    F1 --> F2
    F2 --> F3
    
    style SM fill:#1f77b4
    style N1 fill:#d62728
    style F1 fill:#ff7f0e
```

## 📦 Datenfluss

### Inject-Generierungs-Pipeline

```mermaid
flowchart TD
    START([User Request]) --> CONFIG[Configuration<br/>Type, Count]
    
    CONFIG --> LOOP{More Injects?}
    
    LOOP -->|Yes| STATE[State Check<br/>Neo4j Query]
    LOOP -->|No| EXPORT[Export Results]
    
    STATE --> PLAN[Manager: Storyline Plan]
    PLAN --> TTP[Intel: Get TTPs]
    TTP --> SELECT[Action Selection]
    SELECT --> GEN[Generator: Create Inject]
    
    GEN --> VALID[Critic: Validate]
    
    VALID -->|Valid| UPDATE[Update Neo4j State]
    VALID -->|Invalid| REFINE{Refine Count < 2?}
    
    REFINE -->|Yes| GEN
    REFINE -->|No| UPDATE
    
    UPDATE --> LOOP
    
    EXPORT --> END([Complete])
    
    style START fill:#2ca02c
    style END fill:#d62728
    style VALID fill:#ff7f0e
    style UPDATE fill:#9467bd
```

## 🔐 Sicherheits-Architektur

### Datenfluss und Sicherheit

```mermaid
graph TB
    subgraph "Secure Storage"
        ENV[.env File<br/>NOT in Git]
        NEO_PASS[Neo4j Password]
        API_KEY[OpenAI API Key]
    end
    
    subgraph "Application"
        APP[Streamlit App]
        WORKFLOW[Workflow]
    end
    
    subgraph "External Services"
        OPENAI[OpenAI API]
        NEO4J[Neo4j Database]
    end
    
    ENV --> APP
    NEO_PASS --> NEO4J
    API_KEY --> OPENAI
    
    APP --> WORKFLOW
    WORKFLOW --> OPENAI
    WORKFLOW --> NEO4J
    
    style ENV fill:#d62728
    style NEO_PASS fill:#d62728
    style API_KEY fill:#d62728
```

## 🗄️ Datenmodell

### Entity-Relationship Diagram

```mermaid
erDiagram
    SCENARIO ||--o{ INJECT : contains
    SCENARIO {
        string scenario_id
        enum scenario_type
        enum current_phase
        datetime start_time
    }
    
    INJECT ||--|| TECHNICAL_METADATA : has
    INJECT {
        string inject_id
        string time_offset
        enum phase
        string source
        string target
        string content
        string dora_compliance_tag
    }
    
    TECHNICAL_METADATA {
        string mitre_id
        array affected_assets
        string ioc_hash
        string severity
    }
    
    ENTITY ||--o{ RELATIONSHIP : has
    ENTITY {
        string entity_id
        string entity_type
        string name
        string status
    }
    
    RELATIONSHIP {
        string source_id
        string target_id
        string relationship_type
    }
    
    INJECT ||--o{ ENTITY : affects
```

## 🔄 Phasen-Übergänge (FSM)

### Finite State Machine

```mermaid
stateDiagram-v2
    [*] --> NORMAL_OPERATION
    
    NORMAL_OPERATION --> SUSPICIOUS_ACTIVITY : Detection
    NORMAL_OPERATION --> INITIAL_INCIDENT : Direct Attack
    
    SUSPICIOUS_ACTIVITY --> INITIAL_INCIDENT : Confirmed
    SUSPICIOUS_ACTIVITY --> NORMAL_OPERATION : False Positive
    
    INITIAL_INCIDENT --> ESCALATION_CRISIS : Severe Impact
    INITIAL_INCIDENT --> CONTAINMENT : Quick Response
    
    ESCALATION_CRISIS --> CONTAINMENT : Response Actions
    
    CONTAINMENT --> RECOVERY : Systems Restored
    CONTAINMENT --> ESCALATION_CRISIS : Re-Escalation
    
    RECOVERY --> NORMAL_OPERATION : Full Recovery
    
    note right of NORMAL_OPERATION
        Baseline State
        All Systems Operational
    end note
    
    note right of ESCALATION_CRISIS
        Critical State
        Business Impact
    end note
```

## 📊 Deployment-Architektur

### Lokale Entwicklung

```mermaid
graph TB
    subgraph "Development Machine"
        DEV[Developer]
        IDE[IDE/Editor]
        VENV[Python venv]
        STREAMLIT[Streamlit App]
    end
    
    subgraph "Local Services"
        DOCKER[Docker]
        NEO4J_LOCAL[Neo4j Container]
    end
    
    subgraph "External Services"
        OPENAI_API[OpenAI API]
    end
    
    DEV --> IDE
    IDE --> VENV
    VENV --> STREAMLIT
    STREAMLIT --> NEO4J_LOCAL
    STREAMLIT --> OPENAI_API
    DOCKER --> NEO4J_LOCAL
    
    style DEV fill:#2ca02c
    style NEO4J_LOCAL fill:#d62728
    style OPENAI_API fill:#8c564b
```

## 🔧 Technologie-Stack

### Technologie-Layers

```
┌─────────────────────────────────────────┐
│         Frontend Layer                  │
│  ┌───────────────────────────────────┐ │
│  │      Streamlit UI                 │ │
│  │  - Parameter Input                │ │
│  │  - Visualization                  │ │
│  │  - Export Functions               │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│      Orchestration Layer                │
│  ┌───────────────────────────────────┐ │
│  │      LangGraph Workflow            │ │
│  │  - State Management                │ │
│  │  - Node Orchestration              │ │
│  │  - Conditional Edges              │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
┌───────────┐ ┌───────────┐ ┌───────────┐
│  Manager  │ │ Generator │ │  Critic   │
│   Agent   │ │   Agent   │ │   Agent   │
└───────────┘ └───────────┘ └───────────┘
        │           │           │
        └───────────┼───────────┘
                    ▼
┌─────────────────────────────────────────┐
│         Data Layer                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐│
│  │  Neo4j   │ │ ChromaDB │ │  OpenAI  ││
│  │  Graph   │ │  Vector  │ │   API    ││
│  └──────────┘ └──────────┘ └──────────┘│
└─────────────────────────────────────────┘
```

## 📈 Skalierungs-Architektur

### Zukünftige Erweiterungen

```mermaid
graph TB
    subgraph "Current MVP"
        C1[Single User]
        C2[Local Neo4j]
        C3[Streamlit Frontend]
    end
    
    subgraph "Future: Multi-User"
        F1[User Management]
        F2[Project Sharing]
        F3[Collaboration]
    end
    
    subgraph "Future: Cloud"
        F4[Neo4j Cloud]
        F5[API Gateway]
        F6[Load Balancer]
    end
    
    C1 --> F1
    C2 --> F4
    C3 --> F5
    
    style C1 fill:#2ca02c
    style C2 fill:#2ca02c
    style C3 fill:#2ca02c
    style F1 fill:#ff7f0e
    style F4 fill:#ff7f0e
    style F5 fill:#ff7f0e
```

## 📝 Legende

### Farb-Codierung

- 🔵 **Blau**: Frontend/UI Komponenten
- 🟠 **Orange**: Orchestration/Workflow
- 🟢 **Grün**: Agenten
- 🔴 **Rot**: Datenbanken/Storage
- 🟣 **Lila**: Externe Services
- 🟤 **Braun**: LLM/API Services

### Diagramm-Typen

- **Mermaid**: Wird von GitHub und vielen Markdown-Viewern unterstützt
- **ASCII**: Fallback für einfache Text-Editoren
- **Flowcharts**: Für Prozess-Flows
- **State Diagrams**: Für FSM und Zustandsübergänge
- **Sequence Diagrams**: Für Interaktionen zwischen Komponenten

## 🔗 Verwandte Dokumentation

- [README.md](README.md) - Hauptdokumentation
- [STATUS.md](STATUS.md) - Feature-Status
- [SETUP.md](SETUP.md) - Setup-Anleitung

