import requests
import json
import time
import string
from itertools import product
import pandas as pd
import base64
from datetime import datetime

url = "https://bizfileonline.sos.ca.gov/api/Records/businesssearch"
detail_url_template = "https://bizfileonline.sos.ca.gov/api/FilingDetail/business/{}/false"

# Updated token
auth_token = "eyJraWQiOiJFMlZPcEN4WTJiM1NLRGFEbi1GUktrT2Z5Q3lSWW5ZVU8tOVgtcE84RE9VIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULlpsMVhsdDJiTHBxLWRjNlBJaENPU0puVGltSmxselZPdXp6S1N1c1YtT0kiLCJpc3MiOiJodHRwczovL2lkbS5zb3MuY2EuZ292L29hdXRoMi9kZWZhdWx0IiwiYXVkIjoiYXBpOi8vZGVmYXVsdCIsImlhdCI6MTc2Mjk5MjgwOSwiZXhwIjoxNzYyOTk2NDA5LCJjaWQiOiIwb2Fjc3phNzEwb1dRWTFtZDR4NiIsInVpZCI6IjAwdXN1Zmxqcmc2bm54MEhDNHg3Iiwic2NwIjpbIm9wZW5pZCJdLCJhdXRoX3RpbWUiOjE3NjI5ODkxMDgsInN1YiI6InNoaXZhbXNzaW5nOTZAZ21haWwuY29tIn0.sy0DwYHH7cGOnZnZz-htX1vHcTDKzR79OEkLLb1HBumwDgqVUFFPWleXH2ikwu5pUwaLOdD5kwYNeKX7b3Ot_HRtmfyw99-DWV9h9DQsS-ktYWWZYhBopBgdaKz5nZ-wEYej0Fl23QPMnYssfWQhLfMaWO5Pb86fQOI8VBJ5GiIn1Iatd0_Yyjqtrzbbu49v9Jjv5mqNpl3G4DirIi0QLfow19UB27waZCzZxpLeKzhFRpNZYT_kIGY4TNtImmo8Z7y2psfYqyWS7BA5Z6jN8p0rqh0h7sBEF--fKpY0zapDZWQXJ48n7ZVuqDYBO8a7Wu16K9QQxecCDI-lA24u7g"

headers = {
    "Content-Type": "application/json",
    "Authorization": auth_token,
    "Origin": "https://bizfileonline.sos.ca.gov",
    "Referer": "https://bizfileonline.sos.ca.gov/search/business",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "*/*"
}

base_payload = {
    "SEARCH_VALUE": "",
    "SEARCH_FILTER_TYPE_ID": "0",
    "SEARCH_TYPE_ID": "1",
    "FILING_TYPE_ID": "",
    "STATUS_ID": "43",
    "FILING_DATE": {"start": None, "end": None},
    "CORPORATION_BANKRUPTCY_YN": False,
    "CORPORATION_LEGAL_PROCEEDINGS_YN": False,
    "OFFICER_OBJECT": {"FIRST_NAME": "", "MIDDLE_NAME": "", "LAST_NAME": ""},
    "NUMBER_OF_FEMALE_DIRECTORS": "99",
    "NUMBER_OF_UNDERREPRESENTED_DIRECTORS": "99",
    "COMPENSATION_FROM": "",
    "COMPENSATION_TO": "",
    "SHARES_YN": False,
    "OPTIONS_YN": False,
    "BANKRUPTCY_YN": False,
    "FRAUD_YN": False,
    "LOANS_YN": False,
    "AUDITOR_NAME": ""
}

print("=" * 80)
print("COMPREHENSIVE DATA EXTRACTION STRATEGY (STATUS_ID: 43)")
print("=" * 80)
print()
print("DISCOVERY:")
print("  - 2-character searches WORK! (e.g., 'AB' returns 500 records)")
print("  - API limit: 500 records per query (no pagination found)")
print("  - Strategy: Use all 2-character combinations to get comprehensive coverage")
print()
print("This will test multiple strategies:")
print("  1. All 2-letter combinations (AA-ZZ) = 676 combinations")
print("  2. All letter-number combinations (A0-Z9) = 260 combinations")
print("  3. All number-letter combinations (0A-9Z) = 260 combinations")
print("  4. Common business suffixes")
print()
print("WARNING: This will make ~1200+ API calls for extraction!")
print("Then it will make additional API calls to enrich each record with detailed info.")
print("Estimated time: 20-40 minutes (extraction) + additional time for enrichment")
print()
response = input("Continue? (y/n): ")
if response.lower() != 'y':
    print("Aborted.")
    exit()

