import json
from pathlib import Path
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Merge two JSON files and avoid duplicates based on fdc_id'

    def add_arguments(self, parser):
        parser.add_argument('file1', type=str, help='Path to the first JSON file')
        parser.add_argument('file2', type=str, help='Path to the second JSON file')
        parser.add_argument('output', type=str, help='Path for the merged output JSON file')

    def handle(self, *args, **options):
        file1_path = Path(options['file1'])
        file2_path = Path(options['file2'])
        output_path = Path(options['output'])

        if not file1_path.exists() or not file2_path.exists():
            self.stderr.write(self.style.ERROR('One or both input files do not exist'))
            return

        # Dateien einlesen
        with open(file1_path, 'r', encoding='utf-8') as f:
            data1 = json.load(f)
        with open(file2_path, 'r', encoding='utf-8') as f:
            data2 = json.load(f)

        # fdc_id als Schlüssel nutzen, um Duplikate zu vermeiden
        merged_dict = {item['fdc_id']: item for item in data1}

        for item in data2:
            if item['fdc_id'] not in merged_dict:
                merged_dict[item['fdc_id']] = item

        # Zusammengeführte Daten in eine Liste zurückwandeln
        merged_list = list(merged_dict.values())

        # Ausgabe speichern
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_list, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(
            f'Merged {len(data1)} + {len(data2)} entries into {len(merged_list)} unique entries.'
        ))
