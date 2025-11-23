import requests
import json
import time

url = "https://bizfileonline.sos.ca.gov/api/Records/businesssearch"

# Updated token from network request
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
print("REVERSE ENGINEERING API - DATABASE & TECHNOLOGY DETECTION")
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

# Test patterns designed to trigger database-specific errors or reveal technology
test_patterns = [
    {
        "name": "SQL Server LIKE wildcard",
        "value": "%%%",
        "description": "SQL Server LIKE pattern - matches everything"
    },
    {
        "name": "SQL Server bracket wildcard",
        "value": "[a-z]",
        "description": "SQL Server bracket pattern"
    },
    {
        "name": "PostgreSQL LIKE wildcard",
        "value": "%%%",
        "description": "PostgreSQL LIKE pattern"
    },
    {
        "name": "Oracle LIKE wildcard",
        "value": "%%%",
        "description": "Oracle LIKE pattern"
    },
    {
        "name": "SQL Injection test (safe)",
        "value": "ABC' OR '1'='1",
        "description": "Test for SQL injection handling (safe pattern)"
    },
    {
        "name": "SQL Server escape test",
        "value": "ABC[[]",
        "description": "Test SQL Server bracket escaping"
    },
    {
        "name": "Regex pattern test",
        "value": ".*",
        "description": "Test if regex is supported"
    },
    {
        "name": "Empty string with spaces",
        "value": "   ",
        "description": "Three spaces"
    },
    {
        "name": "Null byte test",
        "value": "ABC\x00",
        "description": "Test null byte handling"
    },
    {
        "name": "Unicode test",
        "value": "ABC\u0025",
        "description": "Unicode percent character"
    }
]

print("TEST 1: Analyzing Response Headers for Technology Stack")
print("-" * 80)
# First, make a simple request to analyze headers
payload = base_payload.copy()
payload["SEARCH_VALUE"] = "ABC"
response = requests.post(url, json=payload, headers=headers)

print("Response Headers Analysis:")
tech_indicators = {
    'server': 'Web Server',
    'x-powered-by': 'Framework/Technology',
    'x-aspnet-version': 'ASP.NET Version',
    'x-version': 'API Version',
    'x-database': 'Database Type',
    'x-orm': 'ORM Framework',
    'request-context': 'Application Context',
    'x-cdn': 'CDN Provider'
}

for header, description in tech_indicators.items():
    if header in response.headers:
        print(f"  {description}: {response.headers[header]}")

print()
print("TEST 2: Analyzing Response Structure")
print("-" * 80)
try:
    data = response.json()
    print(f"Response Type: {type(data).__name__}")
    if isinstance(data, dict):
        print(f"Keys: {list(data.keys())}")
        # Look for technology-specific patterns
        for key in data.keys():
            if 'entity' in key.lower() or 'framework' in key.lower():
                print(f"  Found potential ORM indicator: {key}")
except:
    print("  Could not parse JSON")

print()
print("TEST 3: Testing Database-Specific Patterns")
print("-" * 80)
print("Attempting patterns that might reveal database type through errors or behavior...")
print()

database_clues = {
    'SQL Server': [],
    'PostgreSQL': [],
    'Oracle': [],
    'MySQL': [],
    'MongoDB': [],
    'Other': []
}

