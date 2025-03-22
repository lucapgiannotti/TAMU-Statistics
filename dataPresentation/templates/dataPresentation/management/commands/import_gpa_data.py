# dataPresentation/management/commands/import_gpa_data.py

import csv
from django.core.management.base import BaseCommand
from dataPresentation.models import GPAData

class Command(BaseCommand):
    help = 'Import GPA data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to be imported')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, newline='') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                GPAData.objects.create(
                    year=row[0],
                    term=row[1],
                    college=row[2],
                    course=row[3],
                    gpa=row[4]
                )
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))