"""Tag Instagram handles from the guessing pass with enrich_source=handle_guess."""
import csv
from datetime import date

today = str(date.today())

with open('pv_master_unified.csv', encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

tagged = 0
for row in rows:
    handle = (row.get('instagram_handle') or '').strip()
    source = (row.get('instagram_enrich_source') or '').strip()
    if handle and not source:
        row['instagram_enrich_source'] = 'handle_guess'
        row['instagram_enrich_date'] = today
        row['instagram_enrich_confidence'] = 'low'
        row['ig_verified'] = 'false'
        tagged += 1

with open('pv_master_unified.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

print(f'Tagged {tagged} guessed handles')
