import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import re

def limpiar_url(url):
    try:
        parsed = urlparse(url)
        return urlunparse(parsed._replace(fragment="")).rstrip('/')
    except:
        return url.rstrip('/')

def obtener_enlaces_internos(url_fuente, url_base):
    urls = []
    try:
        res = requests.get(url_fuente, timeout=10)
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
    try:
        res = requests.get(url, timeout=10)
        codigo = res.status_code
        soup = BeautifulSoup(res.text, 'html.parser')

        canonicals = [link.get("href").strip() for link in soup.find_all("link", rel="canonical") if link.get("href")]

        meta_robots_tag = soup.find("meta", attrs={"name": "robots"})
        robots = meta_robots_tag['content'].lower() if meta_robots_tag and meta_robots_tag.get('content') else ''

        canonical_valida = any(limpiar_url(c) == limpiar_url(url) for c in canonicals)
        indexable = codigo == 200 and canonical_valida and 'noindex' not in robots and 'nofollow' not in robots

        return codigo, canonicals, robots, indexable

    except:
        return 0, [], '', False

def clasificar_tipo_pagina(url):
    url_lower = url.lower()
    url_path = urlparse(url_lower).path

    # Categorías comunes (añadido /user y /usuario)
    patrones_categoria = [
        r"/(categoria|categorias)/",
        r"/(category|categories)/",
        r"/tag[s]?/",
        r"/(user|usuario)/",
    ]

    patrones_paginador = [
        r"/(pag|page)/",
        r"[?&](pag|page)=\d+",
    ]

    for patron in patrones_categoria:
        if re.search(patron, url_path):
            return "categoria"

    for patron in patrones_paginador:
        if re.search(patron, url_path) or re.search(patron, url_lower):
            return "paginador"

    return "contenido"

