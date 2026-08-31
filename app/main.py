from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from .models import ScrapeRequest, ScrapeResponse
from .scraper import scrape_url

app = FastAPI(
    title="Web Scraping API",
    description="API REST para extraer datos estructurados de cualquier página web.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/", summary="Documentación de la API")
def root():
    return {
        "name": "Web Scraping API",
        "version": "1.0.0",
        "endpoints": {
            "POST /scrape": "Extrae título, párrafos, links, imágenes, headings y precio de una URL",
            "GET /health": "Verifica que el servidor está activo",
            "GET /docs": "Documentación interactiva (Swagger UI)",
            "GET /redoc": "Documentación alternativa (ReDoc)",
        },
        "example_request": {
            "method": "POST",
            "path": "/scrape",
            "body": {"url": "https://quotes.toscrape.com"},
        },
    }


@app.get("/health", summary="Health check")
def health():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/scrape", response_model=ScrapeResponse, summary="Scrapear una URL")
def scrape(request: ScrapeRequest):
    """
    Recibe una URL y devuelve los datos extraídos en JSON:
    título, meta descripción, headings (h1-h4), párrafos, links, imágenes y precio.
    """
    url = request.url.strip()

    if not url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=422,
            detail="La URL debe comenzar con http:// o https://",
        )

    try:
        return scrape_url(url)
    except TimeoutError as exc:
        raise HTTPException(status_code=408, detail=str(exc))
    except ConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {exc}")
