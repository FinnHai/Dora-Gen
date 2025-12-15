"""
Intel Agent - Holt TTPs (Taktiken, Techniken, Prozeduren) aus der Vektor-Datenbank.

Verantwortlich für:
- Abfrage relevanter MITRE ATT&CK TTPs
- Bereitstellung von Kontext für andere Agenten
- TTPs basierend auf aktueller Phase filtern
"""

from typing import List, Dict, Any, Optional
from state_models import CrisisPhase
import chromadb
from chromadb.config import Settings
import os
from dotenv import load_dotenv

load_dotenv()


class IntelAgent:
    """
    Intel Agent für TTP-Abfragen.
    
    Verwaltet eine Vektor-Datenbank (ChromaDB) mit MITRE ATT&CK TTPs
    und stellt relevante TTPs basierend auf der aktuellen Phase bereit.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialisiert den Intel Agent.
        
        Args:
            db_path: Pfad zur ChromaDB (Standard: aus .env oder ./chroma_db)
        """
        self.db_path = db_path or os.getenv("CHROMA_DB_PATH", "./chroma_db")
        
        # ChromaDB Client initialisieren
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Collection für TTPs
        self.collection_name = "mitre_ttps"
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except:
            # Collection existiert noch nicht - wird beim ersten Laden erstellt
            self.collection = None
    
    def get_relevant_ttps(
        self,
        phase: CrisisPhase,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Ruft relevante TTPs für eine bestimmte Phase ab.
        
        Args:
            phase: Aktuelle Krisenphase
            limit: Maximale Anzahl zurückzugebender TTPs
        
        Returns:
            Liste von TTP-Dictionaries mit:
            - technique_id: MITRE ID (z.B. "T1110")
            - name: Name der Technik
            - description: Beschreibung
            - phase_mapping: Zuordnung zu MITRE Phasen
        """
        if not self.collection:
            # Fallback: Basis-TTPs wenn DB noch nicht initialisiert
            return self._get_fallback_ttps(phase, limit)
        
        # Query basierend auf Phase
        phase_keywords = self._get_phase_keywords(phase)
        query_text = f"{phase.value} {' '.join(phase_keywords)}"
        
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=limit
            )
            
            ttps = []
            if results["ids"] and len(results["ids"][0]) > 0:
                for i, technique_id in enumerate(results["ids"][0]):
                    ttps.append({
                        "technique_id": technique_id,
                        "name": results["metadatas"][0][i].get("name", ""),
                        "description": results["documents"][0][i] if results["documents"] else "",
                        "phase_mapping": results["metadatas"][0][i].get("phase", ""),
                        "mitre_id": results["metadatas"][0][i].get("mitre_id", technique_id)
                    })
            
            return ttps if ttps else self._get_fallback_ttps(phase, limit)
            
        except Exception as e:
            print(f"⚠️  Fehler bei TTP-Abfrage: {e}")
            return self._get_fallback_ttps(phase, limit)
    
    def _get_phase_keywords(self, phase: CrisisPhase) -> List[str]:
        """Gibt Keywords für eine Phase zurück."""
        mapping = {
            CrisisPhase.NORMAL_OPERATION: ["reconnaissance", "initial access"],
            CrisisPhase.SUSPICIOUS_ACTIVITY: ["reconnaissance", "initial access", "execution"],
            CrisisPhase.INITIAL_INCIDENT: ["execution", "persistence", "privilege escalation"],
            CrisisPhase.ESCALATION_CRISIS: ["lateral movement", "collection", "exfiltration"],
            CrisisPhase.CONTAINMENT: ["defense evasion", "impact"],
            CrisisPhase.RECOVERY: ["recovery", "restoration"]
        }
        return mapping.get(phase, [])
    
    def _get_fallback_ttps(self, phase: CrisisPhase, limit: int) -> List[Dict[str, Any]]:
        """
        Fallback-TTPs wenn Vektor-DB noch nicht initialisiert ist.
        
        Gibt Basis-MITRE ATT&CK Techniken zurück, die typischerweise
        in der jeweiligen Phase verwendet werden.
        """
        phase_ttps = {
            CrisisPhase.NORMAL_OPERATION: [
                {"technique_id": "T1595", "name": "Active Scanning", "mitre_id": "T1595"},
                {"technique_id": "T1589", "name": "Gather Victim Identity Information", "mitre_id": "T1589"}
            ],
            CrisisPhase.SUSPICIOUS_ACTIVITY: [
                {"technique_id": "T1078", "name": "Valid Accounts", "mitre_id": "T1078"},
                {"technique_id": "T1110", "name": "Brute Force", "mitre_id": "T1110"},
                {"technique_id": "T1059", "name": "Command and Scripting Interpreter", "mitre_id": "T1059"}
            ],
            CrisisPhase.INITIAL_INCIDENT: [
                {"technique_id": "T1543", "name": "Create or Modify System Process", "mitre_id": "T1543"},
                {"technique_id": "T1055", "name": "Process Injection", "mitre_id": "T1055"},
                {"technique_id": "T1070", "name": "Indicator Removal", "mitre_id": "T1070"}
            ],
            CrisisPhase.ESCALATION_CRISIS: [
                {"technique_id": "T1021", "name": "Remote Services", "mitre_id": "T1021"},
                {"technique_id": "T1005", "name": "Data from Local System", "mitre_id": "T1005"},
                {"technique_id": "T1041", "name": "Exfiltration Over C2 Channel", "mitre_id": "T1041"}
            ],
            CrisisPhase.CONTAINMENT: [
                {"technique_id": "T1486", "name": "Data Encrypted for Impact", "mitre_id": "T1486"},
                {"technique_id": "T1490", "name": "Inhibit System Recovery", "mitre_id": "T1490"}
            ],
            CrisisPhase.RECOVERY: [
                {"technique_id": "T1490", "name": "Inhibit System Recovery", "mitre_id": "T1490"},
                {"technique_id": "T1485", "name": "Data Destruction", "mitre_id": "T1485"}
            ]
        }
        
        return phase_ttps.get(phase, [])[:limit]
    
    def initialize_ttp_database(self, ttps: List[Dict[str, Any]]):
        """
        Initialisiert die TTP-Datenbank mit TTPs.
        
        Args:
            ttps: Liste von TTP-Dictionaries mit:
                - technique_id: Eindeutige ID
                - name: Name
                - description: Beschreibung
                - mitre_id: MITRE ATT&CK ID
                - phase: Zuordnung zu Phase
        """
        try:
            # Erstelle oder hole Collection
            if self.collection:
                self.client.delete_collection(name=self.collection_name)
            
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "MITRE ATT&CK TTPs für Szenario-Generierung"}
            )
            
            # Füge TTPs hinzu
            ids = []
            documents = []
            metadatas = []
            
            for ttp in ttps:
                ids.append(ttp.get("technique_id", ttp.get("mitre_id", "")))
                documents.append(ttp.get("description", ttp.get("name", "")))
                metadatas.append({
                    "name": ttp.get("name", ""),
                    "mitre_id": ttp.get("mitre_id", ttp.get("technique_id", "")),
                    "phase": ttp.get("phase", "")
                })
            
            if ids:
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
            
            print(f"✅ {len(ids)} TTPs in Datenbank geladen")
            
        except Exception as e:
            print(f"⚠️  Fehler beim Initialisieren der TTP-Datenbank: {e}")

