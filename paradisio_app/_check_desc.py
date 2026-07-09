import sqlite3
conn = sqlite3.connect('C:/Users/oscar/AI WORKBENCH/Pura Vida Puerto Viejo/pvscraper_full.db')
c = conn.cursor()

# How many have non-empty descriptions?
c.execute("SELECT COUNT(*) FROM listings WHERE description IS NOT NULL AND description != ''")
count = c.fetchone()
print(f'Listings with description: {count[0]} out of 593')

# Show some samples
c.execute("SELECT business_name, description FROM listings WHERE description IS NOT NULL AND description != '' LIMIT 10")
for r in c.fetchall():
    d = r[1]
    print(f'\n--- {r[0]} ---')
    print(d[:300])
    if len(d) > 300:
        print(f'... ({len(d)} total chars)')

# Check description length distribution
c.execute("SELECT MIN(LENGTH(description)), AVG(LENGTH(description)), MAX(LENGTH(description)) FROM listings WHERE description IS NOT NULL AND description != ''")
mn, avg, mx = c.fetchone()
print(f'\n\nDescription lengths: min={mn}, avg={avg:.0f}, max={mx}')
conn.close()
