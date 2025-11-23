"""
FMCSA Company Census File API Client - Using OLD API Endpoint

This version uses the old Socrata API endpoint that doesn't require authentication,
similar to how the Node.js app works.
"""

import requests
import json
import csv
from typing import Dict, List, Optional, Union
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


class FMCSAAPIClientOld:
    """
    Client for interacting with the FMCSA Company Census File API using the OLD endpoint.
    
    This uses the same endpoint format as the Node.js app:
    https://data.transportation.gov/resource/az4n-8mr2.json
    
    No authentication required!
    """
    
    BASE_URL = "https://data.transportation.gov/resource/az4n-8mr2.json"
    
    def __init__(self):
        """Initialize the client - no app token needed!"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FMCSA-API-Client/1.0 (Python)'
        })
    
    def query(self,
              fields: Optional[List[str]] = None,
              where: Optional[str] = None,
              limit: Optional[int] = None,
              offset: Optional[int] = None,
              order: Optional[str] = None,
              timeout: int = 30) -> List[Dict]:
        """
        Query the FMCSA dataset using the old API format.
        
        Args:
            fields: List of field names to select (default: all fields with *)
            where: WHERE clause (e.g., "phy_state='CA'")
            limit: Maximum number of records to return
            offset: Number of records to skip
            order: ORDER BY clause (e.g., "dot_number DESC")
            timeout: Request timeout in seconds
            
        Returns:
            List of records (dictionaries)
        """
        params = {}
        
        # Build $select parameter
        if fields:
            params['$select'] = ','.join(fields)
        else:
            params['$select'] = '*'  # Get all fields
        
        # Build $where parameter
        if where:
            params['$where'] = where
        
        # Add limit
        if limit:
            params['$limit'] = limit
        
        # Add offset
        if offset:
            params['$offset'] = offset
        
        # Add order
        if order:
            params['$order'] = order
        
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def query_all(self,
                  fields: Optional[List[str]] = None,
                  where: Optional[str] = None,
                  order: Optional[str] = None,
                  batch_size: int = 5000,
                  max_records: Optional[int] = None,
                  delay: float = 0.1) -> List[Dict]:
        """
        Query all records matching the criteria (handles pagination automatically).
        
        Args:
            fields: List of field names to select
            where: WHERE clause for filtering
            order: ORDER BY clause
            batch_size: Number of records per batch
            max_records: Maximum number of records to fetch (None = all)
            delay: Delay between requests in seconds
            
        Returns:
            List of all records
        """
        all_records = []
        offset = 0
        
        while True:
            if max_records and len(all_records) >= max_records:
                break
            
            current_limit = batch_size
            if max_records:
                remaining = max_records - len(all_records)
                current_limit = min(batch_size, remaining)
            
            try:
                batch = self.query(
                    fields=fields,
                    where=where,
                    limit=current_limit,
                    offset=offset,
                    order=order
                )
                
                if not batch:
                    break
                
                all_records.extend(batch)
                
                # If we got fewer records than requested, we've reached the end
                if len(batch) < current_limit:
                    break
                
                offset += len(batch)
                
                # Rate limiting
                if delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"Error fetching batch at offset {offset}: {str(e)}")
                break
        
        return all_records
    
    def get_by_dot_number(self, dot_number: Union[int, str]) -> Optional[Dict]:
        """
        Get a single record by DOT number.
        
        Args:
            dot_number: USDOT number
            
        Returns:
            Record dictionary or None if not found
        """
        results = self.query(
            where=f"dot_number='{dot_number}'",
            limit=1
        )
        return results[0] if results else None
    
    def export_to_xlsx(self,
                       filename: str,
                       fields: Optional[List[str]] = None,
                       where: Optional[str] = None,
                       order: Optional[str] = None,
                       max_records: Optional[int] = None):
        """
        Export query results to XLSX file.
        
        Args:
            filename: Output XLSX filename
            fields: List of field names to export
            where: WHERE clause for filtering
            order: ORDER BY clause
            max_records: Maximum number of records to export
        """
        print(f"Fetching data from API...")
        records = self.query_all(
            fields=fields,
            where=where,
            order=order,
            max_records=max_records
        )
        
        if not records:
            print("No records found.")
            return
        
        print(f"Found {len(records)} records. Saving to XLSX...")
        
        if PANDAS_AVAILABLE:
            # Use pandas (preferred method)
            df = pd.DataFrame(records)
            # Reorder columns to match requested field order
            if fields:
                available_fields = [f for f in fields if f in df.columns]
                df = df[available_fields]
            df.to_excel(filename, index=False, engine='openpyxl')
            
        elif OPENPYXL_AVAILABLE:
            # Use openpyxl directly
            wb = Workbook()
            ws = wb.active
            ws.title = "FMCSA Data"
            
            # Write headers
            if fields:
                ws.append(fields)
            elif records:
                ws.append(list(records[0].keys()))
            
            # Write data
            for record in records:
                if fields:
                    row = [record.get(field, '') for field in fields]
                else:
                    row = list(record.values())
                ws.append(row)
            
            wb.save(filename)
        else:
            raise Exception("Neither pandas nor openpyxl is available. Install with: pip install pandas openpyxl")
        
        print(f"Exported {len(records)} records to {filename}")


# Example usage
if __name__ == "__main__":
    client = FMCSAAPIClientOld()
    
    # Test query
    print("Testing API connection...")
    result = client.query(
        fields=['dot_number', 'legal_name', 'phy_state'],
        where="phy_state='CA'",
        limit=5
    )
    print(f"Found {len(result)} records")
    for record in result:
        print(f"  DOT {record.get('dot_number')}: {record.get('legal_name')}")

