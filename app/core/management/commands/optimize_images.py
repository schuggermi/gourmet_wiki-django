import os
from django.core.management.base import BaseCommand
from PIL import Image

class Command(BaseCommand):
    help = "Optimiert Bilder im static-Ordner oder einzelne Dateien und erstellt WebP-Versionen"

    def add_arguments(self, parser):
        parser.add_argument(
            '--files',
            nargs='+',
            type=str,
            help='Liste von Bilddateien, die optimiert werden sollen'
        )
        parser.add_argument(
            '--quality',
            type=int,
            default=75,
            help='Qualität für optimierte JPEG/PNG/WebP-Bilder (1-100, Standard=75)'
        )

    def handle(self, *args, **kwargs):
        files = kwargs.get('files')
        quality = kwargs.get('quality')

        if files:
            # Einzelne Dateien optimieren
            for file_path in files:
                if os.path.exists(file_path):
                    self.optimize_image(file_path, quality)
                else:
                    self.stdout.write(self.style.WARNING(f"Datei existiert nicht: {file_path}"))
        else:
            # Alle Bilder im static-Ordner optimieren
            static_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static')
            for root, dirs, files in os.walk(static_root):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        file_path = os.path.join(root, file)
                        self.optimize_image(file_path, quality)

    def optimize_image(self, path, quality):
        try:
            img = Image.open(path)
            original_format = img.format

            # Optimieren und Original überschreiben (JPEG/PNG)
            if original_format == 'JPEG':
                img.save(path, 'JPEG', optimize=True, quality=quality)
            elif original_format == 'PNG':
                img.save(path, 'PNG', optimize=True)
            elif original_format == 'WEBP':
                img.save(path, 'WEBP', optimize=True, quality=quality)

            self.stdout.write(self.style.SUCCESS(f"Optimiert: {path}"))

            # WebP-Version erstellen (außer wenn es schon WebP ist)
            if original_format != 'WEBP':
                webp_path = os.path.splitext(path)[0] + '.webp'
                img.save(webp_path, 'WEBP', optimize=True, quality=quality)
                self.stdout.write(self.style.SUCCESS(f"WebP erstellt: {webp_path}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Fehler bei {path}: {e}"))
