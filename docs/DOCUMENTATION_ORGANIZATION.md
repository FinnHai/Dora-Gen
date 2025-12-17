# 📚 Dokumentationsorganisation

Diese Datei dokumentiert die neue Struktur der Dokumentation.

## ✅ Durchgeführte Änderungen

### Neue Struktur

Die Dokumentation wurde in folgende Kategorien organisiert:

```
docs/
├── getting-started/      # Schnellstart & Setup
│   ├── QUICK_START.md
│   └── SETUP.md
├── user-guides/          # Benutzeranleitungen
│   ├── ANWENDUNGSANLEITUNG.md
│   ├── FRONTEND.md
│   └── CRISIS_COCKPIT_README.md
├── architecture/         # Architektur & Design
│   ├── ARCHITECTURE.md
│   └── DOCUMENTATION.md
├── development/          # Entwicklung & Deployment
│   └── DEPLOY_TO_GITHUB.md
├── evaluation/           # Evaluation & Tests
│   ├── EVALUATION_SUMMARY.md
│   ├── EVALUATION_METHODOLOGY.md
│   └── README.md
└── thesis/              # Thesis-Dokumentation
    └── THESIS_DOCUMENTATION.md

archive/                 # Veraltete Dateien
├── QUICKSTART.md
└── DOKUMENTATION_UEBERSICHT.md

logs/                    # Automatisch generierte Logs
├── CRITIC_AUDIT_LOG.md
└── README.md
```

### Verschiebungen

**Nach `docs/getting-started/`:**
- `QUICK_START.md`
- `SETUP.md`

**Nach `docs/user-guides/`:**
- `ANWENDUNGSANLEITUNG.md`
- `FRONTEND.md`
- `CRISIS_COCKPIT_README.md`

**Nach `docs/architecture/`:**
- `ARCHITECTURE.md`
- `DOCUMENTATION.md`

**Nach `docs/development/`:**
- `DEPLOY_TO_GITHUB.md`

**Nach `docs/evaluation/`:**
- `EVALUATION_SUMMARY.md`
- `evaluation/EVALUATION_METHODOLOGY.md`
- `evaluation/README.md`

**Nach `docs/thesis/`:**
- `THESIS_DOCUMENTATION.md`

**Nach `archive/`:**
- `QUICKSTART.md` (veraltet, ersetzt durch `QUICK_START.md`)
- `DOKUMENTATION_UEBERSICHT.md` (ersetzt durch `docs/README.md`)

**Nach `logs/`:**
- `CRITIC_AUDIT_LOG.md` (automatisch generiert)

### Aktualisierte Dateien

- ✅ `README.md` - Alle Links aktualisiert
- ✅ `docs/README.md` - Neue zentrale Übersicht erstellt
- ✅ `docs/getting-started/QUICK_START.md` - Links aktualisiert
- ✅ `docs/user-guides/ANWENDUNGSANLEITUNG.md` - Links aktualisiert
- ✅ `docs/thesis/THESIS_DOCUMENTATION.md` - Links aktualisiert
- ✅ `create_pdf_final.py` - Pfade aktualisiert
- ✅ `archive/README.md` - Erklärt archivierte Dateien
- ✅ `logs/README.md` - Erklärt Log-Dateien

## 📖 Verwendung

### Für Benutzer

**Schnellstart:**
→ [docs/getting-started/QUICK_START.md](docs/getting-started/QUICK_START.md)

**Vollständige Anleitung:**
→ [docs/user-guides/ANWENDUNGSANLEITUNG.md](docs/user-guides/ANWENDUNGSANLEITUNG.md)

**Zentrale Übersicht:**
→ [docs/README.md](docs/README.md)

### Für Entwickler

**Architektur:**
→ [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)

**Deployment:**
→ [docs/development/DEPLOY_TO_GITHUB.md](docs/development/DEPLOY_TO_GITHUB.md)

## 🔄 Migration

Wenn du auf alte Pfade verweisende Links findest, aktualisiere sie entsprechend:

| Alter Pfad | Neuer Pfad |
|------------|------------|
| `QUICK_START.md` | `docs/getting-started/QUICK_START.md` |
| `ANWENDUNGSANLEITUNG.md` | `docs/user-guides/ANWENDUNGSANLEITUNG.md` |
| `ARCHITECTURE.md` | `docs/architecture/ARCHITECTURE.md` |
| `CRISIS_COCKPIT_README.md` | `docs/user-guides/CRISIS_COCKPIT_README.md` |
| `THESIS_DOCUMENTATION.md` | `docs/thesis/THESIS_DOCUMENTATION.md` |

## 📝 Hinweise

- Die `archive/` Dateien werden nicht mehr aktualisiert
- Die `logs/` Dateien werden automatisch generiert
- Alle neuen Dokumentationen sollten in `docs/` erstellt werden
- Die Haupt-`README.md` verweist auf die neue Struktur

---

**Erstellt:** 2025-01-15
**Status:** ✅ Abgeschlossen
