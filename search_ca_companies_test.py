"""
Search CA SOS API for companies from main_company.xlsx and match by zip code.

This script:
1. Reads main_company.xlsx
2. For each company (if legal_name doesn't contain '&'), searches CA SOS API
3. Matches results by name similarity
4. Compares zip codes from Principal Address with phy_zip
5. Extracts Statement of Info Due Date if zip matches
"""

import requests
import json
import time
import pandas as pd
import base64
from datetime import datetime
import os
import re
from difflib import SequenceMatcher

# API URLs
search_url = "https://bizfileonline.sos.ca.gov/api/Records/businesssearch"
detail_url_template = "https://bizfileonline.sos.ca.gov/api/FilingDetail/business/{}/false"

# Updated token
auth_token = "eyJraWQiOiJFMlZPcEN4WTJiM1NLRGFEbi1GUktrT2Z5Q3lSWW5ZVU8tOVgtcE84RE9VIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFALjk4RVhBdDUzQkdkZHZxX2FmQXlNcmpRbUotV012SWVfVGhVU2piZjMzZHMiLCJpc3MiOiJodHRwczovL2lkbS5zb3MuY2EuZ292L29hdXRoMi9kZWZhdWx0IiwiYXVkIjoiYXBpOi8vZGVmYXVsdCIsImlhdCI6MTc2MzA3NzQwNywiZXhwIjoxNzYzMDgxMDA3LCJjaWQiOiIwb2Fjc3phNzEwb1dRWTFtZDR4NiIsInVpZCI6IjAwdXN1Zmxqcmc2bm54MEhDNHg3Iiwic2NwIjpbIm9wZW5pZCJdLCJhdXRoX3RpbWUiOjE3NjMwNzc0MDYsInN1YiI6InNoaXZhbXNzaW5nOTZAZ21haWwuY29tIn0.gMpeKV8-bG1JyIntXh81A_W0yjodwFUrr_KA8Na4SMC3dv8R3QET-K07Y5Q45BBH4bR53hhQUNTCGwZsEcfw4BVui4rDcIgC27JJ4h7Tm-1H5gIckHBGOEteFtT78XkZXD52I26HxhN2LL3FK5L6h-1707bJKTjjvJ0mCYKzrM9xN255-GhqU13tDNXA4cP903sSd7cf12n7r3_rT7y-G1tihuEQ_UH_M2oUnEFUhylMfscJDc4WtJ7M6WnztL0s5lmUa5EsYrVXMU-3IoLRTfaDQ3LSCva26u7rAei-BVP9yovn2ogBQgc610UD5lobQXQjakjLjNRRLWhs8f9lhw"

