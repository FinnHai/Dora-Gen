# 🔍 Critic Agent Deep Truth Audit Log

Diese Datei enthält vollständige Audit-Trails für alle Critic-Validierungen.
Jeder Eintrag zeigt die exakten Inputs, den Generator-Draft, die LLM-Antwort und die finale Entscheidung.

---

## 🔍 Audit Entry: INJ-001
**Timestamp:** 2025-12-22T13:57:12.784879

### 1. The Ground Truth (What was in the DB?)
*Crucial: Dump the exact JSON inputs the Critic received.*

- **Active Assets in State:** `[
  "SRV-001",
  "SRV-002",
  "APP-001",
  "APP-002"
]`
- **Current Phase:** `SUSPICIOUS_ACTIVITY`
- **System State (Full Raw):**
```json
{
  "SRV-001": {
    "status": "offline",
    "entity_type": "Server",
    "name": "Domain Controller DC-01",
    "criticality": "standard",
    "last_updated": "2025-12-22T12:55:27.364000000+00:00",
    "last_updated_by_inject": "INJ-TEST",
    "id": "SRV-001",
    "type": "Server"
  },
  "SRV-002": {
    "status": "online",
    "entity_type": "Server",
    "name": "Application Server APP-SRV-01",
    "criticality": "standard",
    "id": "SRV-002",
    "type": "Server"
  },
  "APP-001": {
    "status": "online",
    "entity_type": "Application",
    "name": "Payment Processing System",
    "criticality": "standard",
    "id": "APP-001",
    "type": "Application"
  },
  "APP-002": {
    "status": "online",
    "entity_type": "Application",
    "name": "Customer Database",
    "criticality": "standard",
    "id": "APP-002",
    "type": "Application"
  }
}
```
- **System State (Formatted - wie an LLM gesendet):**
```
- Domain Controller DC-01 (SRV-001, Server): offline
- Application Server APP-SRV-01 (SRV-002, Server): online
- Payment Processing System (APP-001, Application): online
- Customer Database (APP-002, Application): online

⚠️ KRITISCH - VERFÜGBARE ASSET-IDs (NUR DIESE VERWENDEN!): SRV-001, SRV-002, APP-001, APP-002
❌ VERBOTEN: Erstelle KEINE neuen Assets! Verwende NUR die oben genannten Asset-IDs!
```
- **Previous Injects (Full History):**
```json
[]
```
- **Defined Rules:**
  - **FSM Transition Rules:** Valid transitions from `SUSPICIOUS_ACTIVITY` → `['INITIAL_INCIDENT', 'NORMAL_OPERATION']`
  - **State Consistency:** Assets must exist in system_state (checked against: `['SRV-001', 'SRV-002', 'APP-001', 'APP-002']`)
  - **Temporal Consistency:** Time offsets must be chronological
  - **Logical Consistency:** No contradictions with previous injects
  - **Causal Validity:** MITRE techniques must be technically possible (only truly impossible sequences block)

### 2. The Generator's Draft
```json
{
  "inject_id": "INJ-001",
  "time_offset": "T+00:00:15",
  "phase": "SUSPICIOUS_ACTIVITY",
  "source": "Blue Team / SOC",
  "target": "Blue Team / SOC",
  "modality": "SIEM Alert",
  "content": "SIEM-Systeme haben einen ungewöhnlich hohen Datenverkehr von SRV-002 (APP-SRV-01) zu mehreren externen IP-Adressen festgestellt. Diese Netzwerkaktivität könnte auf ein aktives Scanning oder einen Datenexfiltrationsversuch hindeuten. Mehrere fehlgeschlagene Anmeldeversuche wurden ebenfalls auf SRV-002 registriert, was auf verdächtige Zugriffsversuche hinweist.",
  "technical_metadata": {
    "mitre_id": "T1595",
    "affected_assets": [
      "SRV-002",
      "APP-002"
    ],
    "ioc_hash": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "ioc_ip": "192.0.2.1",
    "ioc_domain": "malicious-domain.com",
    "severity": "High"
  },
  "dora_compliance_tag": null,
  "business_impact": "Der Zugriff auf die Customer Database (APP-002) ist beeinträchtigt, was die Bearbeitung von Kundenanfragen verzögern könnte, und die Sicherheit sensibler Kundendaten ist möglicherweise gefährdet."
}
```

### 3. The Critic's Reasoning (Raw LLM Output)
*Crucial: What did the LLM actually say before parsing?*

```
```json
{
    "logical_consistency": false,
    "regulatory_compliance": true,
    "causal_validity": true,
    "errors": ["Affected Asset 'APP-002' ist inkonsistent, da es im Inject nicht erwähnt wird. Es gibt keine Hinweise darauf, dass APP-002 von der beschriebenen Aktivität betroffen ist."],
    "warnings": []
}
```
```

### 4. The Verdict
- **Decision:** ❌ INVALID
- **Detected Errors:** [
  "Affected Asset 'APP-002' ist inkonsistent, da es im Inject nicht erwähnt wird. Es gibt keine Hinweise darauf, dass APP-002 von der beschriebenen Aktivität betroffen ist."
]
- **Warnings:** [
  "Name mismatch for APP-002: Content may use different name than 'Customer Database', but ID is valid. Proceeding."
]
- **Validation Details:**
  - Pydantic Valid: `True`
  - FSM Valid: `True`
  - State Valid: `True`
  - Temporal Valid: `True`
  - Logical Consistency: `False`
  - Causal Validity: `True`
  - Causal Blocking: `False`

***

## 🔍 Audit Entry: INJ-001
**Timestamp:** 2025-12-22T13:57:22.572014

### 1. The Ground Truth (What was in the DB?)
*Crucial: Dump the exact JSON inputs the Critic received.*

- **Active Assets in State:** `[
  "SRV-001",
  "SRV-002",
  "APP-001",
  "APP-002"
]`
- **Current Phase:** `SUSPICIOUS_ACTIVITY`
- **System State (Full Raw):**
```json
{
  "SRV-001": {
    "status": "offline",
    "entity_type": "Server",
    "name": "Domain Controller DC-01",
    "criticality": "standard",
    "last_updated": "2025-12-22T12:55:27.364000000+00:00",
    "last_updated_by_inject": "INJ-TEST",
    "id": "SRV-001",
    "type": "Server"
  },
  "SRV-002": {
    "status": "online",
    "entity_type": "Server",
    "name": "Application Server APP-SRV-01",
    "criticality": "standard",
    "id": "SRV-002",
    "type": "Server"
  },
  "APP-001": {
    "status": "online",
    "entity_type": "Application",
    "name": "Payment Processing System",
    "criticality": "standard",
    "id": "APP-001",
    "type": "Application"
  },
  "APP-002": {
    "status": "online",
    "entity_type": "Application",
    "name": "Customer Database",
    "criticality": "standard",
    "id": "APP-002",
    "type": "Application"
  }
}
```
- **System State (Formatted - wie an LLM gesendet):**
```
- Domain Controller DC-01 (SRV-001, Server): offline
- Application Server APP-SRV-01 (SRV-002, Server): online
- Payment Processing System (APP-001, Application): online
- Customer Database (APP-002, Application): online

⚠️ KRITISCH - VERFÜGBARE ASSET-IDs (NUR DIESE VERWENDEN!): SRV-001, SRV-002, APP-001, APP-002
❌ VERBOTEN: Erstelle KEINE neuen Assets! Verwende NUR die oben genannten Asset-IDs!
```
- **Previous Injects (Full History):**
```json
[]
```
- **Defined Rules:**
  - **FSM Transition Rules:** Valid transitions from `SUSPICIOUS_ACTIVITY` → `['INITIAL_INCIDENT', 'NORMAL_OPERATION']`
  - **State Consistency:** Assets must exist in system_state (checked against: `['SRV-001', 'SRV-002', 'APP-001', 'APP-002']`)
  - **Temporal Consistency:** Time offsets must be chronological
  - **Logical Consistency:** No contradictions with previous injects
  - **Causal Validity:** MITRE techniques must be technically possible (only truly impossible sequences block)

