"""
Company Name Cleaning and Deduplication Script
This script cleans company names and identifies duplicates/similar entries.
"""

import pandas as pd
import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher
import csv
import json
import os

# ============================================================================
# STEP 1: Encoding Fixes - Map corrupted characters to their proper form
# ============================================================================
ENCODING_FIXES = {
    '┬«': '®',
    'Γהó': '™',
    'Γפ¼┬½': '®',
    '??ó': '™',
    '?«': '®',
    '?�': '®',
    '??': '®',
    '├⌐': 'é',
    '├ה': 'Ä',
    'Γאכ': '™',
    'Γאª': '™',
    '≡ƒתנ': '',  # Emoji artifacts - remove
    '≡ƒף╢': '',  # Emoji artifacts - remove
    '┐': '',
    '├': '',
    'Â®': '®',  # Encoded trademark
    'Â': '',  # Stray encoding artifact
    '��': '®',
    '�': '',
    '\xa0': ' ',  # Non-breaking space
    '\u200b': '',  # Zero-width space
}

# ============================================================================
# STEP 2: Legal Suffix Standardization
# ============================================================================
LEGAL_SUFFIXES = {
    # Variations of Inc/Incorporated
    r'\bInc\.?\b': 'Inc',
    r'\bIncorporated\b': 'Inc',
    r'\bINCORPORATED\b': 'Inc',
    r'\bINC\b': 'Inc',
    
    # Variations of LLC
    r'\bL\.?L\.?C\.?\b': 'LLC',
    r'\bLimited Liability Company\b': 'LLC',
    r'\bLimited Liability Co\.?\b': 'LLC',
    
    # Variations of Corp/Corporation
    r'\bCorp\.?\b': 'Corp',
    r'\bCorporation\b': 'Corp',
    r'\bCORPORATION\b': 'Corp',
    r'\bCORP\b': 'Corp',
    
    # Variations of Ltd/Limited
    r'\bLtd\.?\b': 'Ltd',
    r'\bLimited\b': 'Ltd',
    r'\bLIMITED\b': 'Ltd',
    
    # Variations of Co/Company
    r'\bCo\.?\b(?!\.)': 'Co',
    r'\bCompany\b': 'Co',
    r'\bCOMPANY\b': 'Co',
    
    # Professional designations
    r'\bP\.?C\.?\b': 'PC',
    r'\bP\.?L\.?L\.?C\.?\b': 'PLLC',
    r'\bP\.?A\.?\b': 'PA',
    r'\bL\.?L\.?P\.?\b': 'LLP',
    r'\bL\.?P\.?\b': 'LP',
    
    # N.A. (National Association - banks)
    r'\bN\.?A\.?\b': 'NA',
}

# ============================================================================
# STEP 3: Common Company Name Standardizations
# ============================================================================
COMPANY_STANDARDIZATIONS = [
    # RE/MAX variations - order matters, most specific first
    (r'\bRE/?MAX\b', 'RE/MAX'),
    (r'\bRemax\b', 'RE/MAX'),
    (r'\bREMAX\b', 'RE/MAX'),
    (r'\bRe/max\b', 'RE/MAX'),
    (r'\bRe/Max\b', 'RE/MAX'),
    
    # Verizon
    (r'\bVerizonwireless\b', 'Verizon Wireless'),
    (r'\bVerizonbusiness\b', 'Verizon Business'),
    (r'\bVerizonmedia\b', 'Verizon Media'),
    
    # Common variations
    (r'\bChick-Fil-A\b', 'Chick-fil-A'),
    (r'\bChickfila\b', 'Chick-fil-A'),
    (r'\bCHICK-FIL-A\b', 'Chick-fil-A'),
    
    # UPS variations
    (r'\bU\.P\.S\.\b', 'UPS'),
]


def fix_encoding(text):
    """Fix corrupted encoding characters."""
    if pd.isna(text):
        return text
    
    text = str(text)
    
    # Apply encoding fixes
    for corrupted, fixed in ENCODING_FIXES.items():
        text = text.replace(corrupted, fixed)
    
    # Try to normalize unicode
    try:
        # Normalize unicode characters
        text = unicodedata.normalize('NFKC', text)
    except:
        pass
    
    return text


