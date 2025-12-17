#!/bin/bash
# Skript zum Starten von Neo4j mit Docker

echo "🚀 Starte Neo4j Container..."

# Prüfe ob Docker läuft
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker Daemon läuft nicht!"
    echo "   Bitte starte Docker Desktop oder den Docker Daemon."
    exit 1
fi

# Prüfe ob Container bereits existiert
if docker ps -a | grep -q neo4j; then
    echo "📦 Neo4j Container existiert bereits"
    
    # Prüfe ob Container läuft
    if docker ps | grep -q neo4j; then
        echo "✅ Neo4j läuft bereits"
        docker ps | grep neo4j
    else
        echo "🔄 Starte bestehenden Container..."
        docker start neo4j
        echo "✅ Neo4j gestartet"
    fi
else
    echo "🆕 Erstelle neuen Neo4j Container..."
    
    # Lese Passwort aus .env, falls vorhanden
    if [ -f .env ]; then
        NEO4J_PASS=$(grep NEO4J_PASSWORD .env | cut -d'=' -f2)
        if [ -z "$NEO4J_PASS" ] || [ "$NEO4J_PASS" = "your_password_here" ]; then
            NEO4J_PASS="password"
            echo "⚠️  Verwende Standard-Passwort 'password' (konfiguriere NEO4J_PASSWORD in .env)"
        else
            echo "✓ Verwende Passwort aus .env"
        fi
    else
        NEO4J_PASS="password"
        echo "⚠️  Keine .env gefunden, verwende Standard-Passwort 'password'"
    fi
    
    docker run -d \
        --name neo4j \
        -p 7474:7474 -p 7687:7687 \
        -e NEO4J_AUTH=neo4j/$NEO4J_PASS \
        -e NEO4J_PLUGINS='["apoc"]' \
        neo4j:latest
    
    echo "⏳ Warte 15 Sekunden auf Neo4j Initialisierung..."
    sleep 15
    echo "✅ Neo4j Container erstellt und gestartet"
fi

echo ""
echo "🌐 Neo4j Browser: http://localhost:7474"
echo "🔌 Bolt URI: bolt://localhost:7687"
echo "👤 Username: neo4j"
if [ -n "$NEO4J_PASS" ]; then
    echo "🔑 Password: $NEO4J_PASS"
else
    echo "🔑 Password: (aus .env)"
fi
echo ""