### 2. The Generator's Draft
```json
{
  "inject_id": "INJ-001",
  "time_offset": "T+00:00:30",
  "phase": "SUSPICIOUS_ACTIVITY",
  "source": "Blue Team / SOC",
  "target": "Blue Team / SOC",
  "modality": "SIEM Alert",
  "content": "Das Überwachungssystem meldet ungewöhnlichen Datenverkehr von SRV-002 zu externen IP-Adressen. Mehrere fehlgeschlagene Login-Versuche wurden ebenfalls bei SRV-002 registriert. Zudem berichten Benutzer über langsamen Zugriff auf die Customer Database (APP-002). Erste Untersuchungen zeigen, dass einige Workstations gesperrte Dateien mit Lösegeldforderungen aufweisen.",
  "technical_metadata": {
    "mitre_id": "T1595",
    "affected_assets": [
      "SRV-002",
      "APP-002"
    ],
    "ioc_hash": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yza567bcd890efg1",
    "ioc_ip": "192.168.100.100",
    "ioc_domain": "malicious-domain.com",
    "severity": "High"
  },
  "dora_compliance_tag": null,
  "business_impact": "Unterbrechung kritischer Geschäftsprozesse durch den eingeschränkten Zugriff auf die Customer Database und gesperrte Dateien."
}
```

### 3. The Critic's Reasoning (Raw LLM Output)
*Crucial: What did the LLM actually say before parsing?*

```
```json
{
    "logical_consistency": true,
    "regulatory_compliance": false,
    "causal_validity": true,
    "errors": [],
    "warnings": []
}
```
```

### 4. The Verdict
- **Decision:** ✅ VALID
- **Detected Errors:** []
- **Warnings:** [
  "Regulatorische Aspekte könnten besser abgedeckt sein (optional)"
]
- **Validation Details:**
  - Pydantic Valid: `True`
  - FSM Valid: `True`
  - State Valid: `True`
  - Temporal Valid: `True`
  - Logical Consistency: `True`
  - Causal Validity: `True`
  - Causal Blocking: `False`

***

## 🔍 Audit Entry: INJ-001
**Timestamp:** 2025-12-22T13:58:32.806106

### 1. The Ground Truth (What was in the DB?)
*Crucial: Dump the exact JSON inputs the Critic received.*

- **Active Assets in State:** `[
  "SRV-001",
  "SRV-002",
  "APP-001",
  "APP-002"
]`
- **Current Phase:** `SUSPICIOUS_ACTIVITY`
- **System State (Full Raw):**
```json
{
  "SRV-001": {
    "status": "offline",
    "entity_type": "Server",
    "name": "Domain Controller DC-01",
    "criticality": "standard",
    "last_updated": "2025-12-22T12:58:14.374000000+00:00",
    "last_updated_by_inject": "INJ-TEST",
    "id": "SRV-001",
    "type": "Server"
  },
  "SRV-002": {
    "status": "online",
    "entity_type": "Server",
    "name": "Application Server APP-SRV-01",
    "criticality": "standard",
    "id": "SRV-002",
    "type": "Server"
  },
  "APP-001": {
    "status": "online",
    "entity_type": "Application",
    "name": "Payment Processing System",
    "criticality": "standard",
    "id": "APP-001",
    "type": "Application"
  },
  "APP-002": {
    "status": "online",
    "entity_type": "Application",
    "name": "Customer Database",
    "criticality": "standard",
    "id": "APP-002",
    "type": "Application"
  }
}
```
- **System State (Formatted - wie an LLM gesendet):**
```
- Domain Controller DC-01 (SRV-001, Server): offline
- Application Server APP-SRV-01 (SRV-002, Server): online
- Payment Processing System (APP-001, Application): online
- Customer Database (APP-002, Application): online

⚠️ KRITISCH - VERFÜGBARE ASSET-IDs (NUR DIESE VERWENDEN!): SRV-001, SRV-002, APP-001, APP-002
❌ VERBOTEN: Erstelle KEINE neuen Assets! Verwende NUR die oben genannten Asset-IDs!
```
- **Previous Injects (Full History):**
```json
[]
```
- **Defined Rules:**
  - **FSM Transition Rules:** Valid transitions from `SUSPICIOUS_ACTIVITY` → `['INITIAL_INCIDENT', 'NORMAL_OPERATION']`
  - **State Consistency:** Assets must exist in system_state (checked against: `['SRV-001', 'SRV-002', 'APP-001', 'APP-002']`)
  - **Temporal Consistency:** Time offsets must be chronological
  - **Logical Consistency:** No contradictions with previous injects
  - **Causal Validity:** MITRE techniques must be technically possible (only truly impossible sequences block)

### 2. The Generator's Draft
```json
{
  "inject_id": "INJ-001",
  "time_offset": "T+00:00:15",
  "phase": "SUSPICIOUS_ACTIVITY",
  "source": "Blue Team / SOC",
  "target": "Management",
  "modality": "SIEM Alert",
  "content": "Ungewöhnlich hohe Netzwerkaktivität wurde von einem unbekannten IP-Bereich auf den Servern APP-SRV-01 (SRV-002) und APP-002 festgestellt. Mehrere fehlgeschlagene Anmeldeversuche auf SRV-002 weisen auf potenziellen unautorisierten Zugang hin. Dringende Untersuchung erforderlich.",
  "technical_metadata": {
    "mitre_id": "T1595",
    "affected_assets": [
      "SRV-002",
      "APP-002"
    ],
    "ioc_hash": "3f2a5d6a7c2e0b4d4a5e6b7d8c9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7",
    "ioc_ip": "192.168.1.100",
    "ioc_domain": "suspicious-domain.com",
    "severity": "High"
  },
  "dora_compliance_tag": null,
  "business_impact": "Beeinträchtigung des Zugriffs auf die Customer Database (APP-002) behindert kritische Geschäftsprozesse."
}
```

### 3. The Critic's Reasoning (Raw LLM Output)
*Crucial: What did the LLM actually say before parsing?*

```
```json
{
    "logical_consistency": true,
    "regulatory_compliance": false,
    "causal_validity": true,
    "errors": [],
    "warnings": []
}
```
```

### 4. The Verdict
- **Decision:** ✅ VALID
- **Detected Errors:** []
- **Warnings:** [
  "Regulatorische Aspekte könnten besser abgedeckt sein (optional)"
]
- **Validation Details:**
  - Pydantic Valid: `True`
  - FSM Valid: `True`
  - State Valid: `True`
  - Temporal Valid: `True`
  - Logical Consistency: `True`
  - Causal Validity: `True`
  - Causal Blocking: `False`

***

## 🔍 Audit Entry: INJ-001
**Timestamp:** 2025-12-22T14:07:50.973008

