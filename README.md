# Willhaben Schuh-Inserat Assistent

Dieses kleine Programm hilft dir dabei, alte Kinderschuhe schneller auf **willhaben.at** zu inserieren.

## Was es kann

1. Du lädst eigene Schuh-Fotos hoch.
2. Das Programm erkennt (mit GPT Vision) Marke/Typ/Zustand und schlägt einen Preis vor.
3. Du bestätigst oder korrigierst den Preis.
4. Es erstellt daraus ein strukturiertes Inserat.
5. Optional: Es kann den Inserat-Entwurf per Browser-Automation in Willhaben eintragen (manuelle Kontrolle bleibt bei dir).

> Hinweis: Für automatisiertes Einstellen bitte immer die aktuellen Nutzungsbedingungen von willhaben.at beachten.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional (für KI-Auswertung):

```bash
export OPENAI_API_KEY="dein_api_key"
```

Optional (für Browser-Automation):

```bash
playwright install chromium
```

## Start

```bash
streamlit run app.py
```

Dann im Browser:
- Fotos hochladen
- Kategorie/Größe ergänzen
- Preisvorschlag prüfen
- Finalen Preis bestätigen
- Inserat-JSON erzeugen

## Browser-Automation (optional)

Die Funktion erstellt **keine unsichtbaren Hintergrund-Posts**. Stattdessen öffnet sie einen sichtbaren Browser, damit du vor dem finalen Veröffentlichen alles kontrollieren kannst.

Aktuell ist die Automation als **sicheres Grundgerüst** implementiert (`fill_willhaben_draft`). Je nach Änderungen im Willhaben-Formular müssen die Selektoren angepasst werden.
