#!/bin/bash
# Startet den CRUX API Server

cd "$(dirname "$0")"
source venv/bin/activate

# Prüfe ob Port 8000 belegt ist
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "Port 8000 ist bereits belegt. Beende alten Prozess..."
    kill $(lsof -ti:8000)
    sleep 2
fi

echo "Starte CRUX API Server auf http://localhost:8000"
python api_server.py





