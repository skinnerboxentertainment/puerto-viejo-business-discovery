"""
Open a Google Maps CID in Playwright and extract visible text content.
Usage: python paradisio_app/_maps_inspect.py [cid]
"""

import asyncio
import json
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Install playwright: pip install playwright && playwright install chromium")
    sys.exit(1)


async def inspect_cid(cid: str, biz_name: str = ""):
    url = f"https://www.google.com/maps?cid={cid}"
    print(f"Opening: {url}")
    print("(waiting up to 45s for Google Maps to load...)")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},
            locale="en-US",
        )
        page = await context.new_page()

        await page.goto(url, wait_until="commit", timeout=30000)
        await page.wait_for_timeout(5000)

        # Handle cookie consent dialog if present
        try:
            consent_btn = await page.wait_for_selector('button:has-text("Accept all"), button:has-text("Reject all"), button:has-text("Aceptar"), div[role="dialog"] button', timeout=3000)
            if consent_btn:
                await consent_btn.click()
                await page.wait_for_timeout(2000)
        except Exception:
            pass

        # Wait for content to stabilize
        try:
            await page.wait_for_selector('h1, [role="main"], [aria-label]', timeout=10000)
        except Exception:
            pass
        await page.wait_for_timeout(2000)

        # Screenshot
        screenshot_dir = Path("docs/paradisio_app/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        slug = biz_name.lower().replace(" ", "_")[:30] if biz_name else cid
        shot_path = screenshot_dir / f"maps_cid_{slug}.png"
        await page.screenshot(path=str(shot_path), full_page=False)
        print(f"Screenshot: {shot_path}")

        # Extract all visible text
        text = await page.evaluate("""
            () => {
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );
                let texts = [];
                let node;
                while (node = walker.nextNode()) {
                    const t = node.textContent.trim();
                    if (t.length > 2) {
                        const style = window.getComputedStyle(node.parentElement);
                        if (style.display !== 'none' && style.visibility !== 'hidden') {
                            texts.push(t);
                        }
                    }
                }
                return texts.join('\\n');
            }
        """)

        # Also get structured data if available
        structured = await page.evaluate("""
            () => {
                let scripts = document.querySelectorAll('script[type="application/ld+json"]');
                return Array.from(scripts).map(s => s.textContent).join('\\n');
            }
        """)

        await browser.close()

    # Write extracted text to a file (avoid unicode issues with console)
    out_path = screenshot_dir / f"maps_text_{slug}.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("=== VISIBLE TEXT ===\n")
        f.write(text)
        if structured:
            f.write("\n\n=== STRUCTURED DATA (JSON-LD) ===\n")
            f.write(structured)
    print(f"Extracted text: {out_path}")
    print(f"Text length: {len(text)} chars, JSON-LD: {len(structured)} chars")

    return text


if __name__ == "__main__":
    cid = sys.argv[1] if len(sys.argv) > 1 else "9649993079907777710"
    name = sys.argv[2] if len(sys.argv) > 2 else "Black Bamboo"
    asyncio.run(inspect_cid(cid, name))
