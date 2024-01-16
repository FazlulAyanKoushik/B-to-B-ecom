from django.core.management import BaseCommand, call_command

from addressio.models import Division, District, Upazila


class Command(BaseCommand):
    help = "Save data into PostOffice"

    def handle(self, *args, **options):
        self.stdout.write("Creating address data")

        call_command("loaddivision")
        call_command("loaddistrictdata")
        call_command("loadupazila")
