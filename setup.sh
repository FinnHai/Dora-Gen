#!/bin/bash
# CRUX Setup-Skript für macOS/Linux
# Automatisiert die Installation des CRUX-Systems

set -e  # Beende bei Fehlern

echo "🚀 CRUX Setup-Skript"
echo "===================="
echo ""

# Farben für Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funktionen
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Prüfe Voraussetzungen
echo "📋 Prüfe Voraussetzungen..."
echo ""

# Python Version prüfen
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$(printf '%s\n' "3.10" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.10" ]; then
        print_error "Python 3.10+ wird benötigt. Gefunden: $PYTHON_VERSION"
        exit 1
    fi
    print_success "Python $PYTHON_VERSION gefunden"
else
    print_error "Python 3 nicht gefunden. Bitte installieren Sie Python 3.10+"
    exit 1
fi

# Node.js prüfen
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_warning "Node.js 18+ wird empfohlen. Gefunden: $(node --version)"
    else
        print_success "Node.js $(node --version) gefunden"
    fi
else
    print_error "Node.js nicht gefunden. Bitte installieren Sie Node.js 18+"
    exit 1
fi

# Docker prüfen
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        print_success "Docker läuft"
    else
        print_warning "Docker installiert, aber Daemon läuft nicht. Bitte starten Sie Docker Desktop."
    fi
else
    print_warning "Docker nicht gefunden. Neo4j Setup wird übersprungen."
fi

echo ""
echo "📦 Schritt 1: Backend Setup"
echo "----------------------------"

# Virtual Environment erstellen
if [ ! -d "venv" ]; then
    echo "Erstelle Virtual Environment..."
    python3 -m venv venv
    print_success "Virtual Environment erstellt"
else
    print_warning "Virtual Environment existiert bereits"
fi

# Virtual Environment aktivieren
echo "Aktiviere Virtual Environment..."
source venv/bin/activate

# pip upgraden
echo "Upgrade pip..."
pip install --upgrade pip --quiet

# Dependencies installieren
echo "Installiere Python Dependencies..."
pip install -r requirements.txt --quiet
print_success "Python Dependencies installiert"

# .env Datei erstellen
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env Datei erstellt (von .env.example)"
        print_warning "Bitte bearbeiten Sie .env und fügen Sie Ihren OPENAI_API_KEY ein!"
    else
        print_warning ".env.example nicht gefunden, erstelle Standard .env..."
        cat > .env << EOF
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_DB_PATH=./chroma_db
EOF
        print_warning "Bitte bearbeiten Sie .env und fügen Sie Ihren OPENAI_API_KEY ein!"
    fi
else
    print_warning ".env Datei existiert bereits"
fi

echo ""
echo "📦 Schritt 2: Frontend Setup"
echo "----------------------------"

cd crux-frontend

# node_modules prüfen
if [ ! -d "node_modules" ]; then
    echo "Installiere Node.js Dependencies..."
    npm install
    print_success "Node.js Dependencies installiert"
else
    print_warning "node_modules existiert bereits"
fi

cd ..

echo ""
echo "📦 Schritt 3: Neo4j Setup"
echo "----------------------------"

# Neo4j starten, falls Docker verfügbar
if command -v docker &> /dev/null && docker info &> /dev/null; then
    if [ -f "scripts/start_neo4j.sh" ]; then
        echo "Starte Neo4j..."
        chmod +x scripts/start_neo4j.sh
        ./scripts/start_neo4j.sh
    else
        print_warning "start_neo4j.sh nicht gefunden"
    fi
else
    print_warning "Docker nicht verfügbar - Neo4j Setup übersprungen"
    print_warning "Sie können Neo4j später mit: ./scripts/start_neo4j.sh starten"
fi

echo ""
echo "✅ Setup abgeschlossen!"
echo ""
echo "📝 Nächste Schritte:"
echo "   1. Bearbeiten Sie .env und fügen Sie Ihren OPENAI_API_KEY ein"
echo "   2. Starten Sie das Backend:"
echo "      source venv/bin/activate"
echo "      python api_server.py"
echo "   3. Starten Sie das Frontend (in einem neuen Terminal):"
echo "      cd crux-frontend"
echo "      npm run dev"
echo ""
echo "🌐 URLs nach dem Start:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Neo4j Browser: http://localhost:7474"
echo ""