# Cookies from browser - IMPORTANT: These are session-specific and expire
# Update these by copying the Cookie header from browser Network tab
browser_cookies = "visid_incap_2857225=wT0ZCqWEQS20gvQHV4Ncbw0xomgAAAAAQUIPAAAAAADB6UhTs6KUkEu0YFUIFXtW; visid_incap_992756=8AoQZZkRQo2mA5Yrnc4KLroyomgAAAAAQUIPAAAAAAA9xae9DhUhtDv7QBmHD3D1; _ga_4PN0044LRV=GS2.1.s1755561599$o1$g1$t1755563356$j60$l0$h0; _ga_HJBXJ6E4E0=GS2.1.s1755899626$o3$g1$t1755899670$j16$l0$h0; _ga_2RE0XT2L0F=GS2.1.s1756323476$o1$g1$t1756323698$j1$l0$h0; _ga_75V2BNQ3DR=GS2.1.s1756332862$o2$g1$t1756332862$j60$l0$h0; _ga_DF674HWF28=GS2.1.s1757616373$o1$g1$t1757616521$j60$l0$h0; _ga_G17MN7HXHK=GS2.1.s1757616540$o1$g0$t1757616542$j58$l0$h0; visid_incap_2299457=EJIBssNwSDCD34xMDTArBbrm0WgAAAAAQUIPAAAAAAATrj2Q0E7Ct0Ygod7Fndq2; _ga_7M1ZZPXDBL=GS2.1.s1758595098$o3$g1$t1758595131$j27$l0$h0; _ga_CXDCWN357W=GS2.1.s1758906420$o1$g1$t1758906450$j30$l0$h0; _ga_ZTZK04QGW2=GS2.1.s1758908794$o2$g1$t1758908794$j60$l0$h0; _hjSessionUser_1388900=eyJpZCI6ImQyZmU2NjA1LTg0OTItNTQ5Mi1iMGJmLTlhZGY1N2ZkMGY2ZCIsImNyZWF0ZWQiOjE3NTkxNzE4Nzg4MDUsImV4aXN0aW5nIjp0cnVlfQ==; _ga_MSJG9B0DQE=GS2.1.s1761962599$o4$g1$t1761963476$j38$l0$h0; nmstat=c511e09e-acc1-5edb-d337-1e4ec10fef88; __utmz=158387685.1761963577.2.2.utmcsr=reservecalifornia.com|utmccn=(referral)|utmcmd=referral|utmcct=/; _ga_NQRMQVQ7T5=GS2.1.s1761963576$o1$g1$t1761963730$j60$l0$h0; ABTasty=uid=xetpfvqgr3mn54ns&fst=1762232950017&pst=-1&cst=1762232950017&ns=1&pvt=1&pvis=1&th=; _ga_006F1FGTXR=GS2.1.s1762232950$o2$g0$t1762232963$j47$l0$h0; _ga_WLDEF7NZZ2=GS2.1.s1762296720$o2$g0$t1762296720$j60$l0$h0; _ga_69TD0KNT0F=GS2.1.s1762296720$o10$g1$t1762296720$j60$l0$h0; _ga_PXR8P55JR4=GS2.1.s1762296720$o2$g0$t1762296720$j60$l0$h0; _ga_VDDSW2MN2F=GS2.1.s1762296720$o2$g0$t1762296720$j60$l0$h0; __utma=158387685.1412306014.1753992556.1761963577.1762898616.3; _ga=GA1.2.1412306014.1753992556; calosba._km_id-2d9f94aea6f8103bdd0b3447fc8546d2d=Aanlg81HTKV9KRhVKXl3zjNjN2P7NtQh; calosba._km_user_name-2d9f94aea6f8103bdd0b3447fc8546d2d=; calosba._km_lead_collection-2d9f94aea6f8103bdd0b3447fc8546d2d=false; _ga_2KMN5NQW5J=GS2.1.s1762898614$o1$g1$t1762899398$j1$l0$h0; ASP.NET_SessionId=uyu3qd2oo0lficawk4tjugo2; nlbi_2299457=fmuNX9qcP0D4l2thyPrJvAAAAACkSrWqv0+9KiezkU8w/sTD; nlbi_2857225=fn80BDwjTBO0DF635Oz8RAAAAAARlyV7UNhLwA7IVVUu9+W1; incap_ses_363_2857225=7Vd2JpMzvj/REb9gn6IJBZ5GFmkAAAAAnkcLH2KyycT47lnnjozYHg==; incap_ses_363_2299457=5/8yHusG7jp0NL9gn6IJBadGFmkAAAAAwP4i81MiRMS1tkLQTCgaNQ==; incap_ses_413_2299457=EnC+CRiQEk7e0540WUW7BUpKFmkAAAAAjSzkTBkhZRCADQw6GVlJVA==; incap_ses_413_2857225=m6OGX8C50k8k56A0WUW7BfZKFmkAAAAAzw9qzJy54XXBTW/cgWlPVw==; incap_ses_341_2299457=r4HyCkrhHTEpZ5PkwXm7BA9eFmkAAAAAdCguNQAJzbj8WWeqlepZTA==; incap_ses_396_2299457=kEXCFkDZVE9Ubt1F8N9+BY1iFmkAAAAAoxe3M9FqOMUkc58vi/5T3w==; incap_ses_396_2857225=8ow4In/kZC6Qb91F8N9+BY5iFmkAAAAAKBXl1U5oKItMKLUfeffR2Q==; incap_ses_414_2299457=QwDKDYPGTBda0y7c19K+BYpjFmkAAAAA46OKm/0NUI4/+dLoydcw6w==; incap_ses_362_2299457=P5WDN8FWAFs6AHBiJRUGBUZmFmkAAAAA6zPNzxUA3v7cPlr8V36Qig==; incap_ses_605_2857225=SKnbOtK+vhQe2vnSVGRlCJNnFmkAAAAAtGCQ5FxOFmg70TeY9yxyIw==; incap_ses_605_2299457=n2+HC0BV60Jd2/nSVGRlCJNnFmkAAAAAfnxHFVifJqF2mjyikM769A==; incap_ses_397_2299457=/5f9SbTZcialx//sbm2CBeRrFmkAAAAAwmxyvPtWSZAzQdFWk+6DxQ==; reese84=3:3xvzxUha3Nf4ppgoIhLEzA==:eZYgkiDwWWzdEK7/iSCSir7HMSl79Cmelp/TAOY+9LTi6Bg21FRQr585qph5+VF9KHZjg9D8kI9k4/2r2gAUF/rvwnyYa19fshnlTYRzhIHB/AyYyjfIjQ7oJnQ22CBhoZLSvuInW8uB/8z2st+rn2Q3qigqetbTFA5PXstQEHXKhcrWD/GawPXsKf5tnjKoxeGlo8n/PMbUQh0U8A16EGj5QoBtXxk6ryWykw8klifIYqXO3Man8MNK0DxrSU8rytRqG97YKIxF8wfyeTGQRvPq6PYuEPD5quZXVnlqehR5zF73k517scQdgG5ecnjS8vY9Gdi6ZwSyydcKjOugxEgRd9/j1mO7uaBJg9eaBZyci4VQQyOF2ZTeC6PYLHmJvpCq3yGWowzCZPnp+HZeXRZyRhNPrFTxlx2Tu0FoJ4pwsu6XCYnEsc8lNb1HWgSDLCMzJauOnhdhBRNfrjo4r6B9SEYknYypiX0OlJqZqQg=:bKhj0AQo1UhqVdgyrQu8D83N1qwfpfghLyBVjwShu6A=; incap_ses_397_2857225=RvwAA21ITAjDx//sbm2CBeRrFmkAAAAAlqVlQoHuMp7j0hFLQZA8nA==; okta-oauth-redirect-params={%22responseType%22:%22code%22%2C%22state%22:%228QiDl3vvMApEAuGfctDSX4OkWq8CzNUWV8nwd5N0ARYaUOV0V1wo1IoCfMosxrsq%22%2C%22nonce%22:%22h89vyYJAS1ReEP9h03hl1PNwVQedsM0I5Z0y2peqrOkd2RlxunjhbYkU2yNXiHBh%22%2C%22scopes%22:[%22openid%22]%2C%22clientId%22:%220oacsza710oWQY1md4x6%22%2C%22urls%22:{%22issuer%22:%22https://idm.sos.ca.gov/oauth2/default%22%2C%22authorizeUrl%22:%22https://idm.sos.ca.gov/oauth2/default/v1/authorize%22%2C%22tokenUrl%22:%22https://idm.sos.ca.gov/oauth2/default/v1/token%22%2C%22revokeUrl%22:%22https://idm.sos.ca.gov/oauth2/default/v1/revoke%22%2C%22logoutUrl%22:%22https://idm.sos.ca.gov/oauth2/default/v1/logout%22}%2C%22ignoreSignature%22:false}; okta-oauth-nonce=h89vyYJAS1ReEP9h03hl1PNwVQedsM0I5Z0y2peqrOkd2RlxunjhbYkU2yNXiHBh; okta-oauth-state=8QiDl3vvMApEAuGfctDSX4OkWq8CzNUWV8nwd5N0ARYaUOV0V1wo1IoCfMosxrsq; nlbi_2299457_2147483392=1373Tn0W8zbd0yIdyPrJvAAAAABqxJ2iqACg8qhpymClhzQw"

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
auth_failed = False  # Flag to track if we need new credentials

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