### 1. The Ground Truth (What was in the DB?)
*Crucial: Dump the exact JSON inputs the Critic received.*

- **Active Assets in State:** `[
  "SRV-001",
  "SRV-002",
  "APP-001",
  "APP-002"
]`
- **Current Phase:** `SUSPICIOUS_ACTIVITY`
- **System State (Full Raw):**
```json
{
  "SRV-001": {
    "status": "compromised",
    "entity_type": "Server",
    "name": "Domain Controller DC-01",
    "criticality": "standard",
    "last_updated": "2025-12-22T12:59:51.694000000+00:00",
    "last_updated_by_inject": "INJ-003",
    "id": "SRV-001",
    "type": "Server"
  },
  "SRV-002": {
    "status": "compromised",
    "entity_type": "Server",
    "name": "Application Server APP-SRV-01",
    "criticality": "standard",
    "last_updated": "2025-12-22T12:59:51.837000000+00:00",
    "last_updated_by_inject": "INJ-003",
    "id": "SRV-002",
    "type": "Server"
  },
  "APP-001": {
    "status": "suspicious",
    "entity_type": "Application",
    "name": "Payment Processing System",
    "criticality": "standard",
    "last_updated": "2025-12-22T12:59:06.543000000+00:00",
    "last_updated_by_inject": "INJ-002",
    "id": "APP-001",
    "type": "Application"
  },
  "APP-002": {
    "status": "degraded",
    "entity_type": "Application",
    "name": "Customer Database",
    "criticality": "standard",
    "last_updated": "2025-12-22T12:58:32.979000000+00:00",
    "last_updated_by_inject": "INJ-001",
    "id": "APP-002",
    "type": "Application"
  }
}
```
- **System State (Formatted - wie an LLM gesendet):**
```
- Domain Controller DC-01 (SRV-001, Server): compromised
- Application Server APP-SRV-01 (SRV-002, Server): compromised
- Payment Processing System (APP-001, Application): suspicious
- Customer Database (APP-002, Application): degraded

⚠️ KRITISCH - VERFÜGBARE ASSET-IDs (NUR DIESE VERWENDEN!): SRV-001, SRV-002, APP-001, APP-002
❌ VERBOTEN: Erstelle KEINE neuen Assets! Verwende NUR die oben genannten Asset-IDs!
```
- **Previous Injects (Full History):**
```json
[]
```
- **Defined Rules:**
  - **FSM Transition Rules:** Valid transitions from `SUSPICIOUS_ACTIVITY` → `['INITIAL_INCIDENT', 'NORMAL_OPERATION']`
  - **State Consistency:** Assets must exist in system_state (checked against: `['SRV-001', 'SRV-002', 'APP-001', 'APP-002']`)
  - **Temporal Consistency:** Time offsets must be chronological
  - **Logical Consistency:** No contradictions with previous injects
  - **Causal Validity:** MITRE techniques must be technically possible (only truly impossible sequences block)

### 2. The Generator's Draft
```json
{
  "inject_id": "INJ-001",
  "time_offset": "T+00:00:15",
  "phase": "SUSPICIOUS_ACTIVITY",
  "source": "Blue Team / SOC",
  "target": "Blue Team / SOC",
  "modality": "SIEM Alert",
  "content": "Unsere Netzwerküberwachungssoftware hat eine ungewöhnliche Erhöhung des eingehenden Datenverkehrs auf dem Payment Processing System (APP-001) festgestellt. Dies könnte ein Anzeichen für einen DDoS-Angriff sein. Ebenfalls wurden verdächtige Zugangsmuster zur Kunden-Datenbank (APP-002) und Anomalien im Zugriff auf den Domain Controller (SRV-001) protokolliert.",
  "technical_metadata": {
    "mitre_id": "T1595",
    "affected_assets": [
      "APP-001",
      "APP-002",
      "SRV-001"
    ],
    "ioc_hash": "d41d8cd98f00b204e9800998ecf8427e",
    "ioc_ip": "192.168.10.15",
    "ioc_domain": "malicious-traffic.example.com",
    "severity": "High"
  },
  "dora_compliance_tag": null,
  "business_impact": "Kritische Funktionen des Zahlungsverkehrs sind bedroht, was zu potenziellen Transaktionsausfällen führen kann."
}
```

### 3. The Critic's Reasoning (Raw LLM Output)
*Crucial: What did the LLM actually say before parsing?*

```
```json
{
    "logical_consistency": true,
    "regulatory_compliance": false,
    "causal_validity": true,
    "errors": [],
    "warnings": []
}
```
```

### 4. The Verdict
- **Decision:** ✅ VALID
- **Detected Errors:** []
- **Warnings:** [
  "Regulatorische Aspekte könnten besser abgedeckt sein (optional)",
  "DORA Compliance: DORA_Art25_BusinessContinuity, DORA_Art25_RecoveryPlan, DORA_Art25_DocumentationAdequacy fehlen",
  "DORA: Business Continuity könnte stärker betont werden",
  "DORA: Recovery Plan sollte in Betracht gezogen werden",
  "DORA: Dokumentation zur Unterstützung der Szenario-Analyse fehlt",
  "Qualitäts-Score könnte verbessert werden: 0.84"
]
- **Validation Details:**
  - Pydantic Valid: `True`
  - FSM Valid: `True`
  - State Valid: `True`
  - Temporal Valid: `True`
  - Logical Consistency: `True`
  - Causal Validity: `True`
  - Causal Blocking: `False`

***

## 🔍 Audit Entry: INJ-009
**Timestamp:** 2025-12-22T14:14:31.655411

### 1. The Ground Truth (What was in the DB?)
*Crucial: Dump the exact JSON inputs the Critic received.*

