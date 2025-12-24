#!/usr/bin/env python3
"""
Quality Assurance Test Runner für CRUX System (Simplified Version)

Führt die 4 strategischen Testszenarien durch ohne Backend-Dependencies.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import re


def parse_time_offset(time_offset: str) -> int:
    """Parse Time Offset Format (T+DD:HH:MM oder T+HH:MM) zu Minuten"""
    match = re.match(r'T\+(\d{2}):(\d{2})(?::(\d{2}))?', time_offset)
    if not match:
        return 0
    
    if match.group(3):
        # T+DD:HH:MM Format
        days = int(match.group(1) or '0')
        hours = int(match.group(2) or '0')
        minutes = int(match.group(3) or '0')
        return days * 24 * 60 + hours * 60 + minutes
    else:
        # T+HH:MM Format
        hours = int(match.group(1))
        minutes = int(match.group(2))
        return hours * 60 + minutes


def load_forensic_trace(file_path: str) -> List[Dict[str, Any]]:
    """Lädt Forensic Trace JSONL Datei"""
    events = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events


def extract_injects_from_events(events: List[Dict]) -> tuple[List[Dict], List[Dict]]:
    """
    Extrahiert Injects und Critic Logs aus Events.
    
    Returns:
        (injects, critic_logs) - Tuple von Injects und Critic Logs
    """
    injects = []
    critic_logs = []
    seen_inject_ids = set()
    
    for event in events:
        # Skip Kommentar-Zeilen
        if isinstance(event, str) and event.startswith('#'):
            continue
        
        # Prüfe ob es ein Critic Log ist
        if event.get('event_type') == 'CRITIC':
            inject_id = event.get('data', {}).get('inject_id')
            if inject_id:
                critic_logs.append({
                    'inject_id': inject_id,
                    'timestamp': event.get('timestamp', ''),
                    'validation': event.get('data', {}).get('validation', {}),
                    'decision': event.get('data', {}).get('decision', ''),
                    'iteration': event.get('iteration', 0),
                })
                
                # Versuche Inject zu rekonstruieren (falls nicht schon vorhanden)
                if inject_id not in seen_inject_ids:
                    seen_inject_ids.add(inject_id)
                    # Erstelle minimales Inject-Objekt für Tests
                    injects.append({
                        'inject_id': inject_id,
                        'time_offset': f"T+00:{inject_id.split('-')[1] if '-' in inject_id else '00'}:00",  # Schätzung
                        'content': '',  # Nicht verfügbar in Critic Logs
                        'source': '',
                        'target': '',
                        'phase': '',
                        'technical_metadata': {'affected_assets': []},
                        'dora_compliance_tag': None,
                        'compliance_tags': {},
                    })
        
        # Versuche Inject direkt zu extrahieren
        inject_id = event.get('inject_id')
        if inject_id and inject_id not in seen_inject_ids:
            seen_inject_ids.add(inject_id)
            injects.append({
                'inject_id': inject_id,
                'time_offset': event.get('time_offset', 'T+00:00'),
                'content': event.get('content', ''),
                'source': event.get('source', ''),
                'target': event.get('target', ''),
                'phase': event.get('phase', ''),
                'technical_metadata': event.get('technical_metadata', {'affected_assets': []}),
                'dora_compliance_tag': event.get('dora_compliance_tag'),
                'compliance_tags': event.get('compliance_tags', {}),
            })
    
    return injects, critic_logs


def test_causality_stress_test(injects: List[Dict], graph_links: List[Dict] = None) -> Dict[str, Any]:
    """Test 1: Kausalitäts-Stresstest (Teleportation Test)"""
    print("\n🔬 Test T-01: Kausalitäts-Stresstest (Teleportation Test)")
    print("=" * 70)
    
    if graph_links is None:
        graph_links = []
    
    suspicious_injects = []
    evidence = []
    
    for inject in injects:
        affected_assets = inject.get('technical_metadata', {}).get('affected_assets', [])
        if not affected_assets:
            affected_assets = inject.get('affected_assets', [])
        
        for asset_id in affected_assets:
            # Prüfe ob Asset isoliert ist (keine eingehenden Links)
            has_incoming_links = any(
                link.get('target') == asset_id and 
                link.get('type') in ['CONNECTS_TO', 'USES', 'DEPENDS_ON']
                for link in graph_links
            )
            
            # Prüfe ob es vorherige Injects gibt, die Zugriff ermöglichen
            previous_injects = [
                inj for inj in injects 
                if parse_time_offset(inj.get('time_offset', 'T+00:00')) < parse_time_offset(inject.get('time_offset', 'T+00:00'))
            ]
            
            has_precedent = False
            for prev_inject in previous_injects:
                prev_assets = prev_inject.get('technical_metadata', {}).get('affected_assets', [])
                if not prev_assets:
                    prev_assets = prev_inject.get('affected_assets', [])
                
                for prev_asset in prev_assets:
                    if any(link.get('source') == prev_asset and link.get('target') == asset_id for link in graph_links):
                        has_precedent = True
                        break
                if has_precedent:
                    break
            
            if not has_incoming_links and not has_precedent and affected_assets:
                suspicious_injects.append({
                    'inject': inject,
                    'asset_id': asset_id,
                })
                evidence.append(f"⚠️  Inject {inject.get('inject_id', 'UNKNOWN')} greift auf isoliertes Asset {asset_id} zu ohne Vorstufe")
    
    passed = len(suspicious_injects) == 0
    
    return {
        'test_id': 'T-01',
        'test_name': 'Kausalitäts-Stresstest (Teleportation Test)',
        'hypothesis': 'System verhindert unlogische Angriffe (Teleportation)',
        'action': 'Inject auf isolierte DB ohne Vorstufe',
        'system_reaction': f"{'Keine Teleportation-Versuche erkannt' if passed else f'{len(suspicious_injects)} Teleportation-Versuche erkannt'}",
        'evidence': evidence,
        'passed': passed,
    }


def test_state_persistence(injects: List[Dict]) -> Dict[str, Any]:
    """Test 2: Amnesie-Test (State Persistence)"""
    print("\n🧠 Test T-02: Amnesie-Test (State Persistence)")
    print("=" * 70)
    
    evidence = []
    compromised_assets = {}
    
    # Sammle alle kompromittierten Assets chronologisch
    for inject in injects:
        affected_assets = inject.get('technical_metadata', {}).get('affected_assets', [])
        if not affected_assets:
            affected_assets = inject.get('affected_assets', [])
        
        content_lower = inject.get('content', '').lower()
        
        if any(keyword in content_lower for keyword in ['compromised', 'breach', 'infected', 'hacked']):
            for asset_id in affected_assets:
                if asset_id not in compromised_assets:
                    compromised_assets[asset_id] = {
                        'inject_id': inject.get('inject_id', 'UNKNOWN'),
                        'time_offset': inject.get('time_offset', 'T+00:00'),
                    }
                    evidence.append(f"📌 Asset {asset_id} kompromittiert in {compromised_assets[asset_id]['inject_id']} ({compromised_assets[asset_id]['time_offset']})")
    
    # Prüfe Re-Kompromittierungs-Versuche
    recompromise_attempts = 0
    
    for inject in injects:
        affected_assets = inject.get('technical_metadata', {}).get('affected_assets', [])
        if not affected_assets:
            affected_assets = inject.get('affected_assets', [])
        
        content_lower = inject.get('content', '').lower()
        is_compromise_attempt = any(
            keyword in content_lower 
            for keyword in ['initial access', 'compromise', 'breach']
        )
        
        if is_compromise_attempt:
            for asset_id in affected_assets:
                if asset_id in compromised_assets:
                    prev_time = parse_time_offset(compromised_assets[asset_id]['time_offset'])
                    current_time = parse_time_offset(inject.get('time_offset', 'T+00:00'))
                    
                    if current_time > prev_time:
                        recompromise_attempts += 1
                        evidence.append(
                            f"⚠️  Inject {inject.get('inject_id', 'UNKNOWN')} versucht Re-Kompromittierung von {asset_id} "
                            f"(bereits kompromittiert in {compromised_assets[asset_id]['inject_id']})"
                        )
    
    passed = recompromise_attempts == 0
    
    return {
        'test_id': 'T-02',
        'test_name': 'Amnesie-Test (State Persistence)',
        'hypothesis': 'System erkennt bereits kompromittierte Assets',
        'action': 'Re-Kompromittierung bereits kompromittierter Assets',
        'system_reaction': f"{'Keine Re-Kompromittierungs-Versuche' if passed else f'{recompromise_attempts} Re-Kompromittierungs-Versuche erkannt'}",
        'evidence': evidence,
        'passed': passed,
    }


def test_dora_compliance(injects: List[Dict]) -> Dict[str, Any]:
    """Test 3: DORA-Compliance Audit"""
    print("\n📋 Test T-03: DORA-Compliance Audit")
    print("=" * 70)
    
    evidence = []
    
    # Sammle alle Injects mit DORA-Compliance Tags
    compliant_injects = [
        inj for inj in injects 
        if inj.get('dora_compliance_tag') or (inj.get('compliance_tags', {}).get('DORA'))
    ]
    
    evidence.append(f"📊 {len(compliant_injects)} Injects mit DORA-Compliance Tags gefunden")
    
    compliance_keywords = {
        'IncidentResponse': ['incident', 'response', 'soc', 'alert', 'investigation', 'forensics'],
        'BusinessContinuity': ['backup', 'continuity', 'failover', 'recovery', 'disaster'],
        'RecoveryTesting': ['recovery', 'restore', 'backup', 'test', 'drill'],
        'Communication': ['communication', 'notify', 'stakeholder', 'escalation', 'report'],
        'Monitoring': ['monitor', 'detect', 'alert', 'siem', 'ids', 'surveillance'],
    }
    
    valid_compliance_count = 0
    invalid_compliance_count = 0
    
    for inject in compliant_injects:
        content_lower = inject.get('content', '').lower()
        tags = []
        
        if inject.get('compliance_tags', {}).get('DORA'):
            tags.extend(inject['compliance_tags']['DORA'])
        if inject.get('dora_compliance_tag'):
            tags.append(inject['dora_compliance_tag'])
        
        has_valid_content = False
        for tag in tags:
            keywords = compliance_keywords.get(tag, [])
            if any(keyword in content_lower for keyword in keywords):
                has_valid_content = True
                evidence.append(f"✅ {inject.get('inject_id', 'UNKNOWN')}: Tag '{tag}' durch Content validiert")
                break
        
        if has_valid_content:
            valid_compliance_count += 1
        else:
            invalid_compliance_count += 1
            evidence.append(f"❌ {inject.get('inject_id', 'UNKNOWN')}: Compliance-Tag ohne entsprechenden Content")
    
    # Prüfe Blue Team Injects
    blue_team_injects = [
        inj for inj in injects
        if 'blue' in inj.get('source', '').lower() or 'soc' in inj.get('source', '').lower() or
           'isolat' in inj.get('content', '').lower() or 'contain' in inj.get('content', '').lower()
    ]
    
    evidence.append(f"🛡️  {len(blue_team_injects)} Blue Team Injects gefunden")
    
    passed = invalid_compliance_count == 0 and len(blue_team_injects) > 0
    
    return {
        'test_id': 'T-03',
        'test_name': 'DORA-Compliance Audit',
        'hypothesis': 'Compliance-Tags basieren auf tatsächlichen Injects',
        'action': 'Analyse aller DORA-Compliance Tags',
        'system_reaction': (
            f"Alle {valid_compliance_count} Compliance-Tags sind valide, "
            f"{len(blue_team_injects)} Blue Team Injects vorhanden"
            if passed else
            f"{invalid_compliance_count} ungültige Compliance-Tags gefunden oder keine Blue Team Injects"
        ),
        'evidence': evidence,
        'passed': passed,
    }


def test_cascade_effects(injects: List[Dict], graph_nodes: List[Dict] = None, graph_links: List[Dict] = None) -> Dict[str, Any]:
    """Test 4: Kettenreaktion-Test (Second-Order Effects)"""
    print("\n🌊 Test T-04: Kettenreaktion-Test (Second-Order Effects)")
    print("=" * 70)
    
    if graph_nodes is None:
        graph_nodes = []
    if graph_links is None:
        graph_links = []
    
    evidence = []
    
    # Finde kritische Assets die offline gesetzt wurden
    critical_offline_events = []
    
    for inject in injects:
        affected_assets = inject.get('technical_metadata', {}).get('affected_assets', [])
        if not affected_assets:
            affected_assets = inject.get('affected_assets', [])
        
        content_lower = inject.get('content', '').lower()
        
        if any(keyword in content_lower for keyword in ['offline', 'down', 'unavailable', 'shutdown']):
            for asset_id in affected_assets:
                node = next((n for n in graph_nodes if n.get('id') == asset_id), None)
                node_type = node.get('type', '') if node else ''
                
                if node_type in ['Server', 'Database', 'Network', 'server', 'database', 'network']:
                    critical_offline_events.append({
                        'inject_id': inject.get('inject_id', 'UNKNOWN'),
                        'asset_id': asset_id,
                        'time_offset': inject.get('time_offset', 'T+00:00'),
                    })
    
    evidence.append(f"📊 {len(critical_offline_events)} kritische Offline-Events gefunden")
    
    cascade_detected = 0
    cascade_missed = 0
    
    for event in critical_offline_events:
        source_node = next((n for n in graph_nodes if n.get('id') == event['asset_id']), None)
        if not source_node:
            continue
        
        # Finde abhängige Nodes
        dependent_nodes = [
            n for n in graph_nodes
            if any(
                link.get('source') == event['asset_id'] and link.get('target') == n.get('id') and
                link.get('type') in ['DEPENDS_ON', 'USES', 'RUNS_ON']
                for link in graph_links
            )
        ]
        
        evidence.append(f"🔗 Asset {event['asset_id']} hat {len(dependent_nodes)} abhängige Nodes")
        
        # Prüfe ob diese Nodes später als Degraded/Offline markiert wurden
        for dep_node in dependent_nodes:
            later_injects = [
                inj for inj in injects
                if parse_time_offset(inj.get('time_offset', 'T+00:00')) > parse_time_offset(event['time_offset'])
            ]
            
            dep_assets = dep_node.get('technical_metadata', {}).get('affected_assets', [])
            if not dep_assets:
                dep_assets = dep_node.get('affected_assets', [])
            
            node_mentioned = any(
                dep_node.get('id') in (inj.get('technical_metadata', {}).get('affected_assets', []) or inj.get('affected_assets', []))
                for inj in later_injects
            )
            
            node_status = dep_node.get('status', 'online')
            node_status_changed = node_status in ['degraded', 'offline']
            
            if node_status_changed and not node_mentioned:
                cascade_detected += 1
                evidence.append(
                    f"✅ Cascade erkannt: {dep_node.get('id')} → {node_status} "
                    "(ohne explizite LLM-Erwähnung)"
                )
            elif not node_status_changed and len(dependent_nodes) > 0:
                cascade_missed += 1
                evidence.append(
                    f"❌ Cascade verpasst: {dep_node.get('id')} sollte Degraded sein, "
                    f"ist aber {node_status}"
                )
    
    passed = cascade_detected > 0 or len(critical_offline_events) == 0
    
    return {
        'test_id': 'T-04',
        'test_name': 'Kettenreaktion-Test (Second-Order Effects)',
        'hypothesis': 'Graph propagiert Fehler automatisch (ohne LLM-Erwähnung)',
        'action': 'Kritischer Asset offline setzen, abhängige Nodes beobachten',
        'system_reaction': (
            f"System erkannte {cascade_detected} Second-Order Effects automatisch"
            if passed else
            f"System verpasste {cascade_missed} Second-Order Effects"
        ),
        'evidence': evidence,
        'passed': passed,
    }


def main():
    """Hauptfunktion: Führt alle Tests durch"""
    print("=" * 70)
    print("🔬 CRUX Quality Assurance Framework - Test Runner")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Lade Daten
    print("\n📂 Lade Test-Daten...")
    
    # Versuche Forensic Trace zu laden
    base_path = Path(__file__).parent.parent
    forensic_trace_path = base_path / "logs" / "forensic" / "forensic_trace.jsonl"
    
    if not forensic_trace_path.exists():
        print(f"❌ Forensic Trace nicht gefunden: {forensic_trace_path}")
        print("💡 Tipp: Generiere zuerst ein Szenario oder lade eine Forensic Trace Datei")
        return
    
    events = load_forensic_trace(str(forensic_trace_path))
    print(f"✅ {len(events)} Events geladen")
    
    # Extrahiere Injects und Critic Logs
    injects, critic_logs = extract_injects_from_events(events)
    print(f"✅ {len(injects)} Injects extrahiert")
    print(f"✅ {len(critic_logs)} Critic Logs extrahiert")
    
    if len(injects) == 0 and len(critic_logs) == 0:
        print("❌ Keine Injects oder Critic Logs gefunden. Kann Tests nicht durchführen.")
        return
    
    # Verwende Critic Logs für Tests wenn keine vollständigen Injects vorhanden
    if len(injects) == 0 and len(critic_logs) > 0:
        print("⚠️  Keine vollständigen Injects gefunden, verwende Critic Logs für Tests")
        # Erstelle minimale Injects aus Critic Logs
        for log in critic_logs:
            inject_id = log.get('inject_id')
            if inject_id:
                # Extrahiere Nummer aus Inject-ID für Time Offset Schätzung
                inject_num = '00'
                if '-' in inject_id:
                    parts = inject_id.split('-')
                    if len(parts) > 1 and parts[1].isdigit():
                        inject_num = str(int(parts[1])).zfill(2)
                
                injects.append({
                    'inject_id': inject_id,
                    'time_offset': f"T+00:{inject_num}:00",
                    'content': '',  # Nicht verfügbar
                    'source': '',
                    'target': '',
                    'phase': '',
                    'technical_metadata': {'affected_assets': []},
                    'dora_compliance_tag': None,
                    'compliance_tags': {},
                })
    
    # Demo Graph-Daten (falls Neo4j nicht verfügbar)
    graph_nodes = []
    graph_links = []
    
    # Führe Tests durch
    test_results = []
    
    # Test 1: Kausalitäts-Stresstest (mit Critic Logs)
    test1_result = test_causality_stress_test(injects, graph_links)
    # Erweitere mit Critic Log Evidence
    if critic_logs:
        rejected_logs = [log for log in critic_logs if log.get('decision') == 'reject']
        if rejected_logs:
            test1_result['evidence'].extend([
                f"✅ CRITIC: {len(rejected_logs)} Injects wurden abgelehnt",
                f"   Beispiel: {rejected_logs[0].get('inject_id')} - {rejected_logs[0].get('validation', {}).get('errors', [])[:1]}"
            ])
    test_results.append(test1_result)
    
    # Test 2: Amnesie-Test
    test_results.append(test_state_persistence(injects))
    
    # Test 3: DORA-Compliance (mit Critic Logs)
    test3_result = test_dora_compliance(injects)
    # Erweitere mit Critic Log Evidence
    if critic_logs:
        dora_compliant_logs = [log for log in critic_logs if log.get('validation', {}).get('dora_compliance')]
        test3_result['evidence'].append(f"📊 {len(dora_compliant_logs)} Critic Logs mit DORA-Compliance=True")
    test_results.append(test3_result)
    
    # Test 4: Kettenreaktion-Test
    test_results.append(test_cascade_effects(injects, graph_nodes, graph_links))
    
    # Zeige Ergebnisse
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed_tests = sum(1 for r in test_results if r['passed'])
    total_tests = len(test_results)
    overall_score = (passed_tests / total_tests) * 100
    
    print(f"\nOverall Score: {overall_score:.1f}% ({passed_tests}/{total_tests} Tests bestanden)")
    print("\n" + "-" * 70)
    
    for result in test_results:
        status = "✅ BESTANDEN" if result['passed'] else "❌ FEHLGESCHLAGEN"
        print(f"\n{result['test_id']}: {result['test_name']} - {status}")
        print(f"  Hypothese: {result['hypothesis']}")
        print(f"  Aktion: {result['action']}")
        print(f"  System-Reaktion: {result['system_reaction']}")
        
        if result['evidence']:
            print(f"  Evidence ({len(result['evidence'])} Einträge):")
            for ev in result['evidence'][:5]:  # Zeige nur erste 5
                print(f"    {ev}")
            if len(result['evidence']) > 5:
                print(f"    ... und {len(result['evidence']) - 5} weitere")
    
    # Speichere Ergebnisse als JSON
    output_path = base_path / "logs" / "qa_test_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'overall_score': overall_score,
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'test_results': test_results,
        }, f, indent=2, default=str)
    
    print(f"\n💾 Ergebnisse gespeichert: {output_path}")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()

