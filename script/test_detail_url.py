import requests
import json
import base64
from datetime import datetime

# URL to test
test_url = "https://bizfileonline.sos.ca.gov/api/FilingDetail/business/371023/false"

# Auth token from the main script
auth_token = "eyJraWQiOiJFMlZPcEN4WTJiM1NLRGFEbi1GUktrT2Z5Q3lSWW5ZVU8tOVgtcE84RE9VIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULjRxa0o0YjgxWmxyeGpFWVdadGpBOEJqWkUtQ0xfSV83cHozNHB3alZZSmsiLCJpc3MiOiJodHRwczovL2lkbS5zb3MuY2EuZ292L29hdXRoMi9kZWZhdWx0IiwiYXVkIjoiYXBpOi8vZGVmYXVsdCIsImlhdCI6MTc2MzA3NTk4OSwiZXhwIjoxNzYzMDc5NTg5LCJjaWQiOiIwb2Fjc3phNzEwb1dRWTFtZDR4NiIsInVpZCI6IjAwdXN1Zmxqcmc2bm54MEhDNHg3Iiwic2NwIjpbIm9wZW5pZCJdLCJhdXRoX3RpbWUiOjE3NjMwNjc1NTksInN1YiI6InNoaXZhbXNzaW5nOTZAZ21haWwuY29tIn0.OF1mmpg9uRuB1o47X_8848HB-TvNHzB6maBwZuk3OnyE6CHk-27kOizkGPr5jzrUt11jF4Av0aeoBqhfyN_DipO9W6fO1lwcbVpq2dFc3KASWx3S0BDR2CWLxbA0QnhKieXIyUYrH8rJRgRXIxfWS09AKVJ6hoyPCHcD7coYcnn_JsZ-C03R_MMdND6y0Y3V0MxbHqyLj4GKcNH6C5_eay0_xRmSbnhgtDFE1YaoQy4pGmUQ-eT6TcMSUb2NyJ2tfSzxVyhSf1HOJ9Ep_XRA_u_AcGDRhWsKgmTnhghugPYeCdFWi17TxzZ6XA-fv3jNvPVFNwfO43vAy7Ru3EjPow"

