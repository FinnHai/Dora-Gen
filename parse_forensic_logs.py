#!/usr/bin/env python3
"""
Parse Forensic Logs und konvertiere zu Frontend-Format
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

def parse_forensic_logs(log_file: Path) -> Dict[str, Any]:
    """Parse Forensic Logs und extrahiere Injects und Logs."""
    
    scenario_data = defaultdict(lambda: {
        "injects": {},
        "logs": [],
        "last_timestamp": None
    })
    
    if not log_file.exists():
        print(f"Log-Datei nicht gefunden: {log_file}")
        return {}
    
    with open(log_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                log_entry = json.loads(line)
                scenario_id = log_entry.get("scenario_id")
                if not scenario_id:
                    continue
                
                data = log_entry.get("data", {})
                inject_id = data.get("inject_id")
                timestamp = log_entry.get("timestamp", "")
                iteration = log_entry.get("iteration", 0)
                refine_count = log_entry.get("refine_count", 0)
                event_type = log_entry.get("event_type", "UNKNOWN")
                
                # Track latest timestamp
                if timestamp and (not scenario_data[scenario_id]["last_timestamp"] or 
                                 timestamp > scenario_data[scenario_id]["last_timestamp"]):
                    scenario_data[scenario_id]["last_timestamp"] = timestamp
                
                # Sammle Inject-Informationen
                if inject_id:
                    if inject_id not in scenario_data[scenario_id]["injects"]:
                        validation = data.get("validation", {})
                        scenario_data[scenario_id]["injects"][inject_id] = {
                            "inject_id": inject_id,
                            "iteration": iteration,
                            "refine_count": refine_count,
                            "status": "verified" if data.get("decision") == "accept" else "rejected",
                            "validation": validation,
                            "first_seen": timestamp,
                            "event_type": event_type,
                        }
                    else:
                        # Update mit neueren Daten (höherer refine_count)
                        if refine_count > scenario_data[scenario_id]["injects"][inject_id]["refine_count"]:
                            validation = data.get("validation", {})
                            scenario_data[scenario_id]["injects"][inject_id].update({
                                "status": "verified" if data.get("decision") == "accept" else "rejected",
                                "refine_count": refine_count,
                                "validation": validation,
                            })
                
                # Sammle Logs
                scenario_data[scenario_id]["logs"].append(log_entry)
                
            except json.JSONDecodeError as e:
                print(f"Fehler beim Parsen von Zeile {line_num}: {e}")
                continue
    
    return dict(scenario_data)

def extract_assets_from_warnings(warnings: List[str]) -> List[str]:
    """Extrahiere Asset-IDs aus Warnungen."""
    assets = set()
    for warning in warnings:
        # Suche nach Asset-Patterns wie SRV-APP-001, SRV-CORE-002, etc.
        matches = re.findall(r'(SRV-[A-Z]+-\d+|DB-[A-Z]+-\d+|WS-[A-Z]+-\d+)', warning)
        assets.update(matches)
    return sorted(list(assets))

def convert_to_frontend_format(scenario_data: Dict[str, Any], scenario_id: str) -> Dict[str, Any]:
    """Konvertiere zu Frontend-Format."""
    
    if scenario_id not in scenario_data:
        return {"injects": [], "logs": []}
    
    data = scenario_data[scenario_id]
    
    # Konvertiere Injects
    injects = []
    for inject_id, inject_info in sorted(data["injects"].items(), key=lambda x: x[1]["iteration"]):
        validation = inject_info.get("validation", {})
        errors = validation.get("errors", [])
        warnings = validation.get("warnings", [])
        
        # Extrahiere Assets aus Warnings
        affected_assets = extract_assets_from_warnings(warnings)
        
        # Erstelle Refinement-History wenn Refine-Count > 0
        refinement_history = None
        if inject_info.get("refine_count", 0) > 0 and errors:
            refinement_history = [{
                "original": f"Inject {inject_id} (original)",
                "corrected": f"Inject {inject_id} (refined)",
                "errors": errors,
            }]
        
        # Bestimme Phase basierend auf Iteration (vereinfacht)
        phases = ["SUSPICIOUS_ACTIVITY", "INITIAL_INCIDENT", "ESCALATION_CRISIS", "CONTAINMENT", "RECOVERY"]
        phase = phases[min(inject_info["iteration"], len(phases) - 1)]
        
        injects.append({
            "inject_id": inject_id,
            "time_offset": f"T+{inject_info['iteration']:02d}:00",
            "content": f"Inject {inject_id} - Generated in iteration {inject_info['iteration']}",
            "status": inject_info["status"],
            "phase": phase,
            "source": "System",
            "target": "SOC",
            "modality": "SIEM Alert",
            "mitre_id": None,
            "affected_assets": affected_assets,
            "refinement_history": refinement_history,
        })
    
    # Konvertiere Logs
    logs = []
    for log_entry in sorted(data["logs"], key=lambda x: x.get("timestamp", "")):
        log_data = log_entry.get("data", {})
        validation = log_data.get("validation", {})
        inject_id = log_data.get("inject_id", "UNKNOWN")
        event_type = log_entry.get("event_type", "UNKNOWN")
        decision = log_data.get("decision", "unknown")
        
        # Erstelle Message
        if event_type == "CRITIC":
            if decision == "reject":
                message = f"[CRITIC] Inject {inject_id} rejected"
            elif decision == "accept":
                message = f"[CRITIC] Inject {inject_id} accepted"
            else:
                message = f"[CRITIC] Scanning Inject {inject_id}..."
        elif event_type == "GENERATOR":
            message = f"[DRAFT] Inject {inject_id} generated"
        else:
            message = f"[{event_type}] Event for {inject_id}"
        
        logs.append({
            "timestamp": log_entry.get("timestamp", ""),
            "inject_id": inject_id,
            "event_type": event_type,
            "message": message,
            "details": {
                "validation": {
                    "is_valid": validation.get("is_valid", True),
                    "errors": validation.get("errors", []),
                    "warnings": validation.get("warnings", []),
                },
                "decision": decision,
                "iteration": log_entry.get("iteration"),
                "refine_count": log_entry.get("refine_count", 0),
            },
        })
    
    return {
        "scenario_id": scenario_id,
        "injects": injects,
        "logs": logs,
    }

def main():
    log_file = Path("logs/forensic/forensic_trace.jsonl")
    
    print(f"Parse Forensic Logs: {log_file}")
    scenario_data = parse_forensic_logs(log_file)
    
    if not scenario_data:
        print("Keine Szenario-Daten gefunden!")
        return
    
    # Finde neuestes Szenario
    latest_scenario_id = max(
        scenario_data.keys(),
        key=lambda sid: scenario_data[sid]["last_timestamp"] or ""
    )
    
    print(f"\nNeuestes Szenario: {latest_scenario_id}")
    print(f"Injects gefunden: {len(scenario_data[latest_scenario_id]['injects'])}")
    print(f"Logs gefunden: {len(scenario_data[latest_scenario_id]['logs'])}")
    
    # Konvertiere zu Frontend-Format
    frontend_data = convert_to_frontend_format(scenario_data, latest_scenario_id)
    
    # Output als JSON
    output_file = Path("crux-frontend/lib/real-data.json")
    with open(output_file, 'w') as f:
        json.dump(frontend_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Daten gespeichert in: {output_file}")
    print(f"   - Scenario ID: {frontend_data['scenario_id']}")
    print(f"   - Injects: {len(frontend_data['injects'])}")
    print(f"   - Logs: {len(frontend_data['logs'])}")

if __name__ == "__main__":
    main()

