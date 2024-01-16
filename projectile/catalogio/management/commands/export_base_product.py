from typing import Any
import pandas as pd
from django.core.management import BaseCommand
from tqdm import tqdm
import uuid
from django.http import HttpResponse
from tempfile import NamedTemporaryFile
from catalogio.models import BaseProduct
import os


class Command(BaseCommand):
    help = "Base Product download in Excel file"

    def handle(self, *args, **options):
        base_products = BaseProduct.objects.all()

        # Create a list of dictionaries containing the data
        data = [
            {
                "Name": product.name,
                "Brand": product.brand.name if product.brand else "",
                "Strength": product.strength,
                "Category": product.category.name if product.category else "",
                "Dosage Form": product.dosage_form.name if product.dosage_form else "",
                "Description": product.description,
                "Unit": product.unit,
                "Manufacturer": product.manufacturer.name
                if product.manufacturer
                else "",
                "Route of Administration": product.route_of_administration.name
                if product.route_of_administration
                else "",
                "Medicine Physical State": product.medicine_physical_state.name
                if product.medicine_physical_state
                else "",
            }
            for product in tqdm(base_products)
        ]

        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(data)

        # Save the DataFrame to Excel format
        df.to_excel("base_products.xlsx", index=False)

