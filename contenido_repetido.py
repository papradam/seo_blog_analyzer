import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
import re
from typing import List, Dict

def es_bloque_editorial(tag) -> bool:
    texto_total = tag.get_text(separator=" ", strip=True)
    if not texto_total or len(texto_total) < 100:
        return False

    num_p = len(tag.find_all('p'))
    num_h = len(tag.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
    if (num_p + num_h) < 2:
        return False

    hijos = tag.find_all(['div', 'section', 'article', 'main'])
    texto_hijos = " ".join(h.get_text(separator=" ", strip=True) for h in hijos)
    if len(texto_total) == 0 or (len(texto_hijos) / len(texto_total)) > 0.8:
        return False

    if len(texto_total) >= 300 or re.search(r'[.!?]', texto_total):
        return True

    palabras = texto_total.split()
    cortas = [w for w in palabras if len(w) < 3]
    return len(cortas) / len(palabras) <= 0.3

def extraer_bloques_editoriales(url: str) -> List[Dict[str, str]]:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        body = soup.body
        if not body:
            return []

        for tag in body.find_all(['nav', 'header', 'footer', 'head', 'script', 'style']):
            tag.decompose()

        bloques = []
        for tag in body.find_all(['div', 'section', 'article', 'main', 'span']):
            if not es_bloque_editorial(tag):
                continue

            bloques.append({
                "texto": tag.get_text(separator="\n", strip=True),
                "html": str(tag)
            })

        # Verificar si el h1 ya está incluido por texto
            # Verificar si cada h1 (en HTML) ya está incluido en los bloques
        for h1_tag in soup.find_all("h1"):
            h1_html = str(h1_tag)
            ya_incluido = any(h1_html in b["html"] for b in bloques)
            if not ya_incluido:
                bloques.insert(0, {
                    "texto": h1_tag.get_text(separator=" ", strip=True),
                    "html": h1_html
                })


        return bloques
    except:
        return []
