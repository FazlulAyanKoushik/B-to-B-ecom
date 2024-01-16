from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import QuerySet

from tqdm import tqdm

from catalogio.models import Brand, DosageForm, Manufacturer


class Command(BaseCommand):
    help = "Band, Dosage form and Manufracturer will be udated in title case"

    def handle(self, *args, **options):
        brands = Brand.objects.filter()

        for brand in tqdm(brands):
            with transaction.atomic():
                """
                convert first letter of brand's name into Capital letter
                example a flox -> A Flox
                """
                brand.name = brand.name.title()

                brand.save()

        manufacturers = Manufacturer.objects.filter()
        for manufacturer in tqdm(manufacturers):
            with transaction.atomic():
                """
                convert first letter of manufacturer's name into Capital letter
                example ibn sina pharmaceuticles -> Ibn Sina Pharmaceuticles
                """
                manufacturer.name = manufacturer.name.title()

                manufacturer.save()

        dosage_forms = DosageForm.objects.filter()
        for dosage_form in tqdm(dosage_forms):
            with transaction.atomic():
                """
                convert first letter of dosage form name into Capital letter
                example eye ointment -> Eye Ointment
                """
                dosage_form.name = dosage_form.name.title()

                dosage_form.save()
