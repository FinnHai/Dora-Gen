#!/usr/bin/env python3
"""
Erstellt eine kombinierte PDF-Dokumentation aus allen Markdown-Dateien.
"""

import os
import subprocess
from pathlib import Path

def read_markdown_file(filepath):
    """Liest eine Markdown-Datei und gibt den Inhalt zurück."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️  Fehler beim Lesen von {filepath}: {e}")
        return ""

def create_combined_documentation():
    """Erstellt eine kombinierte Dokumentation aus allen MD-Dateien."""
    
    # Reihenfolge der Dokumentationsdateien
    doc_files = [
        "README.md",
        "STATUS.md",
        "QUICKSTART.md",
        "SETUP.md",
        "FRONTEND.md",
        "ARCHITECTURE.md",
        "DOCUMENTATION.md",
    ]
    
    # Titel und Einleitung
    combined = """# DORA-konformer Szenariengenerator
## Vollständige Dokumentation

**Version:** MVP 1.0  
**Datum:** 2025-01-XX  
**Projekt:** DORA-konformer Szenariengenerator für Krisenmanagement

---

**Inhaltsverzeichnis:**

1. [Projektübersicht](#projektübersicht)
2. [Status & Capabilities](#status--capabilities)
3. [Schnellstart](#schnellstart)
4. [Setup-Anleitung](#setup-anleitung)
5. [Frontend-Anleitung](#frontend-anleitung)
6. [Architektur](#architektur)
7. [Dokumentations-Übersicht](#dokumentations-übersicht)

---

"""
    
    # Lese alle Dokumentationsdateien
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            print(f"📄 Lese {doc_file}...")
            content = read_markdown_file(doc_file)
            
            # Entferne Titel (erste Zeile mit #) um Duplikate zu vermeiden
            lines = content.split('\n')
            if lines and lines[0].startswith('#'):
                # Überspringe den Haupttitel, behalte aber Untertitel
                content = '\n'.join(lines[1:])
            
            # Füge Seitenumbruch und Titel hinzu
            doc_name = doc_file.replace('.md', '').replace('_', ' ').title()
            combined += f"\n\n\\newpage\n\n# {doc_name}\n\n{content}\n\n---\n"
        else:
            print(f"⚠️  Datei nicht gefunden: {doc_file}")
    
    # Speichere kombinierte Dokumentation
    output_file = "COMBINED_DOCUMENTATION.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined)
    
    print(f"\n✅ Kombinierte Dokumentation erstellt: {output_file}")
    return output_file

def convert_to_pdf(md_file):
    """Konvertiert Markdown zu PDF mit pandoc."""
    
    pdf_file = "DORA_Scenario_Generator_Documentation.pdf"
    
    # Prüfe ob pandoc installiert ist
    try:
        subprocess.run(['pandoc', '--version'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n⚠️  Pandoc ist nicht installiert.")
        print("\n📥 Installation:")
        print("   macOS: brew install pandoc")
        print("   Linux: sudo apt-get install pandoc")
        print("   Windows: choco install pandoc")
        print("\n💡 Alternative: Verwende online Tools wie:")
        print("   - https://www.markdowntopdf.com/")
        print("   - https://dillinger.io/")
        return None
    
    # Pandoc-Befehl mit schöner Formatierung
    cmd = [
        'pandoc',
        md_file,
        '-o', pdf_file,
        '--pdf-engine=pdflatex',  # oder xelatex für bessere Unicode-Unterstützung
        '--toc',  # Inhaltsverzeichnis
        '--toc-depth=3',  # Tiefe des Inhaltsverzeichnisses
        '--number-sections',  # Nummerierte Abschnitte
        '--highlight-style=tango',  # Code-Highlighting
        '-V', 'geometry:margin=2.5cm',  # Seitenränder
        '-V', 'fontsize=11pt',  # Schriftgröße
        '-V', 'documentclass=article',  # Dokumenttyp
    ]
    
    try:
        print(f"\n🔄 Konvertiere zu PDF...")
        subprocess.run(cmd, check=True)
        print(f"✅ PDF erstellt: {pdf_file}")
        return pdf_file
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Fehler bei PDF-Konvertierung: {e}")
        print("\n💡 Versuche alternative Methode ohne LaTeX...")
        
        # Alternative: HTML zu PDF (benötigt wkhtmltopdf)
        try:
            html_file = md_file.replace('.md', '.html')
            subprocess.run(['pandoc', md_file, '-o', html_file, '--standalone', '--toc'], check=True)
            print(f"✅ HTML erstellt: {html_file}")
            print("   Du kannst diese HTML-Datei in einem Browser öffnen und als PDF drucken.")
            return html_file
        except Exception as e2:
            print(f"❌ Auch HTML-Konvertierung fehlgeschlagen: {e2}")
            return None

def main():
    """Hauptfunktion."""
    print("=" * 60)
    print("PDF-Dokumentation Generator")
    print("=" * 60)
    print()
    
    # Erstelle kombinierte Dokumentation
    md_file = create_combined_documentation()
    
    if md_file:
        # Versuche PDF zu erstellen
        pdf_file = convert_to_pdf(md_file)
        
        if pdf_file:
            print(f"\n🎉 Erfolg! Dokumentation erstellt:")
            print(f"   📄 Markdown: {md_file}")
            print(f"   📕 PDF: {pdf_file}")
        else:
            print(f"\n📄 Markdown-Datei erstellt: {md_file}")
            print("   Du kannst diese manuell zu PDF konvertieren.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

