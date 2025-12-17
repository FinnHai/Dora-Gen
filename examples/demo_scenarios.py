"""
Demo-Szenarien für schnelles Testen des Systems.

Enthält vordefinierte, realistische Szenarien, die Nutzer
zum Testen der Funktionalität verwenden können.
"""

from state_models import (
    Inject,
    TechnicalMetadata,
    CrisisPhase,
    ScenarioType,
    InjectModality
)
from datetime import datetime


def get_demo_scenario_ransomware() -> dict:
    """
    Demo-Szenario: Ransomware & Double Extortion
    
    Ein realistisches Ransomware-Szenario mit mehreren Phasen.
    """
    injects = [
        Inject(
            inject_id="INJ-001",
            time_offset="T+00:30",
            phase=CrisisPhase.SUSPICIOUS_ACTIVITY,
            source="IT Security Monitoring System",
            target="Blue Team / SOC",
            modality=InjectModality.SIEM_ALERT,
            content="Ein SIEM-Alarm wurde ausgelöst, der auf ungewöhnliche Aktivitäten von PC-05 hinweist. Mehrere fehlgeschlagene Anmeldeversuche wurden von PC-05 registriert, und ein verdächtiges PowerShell-Skript wurde ausgeführt. Eine ungewöhnliche Netzwerkverbindung von APP-SRV-01 zu einer externen IP-Adresse 203.0.113.45 wurde ebenfalls festgestellt.",
            technical_metadata=TechnicalMetadata(
                mitre_id="T1078",
                affected_assets=["PC-05", "APP-SRV-01"],
                ioc_hash=None
            ),
            dora_compliance_tag="Art25_IncidentResponse",
            business_impact="Möglicher Verlust von sensiblen Unternehmensdaten und Betriebsunterbrechung durch verschlüsselte Dateien auf betroffenen Systemen."
        ),
        Inject(
            inject_id="INJ-002",
            time_offset="T+01:00",
            phase=CrisisPhase.INITIAL_INCIDENT,
            source="SOC Analyst",
            target="CISO / Management",
            modality=InjectModality.INTERNAL_REPORT,
            content="Nach weiterer Analyse wurde bestätigt, dass PC-05 kompromittiert wurde. Der Angreifer hat sich über kompromittierte Anmeldedaten Zugang verschafft. Es wurden verschlüsselte Dateien auf APP-SRV-01 gefunden. Die Ransomware 'LockBit' wurde identifiziert. Erste betroffene Systeme: APP-SRV-01, DB-SRV-02.",
            technical_metadata=TechnicalMetadata(
                mitre_id="T1486",
                affected_assets=["PC-05", "APP-SRV-01", "DB-SRV-02"],
                ioc_hash="a1b2c3d4e5f6..."
            ),
            dora_compliance_tag="Art25_IncidentResponse",
            business_impact="Kritische Geschäftsprozesse sind betroffen. Datenbank-Server DB-SRV-02 ist verschlüsselt, was die Kundenverwaltung blockiert."
        ),
        Inject(
            inject_id="INJ-003",
            time_offset="T+01:30",
            phase=CrisisPhase.ESCALATION_CRISIS,
            source="Red Team / Attacker",
            target="Blue Team / SOC",
            modality=InjectModality.EMAIL,
            content="E-Mail von unbekanntem Absender an CISO: 'Wir haben Zugriff auf Ihre Systeme und sensible Kundendaten. Wir haben 48 Stunden Zeit, bevor wir die Daten öffentlich veröffentlichen. Kontaktieren Sie uns unter [Tor-Link].' Anhang: Screenshot von verschlüsselten Dateien und Datenbank-Einträgen.",
            technical_metadata=TechnicalMetadata(
                mitre_id="T1566",
                affected_assets=["Email-Server"],
                ioc_hash=None
            ),
            dora_compliance_tag="Art25_IncidentResponse",
            business_impact="Double Extortion: Angreifer drohen mit Veröffentlichung von Kundendaten. Potenzielle GDPR-Verstöße und Reputationsschaden."
        ),
        Inject(
            inject_id="INJ-004",
            time_offset="T+02:00",
            phase=CrisisPhase.CONTAINMENT,
            source="Blue Team / SOC",
            target="Management",
            modality=InjectModality.INTERNAL_REPORT,
            content="Containment-Maßnahmen wurden eingeleitet: PC-05 wurde vom Netzwerk isoliert. APP-SRV-01 und DB-SRV-02 wurden in Quarantäne versetzt. Alle betroffenen Systeme wurden vom Netzwerk getrennt. Backup-Systeme werden aktiviert.",
            technical_metadata=TechnicalMetadata(
                mitre_id="T1485",
                affected_assets=["PC-05", "APP-SRV-01", "DB-SRV-02", "Backup-System"],
                ioc_hash=None
            ),
            dora_compliance_tag="Art25_BusinessContinuity",
            business_impact="Betriebsunterbrechung: Kritische Systeme sind offline. Backup-Systeme werden aktiviert, aber vollständige Wiederherstellung wird 4-6 Stunden dauern."
        ),
        Inject(
            inject_id="INJ-005",
            time_offset="T+03:00",
            phase=CrisisPhase.RECOVERY,
            source="IT Operations",
            target="Management",
            modality=InjectModality.INTERNAL_REPORT,
            content="Wiederherstellungsprozess läuft: Backup-Systeme sind aktiv. DB-SRV-02 wurde aus dem letzten sauberen Backup wiederhergestellt (vor 6 Stunden). APP-SRV-01 wird neu aufgesetzt. Erwartete vollständige Wiederherstellung: T+06:00.",
            technical_metadata=TechnicalMetadata(
                mitre_id="T1490",
                affected_assets=["DB-SRV-02", "APP-SRV-01", "Backup-System"],
                ioc_hash=None
            ),
            dora_compliance_tag="Art25_BusinessContinuity",
            business_impact="Teilweise Wiederherstellung: Kundenverwaltung ist wieder verfügbar. Vollständige Systemwiederherstellung in 3 Stunden erwartet."
        )
    ]
    
    return {
        "scenario_id": "DEMO-RANSOMWARE-001",
        "scenario_type": ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
        "current_phase": CrisisPhase.RECOVERY,
        "injects": injects,
        "system_state": {
            "entities": [
                {"id": "PC-05", "status": "isolated"},
                {"id": "APP-SRV-01", "status": "recovering"},
                {"id": "DB-SRV-02", "status": "recovered"},
                {"id": "Email-Server", "status": "monitored"}
            ]
        },
        "iteration": 5,
        "max_iterations": 5,
        "errors": [],
        "warnings": [],
        "start_time": datetime.now(),
        "metadata": {"demo": True},
        "workflow_logs": [],
        "agent_decisions": []
    }


