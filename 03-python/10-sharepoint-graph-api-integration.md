# 10. SharePoint & Microsoft Graph API Integration (Deep Dive)

## Why This Matters for Data Engineers
Most large enterprises run on Microsoft 365. Business teams (finance, HR, ops) often store working data in **SharePoint lists/Excel files**, and organizational data (users, licenses, Teams activity) lives in **Azure AD (Entra ID)**. Microsoft Graph API is the **single unified REST endpoint** for all of it — a very common real-world DE requirement is "pull this SharePoint list into the warehouse every night."

## Authentication — OAuth2 Client Credentials Flow (App-Only, No User Login)
```python
# pip install msal requests pandas
import msal
import requests
import os
import logging

logger = logging.getLogger(__name__)

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]
GRAPH_BASE = "https://graph.microsoft.com/v1.0"

def get_access_token():
    """Client-credentials flow — the app itself authenticates, no human login needed.
    Required setup in Azure AD: register an app, add Application (not Delegated)
    permissions like Sites.Read.All / User.Read.All, then grant admin consent."""
    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" not in result:
        error_desc = result.get("error_description", "Unknown error")
        logger.critical(f"Graph API authentication failed: {error_desc}")
        raise RuntimeError(f"Auth failed: {error_desc}")
    return result["access_token"]
```

## Pagination Helper (Graph API uses `@odata.nextLink`)
```python
def fetch_all_pages(url, headers):
    """Loops through Graph API pages until @odata.nextLink is no longer present."""
    results = []
    while url:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 10))
                logger.warning(f"Graph API rate limited, waiting {retry_after}s")
                import time; time.sleep(retry_after)
                continue
            logger.error(f"Graph API request failed: {e} — {response.text}")
            raise
        payload = response.json()
        results.extend(payload.get("value", []))
        url = payload.get("@odata.nextLink")
    return results
```

## Scenario 1: Pull SharePoint List Data (most common enterprise DE request)
```python
def get_site_id(hostname, site_path, headers):
    """First step: resolve a human-readable SharePoint site URL to its Graph API site_id."""
    url = f"{GRAPH_BASE}/sites/{hostname}:{site_path}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["id"]

def get_list_id(site_id, list_display_name, headers):
    url = f"{GRAPH_BASE}/sites/{site_id}/lists"
    lists = fetch_all_pages(url, headers)
    for lst in lists:
        if lst["displayName"] == list_display_name:
            return lst["id"]
    raise ValueError(f"List '{list_display_name}' not found on site")

def pull_sharepoint_list(hostname, site_path, list_display_name):
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    site_id = get_site_id(hostname, site_path, headers)
    list_id = get_list_id(site_id, list_display_name, headers)

    url = f"{GRAPH_BASE}/sites/{site_id}/lists/{list_id}/items?expand=fields"
    items = fetch_all_pages(url, headers)

    rows = [item["fields"] for item in items]
    import pandas as pd
    return pd.DataFrame(rows)

# Usage
df = pull_sharepoint_list(
    hostname="contoso.sharepoint.com",
    site_path="/sites/FinanceTeam",
    list_display_name="Budget Tracker"
)
```
**Real scenario**: Finance maintains a "Budget Tracker" as a SharePoint list (business users find Excel/SharePoint easier than asking IT for a database) — this exact function nightly pulls it into the warehouse so it can be joined with real financial data in dashboards.

## Scenario 2: Download a File from a SharePoint Document Library
```python
def download_sharepoint_file(site_id, file_path, local_save_path, headers):
    """file_path example: 'General/Reports/monthly_budget.xlsx'"""
    url = f"{GRAPH_BASE}/sites/{site_id}/drive/root:/{file_path}:/content"
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()
    with open(local_save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    logger.info(f"Downloaded SharePoint file to {local_save_path}")

# Then read it with pandas as normal (see 03-file-handling-all-formats.md)
import pandas as pd
df = pd.read_excel("monthly_budget.xlsx")
```

## Scenario 3: Pull All Azure AD Users (HR/IT analytics)
```python
def pull_all_users():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{GRAPH_BASE}/users?$select=id,displayName,mail,jobTitle,department,accountEnabled"
    users = fetch_all_pages(url, headers)
    import pandas as pd
    return pd.DataFrame(users)
```
**Real scenario**: IT/HR analytics dashboard showing headcount by department, license utilization, inactive account audits — all sourced from this single call.

## Scenario 4: Pull Teams Channel Messages (engagement analytics)
```python
def pull_teams_messages(team_id, channel_id):
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{GRAPH_BASE}/teams/{team_id}/channels/{channel_id}/messages"
    messages = fetch_all_pages(url, headers)
    import pandas as pd
    return pd.DataFrame(messages)
```
> Note: reading message *content* requires additional privacy/compliance approval in most organizations — many companies only pull metadata (timestamps, participant counts) for engagement analytics, not message text.

## Scenario 5: Pull Outlook Calendar Events (resource/room utilization analytics)
```python
def pull_calendar_events(user_id, start_datetime, end_datetime):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Prefer": 'outlook.timezone="India Standard Time"',
    }
    url = (f"{GRAPH_BASE}/users/{user_id}/calendarView"
           f"?startDateTime={start_datetime}&endDateTime={end_datetime}")
    events = fetch_all_pages(url, headers)
    import pandas as pd
    return pd.DataFrame(events)
```

## Full Production ETL Pipeline: SharePoint → Warehouse (putting it together)
```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def sharepoint_to_warehouse_pipeline():
    try:
        logger.info("Starting SharePoint extraction")
        df = pull_sharepoint_list(
            hostname="contoso.sharepoint.com",
            site_path="/sites/FinanceTeam",
            list_display_name="Budget Tracker",
        )

        if df.empty:
            raise ValueError("SharePoint list returned zero rows — possible upstream issue")

        logger.info(f"Extracted {len(df)} rows, beginning cleaning")
        df.columns = df.columns.str.lower().str.replace(" ", "_")
        df["extracted_at"] = datetime.utcnow()

        logger.info("Loading into warehouse")
        from sqlalchemy import create_engine
        engine = create_engine(os.getenv("WAREHOUSE_CONN_STRING"))
        df.to_sql("stg_sharepoint_budget", engine, if_exists="replace", index=False)

        logger.info(f"Pipeline completed successfully: {len(df)} rows loaded")

    except ValueError as e:
        logger.error(f"Data quality issue: {e}")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"Graph API call failed: {e}")
        raise
    except Exception as e:
        logger.critical(f"Unexpected pipeline failure: {e}")
        raise
```

## Common Errors & Fixes
| Error | Cause | Fix |
|---|---|---|
| `AADSTS700016` | Wrong client_id/tenant_id | Double-check Azure AD app registration values |
| `403 Forbidden` | Missing or non-consented API permission | Add Application permission in Azure AD, grant admin consent |
| `429 Too Many Requests` | Rate limited | Respect `Retry-After` header, implement backoff |
| Empty `value` array | Wrong site/list name, or user genuinely has no data | Verify site path and list display name exactly match SharePoint |

## Try It Yourself
1. Register a free Azure AD app (trial tenant) and successfully retrieve an access token.
2. Write a function to pull any SharePoint list you have access to into a pandas DataFrame.
3. Add retry logic (`tenacity`) around the Graph API calls for resilience against transient 5xx errors.
