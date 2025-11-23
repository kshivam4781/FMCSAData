# FMCSA API Structure Analysis

## Overview

The URL you provided contains a **SoQL (Socrata Query Language)** query that selects **142 fields** from the FMCSA Company Census File dataset.

## Decoded Query

The URL-encoded query decodes to:

```sql
SELECT
  `mcs150_date`,
  `add_date`,
  `status_code`,
  `dot_number`,
  ... (142 fields total)
  `docket1_status_code`,
  `docket2_status_code`,
  `docket3_status_code`
```

## API Endpoint Structure

**Base URL**: `https://data.transportation.gov/api/v3/views/az4n-8mr2`

**Query Endpoint**: `{BASE_URL}/query.json`

## Request Methods

### GET Method (for shorter queries)
```
GET {BASE_URL}/query.json?query=SELECT...&pageNumber=1&pageSize=10&app_token=TOKEN
```

### POST Method (recommended for long queries)
```
POST {BASE_URL}/query.json
Content-Type: application/json
X-App-Token: YOUR_TOKEN

{
  "query": "SELECT ...",
  "page": {
    "pageNumber": 1,
    "pageSize": 5000
  },
  "includeSynthetic": false
}
```

## Field Categories

The 142 fields are organized into these categories:

### 1. Identification & Dates (15 fields)
- `dot_number` - USDOT number (unique identifier)
- `dun_bradstreet_no` - DUNS number
- `legal_name` - Legal company name
- `dba_name` - Doing Business As name
- `mcs150_date`, `add_date`, `mcsipdate`, `review_date`, `safety_rating_date`

### 2. Status & Operations (10 fields)
- `status_code` - Carrier status
- `carrier_operation` - Type of operation
- `business_org_id`, `business_org_desc` - Business organization type
- `hm_ind` - Hazardous Materials indicator
- `prior_revoke_flag`, `prior_revoke_dot_number`

### 3. Physical Address (7 fields)
- `phy_street`, `phy_city`, `phy_state`, `phy_zip`, `phy_country`, `phy_cnty`
- `phy_omc_region`, `phy_barrio`, `phy_nationality_indicator`
- `undeliv_phy` - Undeliverable physical address flag

### 4. Mailing Address (7 fields)
- `carrier_mailing_street`, `carrier_mailing_city`, `carrier_mailing_state`
- `carrier_mailing_zip`, `carrier_mailing_country`, `carrier_mailing_cnty`
- `carrier_mailing_und_date`, `mail_barrio`, `mail_nationality_indicator`

### 5. Contact Information (4 fields)
- `phone`, `fax`, `cell_phone`, `email_address`

### 6. Company Officers (2 fields)
- `company_officer_1`, `company_officer_2`

### 7. Equipment & Fleet (10 fields)
- `truck_units`, `power_units`, `bus_units`, `fleetsize`
- `total_cars`, `carship`
- `mcs150_mileage`, `mcs150_mileage_year`, `mcs151_mileage`
- `mcs150_update_code_id`

### 8. Drivers (8 fields)
- `total_drivers`, `total_cdl`, `total_intrastate_drivers`
- `driver_inter_total`
- `interstate_beyond_100_miles`, `interstate_within_100_miles`
- `intrastate_beyond_100_miles`, `intrastate_within_100_miles`
- `avg_drivers_leased_per_month`

### 9. Cargo Types (30 fields)
All cargo type fields start with `crgo_`:
- `crgo_genfreight` - General Freight
- `crgo_household` - Household Goods
- `crgo_metalsheet` - Metal/Sheet
- `crgo_motoveh` - Motor Vehicles
- `crgo_drivetow` - Drive/Tow
- `crgo_logpole` - Logs/Poles
- `crgo_bldgmat` - Building Materials
- `crgo_mobilehome` - Mobile Homes
- `crgo_machlrg` - Machinery/Large Objects
- `crgo_produce` - Produce
- `crgo_liqgas` - Liquified Gases
- `crgo_intermodal` - Intermodal
- `crgo_passengers` - Passengers
- `crgo_oilfield` - Oil Field Equipment
- `crgo_livestock` - Livestock
- `crgo_grainfeed` - Grain/Feed
- `crgo_coalcoke` - Coal/Coke
- `crgo_meat` - Meat
- `crgo_garbage` - Garbage/Refuse
- `crgo_usmail` - US Mail
- `crgo_chem` - Chemicals
- `crgo_drybulk` - Dry Bulk
- `crgo_coldfood` - Refrigerated Food
- `crgo_beverages` - Beverages
- `crgo_paperprod` - Paper Products
- `crgo_utility` - Utility
- `crgo_farmsupp` - Farm Supplies
- `crgo_construct` - Construction
- `crgo_waterwell` - Water Well
- `crgo_cargoothr` - Other Cargo
- `crgo_cargoothr_desc` - Other Cargo Description