def test_credentials(test_token=None, test_cookies=None):
    """Test if provided credentials work by making a test API call"""
    # Create a temporary session for testing
    test_session = requests.Session()
    
    # Parse and set test cookies if provided
    if test_cookies:
        test_cookies_dict = parse_cookies(test_cookies)
        test_session.cookies.update(test_cookies_dict)
    
    # Create test headers
    test_headers = headers.copy()
    if test_token:
        test_headers["Authorization"] = test_token
    
    # Make a simple test request (search for a common term)
    test_payload = base_search_payload.copy()
    test_payload["SEARCH_VALUE"] = "TEST"
    test_payload["SEARCH_FILTER_TYPE_ID"] = "1"
    
    try:
        response = test_session.post(search_url, json=test_payload, headers=test_headers, timeout=10)
        
        # Check if response is valid JSON (not HTML/Incapsula)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '').lower()
            response_text_lower = response.text.strip().lower()
            
            if 'text/html' in content_type or response_text_lower.startswith('<html') or 'incapsula' in response_text_lower:
                return False, "Received HTML/Incapsula challenge page"
            
            try:
                data = response.json()
                # If we get JSON (even if empty), credentials are working
                return True, "Credentials validated successfully"
            except json.JSONDecodeError:
                return False, "Invalid JSON response"
        elif response.status_code == 401:
            return False, "401 Unauthorized - Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"Test failed: {str(e)[:100]}"

def prompt_for_new_credentials():
    """Prompt user to provide new token and/or cookies - keeps asking until valid credentials are provided"""
    global auth_failed
    
    while True:
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
        print("(Press Ctrl+C to exit if you want to update the script manually)")
        print()
        
        new_token = input("Enter new Authorization token (or press Enter to skip): ").strip()
        new_cookies = input("Enter new Cookie string (or press Enter to skip): ").strip()
        
        if not new_token and not new_cookies:
            print()
            print("No credentials provided.")
            response = input("Exit and update script manually? (y/n): ").strip().lower()
            if response == 'y':
                print()
                print("Exiting. Please update the script with new credentials and restart.")
                return False
            else:
                continue  # Ask again
        
        # Test the credentials before accepting them
        print()
        print("Testing credentials...")
        is_valid, message = test_credentials(new_token if new_token else None, new_cookies if new_cookies else None)
        
        if is_valid:
            # Credentials are valid, update them
            update_credentials(new_token if new_token else None, new_cookies if new_cookies else None)
            auth_failed = False
            print(f"SUCCESS: {message}")
            print()
            print("Credentials validated and updated. Continuing...")
            print()
            return True
        else:
            print(f"FAILED: Credentials test failed: {message}")
            print("Please provide correct credentials.")
            # Continue loop to ask again

