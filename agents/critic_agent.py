"""
Critic Agent - Wissenschaftlich basierte Validierung von Injects.

Verantwortlich für:
- Evidenzbasierte Validierung mit quantifizierbaren Metriken
- Statistische Signifikanz-Tests
- Multi-Layer Validierung (symbolisch → LLM)
- Compliance-Validierung mit variablen Standards
- Causal Validity (MITRE ATT&CK Graph Konformität)
- Refine-Loop mit wissenschaftlichen Verbesserungsvorschlägen

Wissenschaftliche Methoden:
- Quantifizierbare Metriken (0.0-1.0 Scores)
- Konfidenz-Intervalle (95% CI)
- Statistische Signifikanz-Tests (p-value)
- Reproduzierbare Validierung
- Evidence-based Entscheidungen
"""

from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from state_models import Inject, ValidationResult, CrisisPhase
from workflows.fsm import CrisisFSM
from agents.critic_metrics import ScientificValidator, ValidationMetrics
from utils.json_encoder import DateTimeEncoder
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from pathlib import Path

# Optional: Compliance-Framework Import (für variable Compliance-Standards)
COMPLIANCE_AVAILABLE = False
ComplianceStandard = None
DORAComplianceFramework = None
NISTComplianceFramework = None
ISO27001ComplianceFramework = None

try:
    import sys
    import importlib.util
    from pathlib import Path
    # Ensure parent directory is in path
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    # Handle case-insensitive filesystem (macOS): Import Compliance as compliance
    # Use importlib to load Compliance directory as 'compliance' module
    compliance_dir = parent_dir / "Compliance"
    if compliance_dir.exists() and compliance_dir.is_dir():
        # Load the module using importlib
        spec = importlib.util.spec_from_file_location(
            "compliance", 
            compliance_dir / "__init__.py",
            submodule_search_locations=[str(compliance_dir)]
        )
        if spec and spec.loader:
            compliance_module = importlib.util.module_from_spec(spec)
            sys.modules["compliance"] = compliance_module
            spec.loader.exec_module(compliance_module)
            
            # Now import from the loaded module
            from compliance.base import ComplianceStandard
            from compliance.dora import DORAComplianceFramework
            from compliance.nist import NISTComplianceFramework
            from compliance.iso27001 import ISO27001ComplianceFramework
            COMPLIANCE_AVAILABLE = True
        else:
            COMPLIANCE_AVAILABLE = False
    else:
        # Fallback: try normal import (in case directory is already lowercase)
        from compliance.base import ComplianceStandard
        from compliance.dora import DORAComplianceFramework
        from compliance.nist import NISTComplianceFramework
        from compliance.iso27001 import ISO27001ComplianceFramework
        COMPLIANCE_AVAILABLE = True
except (ImportError, ModuleNotFoundError, Exception) as e:
    # Fallback für Rückwärtskompatibilität - funktioniert auch ohne compliance Modul
    COMPLIANCE_AVAILABLE = False

load_dotenv()


