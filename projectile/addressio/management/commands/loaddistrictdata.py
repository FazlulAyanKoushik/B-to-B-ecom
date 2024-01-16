import json
import os

from django.core.management import BaseCommand
from tqdm import tqdm

from ...models import District, Division


class Command(BaseCommand):
    help = "Save data into District"

    def handle(self, *args, **options):
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/bangladesh-geojson-master/bd-districts.json",
        )

        with open(file_path, "r", encoding="utf-8") as f:
            base_data = json.load(f)

        self.stdout.write(self.style.SUCCESS(f"Creating districts ... "))

        for data in tqdm(base_data["districts"]):
            division = Division.objects.get(id=data["division_id"])

            District.objects.get_or_create(
                name=data["name"].title(),
                defaults={
                    "id": int(data["id"]),
                    "name": data["name"].title(),
                    "bengali_name": data["bn_name"],
                    "latitude": data["lat"],
                    "longitude": data["long"],
                    "division": division,
                },
            )

        self.stdout.write(self.style.SUCCESS(f"Successfully created district"))
