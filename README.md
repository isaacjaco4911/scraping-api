# Web Scraping API

[![Python](https://img.shields.io/badge/Python-3.9-3776ab?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup4-4.12-orange)](https://beautiful-soup-4.readthedocs.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

API REST construida con **FastAPI** que extrae datos estructurados de cualquier página web con un simple `POST`. Ideal para proyectos de data, automatización de contenido, monitoreo de precios, o como microservicio de scraping.

---

## Qué extrae

| Campo | Descripción |
|---|---|
| `title` | Título de la página (`<title>`) |
| `meta_description` | Meta descripción SEO |
| `headings` | H1 a H4 agrupados por nivel |
| `paragraphs` | Todos los párrafos de texto |
| `links` | URLs absolutas encontradas en la página |
| `images` | `src` y `alt` de cada imagen |
| `price` | Precio detectado (útil para e-commerce) |
| `status_code` | Código HTTP de la respuesta |
| `response_time_ms` | Tiempo de respuesta en milisegundos |
| `scraped_at` | Timestamp UTC del scraping |

---

## Cómo correr localmente

### 1. Clonar e instalar dependencias

```bash
git clone https://github.com/tu-usuario/scraping-api.git
cd scraping-api
pip install -r requirements.txt
```

### 2. Levantar el servidor

```bash
uvicorn app.main:app --reload
```

El servidor queda disponible en `http://localhost:8000`.
La documentación interactiva (Swagger UI) queda en `http://localhost:8000/docs`.

---

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Info y guía rápida de la API |
| `GET` | `/health` | Estado del servidor |
| `POST` | `/scrape` | Scrapea una URL y devuelve JSON |
| `GET` | `/docs` | Swagger UI (automático por FastAPI) |
| `GET` | `/redoc` | Documentación ReDoc |

---

## Ejemplos de uso

### Con curl

```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://quotes.toscrape.com"}'
```

### Con Python

```python
import requests

response = requests.post(
    "http://localhost:8000/scrape",
    json={"url": "https://quotes.toscrape.com"}
)
data = response.json()

print("Título:", data["title"])
print("Tiempo:", data["response_time_ms"], "ms")
print("Párrafos:", data["paragraphs"][:2])
print("Links:", data["links"][:3])
print("Imágenes:", data["images"][:2])
```

### Ejemplo de respuesta completa

```json
{
  "url": "https://quotes.toscrape.com/",
  "status_code": 200,
  "response_time_ms": 387.43,
  "title": "Quotes to Scrape",
  "meta_description": null,
  "headings": {
    "h1": ["Quotes to Scrape"],
    "h2": ["Top Ten tags"]
  },
  "paragraphs": [
    "“The world as we have created it is a process of our thinking.”",
    "“It is our choices, Harry, that show what we truly are, far more than our abilities.”"
  ],
  "links": [
    "https://quotes.toscrape.com/login",
    "https://quotes.toscrape.com/author/Albert-Einstein",
    "https://quotes.toscrape.com/tag/change/page/1/"
  ],
  "images": [
    {
      "src": "https://quotes.toscrape.com/static/img/logo.png",
      "alt": "Quotes to Scrape"
    }
  ],
  "price": null,
  "scraped_at": "2024-01-15T10:23:45.123456+00:00"
}
```

### E-commerce (detección de precio)

```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"}'
```

El campo `price` devuelve el precio detectado en la página (ej. `"£51.77"`).

---

## Stack

- **[FastAPI](https://fastapi.tiangolo.com)** — Framework web moderno con validación automática y docs integradas
- **[Uvicorn](https://www.uvicorn.org)** — Servidor ASGI de alto rendimiento
- **[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)** — Parser HTML/XML
- **[Requests](https://requests.readthedocs.io)** — Cliente HTTP
- **[Pydantic v2](https://docs.pydantic.dev)** — Validación y serialización de datos

---

## Deploy gratuito

### Railway

1. Ir a [railway.app](https://railway.app) y conectar el repositorio de GitHub
2. Railway detecta automáticamente el proyecto Python
3. Agregar como **Start Command**:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Render

1. Ir a [render.com](https://render.com), crear un **Web Service**
2. Conectar el repositorio de GitHub
3. Configurar:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Ambas plataformas ofrecen plan gratuito sin necesidad de tarjeta de crédito.

---

## Limitaciones conocidas

- Sitios con **JavaScript pesado** (SPAs React/Angular/Vue) devuelven el HTML estático sin renderizar — el scraping obtiene solo la estructura inicial
- Algunos sitios implementan **bloqueos avanzados** (Cloudflare, reCAPTCHA) que no se pueden bypasear con User-Agent
- Sin soporte para cookies de sesión, proxies o autenticación (fuera del alcance de este proyecto)

---

## Licencia

MIT
