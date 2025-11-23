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
auth_token = "eyJraWQiOiJFMlZPcEN4WTJiM1NLRGFEbi1GUktrT2Z5Q3lSWW5ZVU8tOVgtcE84RE9VIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULjk4RVhBdDUzQkdkZHZxX2FmQXlNcmpRbUotV012SWVfVGhVU2piZjMzZHMiLCJpc3MiOiJodHRwczovL2lkbS5zb3MuY2EuZ292L29hdXRoMi9kZWZhdWx0IiwiYXVkIjoiYXBpOi8vZGVmYXVsdCIsImlhdCI6MTc2MzA3NzQwNywiZXhwIjoxNzYzMDgxMDA3LCJjaWQiOiIwb2Fjc3phNzEwb1dRWTFtZDR4NiIsInVpZCI6IjAwdXN1Zmxqcmc2bm54MEhDNHg3Iiwic2NwIjpbIm9wZW5pZCJdLCJhdXRoX3RpbWUiOjE3NjMwNzc0MDYsInN1YiI6InNoaXZhbXNzaW5nOTZAZ21haWwuY29tIn0.gMpeKV8-bG1JyIntXh81A_W0yjodwFUrr_KA8Na4SMC3dv8R3QET-K07Y5Q45BBH4bR53hhQUNTCGwZsEcfw4BVui4rDcIgC27JJ4h7Tm-1H5gIckHBGOEteFtT78XkZXD52I26HxhN2LL3FK5L6h-1707bJKTjjvJ0mCYKzrM9xN255-GhqU13tDNXA4cP903sSd7cf12n7r3_rT7y-G1tihuEQ_UH_M2oUnEFUhylMfscJDc4WtJ7M6WnztL0s5lmUa5EsYrVXMU-3IoLRTfaDQ3LSCva26u7rAei-BVP9yovn2ogBQgc610UD5lobQXQjakjLjNRRLWhs8f9lhw"