headers = {
    "Content-Type": "application/json",
    "Authorization": auth_token,
    "Origin": "https://bizfileonline.sos.ca.gov",
    "Referer": "https://bizfileonline.sos.ca.gov/search/business",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "*/*"
}

base_search_payload = {
    "SEARCH_VALUE": "",
    "SEARCH_FILTER_TYPE_ID": "0",
    "SEARCH_TYPE_ID": "1",
    "FILING_TYPE_ID": "",
    "STATUS_ID": "0",
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

def search_business(search_value, search_filter_type_id="0"):
    """Search for business using CA SOS API"""
    global auth_failed
    
    payload = base_search_payload.copy()
    payload["SEARCH_VALUE"] = search_value
    payload["SEARCH_FILTER_TYPE_ID"] = search_filter_type_id
    
    try:
        response = session.post(search_url, json=payload, headers=headers, timeout=15)
        
        # Update cookies from response
        if response.cookies:
            session.cookies.update(response.cookies)
        
        if response.status_code == 200:
            # Check if response is HTML (authentication failure)
            content_type = response.headers.get('Content-Type', '').lower()
            response_text = response.text.strip()
            response_text_lower = response_text.lower()
            
            if 'text/html' in content_type or response_text_lower.startswith('<html') or 'incapsula' in response_text_lower:
                auth_failed = True
                print(f"    Authentication failed for search '{search_value}' (received HTML/Incapsula challenge)")
                if prompt_for_new_credentials():
                    return search_business(search_value, search_filter_type_id)
                else:
                    return None
            
            try:
                data = response.json()
                if 'rows' in data and isinstance(data['rows'], dict):
                    auth_failed = False
                    return data['rows']
                else:
                    return {}
            except json.JSONDecodeError as e:
                if response_text_lower.startswith('<html') or 'incapsula' in response_text_lower:
                    auth_failed = True
                    print(f"    Authentication failed for search '{search_value}' (HTML response detected)")
                    if prompt_for_new_credentials():
                        return search_business(search_value, search_filter_type_id)
                    else:
                        return {}
                else:
                    print(f"    JSON decode error for search '{search_value}': {str(e)[:100]}")
                    return {}
        elif response.status_code == 401:
            auth_failed = True
            print(f"    Authentication failed for search '{search_value}' (401 Unauthorized)")
            if prompt_for_new_credentials():
                return search_business(search_value, search_filter_type_id)
            else:
                return None
        else:
            return {}
    except Exception as e:
        print(f"    Error searching '{search_value}': {str(e)[:50]}")
        return {}
    
    return {}

def get_business_detail(record_id):
    """Get detailed information for a business record"""
    global auth_failed
    
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
        response = session.get(url, headers=get_headers, timeout=15)
        
        # Update cookies from response
        if response.cookies:
            session.cookies.update(response.cookies)
        
        if response.status_code == 200:
            # Check if response is HTML (authentication failure)
            content_type = response.headers.get('Content-Type', '').lower()
            response_text_lower = response.text.strip().lower()
            
            if 'text/html' in content_type or response_text_lower.startswith('<html') or 'incapsula' in response_text_lower:
                auth_failed = True
                print(f"    Authentication failed for detail {record_id} (received HTML/Incapsula challenge)")
                if prompt_for_new_credentials():
                    return get_business_detail(record_id)
                else:
                    return None
            
            try:
                data = response.json()
                auth_failed = False
                return data
            except json.JSONDecodeError as e:
                if response_text_lower.startswith('<html') or 'incapsula' in response_text_lower:
                    auth_failed = True
                    print(f"    Authentication failed for detail {record_id} (HTML response detected)")
                    if prompt_for_new_credentials():
                        return get_business_detail(record_id)
                    else:
                        return None
                return None
        elif response.status_code == 401:
            auth_failed = True
            print(f"    Authentication failed for detail {record_id} (401 Unauthorized)")
            if prompt_for_new_credentials():
                return get_business_detail(record_id)
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"    Error fetching detail for {record_id}: {str(e)[:50]}")
        return None
    
    return None