def normalize_spacing(text):
    """Normalize spacing in company names."""
    if pd.isna(text):
        return text
    
    text = str(text)
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s{2,}', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove spaces before punctuation
    text = re.sub(r'\s+([,\.;:])', r'\1', text)
    
    # Ensure space after punctuation (but not in abbreviations like U.S.)
    text = re.sub(r'([,;:])(?=[^\s])', r'\1 ', text)
    
    return text


def standardize_suffixes(text):
    """Standardize legal suffixes."""
    if pd.isna(text):
        return text
    
    text = str(text)
    
    for pattern, replacement in LEGAL_SUFFIXES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def apply_company_standardizations(text):
    """Apply company-specific standardizations."""
    if pd.isna(text):
        return text
    
    text = str(text)
    
    for pattern, replacement in COMPANY_STANDARDIZATIONS:
        text = re.sub(pattern, replacement, text)
    
    return text


def normalize_case(text):
    """Smart case normalization - preserve intentional casing."""
    if pd.isna(text):
        return text
    
    text = str(text)
    
    # If the name is all uppercase, convert to title case
    if text.isupper() and len(text) > 3:
        # But preserve common acronyms and brand names
        words = text.split()
        result = []
        acronyms = {'LLC', 'INC', 'LLP', 'PC', 'PA', 'LP', 'NA', 'USA', 'US', 'IBM', 'HP', 'GE', 'AT&T', 'UPS', 'CEO', 'CFO'}
        preserve_brands = {'RE/MAX': 'RE/MAX', 'REMAX': 'RE/MAX'}
        for word in words:
            if word.upper() in acronyms:
                result.append(word.upper())
            elif word.upper() in preserve_brands:
                result.append(preserve_brands[word.upper()])
            else:
                result.append(word.title())
        text = ' '.join(result)
    
    return text


def remove_trailing_punctuation(text):
    """Remove trailing punctuation that doesn't belong."""
    if pd.isna(text):
        return text
    
    text = str(text)
    
    # Remove trailing commas, periods (unless part of Inc., etc.)
    text = re.sub(r',\s*$', '', text)
    
    # Remove quotes wrapping the whole name
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    
    return text


def create_normalized_key(text):
    """Create a normalized key for matching similar companies."""
    if pd.isna(text):
        return ''
    
    text = str(text).lower()
    
    # Remove trademark/registered symbols before other processing
    text = re.sub(r'[®™©]', '', text)
    
    # Remove all punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # Remove common suffixes for matching purposes
    suffixes_to_remove = [
        r'\binc\b', r'\bllc\b', r'\bcorp\b', r'\bcorporation\b',
        r'\bltd\b', r'\blimited\b', r'\bco\b', r'\bcompany\b',
        r'\bpc\b', r'\bpllc\b', r'\bpa\b', r'\bllp\b', r'\blp\b',
        r'\bna\b', r'\bthe\b'
    ]
    
    for suffix in suffixes_to_remove:
        text = re.sub(suffix, '', text)
    
    # Remove ALL spaces to catch "HomeDepot" vs "Home Depot"
    text = re.sub(r'\s+', '', text)
    
    return text


def clean_company_name(name):
    """Apply all cleaning steps to a company name."""
    if pd.isna(name):
        return name
    
    # Step 1: Fix encoding
    name = fix_encoding(name)
    
    # Step 2: Remove trailing punctuation
    name = remove_trailing_punctuation(name)
    
    # Step 3: Normalize spacing
    name = normalize_spacing(name)
    
    # Step 4: Standardize suffixes
    name = standardize_suffixes(name)
    
    # Step 5: Apply company-specific standardizations
    name = apply_company_standardizations(name)
    
    # Step 6: Normalize case (optional - only for ALL CAPS)
    name = normalize_case(name)
    
    # Final spacing cleanup
    name = normalize_spacing(name)
    
    return name


def find_similar_companies(df, similarity_threshold=0.85):
    """Find companies with similar names using normalized keys."""
    
    # Group by normalized key
    key_groups = defaultdict(list)
    
    for idx, row in df.iterrows():
        key = create_normalized_key(row['cleaned_name'])
        if key:  # Only add non-empty keys
            key_groups[key].append({
                'original': row['company_name'],
                'cleaned': row['cleaned_name'],
                'count': row['count'],
                'idx': idx
            })
    
    # Find groups with multiple entries (potential duplicates)
    duplicates = {k: v for k, v in key_groups.items() if len(v) > 1}
    
    return duplicates, key_groups


