# FMCSA Company Census File API Client

This project provides a Python client for querying the **FMCSA (Federal Motor Carrier Safety Administration) Company Census File** via the Socrata Open Data API (SODA) v3.0.

## Dataset Information

- **Dataset ID**: `az4n-8mr2`
- **Total Records**: 2,199,279 active entities
- **API Endpoint**: `https://data.transportation.gov/api/v3/views/az4n-8mr2`
- **Documentation**: https://dev.socrata.com/foundry/data.transportation.gov/az4n-8mr2

The Company Census File contains records for active entities registered with FMCSA, including:
- Entity identifying data (DOT number, legal name, DBA name)
- Business operations data
- Equipment and driver data
- Carrier review data
- Physical and mailing addresses
- Safety ratings and reviews
- Cargo types
- Vehicle ownership and lease information

## Features

- ✅ Query with custom field selection
- ✅ Filter records using WHERE clauses
- ✅ Sort results with ORDER BY
- ✅ Pagination support
- ✅ Export to CSV or JSON
- ✅ Rate limiting and error handling
- ✅ Support for app tokens (higher rate limits)

## Installation

```bash
pip install requests
```

## Quick Start

```python
from fmcsa_api_client import FMCSAAPIClient

# Initialize client
client = FMCSAAPIClient(app_token="YOUR_APP_TOKEN")  # Optional but recommended

# Get a specific carrier by DOT number
carrier = client.get_by_dot_number(12345)
print(carrier['legal_name'])

# Query carriers in California
result = client.query(
    fields=['dot_number', 'legal_name', 'phy_state', 'phy_city'],
    where="`phy_state`='CA'",
    order="dot_number ASC",
    page_size=100
)

# Export to CSV
client.export_to_csv(
    'carriers_ca.csv',
    fields=['dot_number', 'legal_name', 'phy_city', 'safety_rating'],
    where="`phy_state`='CA'",
    max_records=10000
)
```

## API Methods

### `query()`
Query the dataset with custom parameters.

**Parameters:**
- `fields`: List of field names to select (default: all 142 fields)
- `where`: WHERE clause (e.g., `"dot_number=12345"` or `"phy_state='CA'"`)
- `order`: ORDER BY clause (e.g., `"dot_number DESC"`)
- `page_number`: Page number (1-indexed)
- `page_size`: Records per page (max recommended: 5000)
- `use_post`: Use POST method (recommended for long queries)

**Returns:** Dictionary with `data` (list of records) and metadata

### `query_all_pages()`
Query all pages of results automatically.

**Parameters:**
- Same as `query()` plus:
- `max_pages`: Maximum pages to fetch (None = all)
- `delay`: Delay between requests in seconds

**Returns:** List of all records

### `get_by_dot_number()`
Get a single record by USDOT number.

**Parameters:**
- `dot_number`: USDOT number (int or str)

**Returns:** Record dictionary or None

### `export_to_csv()`
Export query results to CSV file.

**Parameters:**
- `filename`: Output CSV filename
- `fields`: Fields to export
- `where`: WHERE clause
- `order`: ORDER BY clause
- `max_records`: Maximum records to export

### `export_to_json()`
Export query results to JSON file.

**Parameters:** Same as `export_to_csv()`

## Available Fields (142 total)

The dataset includes 142 fields organized into categories:

### Identification
- `dot_number`, `dun_bradstreet_no`, `legal_name`, `dba_name`

### Dates
- `mcs150_date`, `add_date`, `mcsipdate`, `review_date`, `safety_rating_date`

### Addresses
- Physical: `phy_street`, `phy_city`, `phy_state`, `phy_zip`, `phy_country`, `phy_cnty`
- Mailing: `carrier_mailing_street`, `carrier_mailing_city`, `carrier_mailing_state`, etc.

### Contact
- `phone`, `fax`, `cell_phone`, `email_address`

### Operations
- `carrier_operation`, `business_org_desc`, `status_code`
- `interstate_beyond_100_miles`, `interstate_within_100_miles`
- `intrastate_beyond_100_miles`, `intrastate_within_100_miles`

### Equipment & Drivers
- `truck_units`, `power_units`, `bus_units`, `fleetsize`
- `total_drivers`, `total_cdl`, `total_intrastate_drivers`

### Cargo Types (30+ fields)
- `crgo_genfreight`, `crgo_household`, `crgo_metalsheet`, `crgo_motoveh`, etc.

### Vehicle Ownership
- Owned: `owntruck`, `owntract`, `owntrail`, `owncoach`, etc.
- Term leased: `trmtruck`, `trmtract`, `trmtrail`, etc.
- Trip leased: `trptruck`, `trptract`, `trptrail`, etc.

### Safety
- `safety_rating`, `safety_rating_date`, `review_type`, `review_id`
- `recordable_crash_rate`, `mcsipstep`

### Other
- `docket1`, `docket2`, `docket3` (with prefixes and status codes)
- `hm_ind` (Hazardous Materials indicator)
- And many more...

## Example Queries

### Find carriers by state
```python
result = client.query(
    where="`phy_state`='TX'",
    page_size=100
)
```

### Find carriers with specific cargo type
```python
result = client.query(
    where="`crgo_genfreight`='Y'",
    order="dot_number ASC"
)
```

### Find carriers with safety rating
```python
result = client.query(
    fields=['dot_number', 'legal_name', 'safety_rating', 'safety_rating_date'],
    where="`safety_rating` IS NOT NULL",
    order="safety_rating_date DESC"
)
```

### Find carriers by DOT number range
```python
result = client.query(
    where="`dot_number` >= 1000 AND `dot_number` <= 2000"
)
```

## App Tokens

While the API works without an app token, using one provides:
- Higher rate limits
- Guaranteed access to your own request pool
- Better reliability

Get your app token at: https://dev.socrata.com/register

## Rate Limiting

The API has rate limits. The client includes:
- Automatic delays between requests in `query_all_pages()`
- Error handling for rate limit responses
- Support for pagination to handle large datasets

## Notes

- The API uses **SoQL** (Socrata Query Language), similar to SQL
- Field names must be wrapped in backticks: `` `field_name` ``
- String values in WHERE clauses must be in single quotes: `'value'`
- POST method is recommended for long queries
- Maximum recommended page size is 5000 records

## License

This code is provided as-is for working with the public FMCSA dataset.