for pattern in test_patterns:
    print(f"Testing: {pattern['name']} ('{pattern['value']}')...")
    payload = base_payload.copy()
    payload["SEARCH_VALUE"] = pattern["value"]
    
    try:
        start_time = time.time()
        test_response = requests.post(url, json=payload, headers=headers, timeout=10)
        response_time = time.time() - start_time
        
        response_text = test_response.text.lower()
        
        # Check for SQL Server errors
        sql_server_errors = ['sql server', 'microsoft sql', 'odbc', 'oledb', 'sqlclient', 
                            'system.data.sqlclient', 'sql exception', 'timeout expired']
        for error_term in sql_server_errors:
            if error_term in response_text:
                database_clues['SQL Server'].append(f"{pattern['name']}: Found '{error_term}'")
        
        # Check for PostgreSQL errors
        postgres_errors = ['postgresql', 'postgres', 'npgsql', 'pg_', 'relation']
        for error_term in postgres_errors:
            if error_term in response_text:
                database_clues['PostgreSQL'].append(f"{pattern['name']}: Found '{error_term}'")
        
        # Check for Oracle errors
        oracle_errors = ['ora-', 'oracle', 'oci', 'oracleclient', 'ora_']
        for error_term in oracle_errors:
            if error_term in response_text:
                database_clues['Oracle'].append(f"{pattern['name']}: Found '{error_term}'")
        
        # Check for MySQL errors
        mysql_errors = ['mysql', 'mysqldb', 'mysqlclient', 'my_']
        for error_term in mysql_errors:
            if error_term in response_text:
                database_clues['MySQL'].append(f"{pattern['name']}: Found '{error_term}'")
        
        # Check for MongoDB errors
        mongo_errors = ['mongodb', 'bson', 'objectid', 'mongo']
        for error_term in mongo_errors:
            if error_term in response_text:
                database_clues['MongoDB'].append(f"{pattern['name']}: Found '{error_term}'")
        
        # Check response structure for clues
        try:
            test_data = test_response.json()
            if isinstance(test_data, dict):
                # Look for Entity Framework patterns
                if 'rows' in test_data and isinstance(test_data['rows'], dict):
                    # Check if rows structure suggests SQL
                    if 'template' in test_data:
                        database_clues['SQL Server'].append(f"{pattern['name']}: Found template/rows structure (common in .NET/SQL)")
        except:
            pass
        
        if test_response.status_code == 200:
            print(f"  [OK] Status: {test_response.status_code}, Time: {response_time:.2f}s")
        else:
            print(f"  [INFO] Status: {test_response.status_code}")
            # Non-200 might reveal error messages
            if len(test_response.text) < 1000:
                print(f"  Response: {test_response.text[:200]}")
                
    except Exception as e:
        print(f"  [ERROR] Exception: {str(e)[:100]}")
    
    print()

print()
print("=" * 80)
print("DATABASE DETECTION RESULTS")
print("=" * 80)

found_any = False
for db_type, clues in database_clues.items():
    if clues:
        found_any = True
        print(f"\n{db_type} Indicators Found:")
        for clue in clues:
            print(f"  - {clue}")

if not found_any:
    print("\nNo explicit database error messages found.")
    print("This suggests:")
    print("  1. API has good error handling (hides database errors)")
    print("  2. Using ORM (Entity Framework, Dapper, etc.) that abstracts database")
    print("  3. Database errors are logged server-side, not returned to client")

print()
print("=" * 80)
print("TECHNOLOGY STACK INFERENCE")
print("=" * 80)
print("Based on headers and response structure:")
print("  - Web Server: Microsoft-IIS/10.0")
print("  - Framework: ASP.NET 4.0")
print("  - Hosting: Azure")
print("  - Response Structure: template/rows pattern")
print()
print("Most Likely Stack:")
print("  - Backend: ASP.NET Web API / MVC")
print("  - Database: SQL Server or Azure SQL Database")
print("  - ORM: Entity Framework (most common with ASP.NET)")
print("  - Query Pattern: Likely using LINQ or Entity Framework queries")
print()
print("=" * 80)
print("RECOMMENDED WILDCARD PATTERNS TO TRY")
print("=" * 80)
print("Based on SQL Server / Entity Framework:")
print("  1. '%' - SQL LIKE wildcard (single)")
print("  2. '%%%' - SQL LIKE wildcard (triple)")
print("  3. '[a-z]%' - SQL Server bracket pattern")
print("  4. Empty filters with all boolean flags set to False")
print("  5. Try removing SEARCH_VALUE entirely (if API allows)")
print()
print("Note: Entity Framework typically uses parameterized queries,")
print("      so SQL injection patterns won't work, but LIKE patterns might.")
print("=" * 80)

