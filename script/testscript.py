import requests
import json
import time

url = "https://bizfileonline.sos.ca.gov/api/Records/businesssearch"

# Strategy to get ALL records: Try wildcard patterns that match everything
# API requires minimum 3 characters, so we'll use wildcard patterns
# Common SQL wildcards: % (matches any sequence), _ (matches single char)
# We'll try multiple strategies to get all data

# WORKING PATTERNS DISCOVERED FROM REVERSE ENGINEERING:
# Database: SQL Server (stored procedure: usp_FILING_WebSearch)
# These patterns return 500 records (API appears to have pagination limit)
strategies = [
    {"name": "Percent at start (%AB)", "value": "%AB", "description": "SQL LIKE '%AB' - matches records ending with AB (returns 500)"},
    {"name": "Percent both sides (%AB%)", "value": "%AB%", "description": "SQL LIKE '%AB%' - matches records containing AB (returns 500)"},
    {"name": "Numeric range ([0-9])", "value": "[0-9]", "description": "SQL Server bracket pattern for numbers (returns 500)"},
    {"name": "Alpha range ([A-Z])", "value": "[A-Z]", "description": "SQL Server bracket pattern for letters (returns 499)"},
    {"name": "Triple percent (%%%)", "value": "%%%", "description": "SQL LIKE '%%%' - matches any sequence"},
    {"name": "Percent underscore (%_%)", "value": "%_%", "description": "SQL LIKE '%_%' - matches any sequence"},
]

# Base payload template
base_payload = {
    "SEARCH_VALUE":"",  # Will be set per strategy
    "SEARCH_FILTER_TYPE_ID":"0",
    "SEARCH_TYPE_ID":"1",
    "FILING_TYPE_ID":"",
    "STATUS_ID":"",
    "FILING_DATE":{"start":None,"end":None},
    "CORPORATION_BANKRUPTCY_YN":False,
    "CORPORATION_LEGAL_PROCEEDINGS_YN":False,
    "OFFICER_OBJECT":{"FIRST_NAME":"","MIDDLE_NAME":"","LAST_NAME":""},
    "NUMBER_OF_FEMALE_DIRECTORS":"99",
    "NUMBER_OF_UNDERREPRESENTED_DIRECTORS":"99",
    "COMPENSATION_FROM":"",
    "COMPENSATION_TO":"",
    "SHARES_YN":False,
    "OPTIONS_YN":False,
    "BANKRUPTCY_YN":False,
    "FRAUD_YN":False,
    "LOANS_YN":False,
    "AUDITOR_NAME":""
}

# Replace this with the Authorization token you copied from browser
# Updated token from network request (expires - check session-timeout header)
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
print("ATTEMPTING TO RETRIEVE ALL RECORDS")
print("=" * 80)
print("Trying multiple wildcard strategies to get all data...")
print()

# Function to count records in response
def count_records(data):
    if isinstance(data, list):
        return len(data)
    elif isinstance(data, dict):
        # Check for 'rows' key first (API returns rows as a dictionary)
        if 'rows' in data:
            if isinstance(data['rows'], dict):
                return len(data['rows'])  # Count dictionary keys (record IDs)
            elif isinstance(data['rows'], list):
                return len(data['rows'])
        # Check other common keys
        for key in ['data', 'results', 'items', 'records', 'businesses']:
            if key in data:
                if isinstance(data[key], list):
                    return len(data[key])
                elif isinstance(data[key], dict):
                    return len(data[key])  # Also handle dict responses
        if 'total' in data:
            return data.get('total', 0)
        if 'count' in data:
            return data.get('count', 0)
    return 0

# Try all strategies and find the one with most records
best_strategy = None
best_response = None
best_count = 0
best_data = None

for i, strategy in enumerate(strategies, 1):
    print(f"Trying Strategy {i}/{len(strategies)}: {strategy['name']} ('{strategy['value']}')...")
    payload = base_payload.copy()
    payload["SEARCH_VALUE"] = strategy["value"]
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            try:
                data = response.json()
                count = count_records(data)
                print(f"  [OK] Status: {response.status_code}, Records: {count}, Time: {response_time:.2f}s")
                
                if count > best_count:
                    best_count = count
                    best_strategy = strategy
                    best_response = response
                    best_data = data
            except ValueError:
                print(f"  [WARN] Status: {response.status_code}, Invalid JSON response")
        else:
            print(f"  [FAIL] Status: {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] Error: {str(e)}")
    
    print()

# Use the best result
if best_strategy:
    print("=" * 80)
    print(f"BEST RESULT: {best_strategy['name']} returned {best_count} records")
    print("=" * 80)
    print()
    selected_strategy = best_strategy
    response = best_response
    payload = base_payload.copy()
    payload["SEARCH_VALUE"] = selected_strategy["value"]
    # Calculate response time from the best response
    response_time = 0  # Will be shown in detailed analysis
