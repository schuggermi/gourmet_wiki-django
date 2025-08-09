import requests
from django.conf import settings

def get_food_by_fdc_id(fdc_id: int):
    """
    Retrieve detailed food item information from USDA FoodData Central by fdcId.
    """
    url = f"{settings.USDA_FDC_BASE_URL}/food/{fdc_id}"
    print(repr(settings.USDA_FDC_API_KEY))
    params = {}
    headers = {
        "X-Api-Key": settings.USDA_FDC_API_KEY
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching USDA FDC data: {e}")
        return None