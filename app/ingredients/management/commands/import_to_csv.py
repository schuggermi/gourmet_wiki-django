import json
import csv
from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Convert a JSON file of ingredients into a CSV sorted by category"

    def add_arguments(self, parser):
        parser.add_argument(
            "input_file",
            type=str,
            help="Path to the input JSON file",
        )
        parser.add_argument(
            "output_file",
            type=str,
            help="Path to the output CSV file",
        )

    def handle(self, *args, **options):
        input_file = Path(options["input_file"])
        output_file = Path(options["output_file"])

        if not input_file.exists():
            self.stdout.write(self.style.ERROR(f"File {input_file} does not exist."))
            return

        # Load JSON
        with input_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Sort by category_name
        data_sorted = sorted(data, key=lambda x: x["category_name"])

        # Write CSV
        with output_file.open("w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["category_name", "category_name_de", "id", "name", "name_de", "fdc_id"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for item in data_sorted:
                writer.writerow({
                    "category_name": item.get("category_name", ""),
                    "category_name_de": item.get("category_name_de", ""),
                    "id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "name_de": item.get("name_de", ""),
                    "fdc_id": item.get("fdc_id", ""),
                })

        self.stdout.write(self.style.SUCCESS(f"CSV file created successfully at {output_file}"))
