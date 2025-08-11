from apify_client import ApifyClient
import os
from pathlib import Path
from dotenv import load_dotenv

# Load the .env from the project root explicitly
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

ACTOR_ID = os.getenv("APIFY_LINKEDIN_ACTOR_ID", "BHzefUZlZRKWxkTck")
__all__ = ["fetch_linkedin_jobs"]

def fetch_linkedin_jobs(search_query: str, location: str = "India", rows: int = 60):
    """Fetch LinkedIn jobs via Apify actor. Requires APIFY_API_TOKEN in .env or env vars."""
    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        raise RuntimeError("APIFY_API_TOKEN is not set. Put it in .env or Streamlit secrets.")
    client = ApifyClient(token)

    run_input = {
        "title": search_query,
        "location": location,
        "rows": rows,
        "sortby": "relevance",
        "freshness": "all",
        "experience": "all",
        "proxy": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
    }
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    dataset_id = run.get("defaultDatasetId") or run.get("defaultDatasetID")
    if not dataset_id:
        raise RuntimeError("Apify run did not return a dataset ID.")
    return list(client.dataset(dataset_id).iterate_items())