def extract_zip_from_address(address):
    """Extract 5-digit zip code from address string"""
    if not address:
        return None
    
    # Look for 5-digit zip code pattern
    # Match last 5 consecutive digits in the string
    zip_pattern = r'\b(\d{5})\b'
    matches = re.findall(zip_pattern, address)
    
    if matches:
        # Return the last match (usually the zip code at the end)
        return matches[-1]
    
    return None

def clean_title(title):
    """Remove the number part from title like 'Z & L LOGISTICS SERVICES INC (5921441)'"""
    if not title:
        return ""
    
    # Remove pattern like " (5921441)" at the end
    title_cleaned = re.sub(r'\s*\(\d+\)\s*$', '', str(title))
    return title_cleaned.strip()

def calculate_similarity(str1, str2):
    """Calculate similarity percentage between two strings"""
    if not str1 or not str2:
        return 0.0
    
    # Normalize strings: uppercase, remove extra spaces
    str1 = str(str1).upper().strip()
    str2 = str(str2).upper().strip()
    
    if not str1 or not str2:
        return 0.0
    
    # Use SequenceMatcher for similarity
    similarity = SequenceMatcher(None, str1, str2).ratio()
    return similarity * 100  # Return as percentage

def find_best_match(legal_name, search_results):
    """Find the best matching record from search results based on TITLE similarity"""
    if not search_results or not legal_name:
        return None, 0.0
    
    best_match = None
    best_similarity = 0.0
    
    for record_id, record_data in search_results.items():
        title = record_data.get('TITLE', '')
        
        # TITLE can be a list or string
        if isinstance(title, list):
            if title:
                title = title[0]  # Take first title if list
            else:
                continue
        
        # Clean the title (remove number part)
        cleaned_title = clean_title(title)
        
        # Calculate similarity
        similarity = calculate_similarity(legal_name, cleaned_title)
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = (record_id, record_data)
    
    return best_match, best_similarity

def find_all_matches_with_similarity(legal_name, search_results):
    """Find all matches with their similarity percentages, sorted by similarity (descending)"""
    if not search_results or not legal_name:
        return []
    
    matches = []
    
    for record_id, record_data in search_results.items():
        title = record_data.get('TITLE', '')
        
        # TITLE can be a list or string
        if isinstance(title, list):
            if title:
                title = title[0]  # Take first title if list
            else:
                continue
        
        # Clean the title (remove number part)
        cleaned_title = clean_title(title)
        
        # Calculate similarity
        similarity = calculate_similarity(legal_name, cleaned_title)
        
        matches.append({
            'record_id': record_id,
            'record_data': record_data,
            'title': title,
            'cleaned_title': cleaned_title,
            'similarity': similarity
        })
    
    # Sort by similarity (descending)
    matches.sort(key=lambda x: x['similarity'], reverse=True)
    
    return matches

def extract_detail_fields(detail_data):
    """Extract Principal Address zip and Statement of Info Due Date from detail response"""
    principal_address = None
    principal_zip = None
    statement_due_date = None
    
    if not detail_data or 'DRAWER_DETAIL_LIST' not in detail_data:
        return principal_zip, statement_due_date
    
    if not isinstance(detail_data['DRAWER_DETAIL_LIST'], list):
        return principal_zip, statement_due_date
    
    for item in detail_data['DRAWER_DETAIL_LIST']:
        if not isinstance(item, dict):
            continue
        
        label = item.get('LABEL', '')
        value = item.get('VALUE')
        
        # Extract Principal Address
        if label == 'Principal Address':
            principal_address = value
            if principal_address:
                principal_zip = extract_zip_from_address(principal_address)
        
        # Extract Statement of Info Due Date
        elif label == 'Statement of Info Due Date':
            statement_due_date = value
        elif 'Statement' in label and 'Due Date' in label:
            # Fallback for variations of the label
            statement_due_date = value
    
    return principal_zip, statement_due_date

def create_base_result(row, row_index):
    """Create base result dictionary with common fields"""
    legal_name = row.get('legal_name', '').strip() if pd.notna(row.get('legal_name')) else ''
    phy_zip = str(row.get('phy_zip', '')).strip() if pd.notna(row.get('phy_zip')) else ''
    
    return {
        'row_index': row_index,
        'legal_name': legal_name,
        'phy_zip': phy_zip,
        'phone': row.get('phone', '') if pd.notna(row.get('phone')) else '',
        'cell_phone': row.get('cell_phone', '') if pd.notna(row.get('cell_phone')) else '',
        'phy_street': row.get('phy_street', '') if pd.notna(row.get('phy_street')) else '',
        'phy_city': row.get('phy_city', '') if pd.notna(row.get('phy_city')) else '',
        'email_address': row.get('email_address', '') if pd.notna(row.get('email_address')) else '',
        'search_status': '',
        'matched_record_id': None,
        'matched_title': None,
        'match_similarity': None,
        'principal_zip': None,
        'zip_match': False,
        'statement_due_date': None,
        'error_message': None,
        'match_criteria': None  # e.g., "Highest fuzzy match", "Zip matched", etc.
    }