### 10. Vehicle Ownership - Owned (15 fields)
All owned vehicle fields start with `own`:
- `owntruck`, `owntract`, `owntrail`, `owncoach`
- `ownschool_1_8`, `ownschool_9_15`, `ownschool_16`
- `ownbus_16`
- `ownvan_1_8`, `ownvan_9_15`
- `ownlimo_1_8`, `ownlimo_9_15`, `ownlimo_16`

### 11. Vehicle Ownership - Term Leased (15 fields)
All term leased fields start with `trm`:
- `trmtruck`, `trmtract`, `trmtrail`, `trmcoach`
- `trmschool_1_8`, `trmschool_9_15`, `trmschool_16`
- `trmbus_16`
- `trmvan_1_8`, `trmvan_9_15`
- `trmlimo_1_8`, `trmlimo_9_15`, `trmlimo_16`

### 12. Vehicle Ownership - Trip Leased (15 fields)
All trip leased fields start with `trp`:
- `trptruck`, `trptract`, `trptrail`, `trpcoach`
- `trpschool_1_8`, `trpschool_9_15`, `trpschool_16`
- `trpbus_16`
- `trpvan_1_8`, `trpvan_9_15`
- `trplimo_1_8`, `trplimo_9_15`, `trplimo_16`

### 13. Safety & Reviews (7 fields)
- `safety_rating` - Safety rating (e.g., "Satisfactory", "Unsatisfactory", "Conditional")
- `safety_rating_date`
- `review_type`, `review_date`, `review_id`
- `recordable_crash_rate`
- `safety_inv_terr` - Safety investigation territory
- `mcsipstep` - MCSIP step

### 14. Dockets (9 fields)
- `docket1prefix`, `docket1`, `docket1_status_code`
- `docket2prefix`, `docket2`, `docket2_status_code`
- `docket3prefix`, `docket3`, `docket3_status_code`

### 15. Other (4 fields)
- `pointnum` - Point number
- `classdef` - Classification definition
- `carship` - Car ship indicator

## Query Examples

### Select all fields (like your original query)
```sql
SELECT `mcs150_date`, `add_date`, ... (all 142 fields)
```

### Select specific fields
```sql
SELECT `dot_number`, `legal_name`, `phy_state`, `phy_city`
```

### Filter by state
```sql
SELECT * WHERE `phy_state`='CA'
```

### Filter by DOT number
```sql
SELECT * WHERE `dot_number`=12345
```

### Filter by cargo type
```sql
SELECT * WHERE `crgo_genfreight`='Y'
```

### Filter with multiple conditions
```sql
SELECT * WHERE `phy_state`='CA' AND `safety_rating`='Satisfactory'
```

### Order results
```sql
SELECT * ORDER BY `dot_number` DESC
```

### Limit results
```sql
SELECT * LIMIT 100
```

### Combine filters, ordering, and limits
```sql
SELECT `dot_number`, `legal_name`, `safety_rating` 
WHERE `phy_state`='CA' 
ORDER BY `dot_number` ASC 
LIMIT 100
```

## Response Format

The API returns JSON in this format:

```json
{
  "data": [
    {
      "dot_number": 12345,
      "legal_name": "Example Carrier Inc",
      "phy_state": "CA",
      ...
    },
    ...
  ],
  "metadata": {
    ...
  }
}
```

## Pagination

- Use `pageNumber` (1-indexed) and `pageSize` (max recommended: 5000)
- Check if `len(data) < pageSize` to determine if more pages exist

## Rate Limits

- Without app token: Lower rate limits
- With app token: Higher rate limits (recommended)
- Get app token at: https://dev.socrata.com/register

## Important Notes

1. **Field names** must be wrapped in backticks: `` `field_name` ``
2. **String values** in WHERE clauses use single quotes: `'value'`
3. **Numeric values** don't need quotes: `12345`
4. **POST method** is recommended for queries with many fields
5. **SoQL** is similar to SQL but has some differences
6. Dataset contains **2,199,279 records** (as of last update)

