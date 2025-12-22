"""
Thread-safe JSONL Logger für forensisches Logging von Refinement-Loops.

Dieser Logger erfasst:
- [DRAFT]: Rohe, abgelehnte Injects vom Generator
- [CRITIC]: Exakte Validierungsfehler/Warnungen
- [REFINED]: Finale, akzeptierte Injects
"""

import json
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class ForensicLogger:
    """
    Thread-safe JSONL Logger für forensisches Logging.
    
    Jede Zeile ist ein JSON-Objekt mit:
    - timestamp: ISO-Format Zeitstempel
    - scenario_id: ID des Szenarios
    - event_type: 'DRAFT', 'CRITIC', oder 'REFINED'
    - data: Event-spezifische Daten
    """
    
    def __init__(self, log_file: str = "logs/forensic/forensic_trace.jsonl"):
        """
        Initialisiert den Logger.
        
        Args:
            log_file: Pfad zur JSONL-Logdatei (Standard: logs/forensic/forensic_trace.jsonl)
        """
        self.log_file = Path(log_file)
        self.lock = threading.Lock()
        
        # Erstelle Log-Ordner falls nicht vorhanden
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Erstelle Log-Datei mit Header-Kommentar
        if not self.log_file.exists():
            with open(self.log_file, 'w') as f:
                f.write(f"# Forensic Trace Log - Started: {datetime.now().isoformat()}\n")
    
    def log_draft(
        self,
        scenario_id: str,
        inject: Any,
        iteration: int,
        refine_count: int = 0
    ):
        """
        Loggt einen DRAFT Inject (vor Validierung).
        
        Args:
            scenario_id: ID des Szenarios
            inject: Inject-Objekt (Pydantic Model)
            iteration: Aktuelle Iteration
            refine_count: Anzahl der Refine-Versuche (0 = erster Versuch)
        """
        try:
            # Serialisiere Inject zu Dict
            inject_dict = self._serialize_inject(inject)
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "scenario_id": scenario_id,
                "event_type": "DRAFT",
                "iteration": iteration,
                "refine_count": refine_count,
                "data": {
                    "inject": inject_dict,
                    "status": "rejected" if refine_count > 0 else "initial_draft"
                }
            }
            
            self._write_log(log_entry)
        except Exception as e:
            print(f"⚠️  Fehler beim Loggen von DRAFT: {e}")
    
    def log_critic(
        self,
        scenario_id: str,
        inject_id: str,
        validation_result: Any,
        iteration: int,
        refine_count: int = 0
    ):
        """
        Loggt CRITIC Validierungsergebnis.
        
        Args:
            scenario_id: ID des Szenarios
            inject_id: ID des validierten Injects
            validation_result: ValidationResult-Objekt
            iteration: Aktuelle Iteration
            refine_count: Anzahl der Refine-Versuche
        """
        try:
            validation_dict = {
                "is_valid": validation_result.is_valid,
                "logical_consistency": validation_result.logical_consistency,
                "dora_compliance": validation_result.dora_compliance,
                "causal_validity": validation_result.causal_validity,
                "errors": validation_result.errors,
                "warnings": validation_result.warnings
            }
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "scenario_id": scenario_id,
                "event_type": "CRITIC",
                "iteration": iteration,
                "refine_count": refine_count,
                "data": {
                    "inject_id": inject_id,
                    "validation": validation_dict,
                    "decision": "reject" if not validation_result.is_valid else "accept"
                }
            }
            
            self._write_log(log_entry)
        except Exception as e:
            print(f"⚠️  Fehler beim Loggen von CRITIC: {e}")
    
    def log_refined(
        self,
        scenario_id: str,
        inject: Any,
        iteration: int,
        refine_count: int,
        was_refined: bool = False
    ):
        """
        Loggt einen REFINED Inject (nach erfolgreicher Validierung).
        
        Args:
            scenario_id: ID des Szenarios
            inject: Inject-Objekt (Pydantic Model)
            iteration: Aktuelle Iteration
            refine_count: Anzahl der Refine-Versuche bis zur Akzeptanz
            was_refined: Ob dieser Inject aus einem Refinement stammt
        """
        try:
            inject_dict = self._serialize_inject(inject)
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "scenario_id": scenario_id,
                "event_type": "REFINED",
                "iteration": iteration,
                "refine_count": refine_count,
                "data": {
                    "inject": inject_dict,
                    "status": "accepted",
                    "was_refined": was_refined,
                    "refinement_attempts": refine_count
                }
            }
            
            self._write_log(log_entry)
        except Exception as e:
            print(f"⚠️  Fehler beim Loggen von REFINED: {e}")
    
    def _serialize_inject(self, inject: Any) -> Dict[str, Any]:
        """
        Serialisiert ein Inject-Objekt zu einem Dictionary.
        
        Args:
            inject: Inject-Objekt (Pydantic Model)
        
        Returns:
            Dictionary-Repräsentation des Injects
        """
        try:
            if hasattr(inject, 'model_dump'):
                # Pydantic v2
                return inject.model_dump()
            elif hasattr(inject, 'dict'):
                # Pydantic v1
                return inject.dict()
            else:
                # Fallback: Versuche manuelle Serialisierung
                return {
                    "inject_id": getattr(inject, 'inject_id', None),
                    "time_offset": getattr(inject, 'time_offset', None),
                    "phase": str(getattr(inject, 'phase', None)),
                    "source": getattr(inject, 'source', None),
                    "target": getattr(inject, 'target', None),
                    "modality": str(getattr(inject, 'modality', None)),
                    "content": getattr(inject, 'content', None),
                    "technical_metadata": self._serialize_technical_metadata(
                        getattr(inject, 'technical_metadata', None)
                    )
                }
        except Exception as e:
            return {"error": f"Serialization failed: {str(e)}"}
    
    def _serialize_technical_metadata(self, metadata: Any) -> Dict[str, Any]:
        """Serialisiert TechnicalMetadata."""
        if metadata is None:
            return {}
        
        try:
            if hasattr(metadata, 'model_dump'):
                return metadata.model_dump()
            elif hasattr(metadata, 'dict'):
                return metadata.dict()
            else:
                return {
                    "mitre_id": getattr(metadata, 'mitre_id', None),
                    "affected_assets": getattr(metadata, 'affected_assets', []),
                    "ioc_hash": getattr(metadata, 'ioc_hash', None),
                    "ioc_ip": getattr(metadata, 'ioc_ip', None),
                    "ioc_domain": getattr(metadata, 'ioc_domain', None),
                    "severity": getattr(metadata, 'severity', None)
                }
        except Exception as e:
            return {"error": f"Metadata serialization failed: {str(e)}"}
    
    def _write_log(self, log_entry: Dict[str, Any]):
        """
        Thread-safe Schreiben einer Log-Zeile.
        
        Args:
            log_entry: Dictionary mit Log-Daten
        """
        with self.lock:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    json_line = json.dumps(log_entry, ensure_ascii=False)
                    f.write(json_line + '\n')
                    f.flush()  # Sofortiges Schreiben für Debugging
            except Exception as e:
                print(f"⚠️  Fehler beim Schreiben in Log-Datei: {e}")


# Globaler Logger-Instanz (wird pro Szenario erstellt)
_forensic_loggers: Dict[str, ForensicLogger] = {}
_logger_lock = threading.Lock()


def get_forensic_logger(scenario_id: str, log_file: Optional[str] = None) -> ForensicLogger:
    """
    Gibt einen Logger für ein Szenario zurück (thread-safe).
    
    Args:
        scenario_id: ID des Szenarios
        log_file: Optional - Pfad zur Log-Datei (Standard: forensic_trace.jsonl)
    
    Returns:
        ForensicLogger-Instanz
    """
    with _logger_lock:
        if scenario_id not in _forensic_loggers:
            if log_file is None:
                log_file = "logs/forensic/forensic_trace.jsonl"
            _forensic_loggers[scenario_id] = ForensicLogger(log_file)
        return _forensic_loggers[scenario_id]
