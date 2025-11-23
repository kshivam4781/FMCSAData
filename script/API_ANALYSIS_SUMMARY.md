# API Analysis Summary - California SOS Business Search

## Key Discoveries

### 1. **2-Character Limit - NOT ENFORCED!**
- **Finding**: The API **DOES accept 2-character searches**
- **Test Results**:
  - `''` (empty): 0 records
  - `'A'` (1 char): 0 records  
  - `'AB'` (2 chars): **500 records** ✅
  - `'ABC'` (3 chars): 499 records

**Conclusion**: The 3-character minimum is likely **client-side validation only**. The API/stored procedure accepts 2+ characters.

### 2. **Pagination Limit**
- **Maximum records per query**: 500 records
- **No pagination parameters found**: Tested common parameters (page, limit, offset, etc.) - none work
- **Enforcement**: Likely in stored procedure `usp_FILING_WebSearch`

### 3. **Database Confirmed**
- **Database**: SQL Server
- **Evidence**: Stored procedure name `usp_FILING_WebSearch` (usp_ prefix is SQL Server convention)
- **Backend**: ASP.NET 4.0 with stored procedures

## Strategies to Get ALL Data

### Option 1: Two-Character Combinations (Most Comprehensive)
- **AA-ZZ**: 676 combinations (26 × 26)
- **A0-Z9**: 260 combinations (26 × 10)
- **0A-9Z**: 260 combinations (10 × 26)
- **Total**: ~1,196 API calls
- **Estimated time**: 20-40 minutes
- **Coverage**: Should capture most business names

### Option 2: Wildcard Patterns (Faster, Less Complete)
- Use patterns like `[0-9]`, `[A-Z]`, `%AB`, `%INC`, `%LLC`, etc.
- **Pros**: Faster (10-20 queries)
- **Cons**: May miss records, only gets ~3,000-5,000 unique records

### Option 3: Hybrid Approach (Recommended)
1. Start with wildcard patterns (quick wins)
2. Then use 2-character combinations systematically
3. Focus on common business suffixes: INC, LLC, CORP, CO, LTD

## Implementation

### Quick Test Script
```python
# Test if 2 characters work
payload = {"SEARCH_VALUE": "AB", ...}
response = requests.post(url, json=payload, headers=headers)
# Returns 500 records!
```

### Full Extraction Script
See `comprehensive_extract.py` for complete implementation.

**Warning**: Full extraction requires ~1,200 API calls and 20-40 minutes.

## Recommendations

1. **Start Small**: Test with a few 2-character combinations first
2. **Rate Limiting**: Add delays between requests (0.1-0.5 seconds)
3. **Error Handling**: Handle timeouts and rate limits gracefully
4. **Incremental Saving**: Save results periodically (every 100 queries)
5. **Resume Capability**: Track which combinations have been tested

## Estimated Database Size

- **California businesses**: Likely millions of records
- **Current extraction**: ~3,400 unique records from 10 patterns
- **Full extraction**: Could yield 100,000+ unique records with 2-char combinations
- **Complete database**: May require additional strategies (3-char combinations, date ranges, etc.)

## Notes

- API appears to have no rate limiting (but be respectful)
- Token expires (check session-timeout header)
- Some patterns return same records (e.g., `%AB` and `%AB%` return overlapping results)
- Use dictionary to deduplicate by record ID

