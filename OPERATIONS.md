# Educated Owl Books — Operations & Runbook

## 1. PostgreSQL Access

### Enter catalog DB
```bash
sudo -u postgres psql eob_catalog


Exit:

\q


List databases:

\l

2. Core Tables

book_isbn13_clean — canonical ISBN spine

book_metadata — enriched bibliographic data

3. Enrichment Script

Location:

/data/openlibrary/scripts/enrich_openlibrary.py


Python environment:

/var/www/educatedowlbooks.com/venv/bin/python3


Key config:

BATCH_SIZE = 1000
SLEEP_SECONDS = 3
LOG_FILE = "/data/openlibrary/logs/enrich.log"

4. Cron Job (Single-Instance Safe)

Crontab entry:

0 * * * * flock -n /tmp/eob_enrich.lock \
/var/www/educatedowlbooks.com/venv/bin/python3 \
/data/openlibrary/scripts/enrich_openlibrary.py \
>> /data/openlibrary/logs/cron.log 2>&1


Purpose:

Runs once per hour

Prevents overlap via flock

Safe if server restarts

5. Lock Handling

Check lock:

ls /tmp/eob_enrich.lock


Remove stale lock:

rm /tmp/eob_enrich.lock

6. Logs & Monitoring

Cron output:

tail -f /data/openlibrary/logs/cron.log


Check if script is running:

ps -o pid,lstart,cmd -C python3 | grep enrich_openlibrary


System monitoring:

htop
top

7. Ingestion Progress Queries (Common)

Total enriched:

SELECT COUNT(*) FROM book_metadata;


Remaining to enrich:

SELECT
  COUNT(*) AS total_isbns,
  COUNT(m.isbn13) AS enriched_isbns,
  COUNT(*) - COUNT(m.isbn13) AS remaining
FROM book_isbn13_clean s
LEFT JOIN book_metadata m USING (isbn13);


Latest enrichment timestamp:

SELECT
  COUNT(*) AS total,
  MAX(last_enriched) AS latest
FROM book_metadata;


Inspect recent rows:

SELECT *
FROM book_metadata
ORDER BY last_enriched DESC
LIMIT 10;

8. ISBN Validation Logic (Reference)
def is_valid_isbn13(isbn):
    if not isbn.isdigit() or len(isbn) != 13:
        return False
    if not (isbn.startswith("978") or isbn.startswith("979")):
        return False

    total = 0
    for i, d in enumerate(isbn[:12]):
        total += int(d) if i % 2 == 0 else int(d) * 3

    check = (10 - (total % 10)) % 10
    return check == int(isbn[-1])

9. Django / Web Ops

Local dev (Windows):

.\venv\Scripts\activate
python manage.py runserver


Production restart:

systemctl restart gunicorn
systemctl restart nginx


List gunicorn services:

systemctl list-units | grep gunicorn

10. Operational Philosophy

Never delete data automatically

Never overwrite enriched records

Cron jobs must be restart-safe

Slow ingestion is intentional

Logs > dashboards initially

11. Future Ops (Planned)

Commercial score computation job

Seller-driven visibility overrides

Optional external availability checks

Optional metrics export (Grafana later)

12. Emergency Checklist

If enrichment stops:

Check cron log

Check lock file

Verify venv Python path

Test script manually

Resume — no data loss possible

13. One-line Health Check
SELECT COUNT(*), MAX(last_enriched) FROM book_metadata;

