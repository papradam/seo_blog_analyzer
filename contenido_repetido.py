# contenido_repetido.py

from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urlunparse
from difflib import SequenceMatcher

def normalizar_html(html):
    return ' '.join(html.strip().lower().split())

def es_similar(bloque1, bloque2, umbral=0.9):
    s = SequenceMatcher(None, normalizar_html(bloque1), normalizar_html(bloque2))
    return s.ratio() >= umbral

def extraer_bloques_html(url):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        # Eliminar bloques irrelevantes
        for etiqueta in ['nav', 'header', 'footer', 'head', 'script', 'style']:
            for tag in soup.find_all(etiqueta):
                tag.decompose()

        bloques = []
        for tag in soup.find_all(['div', 'section']):
            if tag.get_text(strip=True):  # Solo bloques con texto
                bloques.append(str(tag))
        return bloques
    except:
        return []

def detectar_bloques_comunes(urls):
    if len(urls) < 2:
        return []

    lista_bloques = [extraer_bloques_html(url) for url in urls]
    comunes = set()

    referencia = lista_bloques[0]
    for bloque in referencia:
        repeticiones = 0
        for otros in lista_bloques[1:]:
            if any(es_similar(bloque, b2) for b2 in otros):
                repeticiones += 1
        if repeticiones >= 1:
            comunes.add(bloque)
    return list(comunes)

def limpiar_contenido(texto, bloques_repetidos):
    for bloque in bloques_repetidos:
        if bloque in texto:
            texto = texto.replace(bloque, '')
    return texto

def extraer_texto_limpio(url, bloques_repetidos):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        html = res.text
        limpio = limpiar_contenido(html, bloques_repetidos)
        soup = BeautifulSoup(limpio, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    except:
        return ""