else:
    print("=" * 80)
    print("WARNING: No successful strategy found. Using first strategy as fallback.")
    print("=" * 80)
    print()
    selected_strategy = strategies[0]
    payload = base_payload.copy()
    payload["SEARCH_VALUE"] = selected_strategy["value"]
    start_time = time.time()
    response = requests.post(url, json=payload, headers=headers)
    response_time = time.time() - start_time

print("=" * 80)
print("RESPONSE ANALYSIS")
print("=" * 80)
print(f"Search Value: '{payload['SEARCH_VALUE']}' ({len(payload['SEARCH_VALUE'])} characters)")
print(f"Strategy Used: {selected_strategy['name']}")
print(f"Status Code: {response.status_code}")
if response_time > 0:
    print(f"Response Time: {response_time:.3f} seconds")
print(f"Content Length: {len(response.content)} bytes")
print()

# Analyze response headers for database clues
print("RESPONSE HEADERS (Database Clues):")
print("-" * 80)
db_indicators = [
    'server', 'x-powered-by', 'x-aspnet-version', 
    'x-database', 'x-db-type', 'x-connection-string',
    'request-context', 'x-cdn', 'x-iinfo'
]
for header in db_indicators:
    if header in response.headers:
        print(f"  {header}: {response.headers[header]}")
print()

# Check for SQL error patterns in response
print("CHECKING FOR DATABASE CLUES IN RESPONSE:")
print("-" * 80)
response_text = response.text.lower()

# Check for stored procedure name (definitive SQL Server indicator)
sql_server_indicators = []
if 'usp_' in response_text or 'usp_filing' in response_text:
    sql_server_indicators.append("Stored procedure name (usp_*) - definitive SQL Server indicator")
if 'usp_filing_websearch' in response_text:
    sql_server_indicators.append("Stored procedure: usp_FILING_WebSearch - confirmed SQL Server")

# Common database error patterns (more specific to avoid false positives)
db_patterns = {
    'SQL Server': [
        'sql server', 'microsoft sql', 'system.data.sqlclient', 
        'sqlclient', 'sql exception', 'timeout expired',
        'xml parsing', 'stored procedure', 'usp_'
    ],
    'Oracle': ['ora-', 'oracle error', 'oracleclient', 'oracle database'],
    'MySQL': ['mysql error', 'mysqldb', 'mysqlclient'],
    'PostgreSQL': ['postgresql error', 'postgres error', 'npgsql'],
    'MongoDB': ['mongodb error', 'bson error', 'objectid'],
    'Cosmos DB': ['cosmos error', 'documentdb error'],
    'Azure SQL': ['azure sql', 'sql azure'],
    'Entity Framework': ['entity framework', 'system.data.entity']
}

found_patterns = []
for db_type, patterns in db_patterns.items():
    for pattern in patterns:
        # Use word boundaries for short patterns to avoid false positives
        if len(pattern) <= 4:
            # For short patterns, check if it's a whole word or part of known phrases
            if pattern in response_text:
                # Additional check: make sure it's not part of common words
                if pattern == 'oci':
                    # Skip 'oci' as it's too common in words like "association", "social", etc.
                    continue
                found_patterns.append(f"{db_type} (found: '{pattern}')")
        else:
            if pattern in response_text:
                found_patterns.append(f"{db_type} (found: '{pattern}')")

# Prioritize SQL Server indicators
if sql_server_indicators:
    print("  [CONFIRMED] SQL Server Indicators:")
    for indicator in sql_server_indicators:
        print(f"    - {indicator}")

if found_patterns:
    print("  Other potential database indicators found:")
    for pattern in found_patterns:
        print(f"    - {pattern}")
elif not sql_server_indicators:
    print("  No obvious database error patterns found in response")
print()