# Cookies from browser - these are session-specific and may need to be updated
# Key cookies: Incapsula (visid_incap, incap_ses, nlbi), reese84, ASP.NET_SessionId
cookies = "visid_incap_2857225=wT0ZCqWEQS20gvQHV4Ncbw0xomgAAAAAQUIPAAAAAADB6UhTs6KUkEu0YFUIFXtW; visid_incap_992756=8AoQZZkRQo2mA5Yrnc4KLroyomgAAAAAQUIPAAAAAAA9xae9DhUhtDv7QBmHD3D1; _ga_4PN0044LRV=GS2.1.s1755561599$o1$g1$t1755563356$j60$l0$h0; _ga_HJBXJ6E4E0=GS2.1.s1755899626$o3$g1$t1755899670$j16$l0$h0; _ga_2RE0XT2L0F=GS2.1.s1756323476$o1$g1$t1756323698$j1$l0$h0; _ga_75V2BNQ3DR=GS2.1.s1756332862$o2$g1$t1756332862$j60$l0$h0; _ga_DF674HWF28=GS2.1.s1757616373$o1$g1$t1757616521$j60$l0$h0; _ga_G17MN7HXHK=GS2.1.s1757616540$o1$g0$t1757616542$j58$l0$h0; visid_incap_2299457=EJIBssNwSDCD34xMDTArBbrm0WgAAAAAQUIPAAAAAAATrj2Q0E7Ct0Ygod7Fndq2; _ga_7M1ZZPXDBL=GS2.1.s1758595098$o3$g1$t1758595131$j27$l0$h0; _ga_CXDCWN357W=GS2.1.s1758906420$o1$g1$t1758906450$j30$l0$h0; _ga_ZTZK04QGW2=GS2.1.s1758908794$o2$g1$t1758908794$j60$l0$h0; _hjSessionUser_1388900=eyJpZCI6ImQyZmU2NjA1LTg0OTItNTQ5Mi1iMGJmLTlhZGY1N2ZkMGY2ZCIsImNyZWF0ZWQiOjE3NTkxNzE4Nzg4MDUsImV4aXN0aW5nIjp0cnVlfQ==; _ga_MSJG9B0DQE=GS2.1.s1761962599$o4$g1$t1761963476$j38$l0$h0; nmstat=c511e09e-acc1-5edb-d337-1e4ec10fef88; __utmz=158387685.1761963577.2.2.utmcsr=reservecalifornia.com|utmccn=(referral)|utmcmd=referral|utmcct=/; _ga_NQRMQVQ7T5=GS2.1.s1761963576$o1$g1$t1761963730$j60$l0$h0; ABTasty=uid=xetpfvqgr3mn54ns&fst=1762232950017&pst=-1&cst=1762232950017&ns=1&pvt=1&pvis=1&th=; _ga_006F1FGTXR=GS2.1.s1762232950$o2$g0$t1762232963$j47$l0$h0; _ga_WLDEF7NZZ2=GS2.1.s1762296720$o2$g0$t1762296720$j60$l0$h0; _ga_69TD0KNT0F=GS2.1.s1762296720$o10$g1$t1762296720$j60$l0$h0; _ga_PXR8P55JR4=GS2.1.s1762296720$o2$g0$t1762296720$j60$l0$h0; _ga_VDDSW2MN2F=GS2.1.s1762296720$o2$g0$t1762296720$j60$l0$h0; __utma=158387685.1412306014.1753992556.1761963577.1762898616.3; _ga=GA1.2.1412306014.1753992556; calosba._km_id-2d9f94aea6f8103bdd0b3447fc8546d2d=Aanlg81HTKV9KRhVKXl3zjNjN2P7NtQh; calosba._km_user_name-2d9f94aea6f8103bdd0b3447fc8546d2d=; calosba._km_lead_collection-2d9f94aea6f8103bdd0b3447fc8546d2d=false; _ga_2KMN5NQW5J=GS2.1.s1762898614$o1$g1$t1762899398$j1$l0$h0; ASP.NET_SessionId=uyu3qd2oo0lficawk4tjugo2; nlbi_2299457=fmuNX9qcP0D4l2thyPrJvAAAAACkSrWqv0+9KiezkU8w/sTD; nlbi_2857225=fn80BDwjTBO0DF635Oz8RAAAAAARlyV7UNhLwA7IVVUu9+W1; incap_ses_363_2857225=7Vd2JpMzvj/REb9gn6IJBZ5GFmkAAAAAnkcLH2KyycT47lnnjozYHg==; incap_ses_363_2299457=5/8yHusG7jp0NL9gn6IJBadGFmkAAAAAwP4i81MiRMS1tkLQTCgaNQ==; incap_ses_413_2299457=EnC+CRiQEk7e0540WUW7BUpKFmkAAAAAjSzkTBkhZRCADQw6GVlJVA==; incap_ses_413_2857225=m6OGX8C50k8k56A0WUW7BfZKFmkAAAAAzw9qzJy54XXBTW/cgWlPVw==; incap_ses_397_2857225=CRHwW0zqGAj8WZzsbm2CBZtUFmkAAAAA4XdY1LxZuOSrJ6fdaOpRAw==; incap_ses_341_2299457=r4HyCkrhHTEpZ5PkwXm7BA9eFmkAAAAAdCguNQAJzbj8WWeqlepZTA==; incap_ses_396_2299457=kEXCFkDZVE9Ubt1F8N9+BY1iFmkAAAAAoxe3M9FqOMUkc58vi/5T3w==; incap_ses_396_2857225=8ow4In/kZC6Qb91F8N9+BY5iFmkAAAAAKBXl1U5oKItMKLUfeffR2Q==; incap_ses_414_2299457=QwDKDYPGTBda0y7c19K+BYpjFmkAAAAA46OKm/0NUI4/+dLoydcw6w==; incap_ses_397_2299457=NpuqbDMJdl+dnN3sbm2CBdpjFmkAAAAACU/feMoyzwBH2nTu6Y6Afw==; reese84=3:wDMflh8uM+TMZLVRHI39Cg==:PublgAofJf6zvc9l5UNRC0VioDb+Y7om4m9smquaZ+oOxWvuji3Pw560nkQCUYW0neVO6/UbaBHortc7BBQVNncfWsBgYLzLyXtI6cnGZJPptfg4Sbb1mZSwSiz4re4VtT7NFgTnem2iOJZCmfDHK5kf5QFRo9wKSCEYCjDcVKFXCWJlbQH7lwIgk7z1x/tKl5581m/xC/WR9dfgjIQmhyOtCqdJf6y+9PI/lhcL0aWBgxsBoY4eM9NvttmDKgGnYRrPZwv6dIIALgqTVHaOb4aAyKt3aaNwTz62I3VYUD7kI76Y2D98xt1czovtOdPUMTckIjGEkg/Af85Dizp+DT/XA88jS/ff4++jbctKxFBuAAgvzhU3eyJotFuqTvjdBbHLjVd5Yf5suS5+uVlLwPmws/fJvqRBW6TZDkSednP1JjF2MkxAyThBlCRyR0MZjTORldlMij5ttWejYTMSxmIGHcVuaEM3yaUa30kby44=:ql+m4BGMKb0XwgtW3rexipRGdRgK96K3bwjhBf8GF6M=; incap_ses_362_2299457=P5WDN8FWAFs6AHBiJRUGBUZmFmkAAAAA6zPNzxUA3v7cPlr8V36Qig==; okta-oauth-redirect-params={%22responseType%22:%22code%22%2C%22state%22:%22ZFKabharsv228Y1tMojuasjRNRXgbqHSi3qEuvCLhEOQAd0qRKIvNK5KAFxbfMuG%22%2C%22nonce%22:%22JDXxHnOYviSSCUniBeaFQvlJWSbWR7xnPNzNJZNwyuJMz4Dr7Rk7NbuALvBiwNBZ%22%2C%22scopes%22:[%22openid%22]%2C%22clientId%22:%220oacsza710oWQY1md4x6%22%2C%22urls%22:{%22issuer%22:%22https://idm.sos.ca.gov/oauth2/default%22%2C%22authorizeUrl%22:%22https://idm.sos.ca.gov/oauth2/default/v1/authorize%22%2C%22userinfoUrl%22:%22https://idm.sos.ca.gov/oauth2/default/v1/userinfo%22%2C%22tokenUrl%22:%22https://idm.sos.ca.gov/oauth2/default/v1/token%22%2C%22revokeUrl%22:%22https://idm.sos.ca.gov/oauth2/default/v1/revoke%22%2C%22logoutUrl%22:%22https://idm.sos.ca.gov/oauth2/default/v1/logout%22}%2C%22ignoreSignature%22:false}; okta-oauth-nonce=JDXxHnOYviSSCUniBeaFQvlJWSbWR7xnPNzNJZNwyuJMz4Dr7Rk7NbuALvBiwNBZ; okta-oauth-state=ZFKabharsv228Y1tMojuasjRNRXgbqHSi3qEuvCLhEOQAd0qRKIvNK5KAFxbfMuG; incap_ses_605_2857225=SKnbOtK+vhQe2vnSVGRlCJNnFmkAAAAAtGCQ5FxOFmg70TeY9yxyIw==; incap_ses_605_2299457=n2+HC0BV60Jd2/nSVGRlCJNnFmkAAAAAfnxHFVifJqF2mjyikM769A==; nlbi_2299457_2147483392=FwAJaW/P6AZvAgtgyPrJvAAAAACq5Mx6/RTnTS7xwLWWHssR"