- **Active Assets in State:** `[
  "SRV-001",
  "SRV-002",
  "APP-001",
  "APP-002"
]`
- **Current Phase:** `INITIAL_INCIDENT`
- **System State (Full Raw):**
```json
{
  "SRV-001": {
    "status": "degraded",
    "entity_type": "Server",
    "name": "Domain Controller DC-01",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:13:55.225000000+00:00",
    "last_updated_by_inject": "INJ-008",
    "id": "SRV-001",
    "type": "Server"
  },
  "SRV-002": {
    "status": "degraded",
    "entity_type": "Server",
    "name": "Application Server APP-SRV-01",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:13:55.270000000+00:00",
    "last_updated_by_inject": "INJ-008",
    "id": "SRV-002",
    "type": "Server"
  },
  "APP-001": {
    "status": "compromised",
    "entity_type": "Application",
    "name": "Payment Processing System",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:11:26.073000000+00:00",
    "last_updated_by_inject": "INJ-005",
    "id": "APP-001",
    "type": "Application"
  },
  "APP-002": {
    "status": "compromised",
    "entity_type": "Application",
    "name": "Customer Database",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:12:23.237000000+00:00",
    "last_updated_by_inject": "INJ-006",
    "id": "APP-002",
    "type": "Application"
  }
}
```
- **System State (Formatted - wie an LLM gesendet):**
```
- Domain Controller DC-01 (SRV-001, Server): degraded
- Application Server APP-SRV-01 (SRV-002, Server): degraded
- Payment Processing System (APP-001, Application): compromised
- Customer Database (APP-002, Application): compromised

⚠️ KRITISCH - VERFÜGBARE ASSET-IDs (NUR DIESE VERWENDEN!): SRV-001, SRV-002, APP-001, APP-002
❌ VERBOTEN: Erstelle KEINE neuen Assets! Verwende NUR die oben genannten Asset-IDs!
```
- **Previous Injects (Full History):**
```json
[
  {
    "inject_id": "INJ-001",
    "time_offset": "T+00:00:15",
    "phase": "SUSPICIOUS_ACTIVITY",
    "content": "Unsere Netzwerküberwachungssoftware hat eine ungewöhnliche Erhöhung des eingehenden Datenverkehrs auf dem Payment Processing System (APP-001) festgestellt. Dies könnte ein Anzeichen für einen DDoS-Angriff sein. Ebenfalls wurden verdächtige Zugangsmuster zur Kunden-Datenbank (APP-002) und Anomalien im Zugriff auf den Domain Controller (SRV-001) protokolliert.",
    "affected_assets": [
      "APP-001",
      "APP-002",
      "SRV-001"
    ],
    "mitre_id": "T1595"
  },
  {
    "inject_id": "INJ-002",
    "time_offset": "T+00:00:45",
    "phase": "INITIAL_INCIDENT",
    "content": "Ein massiver Anstieg des Netzwerkverkehrs ist zum Application Server (SRV-002) zu verzeichnen. Verdächtige IP-Adressen senden kontinuierlich Anfragen an das Payment Processing System (APP-001) und die Customer Database (APP-002). Der Datenverkehr hat die Kapazität des Netzwerks erreicht, was zu erheblichen Verzögerungen und Ausfällen führt.",
    "affected_assets": [
      "SRV-002",
      "APP-001",
      "APP-002"
    ],
    "mitre_id": "T1546.014"
  },
  {
    "inject_id": "INJ-003",
    "time_offset": "T+00:02:00",
    "phase": "ESCALATION_CRISIS",
    "content": "Die DDoS-Attacke hat sich intensiviert und führt zu einer kritischen Systembelastung. Der Domain Controller (SRV-001) meldet eine signifikante Zunahme von Authentifizierungsfehlern, was auf mögliche Brute-Force-Angriffe hinweist. Das Payment Processing System (APP-001) zeigt verzögerte Transaktionen und Abbrüche. Mehrere Abteilungen berichten über Schwierigkeiten beim Zugriff auf die Customer Database (APP-002), was die Kundenservice-Leistung beeinträchtigt.",
    "affected_assets": [
      "SRV-001",
      "APP-001",
      "APP-002"
    ],
    "mitre_id": "T1020"
  },
  {
    "inject_id": "INJ-004",
    "time_offset": "T+00:04:00",
    "phase": "CONTAINMENT",
    "content": "Das IT-Sicherheitsteam hat eine Notfallwiederherstellungsprozedur für den Domain Controller (SRV-001) eingeleitet, um die Authentifizierungssysteme zu stabilisieren. Der Application Server (SRV-002) wurde isoliert und unterliegt einer forensischen Analyse. Unsere Zahlungsteams arbeiten daran, alternative Zahlungsabwicklungen durchzuführen, während das Payment Processing System (APP-001) offline bleibt. Die Customer Database (APP-002) wird aus Backups wiederhergestellt, um die Geschäftskontinuität zu sichern.",
    "affected_assets": [
      "SRV-001",
      "SRV-002",
      "APP-001",
      "APP-002"
    ],
    "mitre_id": "T1480"
  },
  {
    "inject_id": "INJ-005",
    "time_offset": "T+00:06:00",
    "phase": "ESCALATION_CRISIS",
    "content": "Es wurde ein massiver Anstieg des Datenverkehrs auf den Application Server (SRV-002) und das Payment Processing System (APP-001) festgestellt. Ungewöhnliche Anmeldemuster auf dem Domain Controller (SRV-001) deuten auf eine Ausweitung des Angriffs hin. Wir haben ein kritisches Sicherheitsteam-Meeting einberufen, um Notfallmaßnahmen zu koordinieren. Die IT-Abteilung wurde angewiesen, alle nicht notwendigen Netzwerkverbindungen zu kappen und kompromittierte Systeme vom Netz zu nehmen. Einige Kunden melden Schwierigkeiten beim Zugriff auf ihre Konten, was auf eine Beeinträchtigung der Customer Database (APP-002) hindeutet.",
    "affected_assets": [
      "SRV-002",
      "APP-001",
      "SRV-001",
      "APP-002"
    ],
    "mitre_id": "T1020"
  },
  {
    "inject_id": "INJ-006",
    "time_offset": "T+00:07:00",
    "phase": "CONTAINMENT",
    "content": "Das Incident Response Team hat den Netzwerkverkehr erfolgreich über spezialisierte DDoS-Protection-Systeme umgeleitet, um die Last auf den Servern zu minimieren. Der Domain Controller DC-01 (SRV-001) wurde isoliert, um die weitere Ausbreitung der Kompromittierung zu verhindern. Der Zugang zur Customer Database (APP-002) ist vorübergehend gesperrt, um Datenabflüsse zu verhindern.",
    "affected_assets": [
      "SRV-001",
      "APP-002"
    ],
    "mitre_id": "T1480"
  },
  {
    "inject_id": "INJ-007",
    "time_offset": "T+00:10:00",
    "phase": "RECOVERY",
    "content": "Nach der erfolgreichen Eindämmung des Angriffs wird nun die Recovery-Phase eingeleitet. Der Domain Controller (SRV-001) wird aus den neuesten Backups wiederhergestellt, um die Domänenverwaltung zu stabilisieren. Parallel dazu wird auf dem Application Server (SRV-002) eine eingehende forensische Analyse durchgeführt, um eventuell verbliebene bösartige Aktivitäten auszuschließen.",
    "affected_assets": [
      "SRV-001",
      "SRV-002"
    ],
    "mitre_id": "T1490"
  },
  {
    "inject_id": "INJ-008",
    "time_offset": "T+00:14:00",
    "phase": "NORMAL_OPERATION",
    "content": "Ein SIEM-Alarm meldet ungewöhnlich hohe Netzwerkaktivität auf dem Domain Controller (SRV-001). Weitere Analysen zeigen, dass gezielte Port-Scans durchgeführt werden, was auf eine aktive Erkundungsphase hinweist.",
    "affected_assets": [
      "SRV-001",
      "SRV-002"
    ],
    "mitre_id": "T1595"
  }
]
```
- **Defined Rules:**
  - **FSM Transition Rules:** Valid transitions from `INITIAL_INCIDENT` → `['ESCALATION_CRISIS', 'CONTAINMENT']`
  - **State Consistency:** Assets must exist in system_state (checked against: `['SRV-001', 'SRV-002', 'APP-001', 'APP-002']`)
  - **Temporal Consistency:** Time offsets must be chronological
  - **Logical Consistency:** No contradictions with previous injects
  - **Causal Validity:** MITRE techniques must be technically possible (only truly impossible sequences block)

