import base64
import json
import os
from dataclasses import dataclass
from typing import List, Optional

import streamlit as st
from pydantic import BaseModel, Field

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class ShoeAnalysis(BaseModel):
    titel: str = Field(description="Kurzer Inseratstitel")
    beschreibung: str = Field(description="Beschreibung auf Deutsch")
    marke: Optional[str] = None
    groesse: Optional[str] = None
    zustand: str = Field(description="z.B. sehr gut, gut, gebraucht")
    preisvorschlag_eur: float = Field(description="Fairer Verkaufspreis in EUR")


@dataclass
class ListingDraft:
    titel: str
    beschreibung: str
    preis_eur: float
    kategorie: str
    marke: Optional[str]
    groesse: Optional[str]
    ort: str


def image_to_data_url(image_bytes: bytes, mime: str = "image/jpeg") -> str:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def analyze_shoe_images_with_ai(images: List[bytes], notes: str) -> ShoeAnalysis:
    if OpenAI is None:
        return ShoeAnalysis(
            titel="Kinder-Schuhe gebraucht",
            beschreibung="Gebrauchte Kinderschuhe in ordentlichem Zustand.",
            zustand="gebraucht",
            preisvorschlag_eur=10.0,
        )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return ShoeAnalysis(
            titel="Kinder-Schuhe gebraucht",
            beschreibung="Gebrauchte Kinderschuhe in ordentlichem Zustand.",
            zustand="gebraucht",
            preisvorschlag_eur=10.0,
        )

    client = OpenAI(api_key=api_key)

    content = [
        {
            "type": "text",
            "text": (
                "Analysiere die hochgeladenen Fotos von gebrauchten Kinderschuhen. "
                "Antworte nur als JSON mit den Feldern: titel, beschreibung, marke, groesse, zustand, preisvorschlag_eur. "
                "Preis realistisch für willhaben.at in Österreich. "
                f"Zusatznotizen: {notes}"
            ),
        }
    ]

    for image in images:
        content.append({"type": "image_url", "image_url": {"url": image_to_data_url(image)}})

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{"role": "user", "content": content}],
        temperature=0.2,
    )

    raw_text = response.output_text.strip()
    data = json.loads(raw_text)
    return ShoeAnalysis(**data)


def fill_willhaben_draft(listing: ListingDraft) -> str:
    """
    Grundgerüst für Browser-Automation.
    Diese Funktion ist absichtlich konservativ und gibt nur eine Anleitung zurück,
    weil Selektoren und Formularstruktur sich ändern können.
    """
    return (
        "Automation vorbereitet. Nächster Schritt: Playwright-Selektoren für das aktuelle "
        "Willhaben-Formular eintragen und nach dem Login nur Entwurf ausfüllen."
    )


def main() -> None:
    st.set_page_config(page_title="Willhaben Schuh-Assistent", layout="centered")
    st.title("👟 Willhaben Schuh-Assistent")
    st.write("Fotos hochladen → Preisvorschlag erhalten → Preis bestätigen → Inserat erzeugen")

    uploaded_files = st.file_uploader(
        "Schuh-Fotos", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True
    )
    notes = st.text_area("Zusatzinfos (optional)", placeholder="z.B. Größe 31, Marke Superfit, kaum getragen")

    category = st.text_input("Kategorie", value="Baby & Kind > Schuhe")
    location = st.text_input("Ort", value="Wien")

    if st.button("Preisvorschlag berechnen"):
        if not uploaded_files:
            st.warning("Bitte lade mindestens ein Foto hoch.")
            return

        images = [f.read() for f in uploaded_files]

        with st.spinner("Analysiere Fotos..."):
            analysis = analyze_shoe_images_with_ai(images, notes)

        st.session_state["analysis"] = analysis.model_dump()

    analysis_data = st.session_state.get("analysis")
    if analysis_data:
        analysis = ShoeAnalysis(**analysis_data)

        st.subheader("Vorschlag")
        st.text_input("Titel", value=analysis.titel, key="titel")
        st.text_area("Beschreibung", value=analysis.beschreibung, key="beschreibung")
        st.text_input("Marke", value=analysis.marke or "", key="marke")
        st.text_input("Größe", value=analysis.groesse or "", key="groesse")
        st.text_input("Zustand", value=analysis.zustand, key="zustand")

        confirmed_price = st.number_input(
            "Finaler Preis (EUR)", min_value=1.0, max_value=500.0, value=float(analysis.preisvorschlag_eur), step=1.0
        )

        if st.button("Inserat-Entwurf erstellen"):
            listing = ListingDraft(
                titel=st.session_state["titel"],
                beschreibung=st.session_state["beschreibung"],
                preis_eur=confirmed_price,
                kategorie=category,
                marke=st.session_state.get("marke") or None,
                groesse=st.session_state.get("groesse") or None,
                ort=location,
            )
            st.session_state["listing"] = listing

    listing: ListingDraft | None = st.session_state.get("listing")
    if listing:
        st.subheader("Inserat JSON")
        payload = {
            "titel": listing.titel,
            "beschreibung": listing.beschreibung,
            "preis_eur": listing.preis_eur,
            "kategorie": listing.kategorie,
            "marke": listing.marke,
            "groesse": listing.groesse,
            "ort": listing.ort,
        }
        st.code(json.dumps(payload, ensure_ascii=False, indent=2), language="json")

        if st.button("Automation-Hinweis anzeigen"):
            st.info(fill_willhaben_draft(listing))


if __name__ == "__main__":
    main()