def get_demo_scenario_ddos() -> dict:
    """
    Demo-Szenario: DDoS auf kritische Funktionen
    
    Ein DDoS-Angriff auf kritische Geschäftsfunktionen.
    """
    injects = [
        Inject(
            inject_id="INJ-001",
            time_offset="T+00:15",
            phase=CrisisPhase.SUSPICIOUS_ACTIVITY,
            source="Network Monitoring System",
            target="Blue Team / SOC",
            modality=InjectModality.SIEM_ALERT,
            content="Ungewöhnlich hoher Netzwerk-Traffic wurde auf dem Web-Server WEB-SRV-01 festgestellt. Traffic-Volumen ist 10x höher als normal. Verdacht auf DDoS-Angriff. Quell-IPs: 198.51.100.0/24, 203.0.113.0/24 (mehrere hundert verschiedene IPs).",
            technical_metadata=TechnicalMetadata(
                mitre_id="T1498",
                affected_assets=["WEB-SRV-01", "Load-Balancer"],
                ioc_hash=None
            ),
            dora_compliance_tag="Art25_IncidentResponse",
            business_impact="Erhöhte Latenz bei Kunden-Transaktionen. Web-Services sind langsamer, aber noch verfügbar."
        ),
        Inject(
            inject_id="INJ-002",
            time_offset="T+00:45",
            phase=CrisisPhase.INITIAL_INCIDENT,
            source="SOC Analyst",
            target="CISO / Management",
            modality=InjectModality.INTERNAL_REPORT,
            content="Bestätigung: DDoS-Angriff auf WEB-SRV-01. Traffic-Volumen erreicht 50 Gbps (normal: 2 Gbps). Load-Balancer ist überlastet. Web-Services sind für externe Kunden nicht mehr erreichbar. Interne Systeme funktionieren noch.",
            technical_metadata=TechnicalMetadata(
                mitre_id="T1498",
                affected_assets=["WEB-SRV-01", "Load-Balancer", "API-Gateway"],
                ioc_hash=None
            ),
            dora_compliance_tag="Art25_BusinessContinuity",
            business_impact="Kritisch: Online-Banking und Kunden-Portal sind nicht erreichbar. Geschätzte betroffene Kunden: 50.000+."
        ),
        Inject(
            inject_id="INJ-003",
            time_offset="T+01:15",
            phase=CrisisPhase.ESCALATION_CRISIS,
            source="DDoS Mitigation Service",
            target="Blue Team / SOC",
            modality=InjectModality.EMAIL,
            content="DDoS-Mitigation-Service wurde aktiviert. Traffic wird jetzt durch Scrubbing-Center geleitet. Angriffsmuster: UDP Flood (Port 53, 80, 443). Angriffsvolumen: 75 Gbps. Erwartete Dauer: Unbekannt. Angreifer wechseln kontinuierlich die Angriffsmuster.",
            technical_metadata=TechnicalMetadata(
                mitre_id="T1498",
                affected_assets=["WEB-SRV-01", "Load-Balancer", "DDoS-Mitigation"],
                ioc_hash=None
            ),
            dora_compliance_tag="Art25_BusinessContinuity",
            business_impact="Kunden können weiterhin nicht auf Online-Services zugreifen. Geschäftskritische Transaktionen sind blockiert. Geschätzter Umsatzausfall: €100.000/Stunde."
        ),
        Inject(
            inject_id="INJ-004",
            time_offset="T+02:00",
            phase=CrisisPhase.CONTAINMENT,
            source="Network Operations",
            target="Management",
            modality=InjectModality.INTERNAL_REPORT,
            content="Containment-Maßnahmen: DDoS-Mitigation filtert jetzt 95% des Angriffstraffics. Load-Balancer wurde neu konfiguriert mit Rate-Limiting. Backup-Web-Server werden aktiviert. Erste Kunden können wieder auf Services zugreifen (langsam, aber funktional).",
            technical_metadata=TechnicalMetadata(
                mitre_id="T1498",
                affected_assets=["WEB-SRV-01", "Load-Balancer", "Backup-Web-Server"],
                ioc_hash=None
            ),
            dora_compliance_tag="Art25_BusinessContinuity",
            business_impact="Teilweise Wiederherstellung: 30% der Kunden können wieder auf Services zugreifen. Performance ist reduziert, aber funktional."
        ),
        Inject(
            inject_id="INJ-005",
            time_offset="T+03:30",
            phase=CrisisPhase.RECOVERY,
            source="IT Operations",
            target="Management",
            modality=InjectModality.INTERNAL_REPORT,
            content="Angriff abgeklungen: DDoS-Angriff ist deutlich reduziert (auf 5 Gbps). Alle Backup-Web-Server sind aktiv. Services sind wieder für 90% der Kunden verfügbar. Monitoring wird fortgesetzt. Angriff dauerte insgesamt 3,5 Stunden.",
            technical_metadata=TechnicalMetadata(
                mitre_id="T1498",
                affected_assets=["WEB-SRV-01", "Backup-Web-Server", "Load-Balancer"],
                ioc_hash=None
            ),
            dora_compliance_tag="Art25_BusinessContinuity",
            business_impact="Wiederherstellung: Services sind wieder normal verfügbar. Geschätzter Gesamtumsatzausfall: €350.000. Post-Incident Review wird durchgeführt."
        )
    ]
    
    return {
        "scenario_id": "DEMO-DDOS-001",
        "scenario_type": ScenarioType.DDOS_CRITICAL_FUNCTIONS,
        "current_phase": CrisisPhase.RECOVERY,
        "injects": injects,
        "system_state": {
            "entities": [
                {"id": "WEB-SRV-01", "status": "recovered"},
                {"id": "Load-Balancer", "status": "operational"},
                {"id": "Backup-Web-Server", "status": "active"},
                {"id": "DDoS-Mitigation", "status": "monitoring"}
            ]
        },
        "iteration": 5,
        "max_iterations": 5,
        "errors": [],
        "warnings": [],
        "start_time": datetime.now(),
        "metadata": {"demo": True},
        "workflow_logs": [],
        "agent_decisions": []
    }


def get_available_demo_scenarios() -> dict:
    """Gibt alle verfügbaren Demo-Szenarien zurück."""
    return {
        "Ransomware & Double Extortion": get_demo_scenario_ransomware,
        "DDoS auf kritische Funktionen": get_demo_scenario_ddos
    }


def load_demo_scenario(scenario_name: str) -> dict:
    """
    Lädt ein Demo-Szenario.
    
    Args:
        scenario_name: Name des Demo-Szenarios
    
    Returns:
        Szenario-Dictionary im gleichen Format wie generate_scenario()
    """
    scenarios = get_available_demo_scenarios()
    
    if scenario_name not in scenarios:
        raise ValueError(f"Demo-Szenario '{scenario_name}' nicht gefunden. Verfügbar: {list(scenarios.keys())}")
    
    return scenarios[scenario_name]()

