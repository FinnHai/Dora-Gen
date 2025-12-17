#!/usr/bin/env python3
"""
Erstellt eine PDF-Dokumentation aus allen Markdown-Dateien.
Verwendet HTML als Zwischenformat und konvertiert zu PDF.
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

def create_pdf_documentation():
    """Erstellt eine PDF-Dokumentation."""
    
    doc_files = [
        ("README.md", "Projektübersicht"),
        ("PROJECT_STATUS.md", "Status & Capabilities"),
        ("docs/getting-started/QUICK_START.md", "Schnellstart"),
        ("docs/getting-started/SETUP.md", "Setup-Anleitung"),
        ("docs/user-guides/FRONTEND.md", "Frontend-Anleitung"),
        ("docs/architecture/ARCHITECTURE.md", "Architektur"),
        ("docs/architecture/DOCUMENTATION.md", "Dokumentations-Übersicht"),
    ]
    
    # HTML-Template mit Styling
    html_template = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>DORA Szenariengenerator - Dokumentation</title>
    <style>
        @page {{
            size: A4;
            margin: 2.5cm;
            @bottom-center {{
                content: "Seite " counter(page) " von " counter(pages);
                font-size: 10pt;
                color: #666;
            }}
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 11pt;
        }}
        h1 {{
            color: #1f77b4;
            border-bottom: 3px solid #1f77b4;
            padding-bottom: 10px;
            page-break-after: avoid;
            font-size: 24pt;
            margin-top: 30px;
        }}
        h2 {{
            color: #2ca02c;
            margin-top: 25px;
            page-break-after: avoid;
            font-size: 18pt;
        }}
        h3 {{
            color: #ff7f0e;
            margin-top: 20px;
            font-size: 14pt;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            page-break-inside: avoid;
            border-left: 4px solid #1f77b4;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid #1f77b4;
            padding-left: 15px;
            margin-left: 0;
            color: #666;
            font-style: italic;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            page-break-inside: avoid;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #1f77b4;
            color: white;
        }}
        .page-break {{
            page-break-before: always;
        }}
        .toc {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
            page-break-after: always;
        }}
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        .toc li {{
            margin: 8px 0;
        }}
        .toc a {{
            text-decoration: none;
            color: #1f77b4;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ddd;
            margin: 30px 0;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 10pt;
        }}
    </style>
</head>
<body>
    <h1>DORA-konformer Szenariengenerator</h1>
    <h2>Vollständige Dokumentation</h2>
    
    <div class="toc">
        <h3>Inhaltsverzeichnis</h3>
        <ul>
{0}
        </ul>
    </div>
    
{1}
    
    <div class="footer">
        <p><strong>DORA-konformer Szenariengenerator MVP 1.0</strong></p>
        <p>Vollständige Projektdokumentation</p>
    </div>
</body>
</html>
"""
    
    # Erstelle Inhaltsverzeichnis
    toc_items = ""
    content_sections = ""
    
    for i, (doc_file, title) in enumerate(doc_files, 1):
        toc_items += f'            <li><a href="#section-{i}">{i}. {title}</a></li>\n'
        
        if os.path.exists(doc_file):
            print(f"📄 Verarbeite {doc_file}...")
            md_content = read_markdown_file(doc_file)
            
            # Entferne Mermaid-Diagramme (ersetze durch Hinweis)
            md_content = md_content.replace('```mermaid', '```\n*[Mermaid-Diagramm - siehe Online-Dokumentation für interaktive Version]*\n```')
            
            # Konvertiere Markdown zu HTML
            html_section = markdown.markdown(
                md_content,
                extensions=['fenced_code', 'tables', 'toc', 'codehilite']
            )
            
            content_sections += f'    <div class="page-break" id="section-{i}"></div>\n'
            content_sections += f'    <h1>{i}. {title}</h1>\n'
            content_sections += html_section
            content_sections += '\n\n<hr>\n\n'
        else:
            print(f"⚠️  Datei nicht gefunden: {doc_file}")
    
    # Erstelle vollständiges HTML
    html_content = html_template.format(toc_items, content_sections)
    
    # Speichere HTML
    html_file = "DORA_Documentation.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ HTML-Dokumentation erstellt: {html_file}")
    
    # Versuche PDF mit weasyprint zu erstellen
    try:
        from weasyprint import HTML
        pdf_file = "DORA_Scenario_Generator_Documentation.pdf"
        print(f"🔄 Konvertiere zu PDF...")
        HTML(filename=html_file).write_pdf(pdf_file)
        print(f"✅ PDF erstellt: {pdf_file}")
        return pdf_file, html_file
    except ImportError:
        print("⚠️  WeasyPrint nicht installiert. Nur HTML erstellt.")
        print("   Installiere mit: pip install weasyprint")
        return None, html_file
    except Exception as e:
        print(f"⚠️  PDF-Konvertierung fehlgeschlagen: {e}")
        print("   HTML-Datei kann im Browser als PDF gedruckt werden.")
        return None, html_file

def main():
    """Hauptfunktion."""
    print("=" * 60)
    print("PDF-Dokumentation Generator")
    print("=" * 60)
    print()
    
    pdf_file, html_file = create_pdf_documentation()
    
    if pdf_file:
        print(f"\n🎉 Erfolg! Dokumentation erstellt:")
        print(f"   📕 PDF: {pdf_file}")
        print(f"   📄 HTML: {html_file}")
    else:
        print(f"\n📄 HTML-Dokumentation erstellt: {html_file}")
        print("\n📄 Nächste Schritte:")
        print("   1. Öffne die HTML-Datei in einem Browser")
        print("   2. Drucke als PDF (Cmd+P / Ctrl+P)")
        print("   3. Wähle 'Als PDF speichern'")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