# Cookies from browser - IMPORTANT: These are session-specific and expire
# Update these by copying the Cookie header from browser Network tab
# Key cookies: Incapsula (visid_incap, incap_ses, nlbi), reese84, ASP.NET_SessionId
browser_cookies = "visid_incap_2857225=wT0ZCqWEQS20gvQHV4Ncbw0xomgAAAAAQUIPAAAAAADB6UhTs6KUkEu0YFUIFXtW; visid_incap_992756=8AoQZZkRQo2mA5Yrnc4KLroyomgAAAAAQUIPAAAAAAA9xae9DhUhtDv7QBmHD3D1; _ga_4PN0044LRV=GS2.1.s1755561599$o1$g1$t1755563356$j60$l0$h0; _ga_HJBXJ6E4E0=GS2.1.s1755899626$o3$g1$t1755899670$j16$l0$h0; _ga_2RE0XT2L0F=GS2.1.s1756323476$o1$g1$t1756323698$j1$l0$h0; _ga_75V2BNQ3DR=GS2.1.s1756332862$o2$g1$t1756332862$j60$l0$h0; _ga_DF674HWF28=GS2.1.s1757616373$o1$g1$t1757616521$j60$l0$h0; _ga_G17MN7HXHK=GS2.1.s1757616540$o1$g0$t1757616542$j58$l0$h0; visid_incap_2299457=EJIBssNwSDCD34xMDTArBbrm0WgAAAAAQUIPAAAAAAATrj2Q0E7Ct0Ygod7Fndq2; _ga_7M1ZZPXDBL=GS2.1.s1758595098$o3$g1$t1758595131$j27$l0$h0; _ga_CXDCWN357W=GS2.1.s1758906420$o1$g1$t1758906450$j30$l0$h0; _ga_ZTZK04QGW2=GS2.1.s1758908794$o2$g1$t1758908794$j60$l0$h0; _hjSessionUser_1388900=eyJpZCI6ImQyZmU2NjA1LTg0OTItNTQ5Mi1iMGJmLTlhZGY1N2ZkMGY2ZCIsImNyZWF0ZWQiOjE3NTkxNzE4Nzg4MDUsImV4aXN0aW5nIjp0cnVlfQ==; _ga_MSJG9B0DQE=GS2.1.s1761962599$o4$g1$t1761963476$j38$l0$h0; nmstat=c511e09e-acc1-5edb-d337-1e4ec10fef88; __utmz=158387685.1761963577.2.2.utmcsr=reservecalifornia.com|utmccn=(referral)|utmcmd=referral|utmcct=/; _ga_NQRMQVQ7T5=GS2.1.s1761963576$o1$g1$t1761963730$j60$l0$h0; ABTasty=uid=xetpfvqgr3mn54ns&fst=1762232950017&pst=-1&cst=1762232950017&ns=1&pvt=1&pvis=1&th=; _ga_006F1FGTXR=GS2.1.s1762232950$o2$g0$t1762232963$j47$l0$h0; _ga_WLDEF7NZZ2=GS2.1.s1762296720$o2$g0$t1762296720$j60$l0$h0; _ga_69TD0KNT0F=GS2.1.s1762296720$o10$g1$t1762296720$j60$l0$h0; _ga_PXR8P55JR4=GS2.1.s1762296720$o2$g0$t1762296720$j60$l0$h0; _ga_VDDSW2MN2F=GS2.1.s1762296720$o2$g0$t1762296720$j60$l0$h0; __utma=158387685.1412306014.1753992556.1761963577.1762898616.3; _ga=GA1.2.1412306014.1753992556; calosba._km_id-2d9f94aea6f8103bdd0b3447fc8546d2d=Aanlg81HTKV9KRhVKXl3zjNjN2P7NtQh; calosba._km_user_name-2d9f94aea6f8103bdd0b3447fc8546d2d=; calosba._km_lead_collection-2d9f94aea6f8103bdd0b3447fc8546d2d=false; _ga_2KMN5NQW5J=GS2.1.s1762898614$o1$g1$t1762899398$j1$l0$h0; ASP.NET_SessionId=uyu3qd2oo0lficawk4tjugo2; nlbi_2299457=fmuNX9qcP0D4l2thyPrJvAAAAACkSrWqv0+9KiezkU8w/sTD; nlbi_2857225=fn80BDwjTBO0DF635Oz8RAAAAAARlyV7UNhLwA7IVVUu9+W1; incap_ses_363_2857225=7Vd2JpMzvj/REb9gn6IJBZ5GFmkAAAAAnkcLH2KyycT47lnnjozYHg==; incap_ses_363_2299457=5/8yHusG7jp0NL9gn6IJBadGFmkAAAAAwP4i81MiRMS1tkLQTCgaNQ==; incap_ses_413_2299457=EnC+CRiQEk7e0540WUW7BUpKFmkAAAAAjSzkTBkhZRCADQw6GVlJVA==; incap_ses_413_2857225=m6OGX8C50k8k56A0WUW7BfZKFmkAAAAAzw9qzJy54XXBTW/cgWlPVw==; incap_ses_341_2299457=r4HyCkrhHTEpZ5PkwXm7BA9eFmkAAAAAdCguNQAJzbj8WWeqlepZTA==; incap_ses_396_2299457=kEXCFkDZVE9Ubt1F8N9+BY1iFmkAAAAAoxe3M9FqOMUkc58vi/5T3w==; incap_ses_396_2857225=8ow4In/kZC6Qb91F8N9+BY5iFmkAAAAAKBXl1U5oKItMKLUfeffR2Q==; incap_ses_414_2299457=QwDKDYPGTBda0y7c19K+BYpjFmkAAAAA46OKm/0NUI4/+dLoydcw6w==; incap_ses_362_2299457=P5WDN8FWAFs6AHBiJRUGBUZmFmkAAAAA6zPNzxUA3v7cPlr8V36Qig==; incap_ses_605_2857225=SKnbOtK+vhQe2vnSVGRlCJNnFmkAAAAAtGCQ5FxOFmg70TeY9yxyIw==; incap_ses_605_2299457=n2+HC0BV60Jd2/nSVGRlCJNnFmkAAAAAfnxHFVifJqF2mjyikM769A==; incap_ses_397_2299457=/5f9SbTZcialx//sbm2CBeRrFmkAAAAAwmxyvPtWSZAzQdFWk+6DxQ==; reese84=3:3xvzxUha3Nf4ppgoIhLEzA==:eZYgkiDwWWzdEK7/iSCSir7HMSl79Cmelp/TAOY+9LTi6Bg21FRQr585qph5+VF9KHZjg9D8kI9k4/2r2gAUF/rvwnyYa19fshnlTYRzhIHB/AyYyjfIjQ7oJnQ22CBhoZLSvuInW8uB/8z2st+rn2Q3qigqetbTFA5PXstQEHXKhcrWD/GawPXsKf5tnjKoxeGlo8n/PMbUQh0U8A16EGj5QoBtXxk6ryWykw8klifIYqXO3Man8MNK0DxrSU8rytRqG97YKIxF8wfyeTGQRvPq6PYuEPD5quZXVnlqehR5zF73k517scQdgG5ecnjS8vY9Gdi6ZwSyydcKjOugxEgRd9/j1mO7uaBJg9eaBZyci4VQQyOF2ZTeC6PYLHmJvpCq3yGWowzCZPnp+HZeXRZyRhNPrFTxlx2Tu0FoJ4pwsu6XCYnEsc8lNb1HWgSDLCMzJauOnhdhBRNfrjo4r6B9SEYknYypiX0OlJqZqQg=:bKhj0AQo1UhqVdgyrQu8D83N1qwfpfghLyBVjwShu6A=; incap_ses_397_2857225=RvwAA21ITAjDx//sbm2CBeVrFmkAAAAAlqVlQoHuMp7j0hFLQZA8nA==; okta-oauth-redirect-params={%22responseType%22:%22code%22%2C%22state%22:%228QiDl3vvMApEAuGfctDSX4OkWq8CzNUWV8nwd5N0ARYaUOV0V1wo1IoCfMosxrsq%22%2C%22nonce%22:%22h89vyYJAS1ReEP9h03hl1PNwVQedsM0I5Z0y2peqrOkd2RlxunjhbYkU2yNXiHBh%22%2C%22scopes%22:[%22openid%22]%2C%22clientId%22:%220oacsza710oWQY1md4x6%22%2C%22urls%22:{%22issuer%22:%22https://idm.sos.ca.gov/oauth2/default%22%2C%22authorizeUrl%22:%22https://idm.sos.ca.gov/oauth2/default/v1/authorize%22%2C%22userinfoUrl%22:%22https://idm.sos.ca.gov/oauth2/default/v1/userinfo%22%2C%22tokenUrl%22:%22https://idm.sos.ca.gov/oauth2/default/v1/token%22%2C%22revokeUrl%22:%22https://idm.sos.ca.gov/oauth2/default/v1/revoke%22%2C%22logoutUrl%22:%22https://idm.sos.ca.gov/oauth2/default/v1/logout%22}%2C%22ignoreSignature%22:false}; okta-oauth-nonce=h89vyYJAS1ReEP9h03hl1PNwVQedsM0I5Z0y2peqrOkd2RlxunjhbYkU2yNXiHBh; okta-oauth-state=8QiDl3vvMApEAuGfctDSX4OkWq8CzNUWV8nwd5N0ARYaUOV0V1wo1IoCfMosxrsq; nlbi_2299457_2147483392=1373Tn0W8zbd0yIdyPrJvAAAAABqxJ2iqACg8qhpymClhzQw"

