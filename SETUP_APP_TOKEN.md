# Setting Up Your App Token

## The API Requires Authentication

The FMCSA API requires an app token for all requests. You'll get a `403 Forbidden` error without one.

## How to Get Your App Token

1. **Visit**: https://dev.socrata.com/register
2. **Sign up** for a free account (or log in if you already have one)
3. **Create an app token** - it's free and takes just a minute
4. **Copy your token** - it will look something like: `abc123xyz456...`

## How to Use Your Token

### Option 1: Update the Script Directly

Edit `get_ca_companies.py` and change this line:

```python
client = FMCSAAPIClient(app_token=None)
```

To:

```python
client = FMCSAAPIClient(app_token="YOUR_TOKEN_HERE")
```

### Option 2: Use Environment Variable (Recommended)

1. Set an environment variable:
   - **Windows PowerShell**: `$env:FMCSA_APP_TOKEN="your_token_here"`
   - **Windows CMD**: `set FMCSA_APP_TOKEN=your_token_here`
   - **Linux/Mac**: `export FMCSA_APP_TOKEN="your_token_here"`

2. The script will automatically use it if you update it to check for the environment variable.

### Option 3: Create a Config File

Create a file called `.env` (or `config.txt`) with:
```
FMCSA_APP_TOKEN=your_token_here
```

Then update the script to read from it.

## Test Your Token

After adding your token, run:

```bash
python test_api_connection.py
```

You should see `[SUCCESS]` messages instead of `[ERROR]` messages.

## Notes

- App tokens are **free**
- They give you higher rate limits
- Keep your token private (don't commit it to version control)
- One token can be used for multiple scripts/projects

