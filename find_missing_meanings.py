import csv
import re
from entries.models import Entry

missing = []
for e in Entry.objects.all():
    n = getattr(e, 'notes', '') or ''
    t = getattr(e, 'term', '') or ''
    if not n or '[traducción' in n or re.search(r'idiomatic|common phrase|slang term|colloquial|expression|chapter|see notes|no translation', n, re.I):
        missing.append((e.id, t, n))

with open('missing_meanings.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'TERM', 'NOTES'])
    writer.writerows(missing)

print(f"Wrote {len(missing)} entries to missing_meanings.csv")
