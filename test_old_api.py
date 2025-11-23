"""
Test the old Socrata API endpoint (like the Node.js app uses)
This endpoint might not require authentication
"""

import requests

def test_old_api():
    """Test the old API endpoint format"""
    print("=" * 70)
    print("Testing OLD Socrata API Endpoint (like Node.js app)")
    print("=" * 70)
    
    # Old endpoint format (same as Node.js app)
    url = "https://data.transportation.gov/resource/az4n-8mr2.json"
    
    # Test 1: Simple query with $where and $select
    print("\nTest 1: Query with $where and $select parameters")
    print("-" * 70)
    
    params = {
        '$where': "dot_number='12345'",
        '$select': 'dot_number,legal_name,mcs150_date',
        '$limit': 5
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Got {len(data)} records")
            if data:
                print(f"Sample record: {data[0]}")
        else:
            print(f"[ERROR] Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
    
    # Test 2: Query for California companies
    print("\nTest 2: Query California companies")
    print("-" * 70)
    
    params2 = {
        '$where': "phy_state='CA'",
        '$select': 'dot_number,legal_name,phy_city',
        '$limit': 3
    }
    
    try:
        response = requests.get(url, params=params2, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Got {len(data)} records")
            for i, record in enumerate(data[:3], 1):
                print(f"  {i}. DOT {record.get('dot_number')}: {record.get('legal_name')} - {record.get('phy_city')}")
        else:
            print(f"[ERROR] Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
    
    print("\n" + "=" * 70)
    print("If both tests show [SUCCESS], you can use this endpoint without authentication!")
    print("=" * 70)

if __name__ == "__main__":
    test_old_api()

