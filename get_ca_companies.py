"""
Fetch all California companies from FMCSA dataset with specific fields.

This script queries all companies where phy_state = 'CA' and exports
only the requested fields to an XLSX file.
"""

from fmcsa_api_client_old import FMCSAAPIClientOld
import time
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    try:
        from openpyxl import Workbook
        OPENPYXL_AVAILABLE = True
    except ImportError:
        OPENPYXL_AVAILABLE = False


def main():
    # Initialize the client using OLD API endpoint (no authentication needed!)
    # This uses the same endpoint as the Node.js app
    client = FMCSAAPIClientOld()
    
    # Define the fields you want to retrieve
    fields = [
        'mcs150_date',
        'add_date',
        'dot_number',
        'safety_inv_terr',
        'carrier_operation',
        'total_cars',
        'prior_revoke_dot_number',
        'mcs150_update_code_id',
        'prior_revoke_flag',
        'phone',
        'cell_phone',
        'company_officer_1',
        'company_officer_2',
        'business_org_desc',
        'truck_units',
        'power_units',
        'bus_units',
        'fleetsize',
        'review_id',
        'total_cdl',
        'total_drivers',
        'legal_name',
        'dba_name',
        'phy_street',
        'phy_city',
        'phy_zip',
        'carrier_mailing_city',
        'carrier_mailing_zip',
        'driver_inter_total',
        'email_address',
        'review_type',
        'review_date',
        'owntruck',
        'owntract',
        'owntrail',
        'owncoach'
    ]
    
    print("=" * 70)
    print("FMCSA California Companies Data Export")
    print("=" * 70)
    print(f"\nFetching all companies where phy_state = 'CA'")
    print(f"Selected fields: {len(fields)}")
    print(f"\nFields: {', '.join(fields[:10])}... ({len(fields)} total)")
    print("\nThis may take a while depending on the number of records...")
    print("=" * 70)
    
    # First, let's check how many records we're dealing with
    print("\nStep 1: Checking total number of California companies...")
    try:
        sample_result = client.query(
            fields=['dot_number'],
            where="phy_state='CA'",
            limit=5000
        )
        sample_count = len(sample_result)
        print(f"   Found at least {sample_count} records in first batch")
        if sample_count == 5000:
            print("   (There are likely more - will fetch all batches)")
    except Exception as e:
        print(f"   Warning: {str(e)}")
        print("   Continuing anyway...")
    
    # Export to XLSX
    print("\nStep 2: Fetching all records and exporting to XLSX...")
    print("   This will fetch all batches automatically...")
    
    output_filename = 'ca_companies_fmcsa.xlsx'
    
    try:
        # Use the client's export method which handles everything
        client.export_to_xlsx(
            filename=output_filename,
            fields=fields,
            where="phy_state='CA'",
            order="dot_number ASC"
        )
        
        print("\n" + "=" * 70)
        print(f"✓ Successfully exported data to: {output_filename}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