### 2. The Generator's Draft
```json
{
  "inject_id": "INJ-009",
  "time_offset": "T+00:04:45",
  "phase": "INITIAL_INCIDENT",
  "source": "Blue Team / SOC",
  "target": "Management",
  "modality": "SIEM Alert",
  "content": "Ein plötzlicher und intensiver Anstieg des eingehenden Datenverkehrs überlastet die Netzwerk-Firewalls und führt zu einem vollständigen Ausfall des Domain Controllers (SRV-001). Der Application Server (SRV-002) zeigt signifikante Leistungseinbußen. Kritische Geschäftsfunktionen sind stark beeinträchtigt.",
  "technical_metadata": {
    "mitre_id": "T1546.014",
    "affected_assets": [
      "SRV-001",
      "SRV-002"
    ],
    "ioc_hash": "b1946ac92492d2347c6235b4d2611184",
    "ioc_ip": "192.168.1.100",
    "ioc_domain": "malicious-site.com",
    "severity": "Critical"
  },
  "dora_compliance_tag": null,
  "business_impact": "Der Ausfall des Domain Controllers (SRV-001) und die Überlastung des Application Servers (SRV-002) führen dazu, dass Authentifizierungsdienste und wichtige Unternehmensanwendungen nicht mehr verfügbar sind. Dies beeinträchtigt die Fähigkeit des Unternehmens, Transaktionen abzuwickeln und den Kundenservice aufrechtzuerhalten, was zu einem erheblichen Umsatzverlust führt."
}
```

### 3. The Critic's Reasoning (Raw LLM Output)
*Crucial: What did the LLM actually say before parsing?*

```
Temporaler Fehler - kein LLM-Call
```

### 4. The Verdict
- **Decision:** ❌ INVALID
- **Detected Errors:** [
  "Temporale Inkonsistenz: Inject INJ-009 hat Zeitstempel T+00:04:45, aber vorheriger Inject INJ-005 hat T+00:06:00 (später). Zeitstempel müssen chronologisch sein."
]
- **Warnings:** []
- **Validation Details:**
  - Pydantic Valid: `True`
  - FSM Valid: `True`
  - State Valid: `True`
  - Temporal Valid: `False`
  - Logical Consistency: `False`
  - Causal Validity: `True`
  - Causal Blocking: `False`

***

## 🔍 Audit Entry: INJ-010
**Timestamp:** 2025-12-22T14:14:48.931373

### 1. The Ground Truth (What was in the DB?)
*Crucial: Dump the exact JSON inputs the Critic received.*

- **Active Assets in State:** `[
  "SRV-001",
  "SRV-002",
  "APP-001",
  "APP-002"
]`
- **Current Phase:** `ESCALATION_CRISIS`
- **System State (Full Raw):**
```json
{
  "SRV-001": {
    "status": "suspicious",
    "entity_type": "Server",
    "name": "Domain Controller DC-01",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:14:31.688000000+00:00",
    "last_updated_by_inject": "INJ-009",
    "id": "SRV-001",
    "type": "Server"
  },
  "SRV-002": {
    "status": "suspicious",
    "entity_type": "Server",
    "name": "Application Server APP-SRV-01",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:14:31.720000000+00:00",
    "last_updated_by_inject": "INJ-009",
    "id": "SRV-002",
    "type": "Server"
  },
  "APP-001": {
    "status": "compromised",
    "entity_type": "Application",
    "name": "Payment Processing System",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:11:26.073000000+00:00",
    "last_updated_by_inject": "INJ-005",
    "id": "APP-001",
    "type": "Application"
  },
  "APP-002": {
    "status": "compromised",
    "entity_type": "Application",
    "name": "Customer Database",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:12:23.237000000+00:00",
    "last_updated_by_inject": "INJ-006",
    "id": "APP-002",
    "type": "Application"
  }
}
```
- **System State (Formatted - wie an LLM gesendet):**
```
- Domain Controller DC-01 (SRV-001, Server): suspicious
- Application Server APP-SRV-01 (SRV-002, Server): suspicious
- Payment Processing System (APP-001, Application): compromised
- Customer Database (APP-002, Application): compromised

⚠️ KRITISCH - VERFÜGBARE ASSET-IDs (NUR DIESE VERWENDEN!): SRV-001, SRV-002, APP-001, APP-002
❌ VERBOTEN: Erstelle KEINE neuen Assets! Verwende NUR die oben genannten Asset-IDs!
```
- **Previous Injects (Full History):**
```json
[
  {
    "inject_id": "INJ-001",
    "time_offset": "T+00:00:15",
    "phase": "SUSPICIOUS_ACTIVITY",
    "content": "Unsere Netzwerküberwachungssoftware hat eine ungewöhnliche Erhöhung des eingehenden Datenverkehrs auf dem Payment Processing System (APP-001) festgestellt. Dies könnte ein Anzeichen für einen DDoS-Angriff sein. Ebenfalls wurden verdächtige Zugangsmuster zur Kunden-Datenbank (APP-002) und Anomalien im Zugriff auf den Domain Controller (SRV-001) protokolliert.",
    "affected_assets": [
      "APP-001",
      "APP-002",
      "SRV-001"
    ],
    "mitre_id": "T1595"
  },
  {
    "inject_id": "INJ-002",
    "time_offset": "T+00:00:45",
    "phase": "INITIAL_INCIDENT",
    "content": "Ein massiver Anstieg des Netzwerkverkehrs ist zum Application Server (SRV-002) zu verzeichnen. Verdächtige IP-Adressen senden kontinuierlich Anfragen an das Payment Processing System (APP-001) und die Customer Database (APP-002). Der Datenverkehr hat die Kapazität des Netzwerks erreicht, was zu erheblichen Verzögerungen und Ausfällen führt.",
    "affected_assets": [
      "SRV-002",
      "APP-001",
      "APP-002"
    ],
    "mitre_id": "T1546.014"
  },
  {
    "inject_id": "INJ-003",
    "time_offset": "T+00:02:00",
    "phase": "ESCALATION_CRISIS",
    "content": "Die DDoS-Attacke hat sich intensiviert und führt zu einer kritischen Systembelastung. Der Domain Controller (SRV-001) meldet eine signifikante Zunahme von Authentifizierungsfehlern, was auf mögliche Brute-Force-Angriffe hinweist. Das Payment Processing System (APP-001) zeigt verzögerte Transaktionen und Abbrüche. Mehrere Abteilungen berichten über Schwierigkeiten beim Zugriff auf die Customer Database (APP-002), was die Kundenservice-Leistung beeinträchtigt.",
    "affected_assets": [
      "SRV-001",
      "APP-001",
      "APP-002"
    ],
    "mitre_id": "T1020"
  },
  {
    "inject_id": "INJ-004",
    "time_offset": "T+00:04:00",
    "phase": "CONTAINMENT",
    "content": "Das IT-Sicherheitsteam hat eine Notfallwiederherstellungsprozedur für den Domain Controller (SRV-001) eingeleitet, um die Authentifizierungssysteme zu stabilisieren. Der Application Server (SRV-002) wurde isoliert und unterliegt einer forensischen Analyse. Unsere Zahlungsteams arbeiten daran, alternative Zahlungsabwicklungen durchzuführen, während das Payment Processing System (APP-001) offline bleibt. Die Customer Database (APP-002) wird aus Backups wiederhergestellt, um die Geschäftskontinuität zu sichern.",
    "affected_assets": [
      "SRV-001",
      "SRV-002",
      "APP-001",
      "APP-002"
    ],
    "mitre_id": "T1480"
  },
  {
    "inject_id": "INJ-005",
    "time_offset": "T+00:06:00",
    "phase": "ESCALATION_CRISIS",
    "content": "Es wurde ein massiver Anstieg des Datenverkehrs auf den Application Server (SRV-002) und das Payment Processing System (APP-001) festgestellt. Ungewöhnliche Anmeldemuster auf dem Domain Controller (SRV-001) deuten auf eine Ausweitung des Angriffs hin. Wir haben ein kritisches Sicherheitsteam-Meeting einberufen, um Notfallmaßnahmen zu koordinieren. Die IT-Abteilung wurde angewiesen, alle nicht notwendigen Netzwerkverbindungen zu kappen und kompromittierte Systeme vom Netz zu nehmen. Einige Kunden melden Schwierigkeiten beim Zugriff auf ihre Konten, was auf eine Beeinträchtigung der Customer Database (APP-002) hindeutet.",
    "affected_assets": [
      "SRV-002",
      "APP-001",
      "SRV-001",
      "APP-002"
    ],
    "mitre_id": "T1020"
  },
  {
    "inject_id": "INJ-006",
    "time_offset": "T+00:07:00",
    "phase": "CONTAINMENT",
    "content": "Das Incident Response Team hat den Netzwerkverkehr erfolgreich über spezialisierte DDoS-Protection-Systeme umgeleitet, um die Last auf den Servern zu minimieren. Der Domain Controller DC-01 (SRV-001) wurde isoliert, um die weitere Ausbreitung der Kompromittierung zu verhindern. Der Zugang zur Customer Database (APP-002) ist vorübergehend gesperrt, um Datenabflüsse zu verhindern.",
    "affected_assets": [
      "SRV-001",
      "APP-002"
    ],
    "mitre_id": "T1480"
  },
  {
    "inject_id": "INJ-007",
    "time_offset": "T+00:10:00",
    "phase": "RECOVERY",
    "content": "Nach der erfolgreichen Eindämmung des Angriffs wird nun die Recovery-Phase eingeleitet. Der Domain Controller (SRV-001) wird aus den neuesten Backups wiederhergestellt, um die Domänenverwaltung zu stabilisieren. Parallel dazu wird auf dem Application Server (SRV-002) eine eingehende forensische Analyse durchgeführt, um eventuell verbliebene bösartige Aktivitäten auszuschließen.",
    "affected_assets": [
      "SRV-001",
      "SRV-002"
    ],
    "mitre_id": "T1490"
  },
  {
    "inject_id": "INJ-008",
    "time_offset": "T+00:14:00",
    "phase": "NORMAL_OPERATION",
    "content": "Ein SIEM-Alarm meldet ungewöhnlich hohe Netzwerkaktivität auf dem Domain Controller (SRV-001). Weitere Analysen zeigen, dass gezielte Port-Scans durchgeführt werden, was auf eine aktive Erkundungsphase hinweist.",
    "affected_assets": [
      "SRV-001",
      "SRV-002"
    ],
    "mitre_id": "T1595"
  },
  {
    "inject_id": "INJ-009",
    "time_offset": "T+00:04:45",
    "phase": "INITIAL_INCIDENT",
    "content": "Ein plötzlicher und intensiver Anstieg des eingehenden Datenverkehrs überlastet die Netzwerk-Firewalls und führt zu einem vollständigen Ausfall des Domain Controllers (SRV-001). Der Application Server (SRV-002) zeigt signifikante Leistungseinbußen. Kritische Geschäftsfunktionen sind stark beeinträchtigt.",
    "affected_assets": [
      "SRV-001",
      "SRV-002"
    ],
    "mitre_id": "T1546.014"
  }
]
```
- **Defined Rules:**
  - **FSM Transition Rules:** Valid transitions from `ESCALATION_CRISIS` → `['CONTAINMENT']`
  - **State Consistency:** Assets must exist in system_state (checked against: `['SRV-001', 'SRV-002', 'APP-001', 'APP-002']`)
  - **Temporal Consistency:** Time offsets must be chronological
  - **Logical Consistency:** No contradictions with previous injects
  - **Causal Validity:** MITRE techniques must be technically possible (only truly impossible sequences block)

