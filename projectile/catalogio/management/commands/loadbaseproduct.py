import json
import os

from django.core.management import BaseCommand
from tqdm import tqdm

from catalogio.models import (
    Brand,
    Ingredient,
    Manufacturer,
    BaseProduct,
    Category,
    DosageForm,
)


class Command(BaseCommand):
    help = "Save data into BaseProduct"

    def handle(self, *args, **options):
        # with transaction.atomic():

        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sql.json")

        with open(file_path, "r") as f:
            base_data = json.load(f)

        category = Category.objects.create(name="Medicine")
        for data in tqdm(base_data):
            ingredients = data["ingredient"].split("+")
            ingredients = [ingredient.strip().lower() for ingredient in ingredients]

            if data["brand"].count("(") == 1 and data["brand"].count(")") == 0:
                brand_name = data["brand"].replace("(", "")
            elif data["brand"].count("(") == 0 and data["brand"].count(")") == 1:
                brand_name = data["brand"].replace(")", "")
            else:
                brand_name = data["brand"]

            baseproduct_brand, _ = Brand.objects.get_or_create(name=brand_name.lower())
            dosage_form, _ = DosageForm.objects.get_or_create(
                name=data["dosage_form"].lower()
            )

            baseproduct_manufacturer, _ = Manufacturer.objects.get_or_create(
                name=data["manufacturer"].lower()
            )
            # preprocessing unit data, checking None or split by , or /
            if data["unit"] is not None:
                if "," in data["unit"]:
                    product_units = data["unit"].split(",")
                elif "/" in data["unit"]:
                    product_units = data["unit"].split("/")
                else:
                    product_units = [data["unit"]]
            else:
                product_units = [""]

            # preprocessing mrp data, checking None or split by , or /
            if data["mrp"] is not None:
                if "," in data["mrp"]:
                    product_mrp = data["mrp"].split(",")
                elif "/" in data["mrp"]:
                    product_mrp = data["mrp"].split("/")
                else:
                    product_mrp = [data["mrp"]]
            else:
                product_mrp = ["0"]

            product_unit_postfix = (
                product_units[-1].split(" ")[-1] if data["unit"] is not None else ""
            ).rstrip()
            if product_unit_postfix != "" and product_unit_postfix in product_units[0]:
                product_unit_postfix = ""

            # adding postfix of unit
            for index, unit in enumerate(product_units):
                product_units[index] = (unit + " " + product_unit_postfix).rstrip()
            if len(product_mrp) > len(product_units):
                product_units += [product_units[-1]] * (
                    len(product_mrp) - len(product_units)
                )
            elif len(product_units) > len(product_mrp):
                product_units = product_units[: len(product_mrp)]

            for index, mrp in enumerate(product_mrp):
                if data["strength"] is not None:
                    strength_split_by_slash = data["strength"].split("/")
                    strength_postfix = ""
                    if len(strength_split_by_slash) > 1:
                        strength_postfix = "/ " + data["strength"].split("/")[-1]
                    strength_prefix = strength_split_by_slash[0]

                    for strength in strength_prefix.split("+"):
                        strength_name = (strength + strength_postfix).strip()
                        strength_name = strength_name.replace("(", "").replace(")", "")

                        if len(strength_name) > 0:
                            base_product = BaseProduct.objects.create(
                                name=(
                                    "%s %s"
                                    % (baseproduct_brand.name.title(), strength_name)
                                ).strip(),
                                description=data["description"]
                                if data["description"] is not None
                                else "",
                                dosage_form=dosage_form,
                                manufacturer=baseproduct_manufacturer,
                                category=category,
                                unit=product_units[index],
                                brand=baseproduct_brand,
                                mrp=mrp if mrp.isnumeric() else 0,
                                strength=strength_name,
                            )
                            for ingredient in ingredients:
                                data_ind, _ = Ingredient.objects.get_or_create(
                                    name=ingredient
                                )
                                base_product.active_ingredients.add(data_ind)
                else:
                    product_name = (
                        "%s %s" % (baseproduct_brand.name.title(), "")
                    ).strip()
                    base_product = BaseProduct.objects.create(
                        name=product_name,
                        description=data["description"]
                        if data["description"] is not None
                        else "",
                        dosage_form=dosage_form,
                        manufacturer=baseproduct_manufacturer,
                        category=category,
                        unit=product_units[index],
                        brand=baseproduct_brand,
                        mrp=mrp if mrp.isnumeric() else 0,
                        strength="",
                    )
                    for ingredient in ingredients:
                        data_ind, _ = Ingredient.objects.get_or_create(name=ingredient)
                        base_product.active_ingredients.add(data_ind)