# Parse cookies into dict
def parse_cookies(cookie_string):
    """Parse cookie string into dictionary"""
    cookie_dict = {}
    if cookie_string:
        for cookie in cookie_string.split('; '):
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookie_dict[key] = value
    return cookie_dict

cookies_dict = parse_cookies(browser_cookies)

# Use requests Session to maintain cookies automatically
session = requests.Session()
session.cookies.update(cookies_dict)

# Global variables for credential management
failed_records = []  # Store record IDs that failed due to auth
auth_failed = False  # Flag to track if we need new credentials

def check_token_expiration(token):
    """Check if JWT token is expired or will expire soon"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None, None
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        token_data = json.loads(decoded)
        
        exp_timestamp = token_data.get('exp')
        if exp_timestamp:
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            now = datetime.now()
            time_until_expiry = (exp_datetime - now).total_seconds()
            return exp_datetime, time_until_expiry
    except:
        pass
    return None, None

def update_credentials(new_token=None, new_cookies=None):
    """Update authentication token and/or cookies"""
    global auth_token, browser_cookies, cookies_dict, headers, session
    
    if new_token:
        auth_token = new_token
        headers["Authorization"] = auth_token
        print(f"  Token updated")
    
    if new_cookies:
        browser_cookies = new_cookies
        cookies_dict = parse_cookies(browser_cookies)
        session.cookies.clear()
        session.cookies.update(cookies_dict)
        print(f"  Cookies updated")

def prompt_for_new_credentials():
    """Prompt user to provide new token and/or cookies"""
    global auth_failed
    
    print()
    print("=" * 80)
    print("AUTHENTICATION FAILED - CREDENTIALS NEEDED")
    print("=" * 80)
    print()
    print("The API request failed due to expired or invalid credentials.")
    print("Please provide new credentials from your browser:")
    print()
    print("1. Open browser Network tab")
    print("2. Make a request to the API")
    print("3. Copy the Authorization header value (the JWT token)")
    print("4. Copy the Cookie header value")
    print()
    
    new_token = input("Enter new Authorization token (or press Enter to skip): ").strip()
    new_cookies = input("Enter new Cookie string (or press Enter to skip): ").strip()
    
    if new_token or new_cookies:
        update_credentials(new_token if new_token else None, new_cookies if new_cookies else None)
        auth_failed = False
        print()
        print("Credentials updated. Retrying failed requests...")
        print()
        return True
    else:
        print()
        print("No credentials provided. Please update the script manually and restart.")
        return False

# Check token expiration at startup
exp_datetime, time_until_expiry = check_token_expiration(auth_token)
if exp_datetime:
    if time_until_expiry <= 0:
        print("WARNING: Auth token is EXPIRED! Please update it before running.")
        print(f"   Token expired at: {exp_datetime}")
    elif time_until_expiry < 300:  # Less than 5 minutes
        print(f"WARNING: Auth token expires in {time_until_expiry/60:.1f} minutes!")
        print(f"   Token expires at: {exp_datetime}")
    else:
        print(f"Token valid until: {exp_datetime} ({time_until_expiry/3600:.1f} hours remaining)")

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
    "STATUS_ID": "1",
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
print("COMPREHENSIVE DATA EXTRACTION STRATEGY")
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
    global auth_failed
    
    payload = base_payload.copy()
    payload["SEARCH_VALUE"] = search_value
    
    try:
        # Use session to maintain cookies across requests
        response = session.post(url, json=payload, headers=headers, timeout=15)
        
        # Update cookies from response (server may send new session cookies)
        if response.cookies:
            session.cookies.update(response.cookies)
        
        stats['total_queries'] += 1
        
        if response.status_code == 200:
            # Check if response is HTML (authentication failure - Incapsula challenge page)
            content_type = response.headers.get('Content-Type', '').lower()
            response_text = response.text.strip()
            response_text_lower = response_text.lower()
            
            if 'text/html' in content_type or response_text_lower.startswith('<html') or 'incapsula' in response_text_lower:
                # This is an HTML response, likely authentication failure
                stats['failed_queries'] += 1
                auth_failed = True
                print(f"    Authentication failed for search '{search_value}' (received HTML/Incapsula challenge)")
                if prompt_for_new_credentials():
                    # Retry with new credentials
                    return fetch_records(search_value)
                else:
                    return {}
            
            try:
                data = response.json()
                if 'rows' in data and isinstance(data['rows'], dict):
                    stats['successful_queries'] += 1
                    auth_failed = False  # Reset flag on success
                    return data['rows']
                else:
                    stats['failed_queries'] += 1
                    return {}
            except json.JSONDecodeError as e:
                # Check if it's HTML masquerading as JSON error
                if response_text_lower.startswith('<html') or 'incapsula' in response_text_lower:
                    stats['failed_queries'] += 1
                    auth_failed = True
                    print(f"    Authentication failed for search '{search_value}' (HTML response detected)")
                    if prompt_for_new_credentials():
                        return fetch_records(search_value)
                    else:
                        return {}
                else:
                    stats['failed_queries'] += 1
                    print(f"    JSON decode error for search '{search_value}': {str(e)[:100]}")
                    return {}
        elif response.status_code == 401:
            # Authentication failed (explicit 401)
            stats['failed_queries'] += 1
            auth_failed = True
            print(f"    Authentication failed for search '{search_value}' (401 Unauthorized)")
            if prompt_for_new_credentials():
                # Retry with new credentials
                return fetch_records(search_value)
            else:
                return {}
        else:
            stats['failed_queries'] += 1
            return {}
    except Exception as e:
        stats['failed_queries'] += 1
        print(f"    Error: {str(e)[:50]}")
        return {}
    
    return {}

def fetch_record_detail(record_id, retry_on_auth_fail=True):
    """Fetch detailed information for a record ID"""
    global auth_failed, failed_records
    
    url = detail_url_template.format(record_id)
    
    # Use same headers but remove Content-Type for GET request
    get_headers = headers.copy()
    get_headers.pop("Content-Type", None)
    
    # Add browser-like headers for GET requests
    get_headers.update({
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Sec-CH-UA": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    })
    
    try:
        # Use session to maintain cookies and update them from responses
        response = session.get(url, headers=get_headers, timeout=15)
        
        # Update cookies from response (in case server sends new ones)
        if response.cookies:
            session.cookies.update(response.cookies)
        stats['enrichment_queries'] += 1
        
        if response.status_code == 200:
            # Check if response has content before parsing JSON
            if not response.text or not response.text.strip():
                stats['enrichment_failed'] += 1
                return None
            
            # Check if response is HTML (authentication failure - Incapsula challenge page)
            content_type = response.headers.get('Content-Type', '').lower()
            response_text_lower = response.text.strip().lower()
            
            if 'text/html' in content_type or response_text_lower.startswith('<html') or 'incapsula' in response_text_lower:
                # This is an HTML response, likely authentication failure
                stats['enrichment_failed'] += 1
                auth_failed = True
                if record_id not in failed_records:
                    failed_records.append(record_id)
                print(f"    Authentication failed for record {record_id} (received HTML/Incapsula challenge)")
                
                if retry_on_auth_fail:
                    if prompt_for_new_credentials():
                        # Retry with new credentials
                        return fetch_record_detail(record_id, retry_on_auth_fail=False)
                    else:
                        return None
                else:
                    return None
            
            try:
                data = response.json()
                stats['enrichment_successful'] += 1
                auth_failed = False  # Reset flag on success
                
                # Check for session-timeout header to monitor session expiration
                if 'session-timeout' in response.headers:
                    timeout_seconds = int(response.headers.get('session-timeout', 0))
                    if timeout_seconds > 0:
                        timeout_hours = timeout_seconds / 3600
                        # Only log once
                        if not hasattr(fetch_record_detail, '_session_timeout_logged'):
                            print(f"    Session timeout: {timeout_hours:.1f} hours remaining")
                            fetch_record_detail._session_timeout_logged = True
                
                return data
            except json.JSONDecodeError as e:
                stats['enrichment_failed'] += 1
                # Check if it's HTML masquerading as JSON error
                if response_text_lower.startswith('<html') or 'incapsula' in response_text_lower:
                    auth_failed = True
                    if record_id not in failed_records:
                        failed_records.append(record_id)
                    print(f"    Authentication failed for record {record_id} (HTML response detected)")
                    
                    if retry_on_auth_fail:
                        if prompt_for_new_credentials():
                            return fetch_record_detail(record_id, retry_on_auth_fail=False)
                        else:
                            return None
                    else:
                        return None
                
                # Only print error for first few failures to avoid spam
                if not hasattr(fetch_record_detail, '_json_error_count'):
                    fetch_record_detail._json_error_count = 0
                if fetch_record_detail._json_error_count < 3:
                    print(f"    JSON decode error for record {record_id}: {str(e)[:100]}")
                    print(f"    Response preview: {response.text[:200]}")
                    fetch_record_detail._json_error_count += 1
                return None
        else:
            stats['enrichment_failed'] += 1
            if response.status_code == 401:
                # Authentication failed
                auth_failed = True
                if record_id not in failed_records:
                    failed_records.append(record_id)
                print(f"    Authorization failed for record {record_id}")
                
                if retry_on_auth_fail:
                    if prompt_for_new_credentials():
                        # Retry with new credentials
                        return fetch_record_detail(record_id, retry_on_auth_fail=False)
                    else:
                        return None
                else:
                    return None
            elif response.status_code != 200:
                print(f"    Error {response.status_code} for record {record_id}")
            return None
    except Exception as e:
        stats['enrichment_failed'] += 1
        print(f"    Exception fetching detail for {record_id}: {str(e)[:100]}")
        return None

def extract_detail_fields(detail_data):
    """Extract Status and Statement of Info Due Date from detail response"""
    status_value = None
    statement_due_date = None
    
    if not detail_data:
        return {
            'STATUS_DETAIL': None,
            'STATEMENT_OF_INFO_DUE_DATE': None
        }
    
    if 'DRAWER_DETAIL_LIST' not in detail_data:
        # Debug: Print structure if DRAWER_DETAIL_LIST is missing
        if not hasattr(extract_detail_fields, '_debug_printed'):
            print(f"    DEBUG: DRAWER_DETAIL_LIST not found. Available keys: {list(detail_data.keys())}")
            extract_detail_fields._debug_printed = True
        return {
            'STATUS_DETAIL': None,
            'STATEMENT_OF_INFO_DUE_DATE': None
        }
    
    if not isinstance(detail_data['DRAWER_DETAIL_LIST'], list):
        if not hasattr(extract_detail_fields, '_debug_printed'):
            print(f"    DEBUG: DRAWER_DETAIL_LIST is not a list. Type: {type(detail_data['DRAWER_DETAIL_LIST'])}")
            extract_detail_fields._debug_printed = True
        return {
            'STATUS_DETAIL': None,
            'STATEMENT_OF_INFO_DUE_DATE': None
        }
    
    # Debug: Print all available labels (only for first record)
    if not hasattr(extract_detail_fields, '_debug_printed'):
        labels_found = [item.get('LABEL') for item in detail_data['DRAWER_DETAIL_LIST'] if item.get('LABEL')]
        print(f"    DEBUG: Available labels in DRAWER_DETAIL_LIST: {labels_found}")
        extract_detail_fields._debug_printed = True
    
    for item in detail_data['DRAWER_DETAIL_LIST']:
        if not isinstance(item, dict):
            continue
        label = item.get('LABEL', '')
        if label == 'Status':
            status_value = item.get('VALUE')
        # Try multiple possible label variations
        elif 'Statement' in label and 'Due Date' in label:
            statement_due_date = item.get('VALUE')
        elif label == 'Statement of Info Due Date':
            statement_due_date = item.get('VALUE')
        elif label == 'Statement of Information Due Date':
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
processed_records = set()  # Track which records we've successfully processed

for i, (record_key, record) in enumerate(all_records.items(), 1):
    record_id = record.get('ID')
    
    if record_id is None:
        continue
    
    # Skip if already processed successfully
    if record_id in processed_records:
        continue
    
    # Fetch detail
    detail_data = fetch_record_detail(record_id)
    
    if detail_data:
        # Debug: Save first detail response to file for inspection
        if not hasattr(fetch_record_detail, '_sample_saved') and detail_data:
            with open('sample_detail_response.json', 'w', encoding='utf-8') as f:
                json.dump(detail_data, f, indent=2, ensure_ascii=False)
            print(f"    DEBUG: Saved sample detail response to sample_detail_response.json")
            fetch_record_detail._sample_saved = True
        
        # Extract fields
        extracted = extract_detail_fields(detail_data)
        record['STATUS_DETAIL'] = extracted['STATUS_DETAIL']
        record['STATEMENT_OF_INFO_DUE_DATE'] = extracted['STATEMENT_OF_INFO_DUE_DATE']
        processed_records.add(record_id)  # Mark as processed
    else:
        # If auth failed, we'll retry failed records later
        if auth_failed:
            print(f"  Pausing enrichment due to authentication failure...")
            break
    
    # Progress update
    if i % 50 == 0:
        elapsed = time.time() - enrichment_start
        print(f"  Progress: {i}/{len(all_records)} ({i/len(all_records)*100:.1f}%) - "
              f"Success: {stats['enrichment_successful']}, Failed: {stats['enrichment_failed']} - "
              f"{elapsed/60:.1f} min")
    
    # Rate limiting
    time.sleep(0.1)

# Retry failed records if credentials were updated
if failed_records:
    print()
    print("=" * 80)
    print("RETRYING FAILED RECORDS")
    print("=" * 80)
    print(f"Retrying {len(failed_records)} records that failed due to authentication...")
    print()
    
    for record_id in failed_records[:]:  # Copy list to avoid modification during iteration
        record_key = str(record_id)
        if record_key in all_records:
            record = all_records[record_key]
            detail_data = fetch_record_detail(record_id, retry_on_auth_fail=False)
            
            if detail_data:
                extracted = extract_detail_fields(detail_data)
                record['STATUS_DETAIL'] = extracted['STATUS_DETAIL']
                record['STATEMENT_OF_INFO_DUE_DATE'] = extracted['STATEMENT_OF_INFO_DUE_DATE']
                failed_records.remove(record_id)  # Remove from failed list on success
                processed_records.add(record_id)
            
            time.sleep(0.1)  # Rate limiting
    
    # Continue with remaining records
    if not auth_failed:
        print()
        print("Continuing with remaining records...")
        print()
        for i, (record_key, record) in enumerate(all_records.items(), 1):
            record_id = record.get('ID')
            
            if record_id is None or record_id in processed_records:
                continue
            
            detail_data = fetch_record_detail(record_id)
            
            if detail_data:
                extracted = extract_detail_fields(detail_data)
                record['STATUS_DETAIL'] = extracted['STATUS_DETAIL']
                record['STATEMENT_OF_INFO_DUE_DATE'] = extracted['STATEMENT_OF_INFO_DUE_DATE']
                processed_records.add(record_id)
            
            if i % 50 == 0:
                elapsed = time.time() - enrichment_start
                print(f"  Progress: {i}/{len(all_records)} ({i/len(all_records)*100:.1f}%) - "
                      f"Success: {stats['enrichment_successful']}, Failed: {stats['enrichment_failed']} - "
                      f"{elapsed/60:.1f} min")
            
            time.sleep(0.1)

enrichment_elapsed = time.time() - enrichment_start
print()
print(f"  Enrichment completed: {stats['enrichment_queries']} queries in {enrichment_elapsed/60:.1f} minutes")
print(f"  Successful: {stats['enrichment_successful']}, Failed: {stats['enrichment_failed']}")
print()

# Save results
output_file = f"all_records_{int(time.time())}.json"
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

