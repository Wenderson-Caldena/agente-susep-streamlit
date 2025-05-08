# agente_susep/ingestion/process_pdf.py

import fitz  # PyMuPDF
import re
from typing import List, Dict

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text

def split_by_articles(text: str) -> List[Dict]:
    """
    Separa o texto completo da norma por artigos, mantendo contexto de seção e subseção.
    """
    # Separa por linhas
    lines = text.splitlines()

    current_section = ""
    current_subsection = ""
    current_article = ""
    buffer = []
    chunks = []

    for line in lines:
        clean = line.strip()

        # Detecta seção
        if re.match(r"^Seção [IVXLCDM]+", clean):
            current_section = clean
            continue

        # Detecta subseção
        if re.match(r"^Subseção [IVXLCDM]+", clean):
            current_subsection = clean
            continue

        # Detecta artigo
        match_art = re.match(r"^(Art\.\s*\d+[\u00bao]?)(.*)$", clean)
        if match_art:
            # Salva o buffer atual antes de começar novo artigo
            if buffer and current_article:
                chunks.append({
                    "section": current_section,
                    "subsection": current_subsection,
                    "article": current_article,
                    "text": "\n".join(buffer).strip()
                })
                buffer = []

            current_article = match_art.group(1)  # ex: Art. 7º
            buffer.append(clean)
        else:
            buffer.append(clean)

    # Salva o último artigo
    if buffer and current_article:
        chunks.append({
            "section": current_section,
            "subsection": current_subsection,
            "article": current_article,
            "text": "\n".join(buffer).strip()
        })

    return chunks

def process_pdf(pdf_path: str, source_name: str) -> List[Dict]:
    text = extract_text_from_pdf(pdf_path)
    article_chunks = split_by_articles(text)

    structured_chunks = []
    for idx, chunk in enumerate(article_chunks):
        structured_chunks.append({
            "chunk_id": idx,
            "source": source_name,
            "section": chunk["section"],
            "subsection": chunk["subsection"],
            "article": chunk["article"],
            "text": chunk["text"]
        })

    return structured_chunks

if __name__ == "__main__":
    path = "data/raw/circular_648.pdf"
    chunks = process_pdf(path, source_name="Circular SUSEP 648")
    for c in chunks[:2]:
        print(c["article"], c["section"], "\n", c["text"][:300], "\n---\n")
