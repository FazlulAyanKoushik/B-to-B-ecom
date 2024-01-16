import json
import os

from django.core.management import BaseCommand
from rest_framework.exceptions import APIException
from tqdm import tqdm

from addressio.models import District, Upazila, Division


class Command(BaseCommand):
    help = "Loads data for Upazila model from a JSON file"

    def handle(self, *args, **options):
        # Get the absolute path of the json file
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/bangladesh-geojson-master/bd-postcodes.json",
        )

        # Read the json data
        with open(file_path, "r", encoding="utf-8") as f:
            base_data = json.load(f)

        self.stdout.write(self.style.SUCCESS(f"Creating upazila ... "))

        for data in tqdm(base_data["postcodes"]):
            # Get district for create upazila
            try:
                district = District.objects.get(id=data["district_id"])
            except District.DoesNotExist:
                self.stdout.write(
                    self.style.SUCCESS(f"District {data['district_id']} cannot found.")
                )
                raise APIException(
                    detail=f"District {data['district_id']} cannot found."
                )

            try:
                division = Division.objects.get(id=data["division_id"])
            except District.DoesNotExist:
                self.stdout.write(
                    self.style.SUCCESS(f"Division {data['division_id']} cannot found.")
                )
                raise APIException(
                    detail=f"Division {data['division_id']} cannot found."
                )

            # Create Upazila if not exist else get
            upazila, created = Upazila.objects.get_or_create(
                name=data["upazila"].title(),
                division=division,
                district=district,
            )
        self.stdout.write(self.style.SUCCESS(f"Successfully created upazila"))
