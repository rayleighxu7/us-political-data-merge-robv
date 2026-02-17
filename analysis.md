[1 tool called]

The file is quite large (over 200MB). Let me create a Python script to analyze it for anomalies and outliers.

[2 tools called]

Now I can see the structure. Let me create a Python script to analyze the large CSV file for anomalies, outliers, and data issues.

[1 tool called]

The file has over 1.4 million rows. Let me create a comprehensive analysis script:

[2 tools called]

Let me fix the encoding issue by removing emojis:

[6 tools called]

The file shows the source file distribution. Let me read from the beginning to get the main analysis results:

[2 tools called]

Now let me get the end of the analysis with the duplicate and consistency checks:

[1 tool called]

I have most of the key findings. Let me fix the encoding issue and get the final summary:

[2 tools called]

Now I have the complete analysis. Let me clean up the analysis script and provide you with a comprehensive summary of all the findings.

## Data Quality Analysis Report for `csv_outputs/cleaned_data_2025-12-05.csv`

### Basic Statistics
- **Total Rows:** 1,476,203
- **Total Columns:** 75
- **Unique Source Files:** 1,796

---

### 🔴 Critical Issues

#### 1. **High Missing Data (43 columns with >90% missing)**
| Column | Missing % |
|--------|-----------|
| `veteran_in_household` | 99.73% |
| `county_supervisorial_district` | 99.39% |
| `company_sales_volume_range` | 99.36% |
| `state_legislative_district` | 99.36% |
| `county_commissioner_district` | 99.28% |
| `household_net_worth` | 98.93% |
| `primary_2024` | 98.66% |
| `cuisine_code` / `cuisine_code_description` | 98.58% |
| `landline_phone` | 98.37% |
| `company_founded_at` | 97.65% |
| `voting_performance_*` columns | 95-96% |
| `home_city`, `home_state`, `home_address`, `home_zipcode` | 90-95% |

#### 2. **Duplicate Emails - MAJOR ISSUE**
- **296,568 unique emails** appear multiple times
- **531,658 total rows** have duplicate emails
- Most duplicated: `jmiller@milleraa.com` (13 times), `sam@liquidperformance.com` (12 times)

#### 3. **Potential Duplicate Records**
- **800,117 rows** share the same `email + first_name + last_name + company_name` combination
- No exact duplicate rows (which is good)
- No duplicate `record_id` values (good)

---

### 🟠 Moderate Issues

#### 4. **Name Field Anomalies**
| Issue | Count | Examples |
|-------|-------|----------|
| First names with numbers/special chars | 194 | `2l`, `Josa?`, `A3`, `Herna?N` |
| Single character first names | 2,805 | `J` (559), `R` (257), `M` (209) |
| First names > 30 chars | 3 | `Dr. Leonie H. Mattison (Dr. Lee)` |
| Last names with numbers/special chars | 327 | `& Emilio`, `3dpx`, `Gardua?O` |

#### 5. **Invalid Email Formats (279 records)**
Examples of malformed emails:
- `cchrchris@24hrdraincleaning.comis@24hrdraincleaning.comhris@24hrdraincleaning.com` (concatenated)
- `contact@360hvacpro.com\r` (carriage return)
- `contact@aaa-plumbers. com` (space in domain)
- `danl'herbier@airductmaintenance.com` (apostrophe)
- `contact@amcplumbing&leakdetection.com` (& in domain)

#### 6. **Phone Number Issues**
| Column | Issue | Count |
|--------|-------|-------|
| work_phone | < 10 digits | 123 |
| work_phone | > 15 digits | 4 |
| mobile_phone | < 10 digits | 7 |

#### 7. **Address/Location Anomalies**
- **117 non-standard company_state values**: `Oklahoma City` (66), `Idaho Falls` (9), `Kansas City` (3) - cities stored as states
- **303 non-US zipcodes**: `OX28 4LE`, `M9M 1M3`, `T4S 2H2` (UK/Canadian formats)
- **7 zipcodes with wrong length**: `7322018335` (10 digits)

---

### 🟡 Minor Issues

#### 8. **URL Formatting**
| Field | Missing http/https | Examples |
|-------|-------------------|----------|
| company_website | 445,574 | `corporatedirectories.com`, `1choiceinc.com` |
| facebook | 32,286 | `www.facebook.com/andinsurance/` |
| twitter | 41,938 | `twitter.com/and_digital` |
| company_linkedin | 196 | `linkedin.com/company/aamco` |

#### 9. **Encoding Issues (Special Characters)**
- **first_name**: 36 records with encoding issues
- **last_name**: 87 records
- **company_name**: 872 records with `Ã`, `Â`, or `â€` characters
- **job_title**: 89 records

#### 10. **Sales Volume Data Format**
- `company_sales_volume_actual` and `location_sales_volume_actual` contain **420,274 values formatted as strings** with `$` and commas (e.g., `$3,820,000`) instead of numeric

#### 11. **Industry Inconsistency**
- `Construction` (95,530) and `construction` (13,765) are stored separately due to case difference

---

### ✅ Data Quality Wins

- **No exact duplicate rows**
- **No duplicate record_ids**
- **Age range valid**: Min 18, Max 100, Mean 54.2
- **No negative employee counts**
- **Gender values clean**: Only `M` (373,556) and `F` (118,308)
- **Home state values are standardized** (0 non-standard)
- **Home zipcodes are valid format**

---

### 📊 Source File Distribution (Top 10)

| Source File | Records |
|-------------|---------|
| www.csv | 157,290 |
| Rob Volmer Project master File - 157k RX ADJUSTED.csv | 144,087 |
| Combined Master File 2_1 | 115,290 |
| allin1match file no 2 - Sheet1.csv | 109,288 |
| Rob Master Sheet (Updated).csv | 106,238 |
| _Rob Master Sheet (190K).csv | 92,855 |
| Zoominfo scarping.xlsx - Texas.csv | 56,399 |
| Zoominfo scraping list 2 - Florida.csv | 28,975 |
| Zoominfo scraping 3 - Pennsylvania.csv | 22,598 |
| Zoominfo scarping.xlsx - North Carolina.csv | 19,486 |

Plus **1,558 state-level files** (250 records each from states like Florida, Texas, Ohio, Michigan, etc.)

---

### Recommendations

1. **Deduplicate by email** - 36% of rows share emails with other records
2. **Standardize company_state** - Move city values to correct column
3. **Clean sales volume columns** - Convert to numeric format
4. **Fix email formats** - Remove carriage returns, fix malformed addresses
5. **Normalize industry names** - Standardize casing
6. **Add http:// prefix to URLs** where missing
7. **Consider dropping columns with >95% missing** if not needed