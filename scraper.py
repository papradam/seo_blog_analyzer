# scraper.py (actualizado con avance por paginadores si pendientes está vacío)

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import re
import json

patron_paginacion = re.compile(r'(page[=/_-]?\d+|pagina[=/_-]?\d+|p[=/_-]?\d+|pag[=/_-]?\d+|/\d{1,3}/?)')
extensiones_invalidas = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip", ".rar")

CATEGORIAS = ["/categoria", "/category", "/temas", "/etiquetas", "/tag", "/archivo"]

def es_url_valida(url):
    try:
        resultado = urlparse(url)
        return resultado.scheme in ["http", "https"] and bool(resultado.netloc)
    except:
        return False

def normalizar_url(url):
    try:
        parsed = urlparse(url)
        clean = parsed._replace(query="", fragment="")
        return urlunparse(clean).rstrip('/').lower()
    except:
        return url.rstrip('/').lower()

def es_categoria(url):
    return any(cat in url for cat in CATEGORIAS)

def extraer_urls_articulos_controlado(url_base, max_articulos=10, pausado=False, urls_ya_evaluadas=None, urls_validas_actuales=None, paginadores_actuales=None):
    if urls_ya_evaluadas is None:
        urls_ya_evaluadas = set()
    if urls_validas_actuales is None:
        urls_validas_actuales = []
    if paginadores_actuales is None:
        paginadores_actuales = []

    urls_fuente = []
    urls_invalidas = []
    urls_paginadores = paginadores_actuales.copy()
    urls_por_paginador = {}
    urls_evaluadas = urls_ya_evaluadas.copy()
    articulos_validos = urls_validas_actuales.copy()

    pendientes = []
    candidatos_iniciales = []
    paginadores_usados = set()

    if not articulos_validos:
        pendientes.append(url_base)
        urls_evaluadas.add(normalizar_url(url_base))

    def es_contenido_valioso(url):
        return "blog" in url or url.endswith(".html") or "/" in url

    def evaluar_html_para_links(html, actual):
        nuevos = []
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            url = urljoin(actual, href)
            url_norm = normalizar_url(url)
            if url_norm not in urls_evaluadas:
                nuevos.append((url, url_norm))
        return nuevos

    def procesar_url(url_actual, origen):
        nuevos_articulos = 0
        try:
            response = requests.get(url_actual, timeout=10)
            response.raise_for_status()
            html = response.text
            urls_fuente.append(url_actual)
            links = evaluar_html_para_links(html, url_actual)

            for original, limpio in links:
                if pausado or len(articulos_validos) >= max_articulos:
                    break
                if limpio in urls_evaluadas:
                    continue
                urls_evaluadas.add(limpio)

                if any(limpio.endswith(ext) for ext in extensiones_invalidas):
                    urls_invalidas.append(original)
                    continue

                if not limpio.startswith(normalizar_url(url_base)):
                    urls_invalidas.append(original)
                    continue

                if patron_paginacion.search(limpio):
                    if limpio not in urls_paginadores:
                        urls_paginadores.append(limpio)
                    continue

                if es_categoria(limpio):
                    urls_invalidas.append(original)
                    continue

                pendientes.append(original)

            if origen == "paginador":
                urls_por_paginador[url_actual] = len(pendientes)

        except Exception as e:
            print(f"[ERROR] {url_actual}: {e}")
            urls_invalidas.append(url_actual)

    def analizar_url(url_original):
        if pausado or len(articulos_validos) >= max_articulos:
            return

        norm = normalizar_url(url_original)
        if norm in urls_evaluadas:
            return
        urls_evaluadas.add(norm)

        if patron_paginacion.search(norm):
            if norm not in urls_paginadores:
                urls_paginadores.append(norm)
            return

        if es_categoria(norm):
            urls_invalidas.append(url_original)
            return

        if len(candidatos_iniciales) < 3:
            candidatos_iniciales.append(url_original)
            return

        if es_contenido_valioso(norm):
            articulos_validos.append(url_original)
        else:
            urls_invalidas.append(url_original)

    # ▶ 1. Procesar URL inicial para recolectar enlaces
    if pendientes:
        procesar_url(pendientes[0], origen="blog")

    # ▶ 2. Evaluar URLs en pendientes
    while pendientes and len(articulos_validos) < max_articulos and not pausado:
        actual = pendientes.pop(0)
        analizar_url(actual)

    # ▶ 3. Evaluar candidatos iniciales si aún no hay suficientes válidos
    if len(articulos_validos) < max_articulos:
        for url in candidatos_iniciales:
            if pausado or len(articulos_validos) >= max_articulos:
                break
            if es_contenido_valioso(normalizar_url(url)):
                articulos_validos.append(url)
            else:
                urls_invalidas.append(url)

    # ▶ 4. Si no hay pendientes y faltan artículos, explorar paginadores uno a uno
    i = 0
    while len(articulos_validos) < max_articulos and i < len(urls_paginadores) and not pausado:
        pag = urls_paginadores[i]
        i += 1
        norm = normalizar_url(pag)
        if norm in paginadores_usados:
            continue
        paginadores_usados.add(norm)
        procesar_url(pag, origen="paginador")

        # Añadir nuevas a pendientes desde paginador
        while pendientes and len(articulos_validos) < max_articulos and not pausado:
            actual = pendientes.pop(0)
            analizar_url(actual)

    return {
        "articulos": articulos_validos,
        "fuente": urls_fuente,
        "invalidas": urls_invalidas,
        "paginadores": urls_paginadores,
        "por_paginador": urls_por_paginador,
        "evaluadas": urls_evaluadas
    }

def extraer_contenido_articulo(url_articulo):
    try:
        response = requests.get(url_articulo, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        titulo = soup.title.string.strip() if soup.title else ""
        h1 = [h.get_text().strip() for h in soup.find_all('h1')]
        h2 = [h.get_text().strip() for h in soup.find_all('h2')]

        parrafos_tags = soup.find_all('p')
        parrafos_texto = [p.get_text().strip() for p in parrafos_tags if p.get_text().strip()]
        parrafos_html = [str(p) for p in parrafos_tags if p.get_text().strip()]

        enlaces = [a['href'] for a in soup.find_all('a', href=True)]

        meta_description = soup.find("meta", attrs={"name": "description"})
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        canonical = soup.find("link", rel="canonical")

        imagenes = soup.find_all("img")
        alt_imagenes = [img.get("alt") for img in imagenes if img.get("alt")]

        schema_data = ""
        schema_scripts = soup.find_all("script", type="application/ld+json")
        for script in schema_scripts:
            try:
                parsed = json.loads(script.string)
                schema_data = parsed
                break
            except:
                continue

        return {
            "url": url_articulo,
            "titulo": titulo,
            "h1": h1,
            "h2": h2,
            "texto": "\n\n".join(parrafos_texto),
            "parrafos_html": parrafos_html,
            "enlaces": enlaces,
            "meta_description": meta_description.get("content") if meta_description else "",
            "meta_keywords": meta_keywords.get("content") if meta_keywords else "",
            "canonical": canonical.get("href") if canonical else "",
            "autor": "",
            "fecha": "",
            "alt_imagenes": alt_imagenes,
            "peso_imagenes_bytes": 0,
            "datos_estructurados": schema_data
        }

    except Exception as e:
        print(f"[ERROR] al analizar {url_articulo}: {e}")
        return {}
