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

def extraer_bloques_editoriales(url: str) -> List[str]:
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

        h1_text = soup.find('h1').get_text(strip=True) if soup.find('h1') else ""
        bloques = []

        for tag in body.find_all(['div', 'section', 'article', 'main', 'span']):
            if not es_bloque_editorial(tag):
                continue

            texto = tag.get_text(separator="\n", strip=True)
            if h1_text and h1_text not in texto:
                texto = h1_text + "\n" + texto
            bloques.append(texto)
        return bloques
    except:
        return []

def extraer_bloques_variables(urls: List[str], umbral_similitud: int = 90) -> Dict[str, List[str]]:
    if len(urls) != 3:
        raise ValueError("Esta función requiere exactamente 3 URLs.")

    bloques_por_url = {url: extraer_bloques_editoriales(url) for url in urls}

    # Comparar por contenido, no por clave
    repetidos = set()
    for i in range(len(urls)):
        for j in range(i + 1, len(urls)):
            for b1 in bloques_por_url[urls[i]]:
                for b2 in bloques_por_url[urls[j]]:
                    if fuzz.token_set_ratio(b1, b2) >= umbral_similitud:
                        repetidos.add(b1)
                        repetidos.add(b2)

    resultado = {}
    for url in urls:
        resultado[url] = [b for b in bloques_por_url[url] if b not in repetidos]

    return resultado
