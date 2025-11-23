"""
Test script to diagnose API connection issues
"""

import requests
from fmcsa_api_client import FMCSAAPIClient

def test_simple_get():
    """Test a simple GET request to the API"""
    print("Testing simple GET request...")
    url = "https://data.transportation.gov/api/v3/views/az4n-8mr2/query.json"
    
    # Very simple query
    params = {
        'query': 'SELECT `dot_number`, `legal_name` LIMIT 5',
        'pageNumber': 1,
        'pageSize': 5
    }
    
    headers = {
        'User-Agent': 'FMCSA-API-Client/1.0 (Python)'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Got {len(data.get('data', []))} records")
            if data.get('data'):
                print(f"Sample record: {data['data'][0]}")
        else:
            print(f"[ERROR] Status Code: {response.status_code}")
            # Check for specific error messages
            error_headers = {
                'X-Error-Code': response.headers.get('X-Error-Code', ''),
                'X-Error-Message': response.headers.get('X-Error-Message', '')
            }
            if error_headers['X-Error-Code']:
                print(f"Error Code: {error_headers['X-Error-Code']}")
            if error_headers['X-Error-Message']:
                print(f"Error Message: {error_headers['X-Error-Message']}")
            try:
                error_data = response.json()
                print(f"Response: {error_data}")
            except:
                print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")

def test_with_client():
    """Test using our client"""
    print("\nTesting with FMCSAAPIClient...")
    client = FMCSAAPIClient(app_token=None)
    
    try:
        result = client.query(
            fields=['dot_number', 'legal_name'],
            page_size=5,
            use_post=False
        )
        print(f"[SUCCESS] Got {len(result.get('data', []))} records")
        if result.get('data'):
            print(f"Sample: DOT {result['data'][0].get('dot_number')} - {result['data'][0].get('legal_name')}")
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    print("=" * 70)
    print("FMCSA API Connection Test")
    print("=" * 70)
    test_simple_get()
    test_with_client()
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print("=" * 70)
    print("If you see 'authentication_required' errors, you MUST get an app token.")
    print("The API requires authentication for all requests.")
    print("\nGet your free app token at: https://dev.socrata.com/register")
    print("\nOnce you have the token, update your script:")
    print("  client = FMCSAAPIClient(app_token='YOUR_TOKEN_HERE')")
    print("=" * 70)

