import sqlite3
conn = sqlite3.connect('C:/Users/oscar/AI WORKBENCH/Pura Vida Puerto Viejo/pvscraper_full.db')
c = conn.cursor()

# Check review-related columns
c.execute('SELECT rating, description, price_range FROM listings WHERE rating IS NOT NULL LIMIT 5')
rows = c.fetchall()
print('Listings with ratings:')
for r in rows:
    print(f'  rating={r[0]} desc={r[1][:80] if r[1] else None} price={r[2]}')

# Count non-null ratings
c.execute('SELECT COUNT(*) FROM listings WHERE rating IS NOT NULL')
print(f'\nListings with rating: {c.fetchone()[0]}')

# Check cached HTML for review data
c.execute('SELECT url, html FROM raw_html_cache WHERE url LIKE "%chinuk%" LIMIT 1')
row = c.fetchone()
if row:
    html = row[1]
    print(f'\nCached page: {row[0]}')
    print(f'HTML size: {len(html)} bytes')
    keywords = ['review', 'testimonial', 'reseña', 'opinion', 'comentario', 'rating', 'estrell']
    for kw in keywords:
        print(f'  "{kw}": {html.lower().count(kw.lower())}')

# Check description field content for review-like text
c.execute('SELECT business_name, description FROM listings WHERE description LIKE "%review%" OR description LIKE "%rating%" LIMIT 5')
rows = c.fetchall()
print(f'\nListings with review mentions in description:')
for r in rows:
    print(f'  {r[0][:40]}: {r[1][:100] if r[1] else "null"}')

conn.close()
