import sqlite3
conn = sqlite3.connect('C:/Users/oscar/AI WORKBENCH/Pura Vida Puerto Viejo/pvscraper_full.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]
print('Tables:', tables)
for tbl in tables:
    c.execute(f'PRAGMA table_info("{tbl}")')
    cols = c.fetchall()
    print(f'\n{tbl} ({len(cols)} cols)')
    for col in cols:
        print(f'  {col[1]:30s} {col[2]}')
    c.execute(f'SELECT COUNT(*) FROM "{tbl}"')
    print(f'  Rows: {c.fetchone()[0]}')
    if 'business_name' in [col[1] for col in cols]:
        c.execute(f'SELECT business_name, instagram_handle FROM "{tbl}" WHERE instagram_handle IS NOT NULL AND instagram_handle != "" LIMIT 5')
        for row in c.fetchall():
            print(f'  IG: {row[0][:40]} -> {row[1]}')
