@echo off
REM CRUX Setup-Skript für Windows
REM Automatisiert die Installation des CRUX-Systems

echo 🚀 CRUX Setup-Skript
echo ====================
echo.

REM Prüfe Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nicht gefunden. Bitte installieren Sie Python 3.10+
    pause
    exit /b 1
)
echo ✅ Python gefunden
python --version

REM Prüfe Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js nicht gefunden. Bitte installieren Sie Node.js 18+
    pause
    exit /b 1
)
echo ✅ Node.js gefunden
node --version

echo.
echo 📦 Schritt 1: Backend Setup
echo ----------------------------

REM Virtual Environment erstellen
if not exist "venv" (
    echo Erstelle Virtual Environment...
    python -m venv venv
    echo ✅ Virtual Environment erstellt
) else (
    echo ⚠️  Virtual Environment existiert bereits
)

REM Virtual Environment aktivieren
echo Aktiviere Virtual Environment...
call venv\Scripts\activate.bat

REM pip upgraden
echo Upgrade pip...
python -m pip install --upgrade pip --quiet

REM Dependencies installieren
echo Installiere Python Dependencies...
pip install -r requirements.txt --quiet
echo ✅ Python Dependencies installiert

REM .env Datei erstellen
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo ✅ .env Datei erstellt (von .env.example)
        echo ⚠️  Bitte bearbeiten Sie .env und fügen Sie Ihren OPENAI_API_KEY ein!
    ) else (
        echo NEO4J_URI=bolt://localhost:7687> .env
        echo NEO4J_USER=neo4j>> .env
        echo NEO4J_PASSWORD=password>> .env
        echo OPENAI_API_KEY=your_openai_api_key_here>> .env
        echo CHROMA_DB_PATH=./chroma_db>> .env
        echo ⚠️  Bitte bearbeiten Sie .env und fügen Sie Ihren OPENAI_API_KEY ein!
    )
) else (
    echo ⚠️  .env Datei existiert bereits
)

echo.
echo 📦 Schritt 2: Frontend Setup
echo ----------------------------

cd crux-frontend

REM node_modules prüfen
if not exist "node_modules" (
    echo Installiere Node.js Dependencies...
    call npm install
    echo ✅ Node.js Dependencies installiert
) else (
    echo ⚠️  node_modules existiert bereits
)

cd ..

echo.
echo ✅ Setup abgeschlossen!
echo.
echo 📝 Nächste Schritte:
echo    1. Bearbeiten Sie .env und fügen Sie Ihren OPENAI_API_KEY ein
echo    2. Starten Sie Neo4j (falls Docker installiert):
echo       docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
echo    3. Starten Sie das Backend:
echo       venv\Scripts\activate
echo       python api_server.py
echo    4. Starten Sie das Frontend (in einem neuen Terminal):
echo       cd crux-frontend
echo       npm run dev
echo.
echo 🌐 URLs nach dem Start:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo    Neo4j Browser: http://localhost:7474
echo.

pause

