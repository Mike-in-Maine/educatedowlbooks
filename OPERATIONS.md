# Educated Owl Books — Architecture Overview

## 1. Purpose

Educated Owl Books (EOB) is a multi-seller book marketplace.

Core design goals:
- Ingest *everything*
- Surface *only sellable books*
- Separate **data ingestion** from **commercial viability**
- Allow slow, resumable enrichment over months

---

## 2. High-level Architecture

Data flow:

Open Library Dumps
→ ISBN Canonicalization
→ PostgreSQL ISBN Spine
→ Slow API Enrichment (cron)
→ book_metadata
→ Seller listings & scoring
→ Frontend search & listings

---

## 3. Data Sources

### Open Library
- **Bulk dumps** (editions)
- **Public API** (enrichment)
- Treated as authoritative bibliographic source

Contains:
- Commercial books
- Government documents
- Pamphlets
- Maps
- Internal publications

➡️ All are ingested, none are deleted automatically.

---

## 4. Canonical ISBN Strategy

### Canonical key: ISBN-13

Rules:
- Must be numeric
- Length = 13
- Must start with `978` or `979`
- Must pass ISBN-13 checksum

Pseudo-ISBNs:
- Many institutional publishers use technically valid but non-commercial ISBNs
- These are **kept**, not filtered at ingestion time

Reason:
> Commercial filtering is a *business concern*, not a data concern.

---

## 5. Core Tables

### `book_isbn13_clean`
Canonical ISBN spine:
- isbn13 (canonical)
- isbn10 (may be malformed)
- edition_key (OL)
- work_key (OL)

Purpose:
- Stable universe of books
- Never rewritten
- Never enriched directly

---

### `book_metadata`
Enriched bibliographic data:
- isbn13 (PK)
- title
- author
- publisher
- publish_year
- cover_url
- source
- last_enriched

Purpose:
- Incremental enrichment
- Safe restarts
- Partial population allowed

---

## 6. Enrichment Philosophy

- Slow by design
- Resume-safe
- Never overwrite existing rows
- API-polite
- Cron-driven

Throughput target:
- ~20–25k books/day
- Full corpus over time, not immediately

---

## 7. Commercial Viability (Future Layer)

Books are **not deleted** if unsellable.

Instead:
- Every book will receive a **commercial score**
- Only books above threshold appear in search

Example scoring factors:
- + Amazon presence
- + AbeBooks presence
- + Multiple sellers
- + Cover image
- − Institutional publisher
- − Pamphlet-like metadata

Seller listings always override score:
> If a seller lists it, it is sellable.

---

## 8. Separation of Concerns

| Layer | Responsibility |
|-----|---------------|
| Ingestion | Collect everything |
| Canonicalization | Normalize identifiers |
| Enrichment | Bibliographic truth |
| Scoring | Commercial relevance |
| Listings | Actual sellability |
| UI | Visibility & search |

This separation allows:
- Long-running ingestion
- Independent UI development
- Later optimization without data loss

---

## 9. Current State

- ~29M ISBNs ingested
- ~25k+ enriched and growing
- Cron enrichment running hourly
- UI not yet consuming metadata directly

---

## 10. Guiding Principle

> **Data is cheap. Curation is expensive.  
> Ingest first. Decide later.**
