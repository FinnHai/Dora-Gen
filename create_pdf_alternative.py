#!/usr/bin/env python3
"""
Alternative PDF-Erstellung mit Python-Bibliotheken.
Erstellt HTML und bietet Optionen für PDF-Konvertierung.
"""

import os
import markdown
from pathlib import Path

def read_markdown_file(filepath):
    """Liest eine Markdown-Datei."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️  Fehler: {e}")
        return ""

def create_html_documentation():
    """Erstellt eine HTML-Version der Dokumentation."""
    
    doc_files = [
        ("README.md", "Projektübersicht"),
        ("STATUS.md", "Status & Capabilities"),
        ("QUICKSTART.md", "Schnellstart"),
        ("SETUP.md", "Setup-Anleitung"),
        ("FRONTEND.md", "Frontend-Anleitung"),
        ("ARCHITECTURE.md", "Architektur"),
        ("DOCUMENTATION.md", "Dokumentations-Übersicht"),
    ]
    
    html_content = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DORA Szenariengenerator - Vollständige Dokumentation</title>
    <style>
        @page {
            size: A4;
            margin: 2.5cm;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #1f77b4;
            border-bottom: 3px solid #1f77b4;
            padding-bottom: 10px;
            page-break-after: avoid;
        }
        h2 {
            color: #2ca02c;
            margin-top: 30px;
            page-break-after: avoid;
        }
        h3 {
            color: #ff7f0e;
            margin-top: 20px;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        pre {
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            page-break-inside: avoid;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #1f77b4;
            padding-left: 15px;
            margin-left: 0;
            color: #666;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #1f77b4;
            color: white;
        }
        .page-break {
            page-break-before: always;
        }
        .toc {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        .toc ul {
            list-style-type: none;
            padding-left: 0;
        }
        .toc li {
            margin: 5px 0;
        }
        .toc a {
            text-decoration: none;
            color: #1f77b4;
        }
        .toc a:hover {
            text-decoration: underline;
        }
        @media print {
            .page-break {
                page-break-before: always;
            }
            body {
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
    <h1>DORA-konformer Szenariengenerator</h1>
    <h2>Vollständige Dokumentation</h2>
    
    <div class="toc">
        <h3>Inhaltsverzeichnis</h3>
        <ul>
"""
    
    # Inhaltsverzeichnis
    for i, (_, title) in enumerate(doc_files, 1):
        html_content += f'            <li><a href="#section-{i}">{i}. {title}</a></li>\n'
    
    html_content += """        </ul>
    </div>
    
"""
    
    # Lese und konvertiere alle Dokumentationsdateien
    for i, (doc_file, title) in enumerate(doc_files, 1):
        if os.path.exists(doc_file):
            print(f"📄 Verarbeite {doc_file}...")
            md_content = read_markdown_file(doc_file)
            
            # Entferne Mermaid-Diagramme (werden in HTML nicht gerendert)
            # Ersetze durch Hinweis
            md_content = md_content.replace('```mermaid', '```\n*[Mermaid-Diagramm - siehe Online-Dokumentation]*\n```')
            
            # Konvertiere Markdown zu HTML
            html_section = markdown.markdown(
                md_content,
                extensions=['fenced_code', 'tables', 'toc']
            )
            
            html_content += f'    <div class="page-break" id="section-{i}"></div>\n'
            html_content += f'    <h1>{i}. {title}</h1>\n'
            html_content += html_section
            html_content += '\n\n<hr>\n\n'
        else:
            print(f"⚠️  Datei nicht gefunden: {doc_file}")
    
    html_content += """
    <div style="margin-top: 50px; padding-top: 20px; border-top: 2px solid #ddd; text-align: center; color: #666;">
        <p>DORA-konformer Szenariengenerator MVP 1.0</p>
        <p>Generiert am: <script>document.write(new Date().toLocaleDateString('de-DE'))</script></p>
    </div>
</body>
</html>
"""
    
    # Speichere HTML
    html_file = "DORA_Scenario_Generator_Documentation.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ HTML-Dokumentation erstellt: {html_file}")
    return html_file

def main():
    """Hauptfunktion."""
    print("=" * 60)
    print("PDF-Dokumentation Generator (Alternative)")
    print("=" * 60)
    print()
    
    # Prüfe ob markdown installiert ist
    try:
        import markdown
    except ImportError:
        print("📦 Installiere markdown...")
        os.system("pip install markdown")
        import markdown
    
    # Erstelle HTML
    html_file = create_html_documentation()
    
    if html_file:
        print(f"\n✅ HTML-Dokumentation erstellt: {html_file}")
        print("\n📄 Nächste Schritte:")
        print("   1. Öffne die HTML-Datei in einem Browser")
        print("   2. Drucke als PDF (Cmd+P / Ctrl+P)")
        print("   3. Wähle 'Als PDF speichern'")
        print("\n💡 Oder verwende online Tools:")
        print("   - https://www.markdowntopdf.com/")
        print("   - https://dillinger.io/")
        print("   - https://www.markdowntopdf.com/")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

