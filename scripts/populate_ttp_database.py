"""
Script zum Befüllen der ChromaDB mit MITRE ATT&CK Enterprise TTPs.

Lädt TTPs von der MITRE ATT&CK API oder aus einer lokalen JSON-Datei
und speichert sie in ChromaDB für semantische Suche.
"""

import os
import sys
import json
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path

# Füge Projekt-Root zum Python-Pfad hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.intel_agent import IntelAgent
from state_models import CrisisPhase


def fetch_mitre_attack_techniques() -> List[Dict[str, Any]]:
    """
    Lädt MITRE ATT&CK Enterprise Techniques von der offiziellen API.
    
    Returns:
        Liste von TTP-Dictionaries
    """
    print("📥 Lade MITRE ATT&CK Enterprise Techniques von der API...")
    
    try:
        # MITRE ATT&CK Enterprise Techniques API
        url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        techniques = []
        
        # Durchlaufe alle Objekte in der CTI-Datenbank
        for obj in data.get("objects", []):
            # Nur Techniques (nicht Tactics oder andere Objekte)
            if obj.get("type") == "attack-pattern" and obj.get("x_mitre_domains", [""])[0] == "enterprise-attack":
                external_refs = obj.get("external_references", [])
                mitre_id = None
                
                # Finde MITRE ID
                for ref in external_refs:
                    if ref.get("source_name") == "mitre-attack":
                        mitre_id = ref.get("external_id")
                        break
                
                if not mitre_id:
                    continue
                
                # Extrahiere Tactics (Phasen-Mapping)
                kill_chain_phases = obj.get("kill_chain_phases", [])
                tactics = [phase.get("phase_name") for phase in kill_chain_phases]
                
                # Mappe Tactics zu Crisis Phases
                phase_mapping = _map_tactics_to_crisis_phases(tactics)
                
                # Erstelle TTP-Dictionary
                technique = {
                    "technique_id": mitre_id,
                    "mitre_id": mitre_id,
                    "name": obj.get("name", ""),
                    "description": obj.get("description", ""),
                    "tactics": tactics,
                    "phase": phase_mapping,
                    "url": f"https://attack.mitre.org/techniques/{mitre_id.replace('.', '/')}"
                }
                
                techniques.append(technique)
        
        print(f"✅ {len(techniques)} Techniques geladen")
        return techniques
        
    except requests.RequestException as e:
        print(f"⚠️  Fehler beim Laden von der API: {e}")
        print("📁 Versuche lokale Fallback-Datei...")
        return _load_from_local_file()
    except Exception as e:
        print(f"⚠️  Fehler beim Verarbeiten der API-Daten: {e}")
        return _load_from_local_file()


