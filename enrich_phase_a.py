"""
Phase A: Enrich dataset from cached PVS HTML.
Extracts WhatsApp, email, other social links, and full description
from the raw HTML we already fetched.
"""

import csv
import json
import re
import sqlite3
from collections import Counter

INPUT_CSV = "pv_within_5km_verified.csv"
OUTPUT_CSV = "pv_within_5km_enriched_a.csv"
DB_PATH = "pvscraper_full.db"

SOCIAL_PLATFORMS = [
    ("tiktok", r"https?://(?:www\.)?tiktok\.com/@?[a-zA-Z0-9_.]+"),
    ("youtube", r"https?://(?:www\.)?youtube\.com/(?:c|channel|user|@)/[a-zA-Z0-9_-]+"),
    ("twitter", r"https?://(?:www\.)?(?:twitter|x)\.com/[a-zA-Z0-9_]+"),
    ("pinterest", r"https?://(?:www\.)?pinterest\.[a-z]+/[a-zA-Z0-9_]+"),
    ("linkedin", r"https?://(?:www\.)?linkedin\.com/(?:company|in)/[a-zA-Z0-9_-]+"),
]


def extract_whatsapp(html: str) -> list[str]:
    """Extract WhatsApp numbers from wa.me links."""
    numbers = []
    for m in re.finditer(r'wa\.me/(\d+)', html):
        num = m.group(1)
        if num not in numbers:
            numbers.append(num)
    return numbers


def extract_emails(html: str, exclude_domain: str = "puertoviejosatellite.com") -> list[str]:
    """Extract email addresses, excluding site-owner domain."""
    emails = []
    for m in re.finditer(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html):
        email = m.group(0)
        if exclude_domain not in email:
            if email not in emails:
                emails.append(email)
    return emails


def extract_social_links(html: str, platform_name: str, pattern: str) -> list[str]:
    """Extract URLs matching a social platform pattern."""
    urls = []
    for m in re.finditer(pattern, html, re.I):
        url = m.group(0)
        if url not in urls:
            urls.append(url)
    return urls


def extract_description(html: str) -> str | None:
    """Extract the listing description from the cached HTML.
    On PVS, the description is the text between the H1/business name
    and the 'Listing Details' heading."""
    # Look for text in a paragraph that's not breadcrumb, nav, or boilerplate
    desc_parts = []

    # Find the "Listing Details" heading
    ld_match = re.search(r'<h2[^>]*>Listing Details</h2>', html)
    if ld_match:
        # Get text between the breadcrumb area and listing details
        # Breadcrumb is in <p> before the H1. Description is typically
        # the paragraph after the breadcrumb/H1 area.
        # Find the H1 or business name text
        before_section = html[:ld_match.start()]

        # Extract paragraphs
        for m in re.finditer(r'<p>(.*?)</p>', before_section, re.DOTALL):
            text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            # Filter out breadcrumbs, nav text, and boilerplate
            if not text or len(text) < 15:
                continue
            if '>' in text or 'Hotels' in text or 'Restaurants' in text:
                continue  # breadcrumb
            if 'Huge thanks' in text or 'most complete' in text or 'contributors' in text:
                continue  # boilerplate footer
            if 'Esa página' in text or 'disponible' in text:
                continue  # translation notice
            desc_parts.append(text)

    return " ".join(desc_parts).strip() or None


def clean_phone_for_display(num: str) -> str:
    """Format a phone number for display."""
    if len(num) == 11 and num.startswith("506"):
        return f"+{num}"
    if len(num) == 12 and num.startswith("1"):
        return f"+{num}"
    return f"+{num}"


def main():
    # Load the current dataset
    with open(INPUT_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    print(f"Loaded {len(rows)} records", flush=True)

    # Connect to SQLite for cached HTML
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row

    # New columns to add
    new_cols = [
        "whatsapp", "email", "tiktok_url", "youtube_url",
        "twitter_url", "other_social_urls", "description_full",
    ]
    for col in new_cols:
        if col not in fieldnames:
            fieldnames.append(col)

    stats = Counter()
    total_with_html = 0

    for r in rows:
        url = r.get("url", "")
        if not url:
            continue

        # Fetch cached HTML
        row = db.execute(
            "SELECT html FROM raw_html_cache WHERE url = ?", (url,)
        ).fetchone()
        if not row:
            continue
        html = row["html"]
        total_with_html += 1

        # WhatsApp
        wa_numbers = extract_whatsapp(html)
        if wa_numbers:
            r["whatsapp"] = "; ".join(clean_phone_for_display(n) for n in wa_numbers)
            stats["whatsapp_found"] += 1

        # Emails
        emails = extract_emails(html)
        if emails:
            r["email"] = "; ".join(emails)
            stats["email_found"] += 1

        # Other social platforms
        found_socials = []
        for platform_name, pattern in SOCIAL_PLATFORMS:
            urls = extract_social_links(html, platform_name, pattern)
            if urls:
                col_name = f"{platform_name}_url"
                if col_name in new_cols:
                    r[col_name] = urls[0]
                    stats[f"{platform_name}_found"] += 1
                found_socials.extend(urls)

        if found_socials:
            r["other_social_urls"] = "; ".join(found_socials)

        # Description
        desc = extract_description(html)
        if desc:
            r["description_full"] = desc[:2000]
            stats["description_found"] += 1

    db.close()

    # Summary
    print(f"\nRecords with cached HTML: {total_with_html} of {len(rows)}", flush=True)
    print("\nEnrichment stats:", flush=True)
    for key, count in sorted(stats.items()):
        label = key.replace("_found", "").replace("_", " ").title()
        print(f"  {label}: {count}", flush=True)

    # Write enriched CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"\nWritten: {OUTPUT_CSV}", flush=True)

    # Quick sanity sample
    print("\nSample enriched records:", flush=True)
    enriched = [r for r in rows if r.get("whatsapp") or r.get("email")]
    for r in enriched[:5]:
        name = (r.get("business_name") or "?")[:40]
        wa = r.get("whatsapp", "-")
        em = r.get("email", "-")
        print(f"  {name:40s} WA={wa:20s} EM={em}")


if __name__ == "__main__":
    main()