# Analyze response structure
print("RESPONSE STRUCTURE ANALYSIS:")
print("-" * 80)
try:
    # Use best_data if available, otherwise parse response
    if best_data is not None:
        data = best_data
    else:
        data = response.json()
    
    # Check if it's a list or dict
    if isinstance(data, dict):
        print(f"  Response type: Dictionary with {len(data)} keys")
        print(f"  Top-level keys: {list(data.keys())[:10]}")
        
        # Look for common database response patterns
        if 'rows' in data:
            rows_type = 'dictionary' if isinstance(data['rows'], dict) else 'list' if isinstance(data['rows'], list) else 'other'
            rows_count = len(data['rows']) if isinstance(data['rows'], (dict, list)) else 'N/A'
            print(f"  [OK] Found 'rows' key ({rows_type}) with {rows_count} records")
        if 'data' in data:
            print("  [OK] Found 'data' key (common API pattern)")
        if 'results' in data:
            print("  [OK] Found 'results' key (common API pattern)")
        if 'items' in data:
            print("  [OK] Found 'items' key (common API pattern)")
        if 'total' in data or 'count' in data:
            print("  [OK] Found pagination/count keys")
        if 'error' in data or 'message' in data:
            print("  [WARN] Found error/message keys - checking content...")
            if 'error' in data:
                print(f"    Error: {str(data['error'])[:200]}")
            if 'message' in data:
                print(f"    Message: {str(data['message'])[:200]}")
                
    elif isinstance(data, list):
        print(f"  Response type: List with {len(data)} items")
        if len(data) > 0:
            print(f"  First item type: {type(data[0]).__name__}")
            if isinstance(data[0], dict):
                print(f"  First item keys: {list(data[0].keys())[:10]}")
    
    # Check for SQL-like field naming (snake_case, UPPER_CASE, PascalCase)
    def check_naming_convention(obj, depth=0):
        if depth > 2:  # Limit recursion
            return
        if isinstance(obj, dict):
            for key in obj.keys():
                if '_' in key and key.isupper():
                    return "UPPER_SNAKE_CASE (common in SQL databases)"
                elif '_' in key:
                    return "snake_case (common in PostgreSQL, MySQL)"
                elif key[0].isupper() and any(c.isupper() for c in key[1:]):
                    return "PascalCase (common in .NET/SQL Server)"
            # Recurse into nested objects
            for value in obj.values():
                if isinstance(value, (dict, list)):
                    result = check_naming_convention(value, depth + 1)
                    if result:
                        return result
        elif isinstance(obj, list) and len(obj) > 0:
            return check_naming_convention(obj[0], depth + 1)
        return None
    
    naming = check_naming_convention(data)
    if naming:
        print(f"  Naming convention: {naming}")
    
    # Count records if available
    record_count = 0
    if isinstance(data, list):
        record_count = len(data)
    elif isinstance(data, dict):
        # Check for 'rows' key first (API returns rows as a dictionary)
        if 'rows' in data:
            if isinstance(data['rows'], dict):
                record_count = len(data['rows'])
                print(f"  Found 'rows' dictionary with {record_count} records")
            elif isinstance(data['rows'], list):
                record_count = len(data['rows'])
                print(f"  Found 'rows' list with {record_count} records")
        # Try to find count in other common keys
        for key in ['data', 'results', 'items', 'records', 'businesses']:
            if key in data:
                if isinstance(data[key], list):
                    record_count = len(data[key])
                    break
                elif isinstance(data[key], dict):
                    record_count = len(data[key])
                    break
        if 'total' in data:
            total = data.get('total', 'N/A')
            print(f"  Total records (from 'total' field): {total}")
            if isinstance(total, (int, float)) and total > record_count:
                record_count = total
        if 'count' in data:
            count = data.get('count', 'N/A')
            print(f"  Count (from 'count' field): {count}")
            if isinstance(count, (int, float)) and count > record_count:
                record_count = count
    
    if record_count > 0:
        print(f"  [OK] Found {record_count} records in response")
    else:
        print("  [WARN] No records found or unable to determine count")
    
    print()
    print("FULL RESPONSE:")
    print("-" * 80)
    print(json.dumps(data, indent=2)[:5000])  # First 5000 chars
    if len(json.dumps(data)) > 5000:
        print(f"\n... (truncated, total length: {len(json.dumps(data))} chars)")
        
except ValueError as e:
    print("  Response is not valid JSON")
    print(f"  Error: {e}")
    print()
    print("RAW RESPONSE (first 2000 chars):")
    print("-" * 80)
    print(response.text[:2000])

print()
print("=" * 80)
print("DATABASE IDENTIFICATION SUMMARY:")
print("=" * 80)
print("Based on reverse engineering and analysis:")
print("  • Server: Microsoft-IIS/10.0")
print("  • Framework: ASP.NET 4.0")
print("  • Hosting: Azure (app-be-web-prod.azurewebsites.net)")
print()
print("CONFIRMED DATABASE: SQL Server")
print("  Evidence:")
print("    1. Stored procedure name: usp_FILING_WebSearch")
print("       (usp_ prefix is SQL Server convention)")
print("    2. Error message revealed: 'usp_FILING_WebSearch'")
print("    3. XML parsing errors (common in SQL Server)")
print("    4. ASP.NET stack typically uses SQL Server")
print()
print("Note: Any 'oci' matches are false positives")
print("      (likely matching 'soci' in words like 'association')")
print("=" * 80)
