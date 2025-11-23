# API Usage Comparison: Node.js App vs Python Client

## Overview

The Node.js application in `DOT_NodeJS_Web` uses a **different API endpoint** than the Python client. Here's the comparison:

## Node.js Application (Current Implementation)

### API Endpoint
```javascript
const API_BASE_URL = "https://data.transportation.gov/resource/az4n-8mr2.json";
```

**This is the OLD Socrata API format** (legacy endpoint)

### How It Queries the API

**Location**: `server.js` lines 182-201

```javascript
async function queryAPIBatch(dotNumbers) {
    const dotConditions = dotNumbers.map(dot => `dot_number = '${dot}'`).join(' OR ');
    const whereClause = `(${dotConditions})`;
    
    const params = {
        '$where': whereClause,
        '$select': 'dot_number,mcs150_date'
    };
    
    const response = await axios.get(API_BASE_URL, { params, timeout: 30000 });
    return response.data;
}
```

### Key Characteristics

1. **Endpoint Format**: `/resource/{dataset-id}.json` (old Socrata format)
2. **Query Method**: GET request with URL parameters
3. **Query Syntax**: Uses `$where` and `$select` parameters (old SoQL syntax)
4. **Authentication**: **NO APP TOKEN** - appears to work without authentication
5. **Batch Size**: Processes 100 DOT numbers per batch
6. **Fields Retrieved**: Only `dot_number` and `mcs150_date`

### Example Request
```
GET https://data.transportation.gov/resource/az4n-8mr2.json?$where=(dot_number='12345' OR dot_number='67890')&$select=dot_number,mcs150_date
```

## Python Client (New Implementation)

### API Endpoint
```python
BASE_URL = "https://data.transportation.gov/api/v3/views/az4n-8mr2"
```

**This is the NEW Socrata API v3.0 format**

### How It Queries the API

**Location**: `fmcsa_api_client.py`

```python
def query(self, fields, where, page_number=1, page_size=5000, use_post=True):
    query_str = self._build_query(fields=fields, where=where, order=order)
    
    payload = {
        "query": query_str,
        "page": {
            "pageNumber": page_number,
            "pageSize": page_size
        },
        "includeSynthetic": False
    }
    
    response = self.session.post(url, json=payload, headers=headers)
```

### Key Characteristics

1. **Endpoint Format**: `/api/v3/views/{dataset-id}/query.json` (new v3.0 format)
2. **Query Method**: POST with JSON body (or GET with `query` parameter)
3. **Query Syntax**: Uses SoQL query string (new format)
4. **Authentication**: **REQUIRES APP TOKEN** - returns 403 without it
5. **Batch Size**: Configurable (default 5000 per page)
6. **Fields Retrieved**: All 142 fields available

### Example Request
```
POST https://data.transportation.gov/api/v3/views/az4n-8mr2/query.json
Content-Type: application/json
X-App-Token: YOUR_TOKEN

{
  "query": "SELECT `dot_number`, `mcs150_date` WHERE `dot_number`='12345' OR `dot_number`='67890'",
  "page": {
    "pageNumber": 1,
    "pageSize": 5000
  }
}
```

## Key Differences

| Feature | Node.js App (Old API) | Python Client (New API) |
|---------|----------------------|------------------------|
| **Endpoint** | `/resource/az4n-8mr2.json` | `/api/v3/views/az4n-8mr2/query.json` |
| **Authentication** | Not required | **Required (app token)** |
| **Query Format** | `$where` and `$select` params | SoQL query string |
| **HTTP Method** | GET only | POST (recommended) or GET |
| **Pagination** | Not used | Built-in pagination |
| **Rate Limits** | Lower (no token) | Higher (with token) |
| **Fields** | Limited selection | All 142 fields available |

## Why the Node.js App Works Without Authentication

The **old API endpoint** (`/resource/...`) might:
1. Still be available for backward compatibility
2. Have different authentication requirements
3. Be deprecated but still functional

However, the **new API v3.0** (`/api/v3/views/...`) **requires authentication**.

## Recommendation

### Option 1: Use the Old API Endpoint (Like Node.js App)

If you want to avoid authentication, you could use the old endpoint:

```python
# Old endpoint (no auth required)
url = "https://data.transportation.gov/resource/az4n-8mr2.json"
params = {
    '$where': "dot_number='12345'",
    '$select': 'dot_number,mcs150_date'
}
response = requests.get(url, params=params)
```

### Option 2: Use the New API with App Token (Recommended)

The new API is more robust and has better rate limits. Just get an app token.

### Option 3: Update Node.js App to Use New API

The Node.js app could be updated to use the new API format for better reliability.

## Testing the Old Endpoint

You can test if the old endpoint still works:

```python
import requests

url = "https://data.transportation.gov/resource/az4n-8mr2.json"
params = {
    '$where': "dot_number='12345'",
    '$select': 'dot_number,legal_name',
    '$limit': 5
}

response = requests.get(url, params=params)
print(response.status_code)
print(response.json())
```

If this works without authentication, you can use it in your Python script!

