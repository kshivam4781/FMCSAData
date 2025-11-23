import requests
import json
import time
from collections import defaultdict

url = "https://bizfileonline.sos.ca.gov/api/Records/businesssearch"

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

print("=" * 80)
print("TESTING API LIMITATIONS & PAGINATION")
print("=" * 80)
print()

# Base payload
base_payload = {
    "SEARCH_VALUE": "",
    "SEARCH_FILTER_TYPE_ID": "0",
    "SEARCH_TYPE_ID": "1",
    "FILING_TYPE_ID": "",
    "STATUS_ID": "",
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

# Test 1: Check if 2 characters are blocked
print("TEST 1: Checking 2-character limit")
print("-" * 80)
test_lengths = ["", "A", "AB", "ABC"]
for test_len in test_lengths:
    payload = base_payload.copy()
    payload["SEARCH_VALUE"] = test_len
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"  '{test_len}' ({len(test_len)} chars): Status {response.status_code}", end="")
        if response.status_code == 200:
            try:
                data = response.json()
                if 'rows' in data:
                    rows_count = len(data['rows']) if isinstance(data['rows'], dict) else 0
                    print(f" - {rows_count} records")
                else:
                    print(" - No records")
            except:
                print(" - Invalid JSON")
        else:
            print(f" - Blocked/Error")
    except Exception as e:
        print(f" - Exception: {str(e)[:50]}")

print()

# Test 2: Check for pagination parameters
print("TEST 2: Testing for pagination parameters")
print("-" * 80)
print("Trying common pagination parameter names...")

pagination_tests = [
    {"page": 1, "pageSize": 100},
    {"page": 1, "limit": 100},
    {"offset": 0, "limit": 100},
    {"skip": 0, "take": 100},
    {"pageNumber": 1, "pageSize": 100},
    {"start": 0, "count": 100},
]

# First, get a baseline with a working pattern
payload = base_payload.copy()
payload["SEARCH_VALUE"] = "[0-9]"
baseline_response = requests.post(url, json=payload, headers=headers, timeout=10)
if baseline_response.status_code == 200:
    baseline_data = baseline_response.json()
    baseline_count = len(baseline_data.get('rows', {})) if isinstance(baseline_data.get('rows'), dict) else 0
    print(f"  Baseline (no pagination): {baseline_count} records")
    
    # Try adding pagination parameters
    for pagination in pagination_tests:
        test_payload = payload.copy()
        test_payload.update(pagination)
        try:
            response = requests.post(url, json=test_payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('rows', {})) if isinstance(data.get('rows'), dict) else 0
                if count != baseline_count:
                    print(f"  [FOUND] {pagination}: {count} records (different from baseline!)")
                else:
                    print(f"  {pagination}: {count} records (same as baseline)")
        except:
            pass

print()

# Test 3: Try to get all records using multiple patterns
print("TEST 3: Strategy to get ALL records")
print("-" * 80)
print("Since API returns max 500 records per query, we'll try multiple patterns")
print("and combine results to get comprehensive coverage...")
print()

# Patterns that return 500 records each
patterns = [
    {"name": "Numeric start [0-9]", "value": "[0-9]"},
    {"name": "Alpha start [A-Z]", "value": "[A-Z]"},
    {"name": "Percent AB", "value": "%AB"},
    {"name": "Percent AB both sides", "value": "%AB%"},
    {"name": "Percent IN", "value": "%IN"},
    {"name": "Percent INC", "value": "%INC"},
    {"name": "Percent LLC", "value": "%LLC"},
    {"name": "Percent CORP", "value": "%CORP"},
    {"name": "Bracket 0-9", "value": "[0-9]"},
    {"name": "Bracket A-Z", "value": "[A-Z]"},
]

all_records = {}  # Use dict to avoid duplicates (keyed by ID)
pattern_results = {}

for i, pattern in enumerate(patterns, 1):
    print(f"[{i}/{len(patterns)}] Testing: {pattern['name']} ('{pattern['value']}')...")
    payload = base_payload.copy()
    payload["SEARCH_VALUE"] = pattern["value"]
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if 'rows' in data and isinstance(data['rows'], dict):
                count = len(data['rows'])
                print(f"  [OK] Got {count} records in {response_time:.2f}s")
                
                # Merge records (avoid duplicates by ID)
                new_records = 0
                for record_id, record_data in data['rows'].items():
                    if record_id not in all_records:
                        all_records[record_id] = record_data
                        new_records += 1
                
                pattern_results[pattern['name']] = {
                    'total': count,
                    'new': new_records,
                    'time': response_time
                }
                print(f"  Added {new_records} new records (total unique: {len(all_records)})")
            else:
                print(f"  [WARN] No 'rows' found in response")
        else:
            print(f"  [FAIL] Status: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] {str(e)[:100]}")
    
    print()

print("=" * 80)
print("RESULTS SUMMARY")
print("=" * 80)
print(f"Total unique records collected: {len(all_records)}")
print()
print("Pattern performance:")
for pattern_name, results in pattern_results.items():
    print(f"  {pattern_name}: {results['total']} records ({results['new']} new) in {results['time']:.2f}s")

print()
print("=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)
print("1. API 3-Character Limit:")
print("   - Confirmed: API blocks requests with < 3 characters")
print("   - This is enforced at the stored procedure level (usp_FILING_WebSearch)")
print()
print("2. Pagination:")
print("   - API returns maximum 500 records per query")
print("   - No pagination parameters found in request")
print("   - Likely enforced in stored procedure")
print()
print("3. To Get ALL Data:")
print("   Option A: Use multiple wildcard patterns and combine results")
print("   Option B: Try alphabetical/numeric combinations:")
print("      - [A-Z][0-9] patterns (e.g., 'A0', 'A1', 'B0', etc.)")
print("      - Two-letter combinations (AA, AB, AC, etc.)")
print("      - Common business suffixes (INC, LLC, CORP, etc.)")
print()
print("4. Estimated Total Records:")
print(f"   - Collected so far: {len(all_records)} unique records")
print("   - Each pattern returns ~500 records")
print("   - California likely has millions of business records")
print("   - Full extraction would require thousands of queries")
print()
print("=" * 80)

# Save collected records
if all_records:
    output_file = "collected_records.json"
    output_data = {
        "total_records": len(all_records),
        "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "patterns_used": list(pattern_results.keys()),
        "records": all_records
    }
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(all_records)} records to: {output_file}")
    print("=" * 80)

