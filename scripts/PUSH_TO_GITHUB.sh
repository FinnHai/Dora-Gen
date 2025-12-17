#!/bin/bash
# Skript zum Pushen auf GitHub mit Personal Access Token

echo "🚀 Push zu GitHub: Dora-Gen"
echo ""
echo "Du benötigst einen Personal Access Token von GitHub."
echo ""
echo "1. Gehe zu: https://github.com/settings/tokens"
echo "2. Klicke auf 'Generate new token (classic)'"
echo "3. Wähle Scopes: 'repo' (vollständiger Zugriff)"
echo "4. Kopiere den Token"
echo ""
read -p "Füge deinen Personal Access Token ein: " TOKEN

if [ -z "$TOKEN" ]; then
    echo "❌ Kein Token eingegeben. Abgebrochen."
    exit 1
fi

# Ersetze URL mit Token
git remote set-url origin https://${TOKEN}@github.com/FinnHai/Dora-Gen.git

echo ""
echo "📤 Pushe Code zu GitHub..."
git push -u origin main

# URL wieder auf normal setzen (ohne Token)
git remote set-url origin https://github.com/FinnHai/dora-scenario-generator.git

echo ""
# URL wieder auf normal setzen (ohne Token)
git remote set-url origin https://github.com/FinnHai/Dora-Gen.git

echo ""
echo "✅ Fertig! Prüfe: https://github.com/FinnHai/Dora-Gen"

