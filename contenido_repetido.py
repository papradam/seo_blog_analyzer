import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from rapidfuzz import fuzz

def normalizar_texto(texto):
    return ' '.join(texto.strip().lower().split())

def es_similar_texto(texto1, texto2, umbral=96):
    score = fuzz.token_set_ratio(normalizar_texto(texto1), normalizar_texto(texto2))
    return score >= umbral

def extraer_bloques_html(url):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        # Eliminar bloques por clase o id irrelevantes
        selectores_excluir = [
            '[class*="sidebar"]', '[class*="ads"]', '[class*="popup"]',
            '[class*="cookie"]', '[class*="newsletter"]',
            '[id*="sidebar"]', '[id*="ads"]', '[id*="popup"]',
            '[id*="cookie"]', '[id*="newsletter"]',
        ]
        for selector in selectores_excluir:
            for tag in soup.select(selector):
                tag.decompose()

        # Etiquetas internas que invalidan un bloque completo
        etiquetas_prohibidas = ['nav', 'header', 'footer', 'script', 'style', 'head']

        bloques = []
        for tag in soup.find_all(['div', 'section', 'article', 'main', 'aside']):
            if not tag.get_text(strip=True):
                continue
            if any(tag.find(et) for et in etiquetas_prohibidas):
                continue
            bloques.append(tag)  # Guardamos el bloque completo (Tag)

        return bloques
    except:
        return []

def detectar_bloques_comunes(urls, n_docs=2):
    if len(urls) < 2:
        return []

    lista_bloques = [extraer_bloques_html(url) for url in urls]
    frecuencia = {}

    for bloques in lista_bloques:
        for tag in bloques:
            texto = tag.get_text(separator=' ', strip=True)
            clave_existente = None
            for clave in frecuencia:
                if es_similar_texto(texto, clave):
                    clave_existente = clave
                    break
            if clave_existente:
                frecuencia[clave_existente] += 1
            else:
                frecuencia[texto] = 1

    comunes = [bloque for bloque, rep in frecuencia.items() if rep >= n_docs]
    return comunes

def extraer_texto_limpio(url, bloques_repetidos, umbral=96):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        for tag in soup.find_all(['div', 'section', 'article', 'main', 'aside']):
            if not tag.get_text(strip=True):
                continue

            # No eliminar si contiene un h1 (título principal)
            if tag.find('h1'):
                continue

            texto_bloque = tag.get_text(separator=' ', strip=True)
            for repetido in bloques_repetidos:
                if es_similar_texto(texto_bloque, repetido, umbral=umbral):
                    tag.decompose()
                    break

        return soup.get_text(separator=' ', strip=True)
    except:
        return ""
