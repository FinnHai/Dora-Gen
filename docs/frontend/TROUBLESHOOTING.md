# Troubleshooting Guide

## Turbopack Cache-Fehler beheben

Wenn du Fehler wie diese siehst:
```
Failed to restore task data (corrupted database or bug)
Unable to open static sorted file
No such file or directory (os error 2)
```

**Lösung:**
```bash
cd /Users/finnheintzann/Desktop/BA/crux-frontend

# Lösche alle Caches
rm -rf .next node_modules/.cache .turbo

# Starte den Server neu
npm run dev
```

## CSS-Fehler beheben

Wenn du `@import rules must precede all rules` Fehler siehst:

**Lösung:**
1. Lösche `.next` Cache: `rm -rf .next`
2. Hard Refresh im Browser: `Cmd+Shift+R` (Mac) oder `Ctrl+Shift+R` (Windows)
3. Oder DevTools → Network Tab → "Disable cache" aktivieren

## TypeScript-Fehler beheben

Wenn TypeScript-Fehler auftreten:

**Lösung:**
```bash
# TypeScript-Cache löschen
rm -rf .next

# Neu kompilieren
npm run dev
```

## Backend-Verbindungsfehler

Wenn das Frontend keine Backend-Daten lädt:

1. **Prüfe ob Backend läuft:**
   ```bash
   cd /Users/finnheintzann/Desktop/BA
   python api_server.py
   ```

2. **Prüfe Browser-Console** (F12) für Fehler

3. **Fallback zu Demo-Daten:**
   - Frontend fällt automatisch auf Demo-Daten zurück wenn Backend nicht verfügbar ist
   - Toggle in `lib/demo-data.ts`: `DEMO_MODE = true`

## Kompletter Reset

Wenn nichts mehr funktioniert:

```bash
cd /Users/finnheintzann/Desktop/BA/crux-frontend

# Lösche alle Caches
rm -rf .next node_modules/.cache .turbo

# Optional: Neu installieren (falls nötig)
# rm -rf node_modules package-lock.json
# npm install

# Starte neu
npm run dev
```

