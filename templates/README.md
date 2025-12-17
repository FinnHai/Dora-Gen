# Templates

Dieses Verzeichnis enthält Infrastruktur-Templates für Neo4j.

## Dateien

- **`infrastructure_templates.py`** - Infrastruktur-Templates
  - Vordefinierte System-Architekturen
  - Standard-Bank-Infrastruktur
  - Template-Management

## Verfügbare Templates

- `standard_bank` - Standard-Bank-Infrastruktur
- `large_bank` - Große Bank-Infrastruktur
- `minimal_bank` - Minimale Test-Infrastruktur

## Verwendung

```python
from templates.infrastructure_templates import get_available_templates, load_template_to_neo4j

# Verfügbare Templates abrufen
templates = get_available_templates()

# Template in Neo4j laden
load_template_to_neo4j(template_name="standard_bank", neo4j_client=client)
```

## Integration

Die Templates werden automatisch vom Neo4j Client verwendet, wenn `initialize_base_infrastructure()` mit einem Template-Namen aufgerufen wird.