def process_company_row_no_special_chars(row, row_index, legal_name, phy_zip):
    """Process company row when legal_name has no special characters - handles multiple matches"""
    results = []
    
    # First try SEARCH_FILTER_TYPE_ID = "1"
    search_results = search_business(legal_name, "1")
    time.sleep(0.1)  # Rate limiting
    
    # If no results, try with SEARCH_FILTER_TYPE_ID = "0"
    if not search_results:
        search_results = search_business(legal_name, "0")
        time.sleep(0.1)  # Rate limiting
    
    if not search_results:
        base_result = create_base_result(row, row_index)
        base_result['search_status'] = 'NOT_FOUND'
        base_result['error_message'] = 'No results found in search'
        return [base_result]
    
    # Get all matches with similarity scores, sorted by similarity (descending)
    all_matches = find_all_matches_with_similarity(legal_name, search_results)
    
    if not all_matches:
        base_result = create_base_result(row, row_index)
        base_result['search_status'] = 'NO_MATCH'
        base_result['error_message'] = 'No matching record found in search results'
        return [base_result]
    
    # Find the highest similarity score
    highest_similarity = all_matches[0]['similarity']
    
    # Group matches by similarity (to handle ties)
    matches_by_similarity = {}
    for match in all_matches:
        sim = match['similarity']
        if sim not in matches_by_similarity:
            matches_by_similarity[sim] = []
        matches_by_similarity[sim].append(match)
    
    # Check matches starting from highest similarity
    highest_fuzzy_matches = []
    zip_matched_matches = []
    all_checked_matches = []
    
    # Process matches in order of similarity
    for similarity in sorted(matches_by_similarity.keys(), reverse=True):
        matches_at_this_level = matches_by_similarity[similarity]
        
        # Track if this is the highest similarity level
        is_highest_level = (similarity == highest_similarity)
        
        for match in matches_at_this_level:
            record_id = match['record_id']
            matched_title = match['title']
            
            # Get business detail
            detail_data = get_business_detail(record_id)
            time.sleep(0.1)  # Rate limiting
            
            if not detail_data:
                continue
            
            # Extract zip and statement due date
            principal_zip, statement_due_date = extract_detail_fields(detail_data)
            
            # Create result for this match
            result = create_base_result(row, row_index)
            result['matched_record_id'] = record_id
            result['matched_title'] = matched_title
            result['match_similarity'] = f"{similarity:.2f}%"
            result['principal_zip'] = principal_zip
            result['statement_due_date'] = statement_due_date
            
            # Check zip match
            zip_matches = False
            if principal_zip and phy_zip:
                principal_zip_clean = re.sub(r'\D', '', str(principal_zip))[-5:] if principal_zip else ''
                phy_zip_clean = re.sub(r'\D', '', str(phy_zip))[-5:] if phy_zip else ''
                zip_matches = (principal_zip_clean == phy_zip_clean)
            
            result['zip_match'] = zip_matches
            
            # Set match criteria
            if is_highest_level:
                result['match_criteria'] = 'Highest fuzzy match'
                highest_fuzzy_matches.append(result)
            else:
                result['match_criteria'] = f'Fuzzy match ({similarity:.2f}%)'
            
            if zip_matches:
                result['match_criteria'] += ' + Zip matched'
                zip_matched_matches.append(result)
                result['search_status'] = 'MATCHED (zip verified)'
            else:
                if principal_zip:
                    result['search_status'] = 'MATCHED (zip mismatch)'
                    result['error_message'] = f'Zip code mismatch: Principal={principal_zip}, Excel={phy_zip}'
                else:
                    result['search_status'] = 'MATCHED (no zip in principal address)'
                    result['error_message'] = 'Could not extract zip code from Principal Address'
            
            all_checked_matches.append(result)
    
    # Determine which results to return
    final_results = []
    seen_record_ids = set()
    
    # Priority 1: If we have zip-matched results, include all of them
    if zip_matched_matches:
        for zm_match in zip_matched_matches:
            if zm_match['matched_record_id'] not in seen_record_ids:
                final_results.append(zm_match)
                seen_record_ids.add(zm_match['matched_record_id'])
    
    # Priority 2: Include highest fuzzy matches (if not already included)
    for hf_match in highest_fuzzy_matches:
        if hf_match['matched_record_id'] not in seen_record_ids:
            final_results.append(hf_match)
            seen_record_ids.add(hf_match['matched_record_id'])
    
    # Priority 3: If no zip matches and we have highest fuzzy matches that don't match zip,
    # also check and include next highest matches (up to top 3) to give options
    if not zip_matched_matches and highest_fuzzy_matches:
        # We already included highest fuzzy matches above
        # Include a few more high-similarity matches for reference (if they exist)
        for match in all_checked_matches:
            if match['matched_record_id'] not in seen_record_ids:
                # Include if similarity is within 5% of highest
                if match['similarity'] >= (highest_similarity - 5.0):
                    final_results.append(match)
                    seen_record_ids.add(match['matched_record_id'])
                    # Limit to top 3 additional matches
                    if len([r for r in final_results if r['matched_record_id'] not in [hf['matched_record_id'] for hf in highest_fuzzy_matches]]) >= 3:
                        break
    
    # If no results were created, return at least the highest match
    if not final_results and all_checked_matches:
        final_results = [all_checked_matches[0]]
    
    return final_results

