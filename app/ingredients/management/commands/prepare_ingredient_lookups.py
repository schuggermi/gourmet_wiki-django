import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from ingredients.models import IngredientLookup, Category

PAGE_SIZE = 200  # Max per USDA docs

SEARCH_URL = settings.USDA_FDC_BASE_URL + "/foods/search"


class Command(BaseCommand):
    help = "Fetch and store all natural (non-branded) ingredients from USDA API"

    def handle(self, *args, **kwargs):
        page_number = 1
        total_records = None

        while True:
            self.stdout.write(f"Fetching page {page_number}...")

            payload = {
                "query": ", raw",
                "dataType": ["SR Legacy", "Survey (FNDDS)", "Foundation"],
                # Natural foods only "Foundation", "Survey (FNDDS)", "Foundation", "SR Legacy"
                "pageSize": PAGE_SIZE,
                "pageNumber": page_number,
            }
            headers = {
                'X-Api-Key': settings.USDA_FDC_API_KEY
            }

            response = requests.post(SEARCH_URL, json=payload, headers=headers)
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Error fetching data: {response.status_code}"))
                break

            data = response.json()

            if total_records is None:
                total_records = data.get('totalHits', 0)
                self.stdout.write(f"Total natural ingredients found: {total_records}")

            foods = data.get('foods', [])
            if not foods:
                self.stdout.write("No more foods found, stopping.")
                break

            for food in foods:
                category = food['foodCategory']
                fdc_id = food['fdcId']
                description = food['description']

                obj, created = IngredientLookup.objects.update_or_create(
                    fdc_id=fdc_id,
                    defaults={
                        'description': description,
                        'category': category
                    }
                )
                if created:
                    self.stdout.write(f"Added ingredient lookup: {description} (fdcId={fdc_id})")

            # Check if we have fetched all pages
            fetched_so_far = page_number * PAGE_SIZE
            if fetched_so_far >= total_records:
                break

            page_number += 1

        self.stdout.write(
            self.style.SUCCESS("Successfully fetched and stored all natural ingredients in IngredientLookup."))