class CriticAgent:
    """
    Critic Agent für Inject-Validierung.
    
    Simuliert Compliance- und Tech-Experten zur Validierung von Injects.
    Führt Reflect-Refine Loop durch, um Injects zu verbessern.
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0.3,
        compliance_standards: Optional[List[ComplianceStandard]] = None
    ):
        """
        Initialisiert den Critic Agent.
        
        Args:
            model_name: OpenAI Modell-Name
            temperature: Temperature (niedrig für konsistente Validierung)
            compliance_standards: Liste von Compliance-Standards (Standard: [DORA])
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialisiere Compliance-Frameworks
        self.compliance_frameworks: Dict[str, Any] = {}
        if COMPLIANCE_AVAILABLE and ComplianceStandard is not None:
            if compliance_standards is None:
                compliance_standards = [ComplianceStandard.DORA]
            
            for standard in compliance_standards:
                if standard == ComplianceStandard.DORA and DORAComplianceFramework is not None:
                    self.compliance_frameworks[standard] = DORAComplianceFramework()
                elif standard == ComplianceStandard.NIST and NISTComplianceFramework is not None:
                    self.compliance_frameworks[standard] = NISTComplianceFramework()
                elif standard == ComplianceStandard.ISO27001 and ISO27001ComplianceFramework is not None:
                    self.compliance_frameworks[standard] = ISO27001ComplianceFramework()
        
        # Initialisiere wissenschaftlichen Validator
        self.scientific_validator = ScientificValidator()
        
        # Metriken-Historie für statistische Analysen
        self.validation_history: List[Dict[str, float]] = []
    
    def validate_inject(
        self,
        inject: Inject,
        previous_injects: List[Inject],
        current_phase: CrisisPhase,
        system_state: Dict[str, Any],
        mode: str = 'thesis',
        compliance_standards: Optional[List[ComplianceStandard]] = None
    ) -> ValidationResult:
        """
        Validiert einen Inject mit mehrschichtiger Validierung.
        
        Strategie: Frühe symbolische Validierung VOR LLM-Call, um API-Costs zu sparen.
        
        Args:
            inject: Zu validierender Inject
            previous_injects: Liste vorheriger Injects für Konsistenz
            current_phase: Aktuelle Phase
            system_state: Aktueller Systemzustand
            mode: 'legacy' = Skip Validation (simuliert altes System), 'thesis' = Full Validation (Default)
        
        Returns:
            ValidationResult mit Validierungs-Ergebnissen
        """
        # LEGACY MODE: Skip Validation komplett (simuliert altes System ohne Logic Guard)
        if mode == 'legacy':
            print(f"[Critic] Legacy Mode: Skipping validation for {inject.inject_id}")
            return ValidationResult(
                is_valid=True,
                logical_consistency=True,
                dora_compliance=True,
                causal_validity=True,
                errors=[],
                warnings=[]
            )
        
        print(f"[Critic] Validiere Inject {inject.inject_id}")
        print(f"   Phase: {current_phase.value} → {inject.phase.value}")
        print(f"   Assets: {inject.technical_metadata.affected_assets}")
        print(f"   MITRE: {inject.technical_metadata.mitre_id}")
        
        errors = []
        warnings = []
        
        # ===== PHASE 1: SYMBOLISCHE VALIDIERUNG (OHNE LLM-CALL) =====
        # Diese Checks sind schnell und kostenlos - machen sie ZUERST
        
        print(f"🔧 [Critic] Phase 1: Symbolische Validierung (ohne LLM-Call)")
        
        # 1.1 Pydantic-Validierung (automatisch)
        try:
            # Inject ist bereits ein Pydantic-Model, Validierung erfolgt automatisch
            pydantic_valid = True
            print(f"   ✅ Pydantic-Validierung: OK")
        except Exception as e:
            print(f"   ❌ Pydantic-Validierung fehlgeschlagen: {e}")
            error_msg = f"Schema-Validierung fehlgeschlagen: {e}"
            # Logge auch Pydantic-Fehler für Audit
            formatted_system_state_str = self._format_system_state(system_state)
            self._log_critic_decision(
                inject_id=inject.inject_id,
                inject=inject,
                system_state=system_state,
                previous_injects=previous_injects,
                current_phase=current_phase,
                llm_validation={"logical_consistency": False, "causal_validity": False, "regulatory_compliance": True, "_raw_llm_output": "Pydantic-Validierungsfehler - kein LLM-Call"},
                final_result={
                    "is_valid": False,
                    "errors": [error_msg],
                    "warnings": [],
                    "pydantic_valid": False,
                    "fsm_valid": True,  # Noch nicht geprüft
                    "state_valid": True,  # Noch nicht geprüft
                    "temporal_valid": True,  # Noch nicht geprüft
                    "logical_consistency": False,
                    "causal_validity": False,
                    "causal_blocking": False
                },
                formatted_system_state_str=formatted_system_state_str
            )
            return ValidationResult(
                is_valid=False,
                logical_consistency=False,
                dora_compliance=True,  # Für Rückwärtskompatibilität
                causal_validity=False,
                errors=[error_msg]
            )
        
        # 1.2 FSM-Validierung (Phase-Übergang) - KRITISCH, früh prüfen
        print(f"   🔧 FSM-Validierung...")
        fsm_result = self._validate_phase_transition_detailed(inject, current_phase, previous_injects)
        if not fsm_result["valid"]:
            errors.extend(fsm_result["errors"])
            print(f"   ❌ FSM-Verstoß: {fsm_result['errors']}")
            # FSM-Verstoß ist kritisch - kein LLM-Call nötig
            # Logge trotzdem für Audit
            formatted_system_state_str = self._format_system_state(system_state)
            self._log_critic_decision(
                inject_id=inject.inject_id,
                inject=inject,
                system_state=system_state,
                previous_injects=previous_injects,
                current_phase=current_phase,
                llm_validation={"logical_consistency": False, "causal_validity": True, "regulatory_compliance": True, "_raw_llm_output": "FSM-Fehler - kein LLM-Call"},
                final_result={
                    "is_valid": False,
                    "errors": errors,
                    "warnings": fsm_result.get("warnings", []),
                    "pydantic_valid": pydantic_valid,
                    "fsm_valid": False,
                    "state_valid": True,  # Noch nicht geprüft
                    "temporal_valid": True,  # Noch nicht geprüft
                    "logical_consistency": False,
                    "causal_validity": True,
                    "causal_blocking": False
                },
                formatted_system_state_str=formatted_system_state_str
            )
            return ValidationResult(
                is_valid=False,
                logical_consistency=False,
                dora_compliance=True,  # Unbekannt ohne LLM-Call
                causal_validity=True,  # Unbekannt ohne LLM-Call
                errors=errors,
                warnings=fsm_result.get("warnings", [])
            )
        print(f"   ✅ FSM-Validierung: OK")
        
        # 1.3 State-Consistency-Check (Asset-Existenz, Status-Konsistenz)
        print(f"   🔧 State-Consistency-Check...")
        state_result = self._validate_state_consistency(inject, system_state, previous_injects)
        if not state_result["valid"]:
            errors.extend(state_result["errors"])
            warnings.extend(state_result.get("warnings", []))
            print(f"   ❌ State-Inkonsistenz: {state_result['errors']}")
            # State-Inkonsistenz ist kritisch - kein LLM-Call nötig
            # Logge trotzdem für Audit
            formatted_system_state_str = self._format_system_state(system_state)
            self._log_critic_decision(
                inject_id=inject.inject_id,
                inject=inject,
                system_state=system_state,
                previous_injects=previous_injects,
                current_phase=current_phase,
                llm_validation={"logical_consistency": False, "causal_validity": True, "regulatory_compliance": True, "_raw_llm_output": "State-Fehler - kein LLM-Call"},
                final_result={
                    "is_valid": False,
                    "errors": errors,
                    "warnings": warnings,
                    "pydantic_valid": pydantic_valid,
                    "fsm_valid": fsm_result["valid"],
                    "state_valid": False,
                    "temporal_valid": True,  # Noch nicht geprüft
                    "logical_consistency": False,
                    "causal_validity": True,
                    "causal_blocking": False
                },
                formatted_system_state_str=formatted_system_state_str
            )
            return ValidationResult(
                is_valid=False,
                logical_consistency=False,
                dora_compliance=True,  # Unbekannt ohne LLM-Call
                causal_validity=True,  # Unbekannt ohne LLM-Call
                errors=errors,
                warnings=warnings
            )
        print(f"   ✅ State-Consistency: OK")
        
        # 1.4 Temporale Konsistenz-Check
        print(f"   🔧 Temporale Konsistenz-Check...")
        temporal_result = self._validate_temporal_consistency(inject, previous_injects)
        if not temporal_result["valid"]:
            errors.extend(temporal_result["errors"])
            warnings.extend(temporal_result.get("warnings", []))
            print(f"   ❌ Temporale Inkonsistenz: {temporal_result['errors']}")
            # Temporale Inkonsistenz ist kritisch - kein LLM-Call nötig
            # Logge trotzdem für Audit
            formatted_system_state_str = self._format_system_state(system_state)
            self._log_critic_decision(
                inject_id=inject.inject_id,
                inject=inject,
                system_state=system_state,
                previous_injects=previous_injects,
                current_phase=current_phase,
                llm_validation={"logical_consistency": False, "causal_validity": True, "regulatory_compliance": True, "_raw_llm_output": "Temporaler Fehler - kein LLM-Call"},
                final_result={
                    "is_valid": False,
                    "errors": errors,
                    "warnings": warnings,
                    "pydantic_valid": pydantic_valid,
                    "fsm_valid": fsm_result["valid"],
                    "state_valid": state_result["valid"],
                    "temporal_valid": False,
                    "logical_consistency": False,
                    "causal_validity": True,
                    "causal_blocking": False
                },
                formatted_system_state_str=formatted_system_state_str
            )
            return ValidationResult(
                is_valid=False,
                logical_consistency=False,
                dora_compliance=True,
                causal_validity=True,
                errors=errors,
                warnings=warnings
            )
        print(f"   ✅ Temporale Konsistenz: OK")
        
        warnings.extend(state_result.get("warnings", []))
        warnings.extend(temporal_result.get("warnings", []))
        
        # ===== PHASE 2: LLM-BASIERTE VALIDIERUNG (NUR WENN SYMBOLISCHE CHECKS OK) =====
        # Nur wenn alle symbolischen Checks passiert sind, LLM-Call machen
        print(f"🔧 [Critic] Phase 2: LLM-basierte Validierung (alle symbolischen Checks OK)")
        # Speichere formatierten System-State für Audit-Log
        formatted_system_state_str = self._format_system_state(system_state)
        
        # Compliance-Validierung mit variablen Standards
        compliance_results: Dict[str, Any] = {}
        if COMPLIANCE_AVAILABLE and self.compliance_frameworks:
            if compliance_standards is None:
                compliance_standards = list(self.compliance_frameworks.keys())
            
            for standard in compliance_standards:
                if standard in self.compliance_frameworks:
                    framework = self.compliance_frameworks[standard]
                    try:
                        compliance_result = framework.validate_inject(
                            inject_content=inject.content,
                            inject_phase=current_phase.value,
                            inject_metadata={
                                "mitre_id": inject.technical_metadata.mitre_id,
                                "affected_assets": inject.technical_metadata.affected_assets,
                                "severity": inject.technical_metadata.severity
                            },
                            context={
                                "previous_injects": [
                                    {
                                        "inject_id": inj.inject_id,
                                        "content": inj.content,
                                        "phase": inj.phase.value
                                    }
                                    for inj in previous_injects
                                ]
                            }
                        )
                        if ComplianceStandard is not None:
                            compliance_results[standard.value] = compliance_result
                        else:
                            compliance_results[str(standard)] = compliance_result
                    except Exception as e:
                        print(f"⚠️  Fehler bei Compliance-Validierung ({standard}): {e}")
        
        llm_validation = self._llm_validate(inject, previous_injects, current_phase, system_state, formatted_system_state_str, compliance_results)
        print(f"   LLM-Ergebnis: logical_consistency={llm_validation['logical_consistency']}, "
              f"regulatory_compliance={llm_validation.get('regulatory_compliance', llm_validation.get('dora_compliance', True))}, "
              f"causal_validity={llm_validation['causal_validity']}")
        
        # Kombiniere alle Ergebnisse
        errors.extend(llm_validation.get("errors", []) or [])
        warnings.extend(llm_validation.get("warnings", []) or [])
        
        # Füge Compliance-Warnungen hinzu
        for standard, result in compliance_results.items():
            if not result.is_compliant:
                warnings.append(f"{standard} Compliance: {', '.join(result.requirements_missing)} fehlen")
            if result.warnings:
                warnings.extend([f"{standard}: {w}" for w in result.warnings])
        
        # Finale Validierung
        # Compliance ist weniger kritisch (nur Warnung, kein Blocking-Fehler)
        # Causal Validity: Nur blockieren wenn wirklich unmöglich, sonst Warnung
        critical_errors = (
            not pydantic_valid
            or not fsm_result["valid"]
            or not state_result["valid"]
            or not temporal_result["valid"]
            or not llm_validation["logical_consistency"]
        )
        
        # Causal Validity: Nur blockieren wenn wirklich unmöglich (z.B. Exfiltration vor Initial Access)
        # Sonst nur Warnung
        causal_blocking = False
        if not llm_validation["causal_validity"]:
            # Prüfe ob es wirklich unmöglich ist oder nur ungewöhnlich
            mitre_id = inject.technical_metadata.mitre_id or ""
            # Nur wirklich unmögliche Sequenzen blockieren
            impossible_sequences = [
                ("T1041", CrisisPhase.NORMAL_OPERATION),  # Exfiltration vor Initial Access
                ("T1486", CrisisPhase.NORMAL_OPERATION),  # Impact vor Execution
                ("T1041", CrisisPhase.SUSPICIOUS_ACTIVITY),  # Exfiltration vor Initial Access
            ]
            if (mitre_id, current_phase) in impossible_sequences:
                causal_blocking = True
        
        is_valid = not critical_errors and not causal_blocking
        
        # Stelle sicher, dass bei invalider Antwort immer eine Begründung vorhanden ist
        if not is_valid:
            if not errors:
                # Sammle alle Gründe warum es nicht valide ist
                reasons = []
                if not pydantic_valid:
                    reasons.append("Pydantic Schema-Validierung fehlgeschlagen")
                if not fsm_result["valid"]:
                    reasons.append("FSM-Phasen-Übergang nicht erlaubt")
                if not state_result["valid"]:
                    reasons.append("State-Konsistenz-Verstoß")
                if not temporal_result["valid"]:
                    reasons.append("Temporale Inkonsistenz")
                if not llm_validation["logical_consistency"]:
                    reasons.append("Logische Inkonsistenz")
                if causal_blocking:
                    reasons.append("Kausale Validität nicht gegeben (unmögliche Sequenz)")
                # DORA-Compliance ist nicht mehr blockierend - nur Warnung
                
                if reasons:
                    errors.append(f"Validierung fehlgeschlagen: {', '.join(reasons)}")
                else:
                    errors.append("Validierung fehlgeschlagen, aber keine spezifischen Fehler gefunden.")
        
        print(f"🔍 [Critic] Validierung abgeschlossen für {inject.inject_id}")
        print(f"   Ergebnis: {'✅ VALIDE' if is_valid else '❌ NICHT VALIDE'}")
        print(f"   Fehler: {len(errors)}, Warnungen: {len(warnings)}")
        if errors:
            print(f"   Fehler-Details: {errors[:3]}")  # Erste 3 Fehler
        
        # ===== WISSENSCHAFTLICHE METRIKEN-BERECHNUNG =====
        # Berechne quantifizierbare Metriken für evidenzbasierte Entscheidung
        print(f"🔬 [Critic] Berechne wissenschaftliche Metriken...")
        
        # 1. Logische Konsistenz-Score
        logical_score = self.scientific_validator.calculate_logical_consistency_score(
            inject=inject,
            previous_injects=previous_injects,
            system_state=system_state
        )
        
        # 2. Kausale Validität-Score
        causal_score = self.scientific_validator.calculate_causal_validity_score(
            inject=inject,
            current_phase=current_phase,
            mitre_id=inject.technical_metadata.mitre_id
        )
        
        # 3. Compliance-Score
        compliance_score = self.scientific_validator.calculate_compliance_score(
            compliance_results=compliance_results
        )
        
        # 4. Temporale Konsistenz-Score
        temporal_score = self.scientific_validator.calculate_temporal_consistency_score(
            inject=inject,
            previous_injects=previous_injects
        ) if previous_injects else 1.0
        
        # 5. Asset-Konsistenz-Score
        asset_score = self.scientific_validator._check_asset_name_consistency(
            inject=inject,
            previous_injects=previous_injects
        )
        
        # Erstelle Metriken-Objekt
        metrics = ValidationMetrics(
            logical_consistency_score=logical_score,
            causal_validity_score=causal_score,
            compliance_score=compliance_score,
            temporal_consistency_score=temporal_score,
            asset_consistency_score=asset_score,
            sample_size=len(previous_injects),
            validation_method="multi_layer"
        )
        
        # Berechne Gesamt-Qualitäts-Score
        metrics.overall_quality_score = self.scientific_validator.calculate_overall_quality_score(metrics)
        
        # Berechne Konfidenz-Intervalle
        if len(previous_injects) >= 2:
            metrics.confidence_interval = self.scientific_validator.calculate_confidence_interval(
                score=metrics.overall_quality_score,
                sample_size=len(previous_injects)
            )
        
        # Statistische Signifikanz-Test
        if len(self.validation_history) >= 2:
            historical_scores = [h["overall_quality_score"] for h in self.validation_history[-10:]]
            significance_test = self.scientific_validator.statistical_significance_test(
                current_score=metrics.overall_quality_score,
                historical_scores=historical_scores
            )
            metrics.p_value = significance_test.get("p_value")
            metrics.statistical_significance = significance_test.get("significant", False)
        
        # Speichere Metriken in Historie
        self.validation_history.append({
            "inject_id": inject.inject_id,
            "overall_quality_score": metrics.overall_quality_score,
            "logical_consistency_score": logical_score,
            "causal_validity_score": causal_score,
            "compliance_score": compliance_score
        })
        
        # Begrenze Historie auf letzte 100 Einträge
        if len(self.validation_history) > 100:
            self.validation_history = self.validation_history[-100:]
        
        print(f"   📊 Metriken: Logical={logical_score:.2f}, Causal={causal_score:.2f}, "
              f"Compliance={compliance_score:.2f}, Overall={metrics.overall_quality_score:.2f}")
        
        # Wissenschaftlich basierte Entscheidung: Verwende Overall Quality Score
        # Anpassung der Validierung basierend auf Metriken
        if metrics.overall_quality_score < self.scientific_validator.thresholds["critical"]:
            # Kritischer Score: Zusätzliche Fehler hinzufügen
            if not any("Qualität" in e for e in errors):
                errors.append(f"Qualitäts-Score zu niedrig: {metrics.overall_quality_score:.2f} < {self.scientific_validator.thresholds['critical']:.2f}")
        elif metrics.overall_quality_score < self.scientific_validator.thresholds["warning"]:
            # Warnung bei mittlerem Score
            if not any("Qualität" in w for w in warnings):
                warnings.append(f"Qualitäts-Score könnte verbessert werden: {metrics.overall_quality_score:.2f}")
        
        # Compliance-Ergebnisse zusammenfassen
        overall_compliance = all(
            getattr(result, 'is_compliant', True)
            for result in compliance_results.values()
        ) if compliance_results else True

        # ===== DEEP TRUTH LOGGING =====
        # Logge die vollständige Entscheidung für Debugging
        self._log_critic_decision(
            inject_id=inject.inject_id,
            inject=inject,
            system_state=system_state,
            previous_injects=previous_injects,
            current_phase=current_phase,
            llm_validation=llm_validation,
            final_result={
                "is_valid": is_valid,
                "errors": errors,
                "warnings": warnings,
                "pydantic_valid": pydantic_valid,
                "fsm_valid": fsm_result["valid"],
                "state_valid": state_result["valid"],
                "temporal_valid": temporal_result["valid"],
                "logical_consistency": llm_validation["logical_consistency"],
                "causal_validity": llm_validation["causal_validity"],
                "compliance_results": {
                    standard: {
                        "is_compliant": result.is_compliant,
                        "requirements_met": result.requirements_met,
                        "requirements_missing": result.requirements_missing
                    }
                    for standard, result in compliance_results.items()
                } if compliance_results else None,
                "causal_blocking": causal_blocking
            },
            formatted_system_state_str=formatted_system_state_str if 'formatted_system_state_str' in locals() else None
        )

        return ValidationResult(
            is_valid=is_valid,
            logical_consistency=(
                fsm_result["valid"] 
                and state_result["valid"] 
                and temporal_result["valid"]
                and llm_validation["logical_consistency"]
            ),
            dora_compliance=overall_compliance,  # Rückwärtskompatibilität
            causal_validity=llm_validation["causal_validity"],
            errors=errors,
            warnings=warnings,
            compliance_results={
                standard: result.dict()
                for standard, result in compliance_results.items()
            } if compliance_results else None
        )
    
    def _validate_phase_transition(
        self,
        inject: Inject,
        current_phase: CrisisPhase,
        previous_injects: List[Inject]
    ) -> bool:
        """Validiert, ob der Phase-Übergang erlaubt ist."""
        # Prüfe ob Phase-Übergang erlaubt ist
        if inject.phase != current_phase:
            # Phase hat sich geändert - prüfe ob Übergang erlaubt
            return CrisisFSM.can_transition(current_phase, inject.phase)
        
        # Phase bleibt gleich - das ist immer erlaubt
        return True
    
    def _validate_phase_transition_detailed(
        self,
        inject: Inject,
        current_phase: CrisisPhase,
        previous_injects: List[Inject]
    ) -> Dict[str, Any]:
        """
        Detaillierte FSM-Validierung mit Fehlermeldungen.
        
        Returns:
            Dict mit "valid" (bool), "errors" (List[str]), "warnings" (List[str])
        """
        errors = []
        warnings = []
        
        # Phase-Übergang prüfen
        if inject.phase != current_phase:
            if not CrisisFSM.can_transition(current_phase, inject.phase):
                errors.append(
                    f"FSM-Verstoß: Übergang von {current_phase.value} zu {inject.phase.value} ist nicht erlaubt. "
                    f"Erlaubte Übergänge von {current_phase.value}: {[p.value for p in CrisisFSM.get_next_phases(current_phase)]}"
                )
                return {"valid": False, "errors": errors, "warnings": warnings}
        
        # Prüfe ob Phase zur Sequenz passt (heuristisch)
        if previous_injects:
            last_phase = previous_injects[-1].phase if previous_injects else current_phase
            # Warnung wenn Phase zurückgeht (außer RECOVERY → NORMAL_OPERATION)
            if inject.phase.value < last_phase.value and not (
                last_phase == CrisisPhase.RECOVERY and inject.phase == CrisisPhase.NORMAL_OPERATION
            ):
                warnings.append(
                    f"Phase geht zurück: {last_phase.value} → {inject.phase.value}. "
                    "Prüfe ob dies logisch ist."
                )
        
        return {"valid": True, "errors": errors, "warnings": warnings}
    
    def _validate_state_consistency(
        self,
        inject: Inject,
        system_state: Dict[str, Any],
        previous_injects: List[Inject]
    ) -> Dict[str, Any]:
        """
        Validiert State-Konsistenz (Asset-Existenz, Status-Konsistenz).
        
        Returns:
            Dict mit "valid" (bool), "errors" (List[str]), "warnings" (List[str])
        """
        errors = []
        warnings = []
        
        # ID-FIRST VALIDATION: Check if asset_id exists in state
        # Only fail if ID is missing, not if description name mismatches
        affected_assets = inject.technical_metadata.affected_assets or []
        
        # Extract known asset IDs from system_state
        known_asset_ids = []
        for entity_id in system_state.keys():
            if not (entity_id.startswith("INJ-") or entity_id.startswith("SCEN-")):
                if isinstance(system_state[entity_id], dict):
                    entity_type = system_state[entity_id].get("entity_type", "").lower()
                    if entity_type in ["server", "application", "database", "service", "asset"] or \
                       entity_id.startswith(("SRV-", "APP-", "DB-", "SVC-")):
                        known_asset_ids.append(entity_id)
        
        for asset_id in affected_assets:
            # ID-FIRST: Check if asset_id exists
            if asset_id in known_asset_ids or asset_id in system_state:
                # ID is correct. Now check description (optional - only warning, not error)
                asset_data = system_state.get(asset_id, {})
                if isinstance(asset_data, dict):
                    asset_name = asset_data.get("name", "")
                    # Check if content mentions asset with different name (optional check)
                    content_lower = inject.content.lower()
                    asset_name_lower = asset_name.lower() if asset_name else ""
                    # This is just for logging - we don't fail on name mismatches
                    if asset_name_lower and asset_name_lower not in content_lower and asset_id.lower() not in content_lower:
                        # Name mismatch detected, but ID is valid - only warning
                        warnings.append(
                            f"Name mismatch for {asset_id}: Content may use different name than '{asset_name}', but ID is valid. Proceeding."
                        )
                    
                    # Prüfe Status-Konsistenz
                    asset_status = asset_data.get("status", "unknown")
                    
                    # Warnung wenn Asset bereits offline/compromised ist und als aktiv behandelt wird
                    if asset_status in ["offline", "compromised", "encrypted"]:
                        # Prüfe ob Inject versucht, auf diesem Asset zu agieren
                        if any(keyword in content_lower for keyword in ["attack", "access", "lateral", "move"]):
                            warnings.append(
                                f"Asset '{asset_id}' ist bereits {asset_status}, aber Inject behandelt es als aktiv. "
                                "Prüfe ob dies logisch ist."
                            )
            else:
                # Asset ID does not exist - THIS IS AN ERROR
                errors.append(
                    f"Unknown Asset ID: {asset_id}. "
                    f"Verfügbare Assets: {known_asset_ids[:10] if known_asset_ids else list(system_state.keys())[:10]}"
                )
        
        # Prüfe Asset-Name-Konsistenz mit vorherigen Injects
        if previous_injects:
            asset_names_used = set()
            for prev_inj in previous_injects[-3:]:  # Letzte 3 Injects
                asset_names_used.update(prev_inj.technical_metadata.affected_assets or [])
            
            # Warnung wenn komplett neue Assets ohne Kontext eingeführt werden
            new_assets = set(affected_assets) - asset_names_used
            if new_assets and len(asset_names_used) > 0:
                warnings.append(
                    f"Neue Assets ohne vorherigen Kontext eingeführt: {new_assets}. "
                    "Prüfe ob dies logisch ist."
                )
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_temporal_consistency(
        self,
        inject: Inject,
        previous_injects: List[Inject]
    ) -> Dict[str, Any]:
        """
        Validiert temporale Konsistenz (Zeitstempel, Sequenz).
        
        Returns:
            Dict mit "valid" (bool), "errors" (List[str]), "warnings" (List[str])
        """
        errors = []
        warnings = []
        
        if not previous_injects:
            return {"valid": True, "errors": errors, "warnings": warnings}
        
        # Parse Zeitstempel
        def parse_time_offset(offset: str) -> int:
            """Konvertiert T+HH:MM zu Minuten seit Start."""
            try:
                match = offset.replace("T+", "").split(":")
                hours = int(match[0])
                minutes = int(match[1])
                return hours * 60 + minutes
            except:
                return 0
        
        current_time = parse_time_offset(inject.time_offset)
        
        # Prüfe ob Zeitstempel zurückgeht
        for prev_inj in previous_injects:
            prev_time = parse_time_offset(prev_inj.time_offset)
            if current_time < prev_time:
                errors.append(
                    f"Temporale Inkonsistenz: Inject {inject.inject_id} hat Zeitstempel {inject.time_offset}, "
                    f"aber vorheriger Inject {prev_inj.inject_id} hat {prev_inj.time_offset} (später). "
                    "Zeitstempel müssen chronologisch sein."
                )
                return {"valid": False, "errors": errors, "warnings": warnings}
        
        # Warnung wenn Zeitstempel sehr weit in der Zukunft springt
        if previous_injects:
            last_time = parse_time_offset(previous_injects[-1].time_offset)
            time_diff = current_time - last_time
            if time_diff > 120:  # Mehr als 2 Stunden Sprung
                warnings.append(
                    f"Großer Zeitsprung: {time_diff} Minuten seit letztem Inject. "
                    "Prüfe ob dies realistisch ist."
                )
        
        return {"valid": True, "errors": errors, "warnings": warnings}
    
    def _check_regulatory_compliance(self, inject: Inject, current_phase: CrisisPhase) -> Dict[str, Any]:
        """
        Generische Regulatorik-Prüfung (Business Continuity, Incident Response).
        
        Fokus auf Architektur-Funktionalität. Regulatorische Anforderungen sind phasenabhängig:
        - Frühe Phasen (NORMAL_OPERATION, SUSPICIOUS_ACTIVITY): Incident Response wichtig
        - Mittlere Phasen (INITIAL_INCIDENT, ESCALATION_CRISIS): Response + Business Continuity
        - Späte Phasen (CONTAINMENT, RECOVERY): Business Continuity + Recovery Plan
        """
        checklist = {
            "risk_management_framework_tested": False,
            "business_continuity_policy_tested": False,
            "response_plan_tested": False,
            "recovery_plan_tested": False,
            "critical_functions_covered": False,
            "realistic_scenario": False,
            "documentation_adequate": False
        }
        
        issues = []
        warnings = []
        
        # Prüfe Content auf regulatorische Aspekte (generisch, keine spezifische Regulatorik)
        content_lower = inject.content.lower()
        
        # 1. Risk Management Framework Testing (optional, nicht kritisch)
        if any(keyword in content_lower for keyword in ["risk assessment", "risk management", "vulnerability", "threat"]):
            checklist["risk_management_framework_tested"] = True
        
        # 2. Business Continuity Policy Testing (nur für späte Phasen erwünscht)
        if any(keyword in content_lower for keyword in ["business continuity", "continuity plan", "operational resilience", "service disruption", "backup"]):
            checklist["business_continuity_policy_tested"] = True
        
        # 3. Response Plan Testing (wichtig für frühe/mittlere Phasen)
        if any(keyword in content_lower for keyword in ["incident response", "response plan", "soc", "security operations", "alert", "detection", "siem"]):
            checklist["response_plan_tested"] = True
        
        # 4. Recovery Plan Testing (nur für RECOVERY-Phase erwünscht)
        if any(keyword in content_lower for keyword in ["recovery", "restore", "backup", "restoration", "remediation"]):
            checklist["recovery_plan_tested"] = True
        
        # 5. Critical Functions Covered (optional, generisch)
        if inject.business_impact or any(keyword in content_lower for keyword in ["critical", "essential", "core", "service"]):
            checklist["critical_functions_covered"] = True
        
        # 6. Realistic Scenario (immer wichtig)
        if inject.technical_metadata.mitre_id and len(inject.technical_metadata.affected_assets) > 0:
            checklist["realistic_scenario"] = True
        else:
            issues.append("Inject benötigt technische Details (MITRE ID, Assets)")
        
        # 7. Documentation Adequate (immer wichtig)
        if len(inject.content) > 50 and inject.technical_metadata.mitre_id:
            checklist["documentation_adequate"] = True
        else:
            issues.append("Inject-Dokumentation sollte detaillierter sein (mindestens 50 Zeichen)")
        
        # PHASENABHÄNGIGE Compliance-Bewertung
        # Frühe Phasen: Response Plan wichtig, Rest optional
        # Späte Phasen: Business Continuity + Recovery wichtig
        
        if current_phase in [CrisisPhase.NORMAL_OPERATION, CrisisPhase.SUSPICIOUS_ACTIVITY]:
            # Frühe Phasen: Response Plan sollte erwähnt werden, Rest optional
            phase_requirements_met = checklist["response_plan_tested"] or checklist["risk_management_framework_tested"]
        elif current_phase in [CrisisPhase.INITIAL_INCIDENT, CrisisPhase.ESCALATION_CRISIS]:
            # Mittlere Phasen: Response Plan wichtig, Business Continuity optional
            phase_requirements_met = checklist["response_plan_tested"]
        elif current_phase == CrisisPhase.CONTAINMENT:
            # Containment: Business Continuity wichtig
            phase_requirements_met = checklist["business_continuity_policy_tested"] or checklist["response_plan_tested"]
        elif current_phase == CrisisPhase.RECOVERY:
            # Recovery: Recovery Plan wichtig
            phase_requirements_met = checklist["recovery_plan_tested"] or checklist["business_continuity_policy_tested"]
        else:
            # Fallback: Mindestens eine Komponente
            phase_requirements_met = any([
                checklist["risk_management_framework_tested"],
                checklist["response_plan_tested"],
                checklist["business_continuity_policy_tested"],
                checklist["recovery_plan_tested"]
            ])
        
        # Basis-Anforderungen (immer wichtig)
        has_basic_requirements = (
            checklist["realistic_scenario"] and 
            checklist["documentation_adequate"]
        )
        
        # Compliance ist erfüllt wenn:
        # 1. Phasenabhängige Anforderungen erfüllt ODER mindestens eine Komponente getestet
        # 2. Basis-Anforderungen erfüllt
        # 3. Keine kritischen Issues
        compliance_status = (
            (phase_requirements_met or any([
                checklist["risk_management_framework_tested"],
                checklist["response_plan_tested"],
                checklist["business_continuity_policy_tested"],
                checklist["recovery_plan_tested"]
            ]))
            and has_basic_requirements 
            and len(issues) == 0
        )
        
        return {
            "compliance_status": compliance_status,
            "checklist_results": checklist,
            "issues": issues,
            "warnings": warnings
        }
    
    def _llm_validate(
        self,
        inject: Inject,
        previous_injects: List[Inject],
        current_phase: CrisisPhase,
        system_state: Dict[str, Any],
        formatted_system_state_str: Optional[str] = None,
        compliance_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """LLM-basierte Validierung mit variablen Compliance-Standards."""
        
        # Generische Regulatorik-Check (vor LLM-Call)
        regulatory_check = self._check_regulatory_compliance(inject, current_phase)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Du bist ein erfahrener Security- und Krisenmanagement-Experte.
Deine Aufgabe ist es, Injects für Krisenszenarien STRENG zu validieren.

WICHTIG: Du bist der QUALITÄTSGARANT des Systems. Sei PRÄZISE und STRENG.

VALIDIERUNGSKRITERIEN:

1. LOGISCHE KONSISTENZ (KRITISCH):
   - Widerspricht der Inject vorherigen Injects?
   - Ist die Sequenz logisch und kausal nachvollziehbar?
   - Ist der Content konsistent mit der Phase?
   
   ⚠️⚠️⚠️ KRITISCH - ASSET-NAMEN (DIESE REGEL IST ABSOLUT VERBINDLICH):
   
   ❌❌❌ FEHLER: Es ist KEIN FEHLER, wenn ein Asset sowohl mit ID als auch mit Namen bezeichnet wird!
   
   ✅✅✅ ERLAUBT (diese sind IMMER OK, niemals als Fehler melden):
   - "SRV-001" → OK
   - "DC-01" → OK (wenn SRV-001 = DC-01)
   - "SRV-001 (DC-01)" → OK (beide zusammen)
   - "Domain Controller SRV-001" → OK (Name + ID)
   - "Application Server APP-SRV-01 (SRV-002)" → OK (verschiedene Namen für dasselbe Asset)
   - "Payment Processing System" → OK (wenn APP-001 = Payment Processing System)
   - "APP-001" → OK
   - "Payment Processing System (APP-001)" → OK
   - "APP-001 wird als Payment Processing System bezeichnet" → OK (beide Namen verwendet)
   
   ❌ NUR DIESE SIND ECHTE FEHLER:
   - Asset-ID existiert nicht (z.B. verwendet "SRV-003" aber nur SRV-001, SRV-002 existieren)
   - Asset ist offline, wird aber als aktiv verwendet (z.B. "SRV-001 ist offline" in Inject 1, aber "Lateral Movement von SRV-001" in Inject 2)
   
   ⚠️ WICHTIG: Wenn ein Asset sowohl mit ID als auch mit Namen bezeichnet wird, ist das IMMER ERLAUBT. 
   Melde dies NIEMALS als "Asset-Name-Inkonsistenz" Fehler!

2. CAUSAL VALIDITY (KRITISCH):
   - Passt die MITRE ATT&CK Technik zur aktuellen Phase?
   - Ist die Sequenz technisch möglich?
   
   ⚠️ WICHTIG - KAUSALE LOGIK:
   - Phasen-Übergänge zeigen bereits die kausale Logik! Wenn wir von SUSPICIOUS_ACTIVITY zu INITIAL_INCIDENT gehen, ist das bereits ein kausaler Vorgänger
   - Du musst NICHT erwarten, dass jeder Schritt explizit in vorherigen Injects erwähnt wird
   - Prüfe nur, ob die Sequenz technisch möglich ist, nicht ob sie explizit erwähnt wurde
   
   WICHTIG: Sei nicht zu streng! Viele MITRE-Techniken können in mehreren Phasen vorkommen.
   
   BEISPIEL FÜR INVALIDITÄT (nur wirklich unmögliche Sequenzen):
   - Phase: NORMAL_OPERATION, MITRE: T1041 (Exfiltration) → FEHLER: Exfiltration vor Initial Access unmöglich!
   - Phase: NORMAL_OPERATION, MITRE: T1486 (Data Encrypted for Impact) → FEHLER: Impact vor Execution unmöglich!
   
   BEISPIEL FÜR VALIDITÄT (diese sind OK):
   - Phase: SUSPICIOUS_ACTIVITY, MITRE: T1595 (Active Scanning) → OK: Scanning kann in verschiedenen Phasen vorkommen
   - Phase: INITIAL_INCIDENT, MITRE: T1546.014 (Event Triggered Execution) → OK: Kann nach SUSPICIOUS_ACTIVITY vorkommen (Phasen-Übergang zeigt Logik)
   - Phase: INITIAL_INCIDENT, MITRE: T1480 (Execution Guardrails) → OK: Kann in verschiedenen Phasen vorkommen, auch wenn nicht explizit erwähnt

3. REGULATORISCHE ASPEKTE (optional, nicht blockierend):
   - Incident Response Plan Testing
   - Business Continuity Plan Testing
   - Recovery Plan Testing
   - Coverage of critical functions
   - Realistic scenario testing
   - Documentation adequate

VALIDIERUNGSREGELN:
- Sei STRENG aber FAIR: Bei echten Verstößen → FEHLER melden, bei Unsicherheiten → Warnung
- Jeder Fehler MUSS eine klare, spezifische Begründung haben
- Warnungen für potenzielle Probleme, Fehler für klare Verstöße
- Prüfe ALLE Aspekte: Logik, Kausalität, State, Temporalität
- ASSET-NAMEN: Erlaube sowohl IDs als auch Namen (siehe oben)
- KAUSALE LOGIK: Phasen-Übergänge zeigen bereits die Logik (siehe oben)

ANTWORT-FORMAT (STRICT JSON):
{{
    "logical_consistency": true/false,
    "regulatory_compliance": true/false,
    "causal_validity": true/false,
    "errors": ["Spezifischer Fehler 1 mit Begründung", "Spezifischer Fehler 2 mit Begründung"],
    "warnings": ["Potenzielle Warnung 1", "Potenzielle Warnung 2"]
}}

FEHLER-MUSTER (wenn diese auftreten → FEHLER):
- Asset existiert nicht im Systemzustand (z.B. verwendet "SRV-003" aber nur SRV-001, SRV-002 existieren)
- Asset ist offline, wird aber als aktiv behandelt (z.B. "SRV-001 ist offline" in Inject 1, aber "Lateral Movement von SRV-001" in Inject 2)
- MITRE-Technik passt nicht zur Phase (nur wirklich unmögliche Sequenzen, siehe oben)
- Temporale Inkonsistenz (Zeitstempel geht zurück)
- Asset-ID ist falsch (z.B. verwendet "SRV-003" statt "SRV-001")

WARNUNG-MUSTER (wenn diese auftreten → WARNUNG, nicht Fehler):
- Großer Zeitsprung ohne Erklärung
- Neue Assets ohne Kontext
- Ungewöhnliche aber mögliche Sequenz
- MITRE-Technik passt möglicherweise nicht perfekt zur Phase (aber technisch möglich)
- Kausale Sequenz könnte besser erklärt werden (aber Phasen-Übergang zeigt bereits Logik)

❌❌❌ ABSOLUT VERBOTEN - MELDE DIESE NIEMALS ALS FEHLER:
- "Asset-Name-Inkonsistenz" wenn ein Asset sowohl mit ID als auch mit Namen bezeichnet wird
- "Asset-Name-Inkonsistenz" wenn verschiedene Namen für dasselbe Asset verwendet werden (z.B. "SRV-001" und "DC-01")
- "Asset-Name-Inkonsistenz" wenn "Payment Processing System" und "APP-001" für dasselbe Asset verwendet werden
- "Asset-Name-Inkonsistenz" wenn "Application Server APP-SRV-01" und "SRV-002" für dasselbe Asset verwendet werden

⚠️ Wenn du denkst, dass verschiedene Namen für dasselbe Asset verwendet werden, ist das ERLAUBT. 
Melde es NIEMALS als Fehler, höchstens als Warnung wenn es wirklich verwirrend ist!"""),
            
            ("human", """Validiere folgenden Inject STRENG:

Inject:
{inject}

Aktuelle Phase: {current_phase}
Vorherige Phase: {previous_phase}

Vorherige Injects (für Konsistenz-Prüfung):
{previous_injects}

Systemzustand (verfügbare Assets und deren Status):
{system_state}

MITRE ATT&CK Technik: {mitre_id}
Regulatorische Checkliste (automatisch geprüft):
{regulatory_checklist_results}

SYMBOLISCHE VALIDIERUNG (bereits geprüft):
- FSM-Übergang: ✓ OK
- State-Consistency: ✓ OK
- Temporale Konsistenz: ✓ OK

LLM-VALIDIERUNG (deine Aufgabe):
Prüfe jetzt:
1. LOGISCHE KONSISTENZ: Widerspricht der Inject der Historie oder dem Systemzustand?
2. CAUSAL VALIDITY: Passt MITRE {mitre_id} zur Phase {current_phase} und zur Sequenz?
3. REGULATORISCHE ASPEKTE: Erfüllt der Inject die grundlegenden Anforderungen? (optional, nicht blockierend)

Antworte STRICT JSON (nur JSON, keine zusätzlichen Erklärungen außerhalb des JSON).""")
        ])
        
        # Formatierung
        previous_injects_str = self._format_previous_injects(previous_injects)
        system_state_str = formatted_system_state_str or self._format_system_state(system_state)
        inject_str = self._format_inject(inject)
        
        # Bestimme vorherige Phase
        previous_phase = previous_injects[-1].phase.value if previous_injects else current_phase.value
        
        # Formatiere Regulatorik-Checkliste für Prompt
        regulatory_checklist_str = "\n".join([
            f"- {key.replace('_', ' ').title()}: {'✓' if value else '✗'}"
            for key, value in regulatory_check["checklist_results"].items()
        ])
        
        chain = prompt | self.llm
        
        # Retry-Logik für LLM-Call
        from utils.retry_handler import safe_llm_call
        
        try:
            def _invoke_chain():
                return chain.invoke({
                    "inject": inject_str,
                    "current_phase": current_phase.value,
                    "previous_phase": previous_phase,
                    "previous_injects": previous_injects_str,
                    "system_state": system_state_str,
                    "mitre_id": inject.technical_metadata.mitre_id or "Unknown",
                    "regulatory_checklist_results": regulatory_checklist_str
                })
            
            response = safe_llm_call(
                _invoke_chain,
                max_attempts=3,
                default_return=None
            )
            
            if response is None:
                # Fallback: Verwende Regulatorik-Check Ergebnisse
                return {
                    "logical_consistency": True,
                    "regulatory_compliance": regulatory_check["compliance_status"],
                    "causal_validity": True,
                    "errors": regulatory_check["issues"],
                    "warnings": regulatory_check["warnings"] + ["Validierung konnte nicht durchgeführt werden - LLM-Call fehlgeschlagen"],
                    "_raw_llm_output": "LLM-Call fehlgeschlagen (response is None)"
                }
            
            # Parse JSON
            import json
            import re
            
            content = response.content
            raw_llm_output = content  # Speichere RAW Output für Audit-Log
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            
            if json_match:
                validation = json.loads(json_match.group())
                
                # Extrahiere und validiere Felder
                logical_consistency = validation.get("logical_consistency", True)
                causal_validity = validation.get("causal_validity", True)
                llm_regulatory_compliance = validation.get("regulatory_compliance", True)
                
                # Kombiniere LLM-Validierung mit Regulatorik-Check
                combined_errors = validation.get("errors", []) or []
                combined_warnings = validation.get("warnings", []) or []
                
                # POST-PROCESSING: Konvertiere falsche "Asset-Name-Inkonsistenz" Fehler zu Warnungen
                # Der LLM meldet manchmal fälschlicherweise Asset-Name-Inkonsistenzen als Fehler,
                # obwohl verschiedene Namen für dasselbe Asset erlaubt sind
                asset_name_error_patterns = [
                    "Asset-Name-Inkonsistenz",
                    "wird sowohl als",
                    "als auch als",
                    "bezeichnet",
                    "sollte aber",
                    "nicht als"
                ]
                
                # Prüfe ob es sich um eine Asset-Name-Inkonsistenz handelt
                real_errors = []
                for error in combined_errors:
                    is_asset_name_error = any(pattern.lower() in error.lower() for pattern in asset_name_error_patterns)
                    # Prüfe ob es ein echter Fehler ist (falsche Asset-ID oder offline Asset)
                    is_real_error = (
                        "existiert nicht" in error.lower() or
                        "offline" in error.lower() or
                        "nicht im Systemzustand" in error.lower() or
                        "Asset-ID ist falsch" in error.lower()
                    )
                    
                    if is_asset_name_error and not is_real_error:
                        # Konvertiere zu Warnung
                        combined_warnings.append(f"Asset-Namensvariation: {error} (erlaubt, nur zur Info)")
                    else:
                        real_errors.append(error)
                
                combined_errors = real_errors
                
                # Regulatorik-Issues sind nur Warnungen, keine Fehler (nicht blockierend)
                # Nur kritische Issues (z.B. fehlende technische Details) sind Fehler
                critical_regulatory_issues = [issue for issue in regulatory_check["issues"] 
                                             if "technische Details" in issue or "Dokumentation" in issue]
                combined_errors.extend(critical_regulatory_issues)
                combined_warnings.extend(regulatory_check["warnings"])
                # Alle anderen Regulatorik-Issues sind nur Warnungen
                non_critical_regulatory_issues = [issue for issue in regulatory_check["issues"] 
                                                 if issue not in critical_regulatory_issues]
                combined_warnings.extend(non_critical_regulatory_issues)
                
                # Regulatorik Compliance: Muss sowohl LLM als auch Checkliste erfüllen
                # ABER: Nicht blockierend - nur Warnung
                checklist_regulatory_compliance = regulatory_check["compliance_status"]
                final_regulatory_compliance = llm_regulatory_compliance and checklist_regulatory_compliance
                
                # Stelle sicher, dass bei False-Werten immer Fehler vorhanden sind
                # ABER: Regulatorik-Compliance ist weniger kritisch - nur Warnung wenn nicht erfüllt
                if not logical_consistency and not combined_errors:
                    combined_errors.append("LLM meldet fehlende logische Konsistenz ohne spezifische Fehler.")
                if not causal_validity and not combined_errors:
                    # Causal Validity: Prüfe ob es wirklich unmöglich ist oder nur ungewöhnlich
                    # Wenn nur ungewöhnlich → Warnung statt Fehler
                    combined_warnings.append("MITRE-Technik passt möglicherweise nicht perfekt zur Phase (prüfe ob technisch möglich)")
                # Regulatorik-Compliance: Warnung statt Fehler (nicht blockierend)
                if not final_regulatory_compliance:
                    if not any("Regulatorik" in w or "Compliance" in w for w in combined_warnings):
                        combined_warnings.append("Regulatorische Aspekte könnten besser abgedeckt sein (optional)")
                
                result = {
                    "logical_consistency": logical_consistency,
                    "dora_compliance": final_regulatory_compliance,  # Für Rückwärtskompatibilität behalten
                    "regulatory_compliance": final_regulatory_compliance,
                    "causal_validity": causal_validity,
                    "errors": combined_errors,
                    "warnings": combined_warnings,
                    "regulatory_checklist": regulatory_check["checklist_results"],
                    "_raw_llm_output": raw_llm_output  # Für Audit-Log - RAW Output vor JSON-Parsing
                }
                return result
            else:
                # Fallback: Verwende Regulatorik-Check Ergebnisse
                return {
                    "logical_consistency": True,
                    "regulatory_compliance": regulatory_check["compliance_status"],
                    "causal_validity": True,
                    "errors": regulatory_check["issues"],
                    "warnings": regulatory_check["warnings"] + ["Validierung konnte nicht vollständig durchgeführt werden"],
                    "_raw_llm_output": content if 'content' in locals() else "Kein JSON-Match gefunden"
                }
                
        except Exception as e:
            # Fallback bei Fehler: Verwende Regulatorik-Check Ergebnisse
            return {
                "logical_consistency": True,
                "regulatory_compliance": regulatory_check["compliance_status"],
                "causal_validity": True,
                "errors": regulatory_check["issues"],
                "warnings": regulatory_check["warnings"] + [f"Validierungsfehler: {e}"],
                "_raw_llm_output": f"Exception: {str(e)}"
            }
    
    def _format_inject(self, inject: Inject) -> str:
        """Formatiert einen Inject für den Prompt."""
        lines = [
            f"Inject ID: {inject.inject_id}",
            f"Time Offset: {inject.time_offset}",
            f"Phase: {inject.phase.value}",
            f"Source: {inject.source}",
            f"Target: {inject.target}",
            f"Modality: {inject.modality.value}",
            f"Content: {inject.content}",
            f"MITRE ID: {inject.technical_metadata.mitre_id}",
            f"Affected Assets: {', '.join(inject.technical_metadata.affected_assets)}"
        ]
        return "\n".join(lines)
    
    def _format_previous_injects(self, previous_injects: List[Inject]) -> str:
        """Formatiert vorherige Injects."""
        if not previous_injects:
            return "Keine vorherigen Injects"
        
        lines = []
        for inj in previous_injects[-5:]:  # Letzte 5
            lines.append(f"- {inj.inject_id} ({inj.time_offset}): {inj.content[:60]}...")
        
        return "\n".join(lines)
    
    def _format_system_state(self, system_state: Dict[str, Any]) -> str:
        """
        Formatiert den Systemzustand mit expliziter Asset-Liste.
        
        WICHTIG: Filtert nur echte Assets, keine INJ-* oder SCEN-* IDs.
        """
        if not system_state or not isinstance(system_state, dict):
            return "Keine Systemzustand-Informationen verfügbar. Verwende Standard-Assets: SRV-001, SRV-002"
        
        # Filtere echte Assets heraus (keine INJ-*, SCEN-* IDs)
        valid_assets = {}
        for entity_id, entity_data in system_state.items():
            # Überspringe Inject-IDs und Szenario-IDs
            if entity_id.startswith("INJ-") or entity_id.startswith("SCEN-"):
                continue
            
            # Nur echte Assets
            if isinstance(entity_data, dict):
                entity_type = entity_data.get("entity_type", "").lower()
                if entity_type in ["server", "application", "database", "service", "asset"] or \
                   entity_id.startswith(("SRV-", "APP-", "DB-", "SVC-")):
                    valid_assets[entity_id] = entity_data
        
        if not valid_assets:
            return "Keine Assets im Systemzustand verfügbar. Verwende Standard-Assets: SRV-001, SRV-002"
        
        lines = []
        asset_list = []
        for entity_id, entity_data in valid_assets.items():
            status = entity_data.get("status", "unknown")
            name = entity_data.get("name", entity_id)
            entity_type = entity_data.get("entity_type", "Asset")
            lines.append(f"- {name} ({entity_id}, {entity_type}): {status}")
            asset_list.append(entity_id)
        
        # WICHTIG: Explizite Liste der verfügbaren Asset-IDs
        result = "\n".join(lines) if lines else "Alle Systeme im Normalbetrieb"
        result += f"\n\n⚠️ KRITISCH - VERFÜGBARE ASSET-IDs (NUR DIESE VERWENDEN!): {', '.join(asset_list)}"
        result += f"\n❌ VERBOTEN: Erstelle KEINE neuen Assets! Verwende NUR die oben genannten Asset-IDs!"
        
        return result
    
    def _log_critic_decision(
        self,
        inject_id: str,
        inject: Inject,
        system_state: Dict[str, Any],
        previous_injects: List[Inject],
        current_phase: CrisisPhase,
        llm_validation: Dict[str, Any],
        final_result: Dict[str, Any],
        formatted_system_state_str: Optional[str] = None
    ) -> None:
        """
        Loggt die vollständige Critic-Entscheidung für Deep Truth Debugging.
        
        Erstellt einen detaillierten Audit-Eintrag in CRITIC_AUDIT_LOG.md.
        """
        # Verwende absoluten Pfad vom Workspace-Root
        workspace_root = Path(__file__).parent.parent
        log_file = workspace_root / "CRITIC_AUDIT_LOG.md"
        
        # Extrahiere Asset-IDs aus system_state
        active_assets = []
        for entity_id, entity_data in system_state.items():
            if entity_id.startswith(("INJ-", "SCEN-")):
                continue
            if isinstance(entity_data, dict):
                entity_type = entity_data.get("entity_type", "").lower()
                if entity_type in ["server", "application", "database", "service", "asset"] or \
                   entity_id.startswith(("SRV-", "APP-", "DB-", "SVC-")):
                    active_assets.append(entity_id)
        
        # Formatiere System-State-String (wie er an LLM gesendet wurde)
        if formatted_system_state_str is None:
            formatted_system_state_str = self._format_system_state(system_state)
        
        # Formatiere vorherige Injects
        previous_injects_json = []
        for prev_inj in previous_injects:
            previous_injects_json.append({
                "inject_id": prev_inj.inject_id,
                "time_offset": prev_inj.time_offset,
                "phase": prev_inj.phase.value,
                "content": prev_inj.content,
                "affected_assets": prev_inj.technical_metadata.affected_assets,
                "mitre_id": prev_inj.technical_metadata.mitre_id
            })
        
        # Vollständiger Inject JSON
        inject_json = {
            "inject_id": inject.inject_id,
            "time_offset": inject.time_offset,
            "phase": inject.phase.value,
            "source": inject.source,
            "target": inject.target,
            "modality": inject.modality.value,
            "content": inject.content,
            "technical_metadata": {
                "mitre_id": inject.technical_metadata.mitre_id,
                "affected_assets": inject.technical_metadata.affected_assets,
                "ioc_hash": inject.technical_metadata.ioc_hash,
                "ioc_ip": inject.technical_metadata.ioc_ip,
                "ioc_domain": inject.technical_metadata.ioc_domain,
                "severity": inject.technical_metadata.severity
            },
            "dora_compliance_tag": inject.dora_compliance_tag,
            "business_impact": inject.business_impact
        }
        
        # Raw LLM Output
        raw_llm_output = llm_validation.get("_raw_llm_output", "Nicht verfügbar")
        
        # Entscheidung
        decision = "✅ VALID" if final_result["is_valid"] else "❌ INVALID"
        
        # Erstelle Markdown-Eintrag
        timestamp = datetime.now().isoformat()
        
        # Hole FSM-Regeln für aktuelle Phase
        try:
            from workflows.fsm import CrisisFSM
            allowed_transitions = CrisisFSM.get_next_phases(current_phase)
            allowed_transitions_str = [p.value for p in allowed_transitions]
        except:
            allowed_transitions_str = ["N/A"]
        
        markdown_entry = f"""## 🔍 Audit Entry: {inject_id}
**Timestamp:** {timestamp}

### 1. The Ground Truth (What was in the DB?)
*Crucial: Dump the exact JSON inputs the Critic received.*

- **Active Assets in State:** `{json.dumps(active_assets, indent=2, ensure_ascii=False, cls=DateTimeEncoder)}`
- **Current Phase:** `{current_phase.value}`
- **System State (Full Raw):**
```json
{json.dumps(system_state, indent=2, ensure_ascii=False, cls=DateTimeEncoder)}
```
- **System State (Formatted - wie an LLM gesendet):**
```
{formatted_system_state_str}
```
- **Previous Injects (Full History):**
```json
{json.dumps(previous_injects_json, indent=2, ensure_ascii=False, cls=DateTimeEncoder)}
```
- **Defined Rules:**
  - **FSM Transition Rules:** Valid transitions from `{current_phase.value}` → `{allowed_transitions_str}`
  - **State Consistency:** Assets must exist in system_state (checked against: `{active_assets}`)
  - **Temporal Consistency:** Time offsets must be chronological
  - **Logical Consistency:** No contradictions with previous injects
  - **Causal Validity:** MITRE techniques must be technically possible (only truly impossible sequences block)

### 2. The Generator's Draft
```json
{json.dumps(inject_json, indent=2, ensure_ascii=False, cls=DateTimeEncoder)}
```

### 3. The Critic's Reasoning (Raw LLM Output)
*Crucial: What did the LLM actually say before parsing?*

```
{raw_llm_output}
```

### 4. The Verdict
- **Decision:** {decision}
- **Detected Errors:** {json.dumps(final_result.get("errors", []), indent=2, ensure_ascii=False, cls=DateTimeEncoder)}
- **Warnings:** {json.dumps(final_result.get("warnings", []), indent=2, ensure_ascii=False, cls=DateTimeEncoder)}
- **Validation Details:**
  - Pydantic Valid: `{final_result.get("pydantic_valid", "N/A")}`
  - FSM Valid: `{final_result.get("fsm_valid", "N/A")}`
  - State Valid: `{final_result.get("state_valid", "N/A")}`
  - Temporal Valid: `{final_result.get("temporal_valid", "N/A")}`
  - Logical Consistency: `{final_result.get("logical_consistency", "N/A")}`
  - Causal Validity: `{final_result.get("causal_validity", "N/A")}`
  - Causal Blocking: `{final_result.get("causal_blocking", "N/A")}`

***

"""
        
        # Append to log file (mit Header falls Datei neu)
        try:
            file_exists = log_file.exists()
            with open(log_file, "a", encoding="utf-8") as f:
                if not file_exists:
                    # Header beim ersten Eintrag
                    f.write("# 🔍 Critic Agent Deep Truth Audit Log\n\n")
                    f.write("Diese Datei enthält vollständige Audit-Trails für alle Critic-Validierungen.\n")
                    f.write("Jeder Eintrag zeigt die exakten Inputs, den Generator-Draft, die LLM-Antwort und die finale Entscheidung.\n\n")
                    f.write("---\n\n")
                f.write(markdown_entry)
            print(f"📝 [Critic] Audit-Log geschrieben: {log_file}")
        except Exception as e:
            print(f"⚠️  [Critic] Fehler beim Schreiben des Audit-Logs: {e}")