def process_company_row_with_special_chars(row, row_index, legal_name, phy_zip):
    """Process company row when legal_name has special characters ('&' or '-') - handles multiple matches"""
    results = []
    
    # First try SEARCH_FILTER_TYPE_ID = "0"
    search_results = search_business(legal_name, "0")
    time.sleep(0.1)  # Rate limiting
    
    # If no results, try with SEARCH_FILTER_TYPE_ID = "1"
    if not search_results:
        search_results = search_business(legal_name, "1")
        time.sleep(0.1)  # Rate limiting
    
    if not search_results:
        base_result = create_base_result(row, row_index)
        base_result['search_status'] = 'NOT_FOUND'
        base_result['error_message'] = 'No results found in search'
        return [base_result]
    
    # Get all matches with similarity scores, sorted by similarity (descending)
    # Note: Special characters are included in the matching
    all_matches = find_all_matches_with_similarity(legal_name, search_results)
    
    if not all_matches:
        base_result = create_base_result(row, row_index)
        base_result['search_status'] = 'NO_MATCH'
        base_result['error_message'] = 'No matching record found in search results'
        return [base_result]
    
    # Find the highest similarity score
    highest_similarity = all_matches[0]['similarity']
    
    # Group matches by similarity (to handle ties)
    matches_by_similarity = {}
    for match in all_matches:
        sim = match['similarity']
        if sim not in matches_by_similarity:
            matches_by_similarity[sim] = []
        matches_by_similarity[sim].append(match)
    
    # Check matches starting from highest similarity
    highest_fuzzy_matches = []
    zip_matched_matches = []
    all_checked_matches = []
    
    # Process matches in order of similarity
    for similarity in sorted(matches_by_similarity.keys(), reverse=True):
        matches_at_this_level = matches_by_similarity[similarity]
        
        # Track if this is the highest similarity level
        is_highest_level = (similarity == highest_similarity)
        
        for match in matches_at_this_level:
            record_id = match['record_id']
            matched_title = match['title']
            
            # Get business detail
            detail_data = get_business_detail(record_id)
            time.sleep(0.1)  # Rate limiting
            
            if not detail_data:
                continue
            
            # Extract zip and statement due date
            principal_zip, statement_due_date = extract_detail_fields(detail_data)
            
            # Create result for this match
            result = create_base_result(row, row_index)
            result['matched_record_id'] = record_id
            result['matched_title'] = matched_title
            result['match_similarity'] = f"{similarity:.2f}%"
            result['principal_zip'] = principal_zip
            result['statement_due_date'] = statement_due_date
            
            # Check zip match
            zip_matches = False
            if principal_zip and phy_zip:
                principal_zip_clean = re.sub(r'\D', '', str(principal_zip))[-5:] if principal_zip else ''
                phy_zip_clean = re.sub(r'\D', '', str(phy_zip))[-5:] if phy_zip else ''
                zip_matches = (principal_zip_clean == phy_zip_clean)
            
            result['zip_match'] = zip_matches
            
            # Set match criteria
            if is_highest_level:
                result['match_criteria'] = 'Highest fuzzy match'
                highest_fuzzy_matches.append(result)
            else:
                result['match_criteria'] = f'Fuzzy match ({similarity:.2f}%)'
            
            if zip_matches:
                result['match_criteria'] += ' + Zip matched'
                zip_matched_matches.append(result)
                result['search_status'] = 'MATCHED (zip verified)'
            else:
                if principal_zip:
                    result['search_status'] = 'MATCHED (zip mismatch)'
                    result['error_message'] = f'Zip code mismatch: Principal={principal_zip}, Excel={phy_zip}'
                else:
                    result['search_status'] = 'MATCHED (no zip in principal address)'
                    result['error_message'] = 'Could not extract zip code from Principal Address'
            
            all_checked_matches.append(result)
    
    # Determine which results to return
    final_results = []
    seen_record_ids = set()
    
    # Priority 1: If we have zip-matched results, include all of them
    if zip_matched_matches:
        for zm_match in zip_matched_matches:
            if zm_match['matched_record_id'] not in seen_record_ids:
                final_results.append(zm_match)
                seen_record_ids.add(zm_match['matched_record_id'])
    
    # Priority 2: Include highest fuzzy matches (if not already included)
    for hf_match in highest_fuzzy_matches:
        if hf_match['matched_record_id'] not in seen_record_ids:
            final_results.append(hf_match)
            seen_record_ids.add(hf_match['matched_record_id'])
    
    # Priority 3: If no zip matches and we have highest fuzzy matches that don't match zip,
    # also check and include next highest matches (up to top 3) to give options
    if not zip_matched_matches and highest_fuzzy_matches:
        # We already included highest fuzzy matches above
        # Include a few more high-similarity matches for reference (if they exist)
        for match in all_checked_matches:
            if match['matched_record_id'] not in seen_record_ids:
                # Include if similarity is within 5% of highest
                if match['similarity'] >= (highest_similarity - 5.0):
                    final_results.append(match)
                    seen_record_ids.add(match['matched_record_id'])
                    # Limit to top 3 additional matches
                    if len([r for r in final_results if r['matched_record_id'] not in [hf['matched_record_id'] for hf in highest_fuzzy_matches]]) >= 3:
                        break
    
    # If no results were created, return at least the highest match
    if not final_results and all_checked_matches:
        final_results = [all_checked_matches[0]]
    
    return final_results

