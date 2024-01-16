import json
import os
from decimal import Decimal

from django.core.management.base import BaseCommand
from tqdm import tqdm

from ...models import Division


class Command(BaseCommand):
    help = "Loads data for Division model from a JSON file"

    def handle(self, *args, **options):
        # Get the absolute path of the json file
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/bangladesh-geojson-master/bd-divisions.json",
        )

        with open(file_path, "r", encoding="utf-8") as f:
            base_data = json.load(f)

        # Create division if not exist else return only division name
        self.stdout.write(self.style.SUCCESS(f"Creating divisions ... "))

        for division_data in tqdm(base_data["divisions"]):
            division, created = Division.objects.get_or_create(
                name=division_data["name"].title(),
                defaults={
                    "id": int(division_data["id"]),
                    "name": division_data["name"].title(),
                    "bengali_name": division_data.get("bn_name"),
                    "latitude": Decimal(division_data["lat"]),
                    "longitude": Decimal(division_data["long"]),
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Successfully created division"))