### 2. The Generator's Draft
```json
{
  "inject_id": "INJ-010",
  "time_offset": "T+00:07:30",
  "phase": "ESCALATION_CRISIS",
  "source": "Red Team / Attacker",
  "target": "Blue Team / SOC",
  "modality": "SIEM Alert",
  "content": "Ein SIEM-Alarm meldet ungewöhnlich hohe Netzwerkaktivität aus mehreren geografischen Regionen, die auf einen automatisierten Exfiltrationsversuch über das Application Server (SRV-002) hindeuten. Der Domain Controller (SRV-001) generiert ebenfalls ungewöhnliche Sicherheitswarnungen, was auf ein erhöhtes Risiko hinweist.",
  "technical_metadata": {
    "mitre_id": "T1020",
    "affected_assets": [
      "SRV-001",
      "SRV-002"
    ],
    "ioc_hash": "d41d8cd98f00b204e9800998ecf8427e",
    "ioc_ip": "192.168.1.100",
    "ioc_domain": "malicious-activity.com",
    "severity": "Critical"
  },
  "dora_compliance_tag": null,
  "business_impact": "Die anhaltende DDoS-Attacke auf das Webportal und der mögliche Datenexfiltrationsversuch gefährden kritische Geschäftsfunktionen wie Kundenzugang und interne Kommunikation. Es besteht das Risiko eines vollständigen Systemausfalls, der die Geschäftskontinuität erheblich beeinträchtigen könnte."
}
```

### 3. The Critic's Reasoning (Raw LLM Output)
*Crucial: What did the LLM actually say before parsing?*

```
Temporaler Fehler - kein LLM-Call
```

### 4. The Verdict
- **Decision:** ❌ INVALID
- **Detected Errors:** [
  "Temporale Inkonsistenz: Inject INJ-010 hat Zeitstempel T+00:07:30, aber vorheriger Inject INJ-007 hat T+00:10:00 (später). Zeitstempel müssen chronologisch sein."
]
- **Warnings:** []
- **Validation Details:**
  - Pydantic Valid: `True`
  - FSM Valid: `True`
  - State Valid: `True`
  - Temporal Valid: `False`
  - Logical Consistency: `False`
  - Causal Validity: `True`
  - Causal Blocking: `False`

***

## 🔍 Audit Entry: INJ-010
**Timestamp:** 2025-12-22T14:14:55.354104

### 1. The Ground Truth (What was in the DB?)
*Crucial: Dump the exact JSON inputs the Critic received.*

