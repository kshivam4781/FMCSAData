import requests
import json
import time
import pandas as pd
import base64
from datetime import datetime
import os
import glob

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

def test_api_connection(test_record_id=None):
    """Test if API is working with current credentials"""
    if test_record_id is None:
        # Use a dummy record ID for testing - just check if we get proper response
        test_record_id = "12345"  # Dummy ID to test auth
    
    url = detail_url_template.format(test_record_id)
    
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
                return False, "Received HTML/Incapsula challenge page"
            
            # Try to parse as JSON
            try:
                data = response.json()
                # If we get JSON (even if it's an error response), auth is working
                return True, "API connection successful"
            except json.JSONDecodeError:
                return False, "Invalid JSON response"
        elif response.status_code == 401:
            return False, "401 Unauthorized"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"Exception: {str(e)[:100]}"

def prompt_for_new_credentials(test_record_id=None):
    """Prompt user to provide new token and/or cookies, keep asking until API works"""
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
        
        new_token = input("Enter new Authorization token (or press Enter to skip): ").strip()
        new_cookies = input("Enter new Cookie string (or press Enter to skip): ").strip()
        
        if not new_token and not new_cookies:
            print()
            print("No credentials provided. Please provide at least one credential.")
            continue
        
        # Update credentials
        update_credentials(new_token if new_token else None, new_cookies if new_cookies else None)
        
        # Test if API is working
        print()
        print("Testing API connection...")
        api_works, message = test_api_connection(test_record_id)
        
        if api_works:
            print(f"✓ {message}")
            auth_failed = False
            print()
            print("Credentials validated. Continuing with enrichment...")
            print()
            return True
        else:
            print(f"✗ API test failed: {message}")
            print("Please provide correct credentials.")
            continue

headers = {
    "Content-Type": "application/json",
    "Authorization": auth_token,
    "Origin": "https://bizfileonline.sos.ca.gov",
    "Referer": "https://bizfileonline.sos.ca.gov/search/business",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "*/*"
}

def find_latest_step1_file():
    """Find the latest Step1 JSON file"""
    step1_files = glob.glob("Step1_*.json")
    if not step1_files:
        return None
    
    # Sort by modification time, most recent first
    step1_files.sort(key=os.path.getmtime, reverse=True)
    return step1_files[0]

