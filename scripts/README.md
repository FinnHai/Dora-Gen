# Scripts

Dieses Verzeichnis enthält Hilfsskripte und Utilities.

## Dateien

- **`check_setup.py`** - Prüft die Systemkonfiguration
  - Validiert Umgebungsvariablen
  - Testet Neo4j-Verbindung
  - Prüft Dependencies

- **`create_pdf_final.py`** - Erstellt PDF-Dokumentation
  - Kombiniert mehrere Markdown-Dateien
  - Generiert formatierte PDF-Ausgabe

- **`start_neo4j.sh`** - Startet Neo4j mit Docker
  - Docker-Container Management
  - Port-Konfiguration

- **`PUSH_TO_GITHUB.sh`** - Deployment-Skript für GitHub
  - Automatisiertes Deployment
  - Git-Operationen

- **`populate_ttp_database.py`** - Befüllt die TTP-Datenbank
  - MITRE ATT&CK Daten
  - ChromaDB Integration

## Verwendung

### Setup prüfen

```bash
python scripts/check_setup.py
```

### Neo4j starten

```bash
./scripts/start_neo4j.sh
```

### TTP-Datenbank befüllen

```bash
python scripts/populate_ttp_database.py
```
