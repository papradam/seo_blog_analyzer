import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs
import re

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def limpiar_url(url):
    """Elimina fragmentos y barras finales innecesarias."""
    try:
        parsed = urlparse(url)
        return urlunparse(parsed._replace(fragment="")).rstrip('/')
    except:
        return url.rstrip('/')

def obtener_enlaces_internos(url_fuente, url_base):
    """Extrae enlaces internos desde una página."""
    urls = []
    try:
        res = requests.get(url_fuente, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        for tag in soup.find_all('a', href=True):
            href = tag['href']
            absoluta = urljoin(url_fuente, href)
            if absoluta.startswith(url_base):
                urls.append(absoluta)
        return list(set(urls))
    except:
        return []

def analizar_indexabilidad(url):
    """
    Evalúa si la página es indexable:
    - Código 200
    - No contiene 'noindex' ni 'nofollow'
    - Canonical válida si existe (pero no se exige tenerla)
    """
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        codigo = res.status_code

        soup = BeautifulSoup(res.text, 'html.parser')

        # Obtener canonicals (puede estar vacío)
        canonicals = [link.get("href").strip() for link in soup.find_all("link", rel="canonical") if link.get("href")]

        # Obtener meta robots
        meta_robots_tag = soup.find("meta", attrs={"name": "robots"})
        robots = meta_robots_tag.get('content', '').lower() if meta_robots_tag else ''

        # Evaluar canonical (si hay)
        canonical_valida = True
        if canonicals:
            canonical_valida = any(limpiar_url(c) == limpiar_url(url) for c in canonicals)

        # Evaluar indexabilidad
        indexable = codigo == 200 and canonical_valida and 'noindex' not in robots and 'nofollow' not in robots

        return codigo, canonicals, robots, indexable

    except:
        return 0, [], '', False

def clasificar_tipo_pagina(url):
    """Clasifica la URL como categoría, paginador o contenido."""
    url_lower = url.lower()
    parsed = urlparse(url_lower)
    url_path = parsed.path
    query_params = parse_qs(parsed.query)

    palabras_categoria = [
        "categoria", "categorias", "category", "categories",
        "tag", "tags", "user", "usuario", "search", "buscar"
    ]

    patrones_paginador = [
        r"/(pag|page)/",
        r"[?&](pag|page)=\d+",
    ]

    for palabra in palabras_categoria:
        if re.search(rf"{palabra}", url_path):
            return "categoria"

    for param in query_params.keys():
        for palabra in palabras_categoria:
            if palabra in param:
                return "categoria"

    for patron in patrones_paginador:
        if re.search(patron, url_lower):
            return "paginador"

    return "contenido"