def process_company_row(row, row_index):
    """Process a single company row from Excel"""
    legal_name = row.get('legal_name', '').strip() if pd.notna(row.get('legal_name')) else ''
    phy_zip = str(row.get('phy_zip', '')).strip() if pd.notna(row.get('phy_zip')) else ''
    
    result = create_base_result(row, row_index)
    
    # Skip if legal_name is empty
    if not legal_name:
        result['search_status'] = 'SKIPPED (empty legal_name)'
        return [result]
    
    # Check if legal_name contains special characters ('-' or '&')
    has_special_chars = ('&' in legal_name or '-' in legal_name)
    
    # Process based on whether special characters are present
    if has_special_chars:
        # Process with special characters: try "0" first, then "1"
        return process_company_row_with_special_chars(row, row_index, legal_name, phy_zip)
    else:
        # Process without special characters: try "1" first, then "0"
        return process_company_row_no_special_chars(row, row_index, legal_name, phy_zip)

def main():
    """Main function to process Excel file"""
    print("=" * 80)
    print("CA SOS COMPANY SEARCH AND ZIP MATCHING")
    print("=" * 80)
    print()
    
    excel_file = "main_company_test.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"Error: File '{excel_file}' not found!")
        return
    
    print(f"Reading Excel file: {excel_file}")
    print()
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file, engine='openpyxl')
        
        # Map column letters to column names (assuming first row is header)
        # Column C = index 2, D = 3, H = 7, J = 9, K = 10, L = 11, O = 14
        # We'll use the actual column names from the Excel file
        
        print(f"Total rows in Excel: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        print()
        
        # Process each row
        results = []
        start_time = time.time()
        
        print("Processing companies...")
        print("=" * 80)
        
        for index, row in df.iterrows():
            result_list = process_company_row(row, index + 2)  # +2 because Excel rows start at 1, and we have header
            # result_list is a list (may contain multiple matches for same company)
            results.extend(result_list)
            
            # Progress update
            if (index + 1) % 10 == 0:
                elapsed = time.time() - start_time
                print(f"  Progress: {index + 1}/{len(df)} ({((index + 1)/len(df)*100):.1f}%) - {elapsed:.1f}s")
        
        print()
        print("=" * 80)
        print("PROCESSING COMPLETE")
        print("=" * 80)
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Save to Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"ca_company_search_results_{timestamp}.xlsx"
        
        print(f"Saving results to: {output_file}")
        results_df.to_excel(output_file, index=False, engine='openpyxl')
        
        # Print summary
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        # Count unique companies (by row_index)
        unique_companies = len(set(r['row_index'] for r in results))
        total_results = len(results)
        
        skipped = len([r for r in results if 'SKIPPED' in r.get('search_status', '')])
        not_found = len([r for r in results if r.get('search_status') == 'NOT_FOUND'])
        matched = len([r for r in results if 'MATCHED' in r.get('search_status', '')])
        zip_matched = len([r for r in results if r.get('zip_match') == True])
        
        print(f"Total unique companies processed: {unique_companies}")
        print(f"Total result rows (may have multiple matches per company): {total_results}")
        print(f"Skipped (contains special chars or empty): {skipped}")
        print(f"Not found in search: {not_found}")
        print(f"Matched: {matched}")
        print(f"Zip code matched: {zip_matched}")
        print(f"Zip code mismatch: {matched - zip_matched}")
        print()
        print(f"Results saved to: {output_file}")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

