"""
Test httpx on Maps CID URLs to see what data is available server-side (no browser).
"""

import json
import re
import time
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Install httpx: pip install httpx")
    exit(1)

CIDS = [
    ("9649993079907777710", "Black Bamboo"),
    ("5872176730909991811", "Amimodo Beach Rooms"),
    ("1614163454683628928", "Bungalows Calalu"),
    ("4732141069441829785", "Gigi O Restaurant"),
]

EXTRACT_PATTERNS = {
    "rating": r'"ratingValue"[^"]*"([^"]+)"',
    "name": r'"name"\s*:\s*"([^"]+)"',
    "telephone": r'"telephone"\s*:\s*"([^"]+)"',
    "address": r'"streetAddress"\s*:\s*"([^"]+)"',
    "priceRange": r'"priceRange"\s*:\s*"([^"]+)"',
    "servesCuisine": r'"servesCuisine"\s*:\s*"([^"]+)"',
    "openingHours": r'"openingHoursSpecification"',
}


def try_fetch(cid, name):
    url = f"https://www.google.com/maps?cid={cid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    print(f"\n=== {name} (CID {cid}) ===")
    try:
        resp = httpx.get(url, headers=headers, follow_redirects=True, timeout=15)
        print(f"Status: {resp.status_code}, Size: {len(resp.text)} bytes")

        # Check for JSON-LD (structured data in script tags)
        ld_json = re.findall(r'<script type="application/ld\+json">(.*?)</script>', resp.text, re.DOTALL)
        if ld_json:
            for i, ld in enumerate(ld_json):
                try:
                    data = json.loads(ld)
                    print(f"  JSON-LD [{i}]: {json.dumps(data, indent=2)[:500]}")
                except json.JSONDecodeError:
                    print(f"  JSON-LD [{i}]: (parse error, raw length {len(ld)})")
        else:
            print(f"  No JSON-LD found")

        # Check for og/meta tags
        og_title = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', resp.text)
        if og_title:
            print(f"  OG Title: {og_title.group(1)}")
        og_desc = re.search(r'<meta\s+property="og:description"\s+content="([^"]+)"', resp.text)
        if og_desc:
            print(f"  OG Desc: {og_desc.group(1)[:100]}")

        # Check for any inline data
        for key, pattern in EXTRACT_PATTERNS.items():
            match = re.search(pattern, resp.text, re.IGNORECASE)
            if match:
                val = match.group(1) if match.groups() else "found"
                print(f"  {key}: {val}")

        # Check response URL (Google may redirect)
        if str(resp.url) != url:
            print(f"  Redirected to: {resp.url}")

    except httpx.TimeoutException:
        print(f"  Timeout")
    except Exception as e:
        print(f"  Error: {e}")


for cid, name in CIDS:
    try_fetch(cid, name)
    time.sleep(2)