- **Active Assets in State:** `[
  "SRV-001",
  "SRV-002",
  "APP-001",
  "APP-002"
]`
- **Current Phase:** `ESCALATION_CRISIS`
- **System State (Full Raw):**
```json
{
  "SRV-001": {
    "status": "suspicious",
    "entity_type": "Server",
    "name": "Domain Controller DC-01",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:14:31.688000000+00:00",
    "last_updated_by_inject": "INJ-009",
    "id": "SRV-001",
    "type": "Server"
  },
  "SRV-002": {
    "status": "suspicious",
    "entity_type": "Server",
    "name": "Application Server APP-SRV-01",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:14:31.720000000+00:00",
    "last_updated_by_inject": "INJ-009",
    "id": "SRV-002",
    "type": "Server"
  },
  "APP-001": {
    "status": "compromised",
    "entity_type": "Application",
    "name": "Payment Processing System",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:11:26.073000000+00:00",
    "last_updated_by_inject": "INJ-005",
    "id": "APP-001",
    "type": "Application"
  },
  "APP-002": {
    "status": "compromised",
    "entity_type": "Application",
    "name": "Customer Database",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:12:23.237000000+00:00",
    "last_updated_by_inject": "INJ-006",
    "id": "APP-002",
    "type": "Application"
  }
}
```
- **System State (Formatted - wie an LLM gesendet):**
```
- Domain Controller DC-01 (SRV-001, Server): suspicious
- Application Server APP-SRV-01 (SRV-002, Server): suspicious
- Payment Processing System (APP-001, Application): compromised
- Customer Database (APP-002, Application): compromised

⚠️ KRITISCH - VERFÜGBARE ASSET-IDs (NUR DIESE VERWENDEN!): SRV-001, SRV-002, APP-001, APP-002
❌ VERBOTEN: Erstelle KEINE neuen Assets! Verwende NUR die oben genannten Asset-IDs!
```
- **Previous Injects (Full History):**
```json
[
  {
    "inject_id": "INJ-001",
    "time_offset": "T+00:00:15",
    "phase": "SUSPICIOUS_ACTIVITY",
    "content": "Unsere Netzwerküberwachungssoftware hat eine ungewöhnliche Erhöhung des eingehenden Datenverkehrs auf dem Payment Processing System (APP-001) festgestellt. Dies könnte ein Anzeichen für einen DDoS-Angriff sein. Ebenfalls wurden verdächtige Zugangsmuster zur Kunden-Datenbank (APP-002) und Anomalien im Zugriff auf den Domain Controller (SRV-001) protokolliert.",
    "affected_assets": [
      "APP-001",
      "APP-002",
      "SRV-001"
    ],
    "mitre_id": "T1595"
  },
  {
    "inject_id": "INJ-002",
    "time_offset": "T+00:00:45",
    "phase": "INITIAL_INCIDENT",
    "content": "Ein massiver Anstieg des Netzwerkverkehrs ist zum Application Server (SRV-002) zu verzeichnen. Verdächtige IP-Adressen senden kontinuierlich Anfragen an das Payment Processing System (APP-001) und die Customer Database (APP-002). Der Datenverkehr hat die Kapazität des Netzwerks erreicht, was zu erheblichen Verzögerungen und Ausfällen führt.",
    "affected_assets": [
      "SRV-002",
      "APP-001",
      "APP-002"
    ],
    "mitre_id": "T1546.014"
  },
  {
    "inject_id": "INJ-003",
    "time_offset": "T+00:02:00",
    "phase": "ESCALATION_CRISIS",
    "content": "Die DDoS-Attacke hat sich intensiviert und führt zu einer kritischen Systembelastung. Der Domain Controller (SRV-001) meldet eine signifikante Zunahme von Authentifizierungsfehlern, was auf mögliche Brute-Force-Angriffe hinweist. Das Payment Processing System (APP-001) zeigt verzögerte Transaktionen und Abbrüche. Mehrere Abteilungen berichten über Schwierigkeiten beim Zugriff auf die Customer Database (APP-002), was die Kundenservice-Leistung beeinträchtigt.",
    "affected_assets": [
      "SRV-001",
      "APP-001",
      "APP-002"
    ],
    "mitre_id": "T1020"
  },
  {
    "inject_id": "INJ-004",
    "time_offset": "T+00:04:00",
    "phase": "CONTAINMENT",
    "content": "Das IT-Sicherheitsteam hat eine Notfallwiederherstellungsprozedur für den Domain Controller (SRV-001) eingeleitet, um die Authentifizierungssysteme zu stabilisieren. Der Application Server (SRV-002) wurde isoliert und unterliegt einer forensischen Analyse. Unsere Zahlungsteams arbeiten daran, alternative Zahlungsabwicklungen durchzuführen, während das Payment Processing System (APP-001) offline bleibt. Die Customer Database (APP-002) wird aus Backups wiederhergestellt, um die Geschäftskontinuität zu sichern.",
    "affected_assets": [
      "SRV-001",
      "SRV-002",
      "APP-001",
      "APP-002"
    ],
    "mitre_id": "T1480"
  },
  {
    "inject_id": "INJ-005",
    "time_offset": "T+00:06:00",
    "phase": "ESCALATION_CRISIS",
    "content": "Es wurde ein massiver Anstieg des Datenverkehrs auf den Application Server (SRV-002) und das Payment Processing System (APP-001) festgestellt. Ungewöhnliche Anmeldemuster auf dem Domain Controller (SRV-001) deuten auf eine Ausweitung des Angriffs hin. Wir haben ein kritisches Sicherheitsteam-Meeting einberufen, um Notfallmaßnahmen zu koordinieren. Die IT-Abteilung wurde angewiesen, alle nicht notwendigen Netzwerkverbindungen zu kappen und kompromittierte Systeme vom Netz zu nehmen. Einige Kunden melden Schwierigkeiten beim Zugriff auf ihre Konten, was auf eine Beeinträchtigung der Customer Database (APP-002) hindeutet.",
    "affected_assets": [
      "SRV-002",
      "APP-001",
      "SRV-001",
      "APP-002"
    ],
    "mitre_id": "T1020"
  },
  {
    "inject_id": "INJ-006",
    "time_offset": "T+00:07:00",
    "phase": "CONTAINMENT",
    "content": "Das Incident Response Team hat den Netzwerkverkehr erfolgreich über spezialisierte DDoS-Protection-Systeme umgeleitet, um die Last auf den Servern zu minimieren. Der Domain Controller DC-01 (SRV-001) wurde isoliert, um die weitere Ausbreitung der Kompromittierung zu verhindern. Der Zugang zur Customer Database (APP-002) ist vorübergehend gesperrt, um Datenabflüsse zu verhindern.",
    "affected_assets": [
      "SRV-001",
      "APP-002"
    ],
    "mitre_id": "T1480"
  },
  {
    "inject_id": "INJ-007",
    "time_offset": "T+00:10:00",
    "phase": "RECOVERY",
    "content": "Nach der erfolgreichen Eindämmung des Angriffs wird nun die Recovery-Phase eingeleitet. Der Domain Controller (SRV-001) wird aus den neuesten Backups wiederhergestellt, um die Domänenverwaltung zu stabilisieren. Parallel dazu wird auf dem Application Server (SRV-002) eine eingehende forensische Analyse durchgeführt, um eventuell verbliebene bösartige Aktivitäten auszuschließen.",
    "affected_assets": [
      "SRV-001",
      "SRV-002"
    ],
    "mitre_id": "T1490"
  },
  {
    "inject_id": "INJ-008",
    "time_offset": "T+00:14:00",
    "phase": "NORMAL_OPERATION",
    "content": "Ein SIEM-Alarm meldet ungewöhnlich hohe Netzwerkaktivität auf dem Domain Controller (SRV-001). Weitere Analysen zeigen, dass gezielte Port-Scans durchgeführt werden, was auf eine aktive Erkundungsphase hinweist.",
    "affected_assets": [
      "SRV-001",
      "SRV-002"
    ],
    "mitre_id": "T1595"
  },
  {
    "inject_id": "INJ-009",
    "time_offset": "T+00:04:45",
    "phase": "INITIAL_INCIDENT",
    "content": "Ein plötzlicher und intensiver Anstieg des eingehenden Datenverkehrs überlastet die Netzwerk-Firewalls und führt zu einem vollständigen Ausfall des Domain Controllers (SRV-001). Der Application Server (SRV-002) zeigt signifikante Leistungseinbußen. Kritische Geschäftsfunktionen sind stark beeinträchtigt.",
    "affected_assets": [
      "SRV-001",
      "SRV-002"
    ],
    "mitre_id": "T1546.014"
  }
]
```
- **Defined Rules:**
  - **FSM Transition Rules:** Valid transitions from `ESCALATION_CRISIS` → `['CONTAINMENT']`
  - **State Consistency:** Assets must exist in system_state (checked against: `['SRV-001', 'SRV-002', 'APP-001', 'APP-002']`)
  - **Temporal Consistency:** Time offsets must be chronological
  - **Logical Consistency:** No contradictions with previous injects
  - **Causal Validity:** MITRE techniques must be technically possible (only truly impossible sequences block)

