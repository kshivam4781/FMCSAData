"""
Example usage of the FMCSA API Client

This script demonstrates various ways to query the FMCSA Company Census File.
"""

from fmcsa_api_client import FMCSAAPIClient


def main():
    # Initialize the client
    # Optionally provide an app_token for higher rate limits
    # Get one at: https://dev.socrata.com/register
    client = FMCSAAPIClient(app_token=None)
    
    print("=" * 60)
    print("FMCSA Company Census File API - Example Usage")
    print("=" * 60)
    
    # Example 1: Get a specific carrier by DOT number
    print("\n1. Get carrier by DOT number:")
    print("-" * 60)
    carrier = client.get_by_dot_number(12345)
    if carrier:
        print(f"   DOT Number: {carrier.get('dot_number')}")
        print(f"   Legal Name: {carrier.get('legal_name')}")
        print(f"   DBA Name: {carrier.get('dba_name')}")
        print(f"   State: {carrier.get('phy_state')}")
        print(f"   City: {carrier.get('phy_city')}")
    else:
        print("   Carrier not found")
    
    # Example 2: Query with specific fields and filters
    print("\n2. Query carriers in California (first 10):")
    print("-" * 60)
    result = client.query(
        fields=['dot_number', 'legal_name', 'phy_city', 'safety_rating'],
        where="`phy_state`='CA'",
        order="dot_number ASC",
        page_size=10
    )
    
    records = result.get('data', [])
    print(f"   Found {len(records)} records")
    for i, record in enumerate(records[:5], 1):
        print(f"   {i}. DOT {record.get('dot_number')}: {record.get('legal_name')} - {record.get('phy_city')}")
    
    # Example 3: Query carriers with specific cargo type
    print("\n3. Query carriers that transport general freight:")
    print("-" * 60)
    result = client.query(
        fields=['dot_number', 'legal_name', 'crgo_genfreight'],
        where="`crgo_genfreight`='Y'",
        page_size=5
    )
    records = result.get('data', [])
    print(f"   Found {len(records)} records (showing first 5)")
    for i, record in enumerate(records, 1):
        print(f"   {i}. DOT {record.get('dot_number')}: {record.get('legal_name')}")
    
    # Example 4: Query carriers with safety ratings
    print("\n4. Query carriers with safety ratings:")
    print("-" * 60)
    result = client.query(
        fields=['dot_number', 'legal_name', 'safety_rating', 'safety_rating_date'],
        where="`safety_rating` IS NOT NULL",
        order="safety_rating_date DESC",
        page_size=5
    )
    records = result.get('data', [])
    print(f"   Found {len(records)} records (showing first 5)")
    for i, record in enumerate(records, 1):
        rating = record.get('safety_rating', 'N/A')
        date = record.get('safety_rating_date', 'N/A')
        print(f"   {i}. DOT {record.get('dot_number')}: {record.get('legal_name')} - Rating: {rating} ({date})")
    
    # Example 5: Show available fields count
    print("\n5. Dataset Information:")
    print("-" * 60)
    print(f"   Total available fields: {len(client.ALL_FIELDS)}")
    print(f"   Sample fields: {', '.join(client.ALL_FIELDS[:10])}...")
    
    # Example 6: Export example (commented out to avoid large downloads)
    print("\n6. Export Example (commented out):")
    print("-" * 60)
    print("   # Export California carriers to CSV")
    print("   # client.export_to_csv(")
    print("   #     'carriers_ca.csv',")
    print("   #     fields=['dot_number', 'legal_name', 'phy_city', 'safety_rating'],")
    print("   #     where=\"`phy_state`='CA'\",")
    print("   #     max_records=1000")
    print("   # )")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

