import re
import time
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .models import ImageData, ScrapeResponse

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

PRICE_PATTERNS = [
    r"\$\s*[\d,.]+",
    r"€\s*[\d,.]+",
    r"£\s*[\d,.]+",
    r"[\d,.]+\s*(?:USD|EUR|GBP|COP|MXN|ARS|BRL)",
]

PRICE_SELECTORS = [
    "[class*=price]",
    "[class*=Price]",
    "[id*=price]",
    "[data-price]",
    ".amount",
    ".cost",
    "[itemprop=price]",
]


def _extract_price(soup: BeautifulSoup) -> Optional[str]:
    for selector in PRICE_SELECTORS:
        el = soup.select_one(selector)
        if el:
            text = el.get_text(strip=True)
            for pattern in PRICE_PATTERNS:
                match = re.search(pattern, text)
                if match:
                    return match.group(0).strip()
    return None


def scrape_url(url: str) -> ScrapeResponse:
    start = time.time()

    try:
        response = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise TimeoutError("Request timed out after 10 seconds")
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Could not connect to {url}")
    except requests.exceptions.HTTPError as exc:
        raise ValueError(f"HTTP error: {exc}")
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"Request failed: {exc}")

    elapsed_ms = round((time.time() - start) * 1000, 2)
    final_url = str(response.url)

    soup = BeautifulSoup(response.text, "html.parser")

    # Title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    # Meta description
    meta_desc: Optional[str] = None
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag:
        content = meta_tag.get("content", "").strip()
        meta_desc = content or None

    # Headings h1–h4
    headings: dict = {}
    for level in range(1, 5):
        texts = [t.get_text(strip=True) for t in soup.find_all(f"h{level}") if t.get_text(strip=True)]
        if texts:
            headings[f"h{level}"] = texts

    # Paragraphs (non-empty)
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]

    # Links — absolute, deduplicated, skip anchors/js/mailto/tel
    seen: set = set()
    links: list = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        absolute = href if href.startswith("http") else urljoin(final_url, href)
        if absolute not in seen:
            seen.add(absolute)
            links.append(absolute)

    # Images — absolute src + alt
    images: list = []
    for img in soup.find_all("img"):
        src = img.get("src", "").strip()
        if not src:
            continue
        if not src.startswith("http"):
            src = urljoin(final_url, src)
        images.append(ImageData(src=src, alt=img.get("alt", "").strip()))

    # Price (e-commerce)
    price = _extract_price(soup)

    return ScrapeResponse(
        url=final_url,
        status_code=response.status_code,
        response_time_ms=elapsed_ms,
        title=title,
        meta_description=meta_desc,
        headings=headings,
        paragraphs=paragraphs,
        links=links,
        images=images,
        price=price,
        scraped_at=datetime.now(timezone.utc).isoformat(),
    )