all_records = {}
stats = {
    'total_queries': 0,
    'successful_queries': 0,
    'failed_queries': 0,
    'total_records_fetched': 0,
    'unique_records': 0,
    'start_time': time.time(),
    'enrichment_queries': 0,
    'enrichment_successful': 0,
    'enrichment_failed': 0
}

def fetch_records(search_value):
    """Fetch records for a given search value"""
    payload = base_payload.copy()
    payload["SEARCH_VALUE"] = search_value
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        stats['total_queries'] += 1
        
        if response.status_code == 200:
            data = response.json()
            if 'rows' in data and isinstance(data['rows'], dict):
                stats['successful_queries'] += 1
                return data['rows']
        else:
            stats['failed_queries'] += 1
            return {}
    except Exception as e:
        stats['failed_queries'] += 1
        print(f"    Error: {str(e)[:50]}")
        return {}
    
    return {}

def fetch_record_detail(record_id):
    """Fetch detailed information for a record ID"""
    url = detail_url_template.format(record_id)
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        stats['enrichment_queries'] += 1
        
        if response.status_code == 200:
            data = response.json()
            stats['enrichment_successful'] += 1
            return data
        else:
            stats['enrichment_failed'] += 1
            return None
    except Exception as e:
        stats['enrichment_failed'] += 1
        return None

def extract_detail_fields(detail_data):
    """Extract Status and Statement of Info Due Date from detail response"""
    status_value = None
    statement_due_date = None
    
    if detail_data and 'DRAWER_DETAIL_LIST' in detail_data:
        for item in detail_data['DRAWER_DETAIL_LIST']:
            if item.get('LABEL') == 'Status':
                status_value = item.get('VALUE')
            elif item.get('LABEL') == 'Statement of Info Due Date':
                statement_due_date = item.get('VALUE')
    
    return {
        'STATUS_DETAIL': status_value,
        'STATEMENT_OF_INFO_DUE_DATE': statement_due_date
    }

# Strategy 1: All 2-letter combinations (AA-ZZ)
print()
print("=" * 80)
print("STRATEGY 1: All 2-letter combinations (AA-ZZ)")
print("=" * 80)
letters = string.ascii_uppercase
two_letter_combos = [f"{a}{b}" for a, b in product(letters, letters)]

print(f"Testing {len(two_letter_combos)} combinations...")
for i, combo in enumerate(two_letter_combos, 1):
    if i % 50 == 0:
        elapsed = time.time() - stats['start_time']
        print(f"  Progress: {i}/{len(two_letter_combos)} ({i/len(two_letter_combos)*100:.1f}%) - "
              f"{len(all_records)} unique records - {elapsed/60:.1f} min")
    
    records = fetch_records(combo)
    new_count = 0
    for record_id, record_data in records.items():
        if record_id not in all_records:
            all_records[record_id] = record_data
            new_count += 1
    stats['total_records_fetched'] += len(records)
    
    time.sleep(0.1)  # Rate limiting

print(f"  Completed: {len(two_letter_combos)} queries, {len(all_records)} unique records")

# Strategy 2: Letter-Number combinations (A0-Z9)
print()
print("=" * 80)
print("STRATEGY 2: Letter-Number combinations (A0-Z9)")
print("=" * 80)
numbers = string.digits
letter_number = [f"{a}{b}" for a, b in product(letters, numbers)]

print(f"Testing {len(letter_number)} combinations...")
for i, combo in enumerate(letter_number, 1):
    if i % 50 == 0:
        elapsed = time.time() - stats['start_time']
        print(f"  Progress: {i}/{len(letter_number)} ({i/len(letter_number)*100:.1f}%) - "
              f"{len(all_records)} unique records - {elapsed/60:.1f} min")
    
    records = fetch_records(combo)
    new_count = 0
    for record_id, record_data in records.items():
        if record_id not in all_records:
            all_records[record_id] = record_data
            new_count += 1
    stats['total_records_fetched'] += len(records)
    
    time.sleep(0.1)

print(f"  Completed: {len(letter_number)} queries, {len(all_records)} unique records")

# Strategy 3: Number-Letter combinations (0A-9Z)
print()
print("=" * 80)
print("STRATEGY 3: Number-Letter combinations (0A-9Z)")
print("=" * 80)
number_letter = [f"{a}{b}" for a, b in product(numbers, letters)]

