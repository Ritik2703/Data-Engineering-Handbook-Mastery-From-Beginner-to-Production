# 6. REST API Integration — requests, Auth, Pagination, Retries

## The `requests` Library — Foundation
```python
import requests

response = requests.get("https://api.example.com/orders", timeout=30)
response.raise_for_status()  # raises an exception for 4xx/5xx status codes
data = response.json()       # parses JSON response body into a Python dict/list
```
> Always set `timeout` — a hung request without one can freeze a pipeline indefinitely.

## Authentication Types (know all of these — every API uses one)

### API Key (header or query param)
```python
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get(url, headers=headers)

# or as a query parameter
response = requests.get(url, params={"api_key": api_key})
```

### Basic Auth
```python
from requests.auth import HTTPBasicAuth
response = requests.get(url, auth=HTTPBasicAuth("username", "password"))
```

### OAuth2 Client Credentials Flow (very common for B2B/enterprise APIs — no user login involved)
```python
def get_oauth2_token(token_url, client_id, client_secret, scope):
    response = requests.post(token_url, data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope,
    })
    response.raise_for_status()
    return response.json()["access_token"]

token = get_oauth2_token(
    "https://auth.example.com/oauth/token",
    client_id="my-client-id",
    client_secret=os.getenv("CLIENT_SECRET"),
    scope="read:orders",
)
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("https://api.example.com/orders", headers=headers)
```
**Real scenario**: this exact pattern is used for Microsoft Graph API (see `10-sharepoint-graph-api-integration.md`), Salesforce, and most modern enterprise SaaS APIs — a scheduled pipeline can't "log in" as a human, so it authenticates as an application instead.

### Session objects (reuse connections, persist auth across many calls — more efficient)
```python
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {token}"})

for endpoint in ["orders", "customers", "products"]:
    response = session.get(f"https://api.example.com/{endpoint}")
    process(response.json())
# Connection pooling under the hood makes repeated calls to the same host faster
```

## Pagination Patterns (every real API pull needs this)

### Offset/Limit pagination
```python
def fetch_all_offset_paginated(base_url, headers):
    all_records = []
    offset = 0
    limit = 100
    while True:
        response = requests.get(base_url, headers=headers, params={"offset": offset, "limit": limit})
        response.raise_for_status()
        page = response.json()
        records = page.get("data", [])
        if not records:
            break
        all_records.extend(records)
        offset += limit
    return all_records
```

### Cursor/token-based pagination (more common in modern APIs — Stripe, Microsoft Graph, Slack)
```python
def fetch_all_cursor_paginated(base_url, headers):
    all_records = []
    cursor = None
    while True:
        params = {"cursor": cursor} if cursor else {}
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        page = response.json()
        all_records.extend(page.get("data", []))
        cursor = page.get("next_cursor")
        if not cursor:
            break
    return all_records
```

### Link-header pagination (GitHub API style)
```python
def fetch_all_link_header_paginated(url, headers):
    all_records = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        all_records.extend(response.json())
        url = response.links.get("next", {}).get("url")  # requests parses the Link header automatically
    return all_records
```

## Retry & Backoff — Production-Grade (using `tenacity`, not hand-rolled loops)
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout))
)
def fetch_page(url, headers, params):
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()
```
`tenacity` handles exponential backoff, max attempts, and selective retry-on-exception-type declaratively — the production standard over hand-rolled retry loops (though understanding the manual version in `02-error-handling.md` is important first).

## Rate Limiting (respecting API limits)
```python
import time

def fetch_with_rate_limit(urls, headers, requests_per_second=5):
    delay = 1.0 / requests_per_second
    results = []
    for url in urls:
        response = requests.get(url, headers=headers)
        if response.status_code == 429:  # Too Many Requests
            retry_after = int(response.headers.get("Retry-After", 5))
            logger.warning(f"Rate limited, waiting {retry_after}s")
            time.sleep(retry_after)
            response = requests.get(url, headers=headers)  # retry once after waiting
        results.append(response.json())
        time.sleep(delay)  # proactively space out requests
    return results
```
**Real scenario**: pulling data from Salesforce/HubSpot/any SaaS API with a documented rate limit (e.g., "100 requests per minute") — proactive throttling avoids ever hitting 429s in the first place.

## POST/PUT/DELETE (writing data, not just reading)
```python
# POST - create
response = requests.post(url, json={"customer_id": 101, "amount": 500}, headers=headers)

# PUT - full update
response = requests.put(f"{url}/1001", json={"status": "shipped"}, headers=headers)

# PATCH - partial update
response = requests.patch(f"{url}/1001", json={"status": "shipped"}, headers=headers)

# DELETE
response = requests.delete(f"{url}/1001", headers=headers)
```

## Handling Different Response Types
```python
response = requests.get(url)

response.json()          # parsed JSON (most common)
response.text             # raw text response
response.content          # raw bytes (for files/images/binary data)
response.status_code      # 200, 404, 500, etc.
response.headers          # response headers dict

# Downloading a file (e.g., a CSV export from an API)
with requests.get(file_url, stream=True) as r:
    r.raise_for_status()
    with open("downloaded.csv", "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
```

## Full Production-Grade Extraction Function (putting it all together)
```python
import logging
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=2, min=2, max=30))
def _fetch_page(url, headers, params):
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()

def extract_all_orders(api_base_url, api_key, updated_since):
    """Pulls all order records updated since a given timestamp, handling pagination,
    retries, and logging — the production-standard extraction pattern."""
    headers = {"Authorization": f"Bearer {api_key}"}
    all_orders = []
    cursor = None

    while True:
        params = {"updated_since": updated_since, "limit": 500}
        if cursor:
            params["cursor"] = cursor
        try:
            page = _fetch_page(api_base_url, headers, params)
        except requests.exceptions.HTTPError as e:
            logger.error(f"Non-retryable HTTP error while extracting orders: {e}")
            raise
        except Exception as e:
            logger.error(f"Extraction failed after retries: {e}")
            raise

        records = page.get("data", [])
        all_orders.extend(records)
        logger.info(f"Fetched {len(records)} records (total so far: {len(all_orders)})")

        cursor = page.get("next_cursor")
        if not cursor:
            break

    logger.info(f"Extraction complete: {len(all_orders)} total orders")
    return all_orders
```

## Try It Yourself
1. Write a paginated extractor for a cursor-based API (use https://jsonplaceholder.typicode.com/posts as a free test API — note it isn't paginated, so simulate pagination logic separately).
2. Add `tenacity`-based retry logic to a function that calls a public API.
3. Implement proactive rate limiting for a loop of 50 API calls at 5 requests/second.

## Interview Traps
- "How do you handle pagination in a Python extractor?" — be ready to describe offset-based vs cursor-based vs link-header, and why cursor-based is generally preferred for large/changing datasets (offset pagination can skip/duplicate records if data changes between page fetches).
- "How do you avoid hardcoding retry logic everywhere?" — mention `tenacity` decorators as the production standard.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every dataset tells a story; listen to it without forcing your assumptions onto it."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