headers = {
    "Authorization": auth_token,
    "Origin": "https://bizfileonline.sos.ca.gov",
    "Referer": "https://bizfileonline.sos.ca.gov/search/business",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Cookie": cookies,
    "Sec-CH-UA": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}

# Check token expiration
def decode_jwt_payload(token):
    """Decode JWT payload to check expiration"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except:
        return None

print("=" * 80)
print(f"Testing URL: {test_url}")
print("=" * 80)

# Check token expiration
token_data = decode_jwt_payload(auth_token)
if token_data:
    exp_timestamp = token_data.get('exp')
    if exp_timestamp:
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        now = datetime.now()
        if exp_datetime < now:
            print(f"WARNING: Token appears to be EXPIRED!")
            print(f"   Expired at: {exp_datetime}")
            print(f"   Current time: {now}")
        else:
            print(f"Token valid until: {exp_datetime}")
    print()

print()

try:
    # Parse cookies into a dict for requests
    cookie_dict = {}
    for cookie in cookies.split('; '):
        if '=' in cookie:
            key, value = cookie.split('=', 1)
            cookie_dict[key] = value
    
    response = requests.get(test_url, headers=headers, cookies=cookie_dict, timeout=15)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        if not response.text or not response.text.strip():
            print("ERROR: Response is empty!")
        else:
            try:
                data = response.json()
                print("SUCCESS: Valid JSON response")
                print()
                print("Full Response:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                print()
                
                # Check for DRAWER_DETAIL_LIST
                if 'DRAWER_DETAIL_LIST' in data:
                    print("=" * 80)
                    print("DRAWER_DETAIL_LIST found!")
                    print("=" * 80)
                    drawer_list = data['DRAWER_DETAIL_LIST']
                    print(f"Number of items: {len(drawer_list)}")
                    print()
                    
                    # Find Statement of Info Due Date
                    soi_found = False
                    status_found = False
                    
                    for item in drawer_list:
                        label = item.get('LABEL', '')
                        value = item.get('VALUE', '')
                        
                        if label == 'Statement of Info Due Date':
                            soi_found = True
                            print(f"FOUND: Statement of Info Due Date = {value}")
                        elif label == 'Status':
                            status_found = True
                            print(f"FOUND: Status = {value}")
                    
                    if not soi_found:
                        print("NOT FOUND: Statement of Info Due Date")
                        print("Available labels:")
                        for item in drawer_list:
                            print(f"  - {item.get('LABEL', 'N/A')}")
                    
                    if not status_found:
                        print("NOT FOUND: Status")
                else:
                    print("ERROR: DRAWER_DETAIL_LIST not found in response")
                    print(f"Available keys: {list(data.keys())}")
                    
            except json.JSONDecodeError as e:
                print(f"ERROR: Invalid JSON - {str(e)}")
                print(f"Response text (first 500 chars): {response.text[:500]}")
    else:
        print(f"ERROR: HTTP {response.status_code}")
        print(f"Response text: {response.text[:500]}")
        
except Exception as e:
    print(f"EXCEPTION: {str(e)}")
    import traceback
    traceback.print_exc()

