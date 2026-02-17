# US Political Data Merge

> **AI Summary:** Python-based ETL project for merging and deduplicating over 1 million records from multiple Excel/CSV sources using deterministic and fuzzy matching, with company name standardization and US political voter data integration.

⚠️ **Note:** Data files are not committed due to PII reasons.

---

## Project Overview

### Upwork Job Description

**Fixed-Price Project:** Merge & Deduplicate 750K+ Person Records from Many Excel/CSV Files into One Master Dataset

### Description

I have numerous Excel and CSV files containing overlapping information on individuals. Across all files there are more than 750,000 person-level records, many referring to the same individuals but with different data fields populated — addresses, phone numbers, emails, businesses, social handles, voter or consumer details, etc.

Some people appear in several files. The goal is to combine all data about each person into one clean, unified record — one row per person with every available data point consolidated.

---

## Scope of Work

- Ingest and normalize all source files (different headers, field names, and formats)
- Identify and merge duplicate records using both:
  - **Deterministic matching** (exact name/address/email/phone matches)
  - **Fuzzy or probabilistic matching** for near-matches
- Standardize and unify field names across all sources
- Retain all unique information while removing duplicate or conflicting entries
- Deliver a master dataset (CSV or SQL) with consistent field naming and one record per person
- Provide light documentation or a script (Python or SQL) describing how the merge and deduplication were performed

---

## Deliverables

1. Final cleaned and deduplicated master dataset
2. Field-mapping dictionary (old → standardized column names)
3. Brief documentation or reproducible script for future merges

---

## Requirements

- Proven experience merging and deduplicating large multi-file datasets (500K+ rows)
- Expertise with Python (Pandas, Dedupe, RecordLinkage, or FuzzyWuzzy) or SQL-based ETL pipelines
- Strong understanding of record linkage, fuzzy matching, and data normalization
- Ability to handle inconsistent schemas and many input files

### Screening Questions

1. Describe a project where you merged and deduplicated 100K+ records from multiple files using deterministic and fuzzy matching.
2. How would you design your matching logic so all data for each person is preserved across many files?
3. What is your fixed-price estimate for this scope (750K+ records, many files)?
4. Will you provide a reusable Python or SQL process for future merges?

---

## Additional Work

- Review, clean and merge + deduplicate 19 state files provided by Sasha
- Generate file with missing voter data
- Review returned voter data, clean and merge + deduplicate
- Review additional church data, clean and merge in with NAICS code 813110
- Report on all company names that do not exist in Sasha files

---

## References

**Upwork Job IDs:**
- ID 42517878
- ID 42168194