def _load_from_local_file() -> List[Dict[str, Any]]:
    """
    Lädt TTPs aus einer lokalen JSON-Datei (Fallback).
    
    Returns:
        Liste von TTP-Dictionaries
    """
    local_file = project_root / "data" / "mitre_techniques.json"
    
    if local_file.exists():
        print(f"📁 Lade aus lokaler Datei: {local_file}")
        with open(local_file, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print("⚠️  Keine lokale Datei gefunden. Erstelle Basis-TTPs...")
        return _create_basic_ttps()


def _map_tactics_to_crisis_phases(tactics: List[str]) -> str:
    """
    Mappt MITRE ATT&CK Tactics zu Crisis Phases.
    
    Args:
        tactics: Liste von MITRE Tactics (z.B. ["initial-access", "execution"])
    
    Returns:
        Crisis Phase als String
    """
    # Mapping von MITRE Tactics zu Crisis Phases
    tactic_to_phase = {
        "reconnaissance": CrisisPhase.NORMAL_OPERATION.value,
        "resource-development": CrisisPhase.NORMAL_OPERATION.value,
        "initial-access": CrisisPhase.SUSPICIOUS_ACTIVITY.value,
        "execution": CrisisPhase.INITIAL_INCIDENT.value,
        "persistence": CrisisPhase.INITIAL_INCIDENT.value,
        "privilege-escalation": CrisisPhase.INITIAL_INCIDENT.value,
        "defense-evasion": CrisisPhase.INITIAL_INCIDENT.value,
        "credential-access": CrisisPhase.INITIAL_INCIDENT.value,
        "discovery": CrisisPhase.INITIAL_INCIDENT.value,
        "lateral-movement": CrisisPhase.ESCALATION_CRISIS.value,
        "collection": CrisisPhase.ESCALATION_CRISIS.value,
        "command-and-control": CrisisPhase.ESCALATION_CRISIS.value,
        "exfiltration": CrisisPhase.ESCALATION_CRISIS.value,
        "impact": CrisisPhase.ESCALATION_CRISIS.value
    }
    
    # Finde die passendste Phase basierend auf den Tactics
    for tactic in tactics:
        if tactic in tactic_to_phase:
            return tactic_to_phase[tactic]
    
    # Default: Initial Incident
    return CrisisPhase.INITIAL_INCIDENT.value


def _create_basic_ttps() -> List[Dict[str, Any]]:
    """
    Erstellt eine Basis-Liste von TTPs wenn keine API/Lokale Datei verfügbar ist.
    
    Returns:
        Liste von Basis-TTP-Dictionaries
    """
    print("📝 Erstelle Basis-TTP-Liste...")
    
    basic_ttps = [
        {
            "technique_id": "T1595",
            "mitre_id": "T1595",
            "name": "Active Scanning",
            "description": "Adversaries may scan victim systems to gather information that can be used for targeting.",
            "tactics": ["reconnaissance"],
            "phase": CrisisPhase.NORMAL_OPERATION.value
        },
        {
            "technique_id": "T1078",
            "mitre_id": "T1078",
            "name": "Valid Accounts",
            "description": "Adversaries may obtain and abuse credentials of existing accounts as a means of gaining Initial Access.",
            "tactics": ["initial-access", "persistence", "privilege-escalation"],
            "phase": CrisisPhase.SUSPICIOUS_ACTIVITY.value
        },
        {
            "technique_id": "T1110",
            "mitre_id": "T1110",
            "name": "Brute Force",
            "description": "Adversaries may use brute force techniques to gain access to accounts when passwords are unknown or when password hashes are obtained.",
            "tactics": ["credential-access"],
            "phase": CrisisPhase.SUSPICIOUS_ACTIVITY.value
        },
        {
            "technique_id": "T1059",
            "mitre_id": "T1059",
            "name": "Command and Scripting Interpreter",
            "description": "Adversaries may abuse command and script interpreters to execute commands, scripts, or binaries.",
            "tactics": ["execution"],
            "phase": CrisisPhase.INITIAL_INCIDENT.value
        },
        {
            "technique_id": "T1543",
            "mitre_id": "T1543",
            "name": "Create or Modify System Process",
            "description": "Adversaries may create or modify system processes to hide their malicious activity.",
            "tactics": ["persistence", "privilege-escalation"],
            "phase": CrisisPhase.INITIAL_INCIDENT.value
        },
        {
            "technique_id": "T1021",
            "mitre_id": "T1021",
            "name": "Remote Services",
            "description": "Adversaries may use remote services to gain access to systems and move laterally.",
            "tactics": ["lateral-movement"],
            "phase": CrisisPhase.ESCALATION_CRISIS.value
        },
        {
            "technique_id": "T1041",
            "mitre_id": "T1041",
            "name": "Exfiltration Over C2 Channel",
            "description": "Adversaries may steal data by exfiltrating it over an existing command and control channel.",
            "tactics": ["exfiltration"],
            "phase": CrisisPhase.ESCALATION_CRISIS.value
        },
        {
            "technique_id": "T1486",
            "mitre_id": "T1486",
            "name": "Data Encrypted for Impact",
            "description": "Adversaries may encrypt data on target systems or on large numbers of systems in a network to interrupt availability to system and network resources.",
            "tactics": ["impact"],
            "phase": CrisisPhase.ESCALATION_CRISIS.value
        }
    ]
    
    return basic_ttps


def save_techniques_to_file(techniques: List[Dict[str, Any]], output_file: Optional[Path] = None):
    """
    Speichert Techniques in eine lokale JSON-Datei.
    
    Args:
        techniques: Liste von TTP-Dictionaries
        output_file: Optional - Ausgabedatei (Standard: data/mitre_techniques.json)
    """
    if output_file is None:
        output_file = project_root / "data" / "mitre_techniques.json"
    
    # Erstelle data-Verzeichnis falls es nicht existiert
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(techniques, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Techniques gespeichert in: {output_file}")


def main():
    """Hauptfunktion zum Befüllen der TTP-Datenbank."""
    print("=" * 60)
    print("🚀 MITRE ATT&CK TTP Database Population")
    print("=" * 60)
    
    # Lade Techniques
    techniques = fetch_mitre_attack_techniques()
    
    if not techniques:
        print("❌ Keine Techniques geladen. Beende.")
        return
    
    # Speichere als Backup
    save_techniques_to_file(techniques)
    
    # Initialisiere Intel Agent
    print("\n📊 Initialisiere ChromaDB...")
    intel_agent = IntelAgent()
    
    # Befülle Datenbank
    print(f"💾 Speichere {len(techniques)} Techniques in ChromaDB...")
    intel_agent.initialize_ttp_database(techniques)
    
    # Teste Abfrage
    print("\n🧪 Teste Abfrage...")
    test_ttps = intel_agent.get_relevant_ttps(CrisisPhase.INITIAL_INCIDENT, limit=3)
    print(f"✅ Test erfolgreich: {len(test_ttps)} TTPs für INITIAL_INCIDENT gefunden")
    for ttp in test_ttps:
        print(f"   - {ttp.get('mitre_id')}: {ttp.get('name')}")
    
    print("\n" + "=" * 60)
    print("✅ TTP-Datenbank erfolgreich befüllt!")
    print("=" * 60)


if __name__ == "__main__":
    main()
