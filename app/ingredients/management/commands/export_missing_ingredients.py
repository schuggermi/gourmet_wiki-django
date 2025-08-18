import json
from pathlib import Path

from django.core.management.base import BaseCommand
from ingredients.models import Ingredient


class Command(BaseCommand):
    help = "Export DB ingredients not present in the input JSON (by fdc_id) to a JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "input_file",
            type=str,
            help="Path to the input JSON file with ingredients",
        )
        parser.add_argument(
            "output_file",
            type=str,
            help="Path to the output JSON file for missing ingredients",
        )

    def handle(self, *args, **options):
        input_file = Path(options["input_file"])
        output_file = Path(options["output_file"])

        if not input_file.exists():
            self.stdout.write(self.style.ERROR(f"File {input_file} does not exist."))
            return

        # Load input JSON and extract fdc_ids
        with input_file.open("r", encoding="utf-8") as f:
            existing_data = json.load(f)

        existing_fdc_ids = {item.get("fdc_id") for item in existing_data if item.get("fdc_id") is not None}

        missing_ingredients = []

        # Iterate DB ingredients
        for ingredient in Ingredient.objects.all():
            if ingredient.fdc_id not in existing_fdc_ids:
                missing_ingredients.append({
                    "id": ingredient.id,
                    "name": ingredient.name,
                    "name_de": "",
                    "category_name": ingredient.category.id if ingredient.category else None,
                    "category_name_de": "",
                    "fdc_id": ingredient.fdc_id,
                })

        # Write missing ingredients to output JSON
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(missing_ingredients, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(
            f"Exported {len(missing_ingredients)} ingredients missing in input JSON to {output_file}"
        ))
