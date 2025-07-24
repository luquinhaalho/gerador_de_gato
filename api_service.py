# api_service.py

import requests
from urllib.parse import quote
from config import CAT_API_URL_BASE, TAGS_API_URL

def fetch_tags():
    """Busca a lista de tags da API."""
    print(f"Buscando tags de: {TAGS_API_URL}")
    response = requests.get(TAGS_API_URL, timeout=10)
    response.raise_for_status()  # Lança um erro se a requisição falhar
    return ["Aleatório"] + response.json()

def build_image_url(tag, text, size, color):
    """Constrói a URL final da imagem com base nos filtros fornecidos."""
    path_parts = [f"{CAT_API_URL_BASE}/cat"]
    query_params = {}

    if tag and tag != "Aleatório":
        path_parts.append(tag)

    if text:
        path_parts.append("says")
        path_parts.append(quote(text))
        
        if size: query_params['fontSize'] = size
        if color: query_params['fontColor'] = color
    
    image_url = "/".join(path_parts)
    
    if query_params:
        query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
        image_url += f"?{query_string}"
    
    return image_url

def fetch_image_data(url):
    """Busca os dados de uma imagem a partir de uma URL final."""
    print(f"URL Final: {url}")
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.content