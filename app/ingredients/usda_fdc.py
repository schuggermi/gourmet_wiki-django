import random
import time
import requests
from django.conf import settings
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout


def get_food_by_fdc_id(fdc_id: int, retries: int = 5, backoff_factor: float = 2.0, jitter: bool = True):
    url = f"{settings.USDA_FDC_BASE_URL}/food/{fdc_id}"
    headers = {"X-Api-Key": settings.USDA_FDC_API_KEY}
    params = {
        'format': 'full'
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=30, params=params)

            if response.status_code == 404:
                print(f"FDC ID {fdc_id} not found in USDA API (HTTP 404).")
                return None

            if response.status_code == 429:
                delay = backoff_factor * (2 ** attempt)
                if jitter:
                    delay += random.uniform(0, 0.5)
                print(f"Rate limited (429) for FDC {fdc_id}. Retrying in {delay:.2f}s...")
                time.sleep(delay)
                continue

            response.raise_for_status()
            return response.json()

        except (ConnectionError, Timeout) as e:
            delay = max(2.0, backoff_factor * (2 ** attempt))
            if jitter:
                delay += random.uniform(0, 0.5)
            print(f"Network error fetching FDC ID {fdc_id}: {e}. Retrying in {delay:.2f}s...")
            time.sleep(delay)

        except HTTPError as e:
            print(f"HTTP error fetching FDC ID {fdc_id}: {e}")
            return None

        except RequestException as e:
            print(f"Unexpected error fetching FDC ID {fdc_id}: {e}")
            return None

    print(f"Failed to fetch FDC ID {fdc_id} after {retries} attempts.")
    return None