### 2. The Generator's Draft
```json
{
  "inject_id": "INJ-010",
  "time_offset": "T+00:11:00",
  "phase": "ESCALATION_CRISIS",
  "source": "Blue Team / SOC",
  "target": "Management",
  "modality": "Internal Report",
  "content": "Ein koordiniertes Botnet verursacht eine Überlastung des Webportals, was die Verfügbarkeit erheblich beeinträchtigt. Der Domain Controller (SRV-001) generiert ungewöhnliche Sicherheitswarnungen, während der Application Server (SRV-002) unerlaubte Zugriffsversuche verzeichnet. Interne Kommunikationssysteme sind aufgrund der Netzwerküberlastungen stark verzögert.",
  "technical_metadata": {
    "mitre_id": "T1020",
    "affected_assets": [
      "SRV-001",
      "SRV-002"
    ],
    "ioc_hash": "F4A5C4E6D1A1B7E8F3A9B7C6D5E4F3A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6E7",
    "ioc_ip": "192.168.1.100",
    "ioc_domain": "malicious-traffic.net",
    "severity": "Critical"
  },
  "dora_compliance_tag": null,
  "business_impact": "Die Überlastung des Webportals führt zu erheblichen Störungen der Kundeninteraktionen, was potenzielle Umsatzeinbußen zur Folge hat. Verzögerungen in den internen Kommunikationssystemen beeinträchtigen die Geschäftskontinuität und die Fähigkeit, schnell auf die Krise zu reagieren."
}
```

### 3. The Critic's Reasoning (Raw LLM Output)
*Crucial: What did the LLM actually say before parsing?*

```
Temporaler Fehler - kein LLM-Call
```

### 4. The Verdict
- **Decision:** ❌ INVALID
- **Detected Errors:** [
  "Temporale Inkonsistenz: Inject INJ-010 hat Zeitstempel T+00:11:00, aber vorheriger Inject INJ-008 hat T+00:14:00 (später). Zeitstempel müssen chronologisch sein."
]
- **Warnings:** []
- **Validation Details:**
  - Pydantic Valid: `True`
  - FSM Valid: `True`
  - State Valid: `True`
  - Temporal Valid: `False`
  - Logical Consistency: `False`
  - Causal Validity: `True`
  - Causal Blocking: `False`

***

## 🔍 Audit Entry: INJ-001
**Timestamp:** 2025-12-22T14:23:03.272296

### 1. The Ground Truth (What was in the DB?)
*Crucial: Dump the exact JSON inputs the Critic received.*

- **Active Assets in State:** `[
  "SRV-001",
  "SRV-002",
  "APP-001",
  "APP-002"
]`
- **Current Phase:** `SUSPICIOUS_ACTIVITY`
- **System State (Full Raw):**
```json
{
  "SRV-001": {
    "status": "compromised",
    "entity_type": "Server",
    "name": "Domain Controller DC-01",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:15:04.684000000+00:00",
    "last_updated_by_inject": "INJ-010",
    "id": "SRV-001",
    "type": "Server"
  },
  "SRV-002": {
    "status": "compromised",
    "entity_type": "Server",
    "name": "Application Server APP-SRV-01",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:15:04.723000000+00:00",
    "last_updated_by_inject": "INJ-010",
    "id": "SRV-002",
    "type": "Server"
  },
  "APP-001": {
    "status": "compromised",
    "entity_type": "Application",
    "name": "Payment Processing System",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:11:26.073000000+00:00",
    "last_updated_by_inject": "INJ-005",
    "id": "APP-001",
    "type": "Application"
  },
  "APP-002": {
    "status": "compromised",
    "entity_type": "Application",
    "name": "Customer Database",
    "criticality": "standard",
    "last_updated": "2025-12-22T13:12:23.237000000+00:00",
    "last_updated_by_inject": "INJ-006",
    "id": "APP-002",
    "type": "Application"
  }
}
```
- **System State (Formatted - wie an LLM gesendet):**
```
- Domain Controller DC-01 (SRV-001, Server): compromised
- Application Server APP-SRV-01 (SRV-002, Server): compromised
- Payment Processing System (APP-001, Application): compromised
- Customer Database (APP-002, Application): compromised

⚠️ KRITISCH - VERFÜGBARE ASSET-IDs (NUR DIESE VERWENDEN!): SRV-001, SRV-002, APP-001, APP-002
❌ VERBOTEN: Erstelle KEINE neuen Assets! Verwende NUR die oben genannten Asset-IDs!
```
- **Previous Injects (Full History):**
```json
[]
```
- **Defined Rules:**
  - **FSM Transition Rules:** Valid transitions from `SUSPICIOUS_ACTIVITY` → `['INITIAL_INCIDENT', 'NORMAL_OPERATION']`
  - **State Consistency:** Assets must exist in system_state (checked against: `['SRV-001', 'SRV-002', 'APP-001', 'APP-002']`)
  - **Temporal Consistency:** Time offsets must be chronological
  - **Logical Consistency:** No contradictions with previous injects
  - **Causal Validity:** MITRE techniques must be technically possible (only truly impossible sequences block)

### 2. The Generator's Draft
```json
{
  "inject_id": "INJ-001",
  "time_offset": "T+00:30",
  "phase": "SUSPICIOUS_ACTIVITY",
  "source": "Red Team / Attacker",
  "target": "Blue Team / SOC",
  "modality": "SIEM Alert",
  "content": "Security event detected related to Active Scanning (MITRE T1595).",
  "technical_metadata": {
    "mitre_id": "T1595",
    "affected_assets": [
      "SRV-001"
    ],
    "ioc_hash": null,
    "ioc_ip": null,
    "ioc_domain": null,
    "severity": "Medium"
  },
  "dora_compliance_tag": null,
  "business_impact": null
}
```

### 3. The Critic's Reasoning (Raw LLM Output)
*Crucial: What did the LLM actually say before parsing?*

```
```json
{
    "logical_consistency": true,
    "regulatory_compliance": false,
    "causal_validity": true,
    "errors": [],
    "warnings": []
}
```
```

### 4. The Verdict
- **Decision:** ✅ VALID
- **Detected Errors:** []
- **Warnings:** [
  "Name mismatch for SRV-001: Content may use different name than 'Domain Controller DC-01', but ID is valid. Proceeding.",
  "Regulatorische Aspekte könnten besser abgedeckt sein (optional)",
  "DORA Compliance: DORA_Art25_BusinessContinuity, DORA_Art25_CriticalFunctionsCoverage, DORA_Art25_RealisticScenario fehlen",
  "DORA: Business Continuity könnte stärker betont werden",
  "DORA: Recovery Plan Testing wurde nicht erwähnt",
  "Qualitäts-Score könnte verbessert werden: 0.82"
]
- **Validation Details:**
  - Pydantic Valid: `True`
  - FSM Valid: `True`
  - State Valid: `True`
  - Temporal Valid: `True`
  - Logical Consistency: `True`
  - Causal Validity: `True`
  - Causal Blocking: `False`

***