def merge_similar_companies(df, key_groups):
    """Merge similar companies into canonical names based on normalized keys."""
    
    # For each group, pick the canonical name (the cleaned name with highest count)
    canonical_mapping = {}  # normalized_key -> canonical_name
    
    for key, companies in key_groups.items():
        if not companies:
            continue
        
        # Sort by count descending, then by cleaned name length (prefer shorter, cleaner names)
        sorted_companies = sorted(companies, key=lambda x: (-x['count'], len(x['cleaned'])))
        canonical = sorted_companies[0]['cleaned']
        canonical_mapping[key] = canonical
    
    # Create a mapping from original name to canonical name
    original_to_canonical = {}
    for key, companies in key_groups.items():
        canonical = canonical_mapping.get(key)
        if canonical:
            for comp in companies:
                original_to_canonical[comp['original']] = canonical
    
    # Apply the canonical mapping
    df['canonical_name'] = df['company_name'].map(original_to_canonical).fillna(df['cleaned_name'])
    
    return df, canonical_mapping


def main():
    print("=" * 80)
    print("COMPANY NAME CLEANING AND DEDUPLICATION")
    print("=" * 80)
    
    # Load data
    print("\n[1/6] Loading data...")
    df = pd.read_csv('csv_outputs/company_name_clean/unique_company_names.csv')
    original_count = len(df)
    print(f"    Loaded {original_count:,} unique company names")
    
    # Clean names
    print("\n[2/6] Cleaning company names...")
    df['cleaned_name'] = df['company_name'].apply(clean_company_name)
    
    # Show examples of changes
    print("\n    Examples of cleaned names:")
    changed = df[df['company_name'] != df['cleaned_name']].head(20)
    for _, row in changed.iterrows():
        try:
            orig = row['company_name'].encode('ascii', 'replace').decode('ascii')
            clean = row['cleaned_name'].encode('ascii', 'replace').decode('ascii')
            print(f"    '{orig}' -> '{clean}'")
        except:
            pass
    
    # Create normalized keys
    print("\n[3/6] Creating normalized keys for matching...")
    df['normalized_key'] = df['cleaned_name'].apply(create_normalized_key)
    
    # Find duplicates based on cleaned names
    print("\n[4/6] Finding exact duplicates after cleaning...")
    cleaned_groups = df.groupby('cleaned_name').agg({
        'company_name': list,
        'count': 'sum'
    }).reset_index()
    
    exact_duplicates = cleaned_groups[cleaned_groups['company_name'].apply(len) > 1]
    print(f"    Found {len(exact_duplicates):,} groups of exact duplicates after cleaning")
    
    # Find similar companies (fuzzy matching on normalized keys)
    print("\n[5/7] Finding similar companies...")
    duplicates, key_groups = find_similar_companies(df)
    print(f"    Found {len(duplicates):,} groups of similar companies")
    
    # Merge similar companies into canonical names
    print("\n[6/7] Merging similar companies into canonical names...")
    df, canonical_mapping = merge_similar_companies(df, key_groups)
    
    # Calculate final unique count after full merge
    final_groups = df.groupby('canonical_name').agg({
        'company_name': list,
        'count': 'sum'
    }).reset_index()
    
    unique_keys = len(key_groups)
    final_unique = len(final_groups)
    
    print(f"\n[7/7] RESULTS:")
    print(f"    Original unique names:       {original_count:,}")
    print(f"    After cleaning (exact):      {len(cleaned_groups):,}")
    print(f"    After full merge (similar):  {final_unique:,}")
    print(f"    Total duplicates removed:    {original_count - final_unique:,}")
    
    # Save outputs
    print("\n" + "=" * 80)
    print("SAVING OUTPUTS")
    print("=" * 80)
    
    # Ensure output directory exists
    output_dir = 'csv_outputs/company_name_clean'
    os.makedirs(output_dir, exist_ok=True)
    
    # Output 1: Full mapping (original -> cleaned -> canonical)
    df[['company_name', 'cleaned_name', 'canonical_name', 'count']].to_csv(
        f'{output_dir}/company_names_cleaned.csv', index=False
    )
    print(f"\n[OK] Saved: {output_dir}/company_names_cleaned.csv")
    
    # Output 2: Aggregated by cleaned name (before full merge)
    aggregated = df.groupby('cleaned_name').agg({
        'company_name': lambda x: ' | '.join(sorted(set(x))),
        'count': 'sum'
    }).reset_index()
    aggregated.columns = ['cleaned_name', 'original_variations', 'total_count']
    aggregated = aggregated.sort_values('total_count', ascending=False)
    aggregated.to_csv(f'{output_dir}/company_names_aggregated.csv', index=False)
    print(f"[OK] Saved: {output_dir}/company_names_aggregated.csv ({len(aggregated):,} unique names)")
    
    # Output 3: FINAL fully merged/deduplicated list
    final_merged = df.groupby('canonical_name').agg({
        'company_name': lambda x: ' | '.join(sorted(set(x))),
        'cleaned_name': lambda x: ' | '.join(sorted(set(x))),
        'count': 'sum'
    }).reset_index()
    final_merged.columns = ['canonical_name', 'original_variations', 'cleaned_variations', 'total_count']
    final_merged = final_merged.sort_values('total_count', ascending=False)
    final_merged.to_csv(f'{output_dir}/company_names_final_merged.csv', index=False)
    print(f"[OK] Saved: {output_dir}/company_names_final_merged.csv ({len(final_merged):,} TRUE UNIQUE companies)")
    
    # Output 4: Similar company groups (for reference)
    with open(f'{output_dir}/similar_companies_review.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['group_key', 'canonical_name', 'cleaned_name', 'original_name', 'count'])
        
        for key, companies in sorted(duplicates.items(), key=lambda x: -sum(c['count'] for c in x[1])):
            canonical = canonical_mapping.get(key, companies[0]['cleaned'])
            for comp in sorted(companies, key=lambda x: -x['count']):
                writer.writerow([key, canonical, comp['cleaned'], comp['original'], comp['count']])
    
    print(f"[OK] Saved: {output_dir}/similar_companies_review.csv ({len(duplicates):,} groups)")
    
    # Output 5: JSON mapping for pandas .replace() function
    mapping = {}
    for _, row in df.iterrows():
        orig = row['company_name']
        canonical = row['canonical_name']
        if orig != canonical:
            mapping[orig] = canonical
    
    with open(f'{output_dir}/company_name_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved: {output_dir}/company_name_mapping.json ({len(mapping):,} mappings for pandas .replace())")
    
    # Output 6: Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    # Top 50 company groups by count (FINAL MERGED)
    print("\nTop 50 companies by total count (FINAL MERGED):")
    print("-" * 60)
    for idx, row in final_merged.head(50).iterrows():
        try:
            variations = row['original_variations'].split(' | ')
            name = row['canonical_name'].encode('ascii', 'replace').decode('ascii')
            if len(variations) > 1:
                print(f"{row['total_count']:>6,}  {name}")
                vars_str = ', '.join(v.encode('ascii', 'replace').decode('ascii') for v in variations[:3])
                print(f"         Merged from: {vars_str}{'...' if len(variations) > 3 else ''}")
            else:
                print(f"{row['total_count']:>6,}  {name}")
        except:
            pass
    
    # Groups with most duplicates merged
    print("\n\nGroups with most original name variations merged:")
    print("-" * 60)
    multi_variation = final_merged[final_merged['original_variations'].str.contains(r'\|', regex=True)].copy()
    multi_variation['variation_count'] = multi_variation['original_variations'].str.count(r'\|') + 1
    top_variations = multi_variation.nlargest(30, 'variation_count')
    
    for _, row in top_variations.iterrows():
        try:
            variations = row['original_variations'].split(' | ')
            name = row['canonical_name'].encode('ascii', 'replace').decode('ascii')
            print(f"\n{name} ({row['variation_count']} variations merged, {row['total_count']:,} total)")
            for v in variations[:5]:
                v_safe = v.encode('ascii', 'replace').decode('ascii')
                print(f"    - {v_safe}")
            if len(variations) > 5:
                print(f"    ... and {len(variations) - 5} more")
        except:
            pass
    
    print("\n" + "=" * 80)
    print("DONE!")
    print("=" * 80)
    
    return df, final_merged


if __name__ == '__main__':
    df, final_merged = main()

