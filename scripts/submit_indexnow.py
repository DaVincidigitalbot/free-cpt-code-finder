#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path('/home/setup/Desktop/FreeCPTCodeFinder')
HOST = 'freecptcodefinder.com'
KEY = '5f3c8a91d7e24b6fa0c935b12d8e4f607a9c1b3d5e6f708192a4b6c8d0e1f234'
KEY_LOCATION = f'https://{HOST}/indexnow-key.txt'
ENDPOINT = 'https://api.indexnow.org/indexnow'

def sitemap_urls(limit: int | None = None) -> list[str]:
    ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    root = ET.parse(ROOT / 'sitemap.xml').getroot()
    urls = [loc.text for loc in root.findall('.//sm:loc', ns) if loc.text]
    return urls[:limit] if limit else urls

def submit(urls: list[str]) -> tuple[int, str]:
    payload = {
        'host': HOST,
        'key': KEY,
        'keyLocation': KEY_LOCATION,
        'urlList': urls,
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={'Content-Type': 'application/json; charset=utf-8'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode('utf-8', errors='replace')

def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    urls = sitemap_urls(limit)
    code, body = submit(urls)
    print(json.dumps({'status': code, 'submitted': len(urls), 'body': body}, indent=2))
    if code not in {200, 202}:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
