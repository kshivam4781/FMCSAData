"""
FMCSA Company Census File API Client

This module provides a Python client for querying the FMCSA Company Census File
via the Socrata Open Data API (SODA) v3.0.

Dataset: https://data.transportation.gov/Transportation/FMCSA-Company-Census-File/az4n-8mr2
API Documentation: https://dev.socrata.com/foundry/data.transportation.gov/az4n-8mr2
"""

import requests
import json
import csv
from typing import Dict, List, Optional, Union
from urllib.parse import quote
import time


class FMCSAAPIClient:
    """
    Client for interacting with the FMCSA Company Census File API.
    
    The dataset contains 2,199,279 records of active entities registered with FMCSA.
    Each record includes entity identifying data, business operations data, 
    equipment and driver data, and carrier review data.
    """
    
    BASE_URL = "https://data.transportation.gov/api/v3/views/az4n-8mr2"
    DATASET_ID = "az4n-8mr2"
    
    # All available fields in the dataset (142 fields total)
    ALL_FIELDS = [
        'mcs150_date', 'add_date', 'status_code', 'dot_number', 'dun_bradstreet_no',
        'phy_omc_region', 'safety_inv_terr', 'carrier_operation', 'business_org_id',
        'mcs150_mileage', 'mcs150_mileage_year', 'mcs151_mileage', 'total_cars',
        'mcs150_update_code_id', 'prior_revoke_flag', 'prior_revoke_dot_number',
        'phone', 'fax', 'cell_phone', 'company_officer_1', 'company_officer_2',
        'business_org_desc', 'truck_units', 'power_units', 'bus_units', 'fleetsize',
        'review_id', 'recordable_crash_rate', 'mail_nationality_indicator',
        'phy_nationality_indicator', 'phy_barrio', 'mail_barrio', 'carship',
        'docket1prefix', 'docket1', 'docket2prefix', 'docket2', 'docket3prefix',
        'docket3', 'pointnum', 'total_intrastate_drivers', 'mcsipstep', 'mcsipdate',
        'hm_ind', 'interstate_beyond_100_miles', 'interstate_within_100_miles',
        'intrastate_beyond_100_miles', 'intrastate_within_100_miles', 'total_cdl',
        'total_drivers', 'avg_drivers_leased_per_month', 'classdef', 'legal_name',
        'dba_name', 'phy_street', 'phy_city', 'phy_country', 'phy_state', 'phy_zip',
        'phy_cnty', 'carrier_mailing_street', 'carrier_mailing_state',
        'carrier_mailing_city', 'carrier_mailing_country', 'carrier_mailing_zip',
        'carrier_mailing_cnty', 'carrier_mailing_und_date', 'driver_inter_total',
        'email_address', 'review_type', 'review_date', 'safety_rating',
        'safety_rating_date', 'undeliv_phy', 'crgo_genfreight', 'crgo_household',
        'crgo_metalsheet', 'crgo_motoveh', 'crgo_drivetow', 'crgo_logpole',
        'crgo_bldgmat', 'crgo_mobilehome', 'crgo_machlrg', 'crgo_produce',
        'crgo_liqgas', 'crgo_intermodal', 'crgo_passengers', 'crgo_oilfield',
        'crgo_livestock', 'crgo_grainfeed', 'crgo_coalcoke', 'crgo_meat',
        'crgo_garbage', 'crgo_usmail', 'crgo_chem', 'crgo_drybulk', 'crgo_coldfood',
        'crgo_beverages', 'crgo_paperprod', 'crgo_utility', 'crgo_farmsupp',
        'crgo_construct', 'crgo_waterwell', 'crgo_cargoothr', 'crgo_cargoothr_desc',
        'owntruck', 'owntract', 'owntrail', 'owncoach', 'ownschool_1_8',
        'ownschool_9_15', 'ownschool_16', 'ownbus_16', 'ownvan_1_8', 'ownvan_9_15',
        'ownlimo_1_8', 'ownlimo_9_15', 'ownlimo_16', 'trmtruck', 'trmtract',
        'trmtrail', 'trmcoach', 'trmschool_1_8', 'trmschool_9_15', 'trmschool_16',
        'trmbus_16', 'trmvan_1_8', 'trmvan_9_15', 'trmlimo_1_8', 'trmlimo_9_15',
        'trmlimo_16', 'trptruck', 'trptract', 'trptrail', 'trpcoach',
        'trpschool_1_8', 'trpschool_9_15', 'trpschool_16', 'trpbus_16',
        'trpvan_1_8', 'trpvan_9_15', 'trplimo_1_8', 'trplimo_9_15', 'trplimo_16',
        'docket1_status_code', 'docket2_status_code', 'docket3_status_code'
    ]
    
    def __init__(self, app_token: Optional[str] = None):
        """
        Initialize the FMCSA API client.
        
        Args:
            app_token: Optional app token for higher rate limits.
                      Get one at: https://dev.socrata.com/register
        """
        self.app_token = app_token
        self.session = requests.Session()
        # Add User-Agent header (required by some APIs)
        self.session.headers.update({
            'User-Agent': 'FMCSA-API-Client/1.0 (Python)'
        })
        if app_token:
            self.session.headers.update({'X-App-Token': app_token})
    
    def _build_query(self, 
                     fields: Optional[List[str]] = None,
                     where: Optional[str] = None,
                     order: Optional[str] = None,
                     limit: Optional[int] = None,
                     offset: Optional[int] = None) -> str:
        """
        Build a SoQL query string.
        
        Args:
            fields: List of field names to select (default: all fields)
            where: WHERE clause (e.g., "dot_number=12345")
            order: ORDER BY clause (e.g., "dot_number DESC")
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            SoQL query string
        """
        if fields is None:
            fields = self.ALL_FIELDS
        
        # Build SELECT clause with backticks around field names
        select_clause = "SELECT " + ", ".join([f"`{field}`" for field in fields])
        
        query_parts = [select_clause]
        
        if where:
            query_parts.append(f"WHERE {where}")
        
        if order:
            query_parts.append(f"ORDER BY {order}")
        
        if limit:
            query_parts.append(f"LIMIT {limit}")
        
        if offset:
            query_parts.append(f"OFFSET {offset}")
        
        return " ".join(query_parts)
    
    def query(self,
              fields: Optional[List[str]] = None,
              where: Optional[str] = None,
              order: Optional[str] = None,
              page_number: int = 1,
              page_size: int = 5000,
              use_post: bool = True,
              timeout: int = 30) -> Dict:
        """
        Query the FMCSA dataset.
        
        Args:
            fields: List of field names to select (default: all fields)
            where: WHERE clause for filtering (e.g., "dot_number=12345")
            order: ORDER BY clause (e.g., "dot_number DESC")
            page_number: Page number (1-indexed)
            page_size: Number of records per page (max recommended: 5000)
            use_post: Use POST method (recommended for long queries)
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary containing 'data' (list of records) and 'metadata'
        """
        query_str = self._build_query(fields=fields, where=where, order=order)
        
        url = f"{self.BASE_URL}/query.json"
        
        payload = {
            "query": query_str,
            "page": {
                "pageNumber": page_number,
                "pageSize": page_size
            },
            "includeSynthetic": False
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        if self.app_token:
            headers['X-App-Token'] = self.app_token
        
        try:
            if use_post:
                response = self.session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=timeout
                )
            else:
                # GET method (for shorter queries)
                # URL encode the query string properly
                from urllib.parse import quote
                params = {
                    'query': query_str,  # requests will encode this, but we can also do it manually
                    'pageNumber': page_number,
                    'pageSize': page_size
                }
                if self.app_token:
                    params['app_token'] = self.app_token
                # Use params which will be properly encoded by requests
                response = self.session.get(url, params=params, timeout=timeout)
            
            # Check for errors
            if response.status_code == 403:
                error_msg = "403 Forbidden - The API may require an app token or have rate limiting."
                if not self.app_token:
                    error_msg += " Try getting an app token at: https://dev.socrata.com/register"
                try:
                    error_detail = response.json()
                    if 'message' in error_detail:
                        error_msg += f"\nAPI Message: {error_detail['message']}"
                except:
                    pass
                raise Exception(error_msg)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                error_msg = "403 Forbidden - The API may require an app token or have rate limiting."
                if not self.app_token:
                    error_msg += " Try getting an app token at: https://dev.socrata.com/register"
                raise Exception(error_msg)
            raise Exception(f"API request failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def query_all_pages(self,
                       fields: Optional[List[str]] = None,
                       where: Optional[str] = None,
                       order: Optional[str] = None,
                       page_size: int = 5000,
                       max_pages: Optional[int] = None,
                       delay: float = 0.1) -> List[Dict]:
        """
        Query all pages of results.
        
        Args:
            fields: List of field names to select
            where: WHERE clause for filtering
            order: ORDER BY clause
            page_size: Number of records per page
            max_pages: Maximum number of pages to fetch (None = all)
            delay: Delay between requests in seconds (to respect rate limits)
            
        Returns:
            List of all records across all pages
        """
        all_records = []
        page_number = 1
        
        while True:
            if max_pages and page_number > max_pages:
                break
            
            result = self.query(
                fields=fields,
                where=where,
                order=order,
                page_number=page_number,
                page_size=page_size
            )
            
            records = result.get('data', [])
            if not records:
                break
            
            all_records.extend(records)
            
            # Check if there are more pages
            if len(records) < page_size:
                break
            
            page_number += 1
            time.sleep(delay)  # Rate limiting
        
        return all_records
    
    def get_by_dot_number(self, dot_number: Union[int, str]) -> Optional[Dict]:
        """
        Get a single record by DOT number.
        
        Args:
            dot_number: USDOT number
            
        Returns:
            Record dictionary or None if not found
        """
        result = self.query(
            where=f"`dot_number`={dot_number}",
            page_size=1
        )
        
        records = result.get('data', [])
        return records[0] if records else None
    
    def export_to_csv(self,
                     filename: str,
                     fields: Optional[List[str]] = None,
                     where: Optional[str] = None,
                     order: Optional[str] = None,
                     max_records: Optional[int] = None):
        """
        Export query results to CSV file.
        
        Args:
            filename: Output CSV filename
            fields: List of field names to export
            where: WHERE clause for filtering
            order: ORDER BY clause
            max_records: Maximum number of records to export
        """
        if fields is None:
            fields = self.ALL_FIELDS
        
        max_pages = None
        if max_records:
            page_size = 5000
            max_pages = (max_records + page_size - 1) // page_size
        
        records = self.query_all_pages(
            fields=fields,
            where=where,
            order=order,
            max_pages=max_pages
        )
        
        if max_records:
            records = records[:max_records]
        
        if not records:
            print("No records found.")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            
            for record in records:
                row = {field: record.get(field, '') for field in fields}
                writer.writerow(row)
        
        print(f"Exported {len(records)} records to {filename}")
    
    def export_to_json(self,
                      filename: str,
                      fields: Optional[List[str]] = None,
                      where: Optional[str] = None,
                      order: Optional[str] = None,
                      max_records: Optional[int] = None):
        """
        Export query results to JSON file.
        
        Args:
            filename: Output JSON filename
            fields: List of field names to export
            where: WHERE clause for filtering
            order: ORDER BY clause
            max_records: Maximum number of records to export
        """
        max_pages = None
        if max_records:
            page_size = 5000
            max_pages = (max_records + page_size - 1) // page_size
        
        records = self.query_all_pages(
            fields=fields,
            where=where,
            order=order,
            max_pages=max_pages
        )
        
        if max_records:
            records = records[:max_records]
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(records, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(records)} records to {filename}")


# Example usage
if __name__ == "__main__":
    # Initialize client (optional: provide app_token for higher rate limits)
    client = FMCSAAPIClient(app_token=None)  # Replace None with your app token
    
    # Example 1: Get a specific carrier by DOT number
    print("Example 1: Get carrier by DOT number")
    carrier = client.get_by_dot_number(12345)
    if carrier:
        print(f"Found: {carrier.get('legal_name')}")
    
    # Example 2: Query with filters
    print("\nExample 2: Query carriers in a specific state")
    result = client.query(
        fields=['dot_number', 'legal_name', 'phy_state', 'phy_city'],
        where="`phy_state`='CA'",
        order="dot_number ASC",
        page_size=10
    )
    print(f"Found {len(result.get('data', []))} records")
    
    # Example 3: Export to CSV
    print("\nExample 3: Export to CSV")
    # client.export_to_csv(
    #     'fmcsa_carriers.csv',
    #     fields=['dot_number', 'legal_name', 'phy_state', 'phy_city'],
    #     where="`phy_state`='CA'",
    #     max_records=1000
    # )