def get_user_confirmed_file():
    """Get file from user with confirmation"""
    # Find latest file
    latest_file = find_latest_step1_file()
    
    if latest_file:
        print("=" * 80)
        print("FOUND LATEST STEP1 FILE")
        print("=" * 80)
        print(f"Latest file: {latest_file}")
        file_size = os.path.getsize(latest_file) / (1024 * 1024)  # Size in MB
        mod_time = datetime.fromtimestamp(os.path.getmtime(latest_file))
        print(f"File size: {file_size:.2f} MB")
        print(f"Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        confirm = input("Use this file? (y/n): ").strip().lower()
        if confirm == 'y':
            return latest_file
    
    # User wants different file or no latest file found
    print()
    print("=" * 80)
    print("SELECT FILE")
    print("=" * 80)
    
    # List all Step1 files
    step1_files = glob.glob("Step1_*.json")
    if step1_files:
        print("\nAvailable Step1 files:")
        for i, f in enumerate(step1_files, 1):
            file_size = os.path.getsize(f) / (1024 * 1024)
            mod_time = datetime.fromtimestamp(os.path.getmtime(f))
            print(f"  {i}. {f} ({file_size:.2f} MB, {mod_time.strftime('%Y-%m-%d %H:%M:%S')})")
        print()
    
    while True:
        filename = input("Enter filename (must exist): ").strip()
        
        if not filename:
            print("Filename cannot be empty. Please try again.")
            continue
        
        # Add .json extension if not provided
        if not filename.endswith('.json'):
            filename += '.json'
        
        if os.path.exists(filename):
            return filename
        else:
            print(f"File '{filename}' not found. Please try again.")
            if step1_files:
                print("Available files listed above.")

def fetch_record_detail(record_id, retry_on_auth_fail=True):
    """Fetch detailed information for a record ID - keeps retrying with credential prompts until success"""
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
    
    # Keep retrying until we get a successful response
    while True:
        try:
            # Use session to maintain cookies and update them from responses
            response = session.get(url, headers=get_headers, timeout=15)
            
            # Update cookies from response (in case server sends new ones)
            if response.cookies:
                session.cookies.update(response.cookies)
            
            if response.status_code == 200:
                # Check if response has content before parsing JSON
                if not response.text or not response.text.strip():
                    return None
                
                # Check if response is HTML (authentication failure - Incapsula challenge page)
                content_type = response.headers.get('Content-Type', '').lower()
                response_text_lower = response.text.strip().lower()
                
                if 'text/html' in content_type or response_text_lower.startswith('<html') or 'incapsula' in response_text_lower:
                    # This is an HTML response, likely authentication failure
                    auth_failed = True
                    if record_id not in failed_records:
                        failed_records.append(record_id)
                    print(f"    Authentication failed for record {record_id} (received HTML/Incapsula challenge)")
                    
                    if retry_on_auth_fail:
                        # Keep prompting for credentials until API test passes, then retry
                        prompt_for_new_credentials(record_id)
                        continue  # Retry the request with new credentials
                    else:
                        return None
                
                try:
                    data = response.json()
                    auth_failed = False  # Reset flag on success
                    # Remove from failed records if it was there
                    if record_id in failed_records:
                        failed_records.remove(record_id)
                    return data
                except json.JSONDecodeError as e:
                    # Check if it's HTML masquerading as JSON error
                    if response_text_lower.startswith('<html') or 'incapsula' in response_text_lower:
                        auth_failed = True
                        if record_id not in failed_records:
                            failed_records.append(record_id)
                        print(f"    Authentication failed for record {record_id} (HTML response detected)")
                        
                        if retry_on_auth_fail:
                            # Keep prompting for credentials until API test passes, then retry
                            prompt_for_new_credentials(record_id)
                            continue  # Retry the request with new credentials
                        else:
                            return None
                    
                    return None
            else:
                if response.status_code == 401:
                    # Authentication failed
                    auth_failed = True
                    if record_id not in failed_records:
                        failed_records.append(record_id)
                    print(f"    Authorization failed for record {record_id}")
                    
                    if retry_on_auth_fail:
                        # Keep prompting for credentials until API test passes, then retry
                        prompt_for_new_credentials(record_id)
                        continue  # Retry the request with new credentials
                    else:
                        return None
                return None
        except Exception as e:
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
        return {
            'STATUS_DETAIL': None,
            'STATEMENT_OF_INFO_DUE_DATE': None
        }
    
    if not isinstance(detail_data['DRAWER_DETAIL_LIST'], list):
        return {
            'STATUS_DETAIL': None,
            'STATEMENT_OF_INFO_DUE_DATE': None
        }
    
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

# Main execution
print("=" * 80)
print("STEP 2: ENRICH RECORDS WITH SOI DUE DATE")
print("=" * 80)
print()

# Get confirmed file from user
json_file = get_user_confirmed_file()

if not json_file:
    print("No file selected. Exiting.")
    exit()

print()
print(f"Loading file: {json_file}")
print()

# Load JSON file
try:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading file: {e}")
    exit()

# Determine structure
if 'records' in data:
    all_records = data['records']
    print(f"Found {len(all_records)} records in 'records' key")
elif isinstance(data, dict):
    # Assume the dict itself contains records
    all_records = data
    print(f"Found {len(all_records)} records in root dict")
else:
    print("Unknown JSON structure. Expected 'records' key or dict of records.")
    exit()

print()
print("=" * 80)
print("CHECKING EXISTING SOI DUE DATE DATA")
print("=" * 80)

# Check which records already have SOI Due Date
enrichment_start = time.time()
processed_records = set()  # Track which records we've successfully processed
already_enriched = 0

for record_key, record in all_records.items():
    record_id = record.get('ID')
    if record_id is None:
        continue
    
    # Check if record already has SOI Due Date
    soi_due_date = record.get('STATEMENT_OF_INFO_DUE_DATE')
    if soi_due_date and str(soi_due_date).strip() and str(soi_due_date).lower() != 'none':
        processed_records.add(record_id)
        already_enriched += 1

records_to_enrich = len(all_records) - already_enriched

print(f"Total records: {len(all_records)}")
print(f"Already have SOI Due Date: {already_enriched}")
print(f"Need enrichment: {records_to_enrich}")
print()

if records_to_enrich == 0:
    print("All records already have SOI Due Date. No enrichment needed.")
    print("=" * 80)
    exit()

print("=" * 80)
print("ENRICHING RECORDS WITH DETAILED INFORMATION")
print("=" * 80)
print(f"Enriching {records_to_enrich} records with Status and Statement of Info Due Date...")
print()

stats = {
    'enrichment_queries': 0,
    'enrichment_successful': 0,
    'enrichment_failed': 0,
    'already_enriched': already_enriched
}

for i, (record_key, record) in enumerate(all_records.items(), 1):
    record_id = record.get('ID')
    
    if record_id is None:
        continue
    
    # Skip if already processed successfully
    if record_id in processed_records:
        continue
    
    # Fetch detail
    detail_data = fetch_record_detail(record_id)
    stats['enrichment_queries'] += 1
    
    if detail_data:
        # Extract fields
        extracted = extract_detail_fields(detail_data)
        record['STATUS_DETAIL'] = extracted['STATUS_DETAIL']
        record['STATEMENT_OF_INFO_DUE_DATE'] = extracted['STATEMENT_OF_INFO_DUE_DATE']
        processed_records.add(record_id)  # Mark as processed
        stats['enrichment_successful'] += 1
    else:
        stats['enrichment_failed'] += 1
        # If auth failed, we'll retry failed records later
        if auth_failed:
            print(f"  Pausing enrichment due to authentication failure...")
            break
    
    # Progress update
    processed_count = stats['enrichment_successful'] + stats['enrichment_failed']
    if processed_count % 50 == 0 and processed_count > 0:
        elapsed = time.time() - enrichment_start
        print(f"  Progress: {processed_count}/{records_to_enrich} ({processed_count/records_to_enrich*100:.1f}%) - "
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
            # Keep retrying until success (will prompt for credentials if needed)
            detail_data = fetch_record_detail(record_id, retry_on_auth_fail=True)
            stats['enrichment_queries'] += 1
            
            if detail_data:
                extracted = extract_detail_fields(detail_data)
                record['STATUS_DETAIL'] = extracted['STATUS_DETAIL']
                record['STATEMENT_OF_INFO_DUE_DATE'] = extracted['STATEMENT_OF_INFO_DUE_DATE']
                failed_records.remove(record_id)  # Remove from failed list on success
                processed_records.add(record_id)
                stats['enrichment_successful'] += 1
            else:
                stats['enrichment_failed'] += 1
            
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
            stats['enrichment_queries'] += 1
            
            if detail_data:
                extracted = extract_detail_fields(detail_data)
                record['STATUS_DETAIL'] = extracted['STATUS_DETAIL']
                record['STATEMENT_OF_INFO_DUE_DATE'] = extracted['STATEMENT_OF_INFO_DUE_DATE']
                processed_records.add(record_id)
                stats['enrichment_successful'] += 1
            else:
                stats['enrichment_failed'] += 1
            
            processed_count = stats['enrichment_successful'] + stats['enrichment_failed']
            if processed_count % 50 == 0 and processed_count > 0:
                elapsed = time.time() - enrichment_start
                print(f"  Progress: {processed_count}/{records_to_enrich} ({processed_count/records_to_enrich*100:.1f}%) - "
                      f"Success: {stats['enrichment_successful']}, Failed: {stats['enrichment_failed']} - "
                      f"{elapsed/60:.1f} min")
            
            time.sleep(0.1)

enrichment_elapsed = time.time() - enrichment_start
print()
print(f"  Enrichment completed: {stats['enrichment_queries']} queries in {enrichment_elapsed/60:.1f} minutes")
print(f"  Already had SOI Due Date: {stats['already_enriched']}")
print(f"  Newly enriched: {stats['enrichment_successful']}, Failed: {stats['enrichment_failed']}")
print()

# Save enriched results back to the SAME JSON file
# Update the original data structure
if 'records' in data:
    data['records'] = all_records
    data['enrichment_date'] = time.strftime("%Y-%m-%d %H:%M:%S")
    data['enrichment_stats'] = stats
else:
    # If original was just a dict, create new structure
    data = {
        "extraction_date": data.get('extraction_date', 'Unknown'),
        "enrichment_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "statistics": data.get('statistics', {}),
        "enrichment_stats": stats,
        "total_unique_records": len(all_records),
        "records": all_records
    }

print(f"Saving enriched data back to {json_file}...")
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Saved {len(all_records)} enriched records to: {json_file}")
print()

# Convert to Excel
print("=" * 80)
print("CONVERTING TO EXCEL")
print("=" * 80)
print("Converting enriched records to Excel format...")

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

# Save to Excel with timestamp
datetimestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
excel_file = f"Final_{datetimestamp}.xlsx"
print(f"Saving to {excel_file}...")
df.to_excel(excel_file, index=False, engine='openpyxl')
print(f"Saved {len(excel_data)} enriched records to: {excel_file}")
print("=" * 80)
print()
print(f"STEP 2 COMPLETE!")
print(f"JSON file (updated): {json_file}")
print(f"Excel file: {excel_file}")
print("=" * 80)

