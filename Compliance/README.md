# Compliance-Framework - Variable Compliance-Anforderungen

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2025-12-20

---

## Übersicht

Das Compliance-Framework ermöglicht es, verschiedene Compliance-Standards zu verwenden und zu validieren. Das System unterstützt:

- **DORA** (Digital Operational Resilience Act) - Standard
- **NIST** (NIST Cybersecurity Framework)
- **ISO 27001** (Information Security Management)
- **Custom Standards** (erweiterbar)

---

## Verwendung

### Basis-Verwendung

```python
from compliance import DORAComplianceFramework, ComplianceStandard

# DORA Framework initialisieren
dora_framework = DORAComplianceFramework()

# Inject validieren
result = dora_framework.validate_inject(
    inject_content="Ein SIEM-Alert wurde ausgelöst...",
    inject_phase="SUSPICIOUS_ACTIVITY",
    inject_metadata={
        "mitre_id": "T1595",
        "affected_assets": ["SRV-001"]
    }
)

print(f"Compliant: {result.is_compliant}")
print(f"Requirements met: {result.requirements_met}")
print(f"Requirements missing: {result.requirements_missing}")
```

### Mehrere Standards gleichzeitig

```python
from compliance import DORAComplianceFramework, NISTComplianceFramework, ISO27001ComplianceFramework
from compliance.base import ComplianceStandard

# Mehrere Frameworks initialisieren
frameworks = {
    ComplianceStandard.DORA: DORAComplianceFramework(),
    ComplianceStandard.NIST: NISTComplianceFramework(),
    ComplianceStandard.ISO27001: ISO27001ComplianceFramework()
}

# Validierung mit allen Standards
results = {}
for standard, framework in frameworks.items():
    results[standard.value] = framework.validate_inject(
        inject_content=inject.content,
        inject_phase=inject.phase.value,
        inject_metadata={...}
    )
```

### Im Critic Agent verwenden

```python
from agents.critic_agent import CriticAgent
from compliance.base import ComplianceStandard

# Critic Agent mit mehreren Standards initialisieren
critic = CriticAgent(
    compliance_standards=[
        ComplianceStandard.DORA,
        ComplianceStandard.NIST
    ]
)

# Validierung durchführen
result = critic.validate_inject(
    inject=inject,
    previous_injects=previous_injects,
    current_phase=current_phase,
    system_state=system_state,
    compliance_standards=[ComplianceStandard.DORA, ComplianceStandard.NIST]
)
```

---

## Verfügbare Standards

### DORA (Digital Operational Resilience Act)

**Anforderungen:**
- Risk Management Framework Testing
- Business Continuity Policy Testing
- Incident Response Plan Testing
- Recovery Plan Testing (optional)
- Critical Functions Coverage
- Realistic Scenario
- Documentation Adequacy (optional)

**Verwendung:**
```python
from compliance import DORAComplianceFramework

framework = DORAComplianceFramework()
result = framework.validate_inject(...)
```

### NIST Cybersecurity Framework

**Anforderungen:**
- Asset Management (Identify)
- Access Control (Protect)
- Security Event Detection (Detect)
- Response Planning (Respond)
- Recovery Planning (Recover, optional)

**Verwendung:**
```python
from compliance import NISTComplianceFramework

framework = NISTComplianceFramework()
result = framework.validate_inject(...)
```

### ISO 27001

**Anforderungen:**
- Information Security Policies
- Technical Vulnerability Management
- Management of Information Security Incidents
- Information Security Continuity

**Verwendung:**
```python
from compliance import ISO27001ComplianceFramework

framework = ISO27001ComplianceFramework()
result = framework.validate_inject(...)
```

---

## Custom Compliance-Standard erstellen

```python
from compliance.base import ComplianceFramework, ComplianceRequirement, ComplianceResult, ComplianceStandard

class CustomComplianceFramework(ComplianceFramework):
    def __init__(self):
        super().__init__(ComplianceStandard.CUSTOM)
    
    def _load_requirements(self) -> List[ComplianceRequirement]:
        return [
            ComplianceRequirement(
                requirement_id="CUSTOM_REQ_001",
                name="Custom Requirement",
                description="Beschreibung der Anforderung",
                category="Category",
                mandatory=True,
                validation_criteria=["Kriterium 1", "Kriterium 2"]
            )
        ]
    
    def validate_inject(
        self,
        inject_content: str,
        inject_phase: str,
        inject_metadata: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ComplianceResult:
        # Implementiere Validierungslogik
        return ComplianceResult(
            is_compliant=True,
            standard=ComplianceStandard.CUSTOM,
            requirements_met=["CUSTOM_REQ_001"],
            requirements_missing=[],
            warnings=[],
            details={}
        )
```

---

## Integration in Workflow

### WorkflowState erweitern

```python
from workflows.state_schema import WorkflowState
from compliance.base import ComplianceStandard

# Im WorkflowState hinzufügen:
compliance_standards: List[ComplianceStandard] = [ComplianceStandard.DORA]
```

### ScenarioWorkflow anpassen

```python
def __init__(
    self,
    neo4j_client: Neo4jClient,
    max_iterations: int = 10,
    compliance_standards: Optional[List[ComplianceStandard]] = None
):
    # ...
    self.critic_agent = CriticAgent(
        compliance_standards=compliance_standards or [ComplianceStandard.DORA]
    )
```

---

## API-Referenz

### ComplianceFramework (Basis-Klasse)

**Methoden:**
- `validate_inject()` - Validiert einen Inject
- `get_requirements()` - Gibt alle Anforderungen zurück
- `get_requirement_by_id()` - Gibt spezifische Anforderung zurück
- `get_requirements_by_category()` - Gibt Anforderungen nach Kategorie zurück

### ComplianceResult

**Felder:**
- `is_compliant: bool` - Ist der Inject compliant?
- `standard: ComplianceStandard` - Verwendeter Standard
- `requirements_met: List[str]` - Erfüllte Anforderungen
- `requirements_missing: List[str]` - Fehlende Anforderungen
- `warnings: List[str]` - Compliance-Warnungen
- `details: Dict[str, Any]` - Zusätzliche Details

---

**Letzte Aktualisierung:** 2025-12-20





