import requests
import json
import time

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
print("ADVANCED WILDCARD TESTING - SQL SERVER STORED PROCEDURE")
print("=" * 80)
print()
print("DISCOVERY FROM REVERSE ENGINEERING:")
print("  - Database: SQL Server (confirmed via stored procedure error)")
print("  - Stored Procedure: usp_FILING_WebSearch")
print("  - Backend: ASP.NET with stored procedures")
print("  - Security: WAF blocks SQL injection attempts")
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

# SQL Server-specific LIKE patterns
# SQL Server LIKE syntax: % matches any sequence, _ matches single char
sql_server_patterns = [
    {
        "name": "Single percent wildcard",
        "value": "%",
        "description": "SQL Server LIKE '%' - matches everything (if 3-char min waived)"
    },
    {
        "name": "Triple percent",
        "value": "%%%",
        "description": "SQL Server LIKE '%%%' - should match all"
    },
    {
        "name": "Percent with underscore",
        "value": "%_%",
        "description": "SQL Server LIKE '%_%' - matches any sequence"
    },
    {
        "name": "Bracket pattern all",
        "value": "[a-z]",
        "description": "SQL Server bracket pattern"
    },
    {
        "name": "Bracket with percent",
        "value": "[a-z]%",
        "description": "SQL Server bracket + wildcard"
    },
    {
        "name": "Double bracket escape",
        "value": "[[%]]",
        "description": "SQL Server escaped bracket pattern"
    },
    {
        "name": "Percent at start",
        "value": "%AB",
        "description": "Starts with wildcard"
    },
    {
        "name": "Percent at end",
        "value": "AB%",
        "description": "Ends with wildcard"
    },
    {
        "name": "Percent both sides",
        "value": "%AB%",
        "description": "Contains pattern"
    },
    {
        "name": "All characters bracket",
        "value": "[!]",
        "description": "SQL Server negated bracket (matches all except !)"
    },
    {
        "name": "Wide range bracket",
        "value": "[0-9]",
        "description": "Numeric range"
    },
    {
        "name": "Alpha range",
        "value": "[A-Z]",
        "description": "Alphabetic range"
    },
    {
        "name": "Combined range",
        "value": "[A-Z0-9]",
        "description": "Alphanumeric range"
    },
    {
        "name": "Multiple underscores",
        "value": "___",
        "description": "Three underscores (matches any 3 chars)"
    },
    {
        "name": "Mixed wildcards",
        "value": "%_%",
        "description": "Percent and underscore combination"
    }
]

def count_records(data):
    """Count records in response"""
    if isinstance(data, list):
        return len(data)
    elif isinstance(data, dict):
        # Check common keys
        for key in ['data', 'results', 'items', 'records', 'businesses', 'rows']:
            if key in data:
                if isinstance(data[key], list):
                    return len(data[key])
                elif isinstance(data[key], dict):
                    # If rows is a dict, count its values/keys
                    if isinstance(data[key], dict) and len(data[key]) > 0:
                        # Try to get count from first item or total
                        return len(data[key])
        if 'total' in data:
            return data.get('total', 0)
        if 'count' in data:
            return data.get('count', 0)
    return 0

print("Testing SQL Server LIKE patterns...")
print("-" * 80)
print()

best_pattern = None
best_count = 0
best_response_data = None
results = []

for i, pattern in enumerate(sql_server_patterns, 1):
    print(f"[{i}/{len(sql_server_patterns)}] Testing: {pattern['name']}")
    print(f"  Pattern: '{pattern['value']}'")
    print(f"  Description: {pattern['description']}")
    
    payload = base_payload.copy()
    payload["SEARCH_VALUE"] = pattern["value"]
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            try:
                data = response.json()
                count = count_records(data)
                
                # Check if rows has data
                rows_count = 0
                if isinstance(data, dict) and 'rows' in data:
                    if isinstance(data['rows'], dict):
                        rows_count = len(data['rows'])
                    elif isinstance(data['rows'], list):
                        rows_count = len(data['rows'])
                
                print(f"  [OK] Status: 200, Response time: {response_time:.2f}s")
                print(f"  Records found: {count}, Rows: {rows_count}")
                
                if rows_count > 0 or count > 0:
                    print(f"  *** SUCCESS! Found {max(count, rows_count)} records ***")
                    if max(count, rows_count) > best_count:
                        best_count = max(count, rows_count)
                        best_pattern = pattern
                        best_response_data = data
                
                results.append({
                    'pattern': pattern['name'],
                    'value': pattern['value'],
                    'status': 200,
                    'count': count,
                    'rows_count': rows_count,
                    'time': response_time
                })
                
            except ValueError as e:
                print(f"  [WARN] Invalid JSON: {str(e)[:50]}")
                results.append({
                    'pattern': pattern['name'],
                    'value': pattern['value'],
                    'status': 200,
                    'error': 'Invalid JSON'
                })
        else:
            print(f"  [INFO] Status: {response.status_code}")
            if response.status_code == 403:
                print(f"  Blocked by WAF/security")
            elif response.status_code == 500:
                error_text = response.text[:200]
                print(f"  Error: {error_text}")
            results.append({
                'pattern': pattern['name'],
                'value': pattern['value'],
                'status': response.status_code
            })
            
    except Exception as e:
        print(f"  [ERROR] Exception: {str(e)[:100]}")
        results.append({
            'pattern': pattern['name'],
            'value': pattern['value'],
            'error': str(e)[:100]
        })
    
    print()

print()
print("=" * 80)
print("RESULTS SUMMARY")
print("=" * 80)

if best_pattern:
    print(f"\nBEST RESULT:")
    print(f"  Pattern: {best_pattern['name']}")
    print(f"  Value: '{best_pattern['value']}'")
    print(f"  Records Found: {best_count}")
    print()
    print("Full response structure:")
    if best_response_data:
        print(json.dumps(best_response_data, indent=2)[:2000])
        if len(json.dumps(best_response_data)) > 2000:
            print(f"\n... (truncated, total: {len(json.dumps(best_response_data))} chars)")
else:
    print("\nNo patterns returned records.")
    print("\nSuccessful patterns (200 status):")
    successful = [r for r in results if r.get('status') == 200]
    for r in successful:
        print(f"  - {r['pattern']} ('{r['value']}'): {r.get('count', 0)} records, {r.get('rows_count', 0)} rows")

print()
print("=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)
print("Based on SQL Server stored procedure (usp_FILING_WebSearch):")
print("  1. The stored procedure likely uses parameterized queries")
print("  2. LIKE patterns should work if the SP uses LIKE in SQL")
print("  3. The 3-character minimum is likely enforced in the stored procedure")
print("  4. Try combining wildcards with actual search terms")
print("  5. The API might require specific SEARCH_FILTER_TYPE_ID values")
print("  6. Consider that the SP might not support wildcards at all")
print("     and requires actual search terms")
print("=" * 80)

