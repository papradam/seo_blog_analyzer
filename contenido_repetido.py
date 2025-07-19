import requests
from bs4 import BeautifulSoup, Tag
from rapidfuzz import fuzz
import re
from typing import List, Dict

ETIQUETAS_EXCLUIDAS = {'nav', 'header', 'footer', 'head', 'script', 'style'}

def es_bloque_editorial(tag: Tag) -> bool:
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

def limpiar_soup(soup: BeautifulSoup) -> BeautifulSoup:
    for tag in soup.find_all(ETIQUETAS_EXCLUIDAS):
        tag.decompose()
    return soup

def extraer_bloques_editoriales(url: str) -> List[Dict[str, str]]:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        body = soup.body
        if not body:
            return []

        soup = limpiar_soup(soup)
        bloques = []

        for tag in body.find_all(['div', 'section', 'article', 'main', 'span']):
            if es_bloque_editorial(tag):
                bloques.append({
                    "texto": tag.get_text(separator="\n", strip=True),
                    "html": str(tag)
                })

        # Verificamos si algún bloque ya contiene al menos una etiqueta <h1>
        bloque_con_h1 = any("<h1" in bloque["html"] for bloque in bloques)

        # Si no hay ningún <h1> en los bloques editoriales, los insertamos al inicio
        if not bloque_con_h1:
            for h1_tag in soup.find_all("h1"):
                h1_texto = h1_tag.get_text(separator=" ", strip=True)
                h1_html = str(h1_tag)
                bloques.insert(0, {
                    "texto": h1_texto,
                    "html": h1_html
                })


        return bloques

    except requests.RequestException as e:
        print(f"[ERROR] Fallo al acceder a la URL: {e}")
        return []

    except Exception as e:
        print(f"[ERROR] Error general en la extracción: {e}")
        return []