print(f"Testing {len(number_letter)} combinations...")
for i, combo in enumerate(number_letter, 1):
    if i % 50 == 0:
        elapsed = time.time() - stats['start_time']
        print(f"  Progress: {i}/{len(number_letter)} ({i/len(number_letter)*100:.1f}%) - "
              f"{len(all_records)} unique records - {elapsed/60:.1f} min")
    
    records = fetch_records(combo)
    new_count = 0
    for record_id, record_data in records.items():
        if record_id not in all_records:
            all_records[record_id] = record_data
            new_count += 1
    stats['total_records_fetched'] += len(records)
    
    time.sleep(0.1)

print(f"  Completed: {len(number_letter)} queries, {len(all_records)} unique records")

# Final summary
stats['unique_records'] = len(all_records)
elapsed_time = time.time() - stats['start_time']

print()
print("=" * 80)
print("EXTRACTION COMPLETE")
print("=" * 80)
print(f"Total queries: {stats['total_queries']}")
print(f"Successful: {stats['successful_queries']}")
print(f"Failed: {stats['failed_queries']}")
print(f"Total records fetched: {stats['total_records_fetched']}")
print(f"Unique records: {stats['unique_records']}")
print(f"Time elapsed: {elapsed_time/60:.1f} minutes")
print()

# Enrichment phase: Fetch detailed information for each record
print("=" * 80)
print("ENRICHING RECORDS WITH DETAILED INFORMATION")
print("=" * 80)
print(f"Enriching {len(all_records)} records with Status and Statement of Info Due Date...")
print()

enrichment_start = time.time()
for i, (record_key, record) in enumerate(all_records.items(), 1):
    record_id = record.get('ID')
    
    if record_id is None:
        continue
    
    # Fetch detail
    detail_data = fetch_record_detail(record_id)
    
    if detail_data:
        # Extract fields
        extracted = extract_detail_fields(detail_data)
        record['STATUS_DETAIL'] = extracted['STATUS_DETAIL']
        record['STATEMENT_OF_INFO_DUE_DATE'] = extracted['STATEMENT_OF_INFO_DUE_DATE']
    
    # Progress update
    if i % 50 == 0:
        elapsed = time.time() - enrichment_start
        print(f"  Progress: {i}/{len(all_records)} ({i/len(all_records)*100:.1f}%) - "
              f"Success: {stats['enrichment_successful']}, Failed: {stats['enrichment_failed']} - "
              f"{elapsed/60:.1f} min")
    
    # Rate limiting
    time.sleep(0.1)

enrichment_elapsed = time.time() - enrichment_start
print()
print(f"  Enrichment completed: {stats['enrichment_queries']} queries in {enrichment_elapsed/60:.1f} minutes")
print(f"  Successful: {stats['enrichment_successful']}, Failed: {stats['enrichment_failed']}")
print()

# Save results
output_file = f"all_records_status43_{int(time.time())}.json"
output_data = {
    "extraction_date": time.strftime("%Y-%m-%d %H:%M:%S"),
    "statistics": stats,
    "total_unique_records": len(all_records),
    "records": all_records
}

print(f"Saving to {output_file}...")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"Saved {len(all_records)} unique records to: {output_file}")
print()

# Convert to Excel
print("=" * 80)
print("CONVERTING TO EXCEL")
print("=" * 80)
print("Converting records to Excel format...")

# Prepare data for Excel - flatten records
excel_data = []
for record_key, record in all_records.items():
    row = record.copy()
    # Flatten TITLE array - join if multiple, or take first
    if 'TITLE' in row and isinstance(row['TITLE'], list):
        row['TITLE'] = ' | '.join(row['TITLE']) if row['TITLE'] else ''
    excel_data.append(row)

# Create DataFrame
df = pd.DataFrame(excel_data)

# Reorder columns for better readability (put important fields first)
column_order = ['ID', 'TITLE', 'STATUS', 'STATUS_DETAIL', 'STATEMENT_OF_INFO_DUE_DATE', 
                'FILING_DATE', 'ENTITY_TYPE', 'STANDING', 'FORMED_IN', 'AGENT', 
                'RECORD_NUM', 'SORT_INDEX', 'ALERT', 'CAN_REINSTATE', 'CAN_FILE_AR', 
                'CAN_FILE_REINSTATEMENT']

# Reorder columns (only include columns that exist)
existing_columns = [col for col in column_order if col in df.columns]
other_columns = [col for col in df.columns if col not in column_order]
df = df[existing_columns + other_columns]

# Save to Excel
excel_file = output_file.replace('.json', '.xlsx')
print(f"Saving to {excel_file}...")
df.to_excel(excel_file, index=False, engine='openpyxl')
print(f"Saved {len(excel_data)} records to: {excel_file}")
print("=" * 80)


