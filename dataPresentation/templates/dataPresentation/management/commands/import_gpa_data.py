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
            header = next(reader)  # Skip the header row
            for row in reader:
                try:
                    # Map columns based on the header
                    data = dict(zip(header, row))
                    GPAData.objects.create(
                        gpa_group=data['GPA Group'],
                        freshman_male=int(data['Freshman Male']),
                        freshman_female=int(data['Freshman Female']),
                        freshman_total=int(data['Freshman Total']),
                        sophomore_male=int(data['Sophomore Male']),
                        sophomore_female=int(data['Sophomore Female']),
                        sophomore_total=int(data['Sophomore Total']),
                        junior_male=int(data['Junior Male']),
                        junior_female=int(data['Junior Female']),
                        junior_total=int(data['Junior Total']),
                        senior_male=int(data['Senior Male']),
                        senior_female=int(data['Senior Female']),
                        senior_total=int(data['Senior Total']),
                    )
                except KeyError as e:
                    self.stdout.write(self.style.ERROR(f'Missing column: {e} in {csv_file}'))
                    continue  # Skip to the next row
                except ValueError as e:
                    self.stdout.write(self.style.ERROR(f'Error converting data in row: {row} from {csv_file}. Error: {e}'))
                    continue
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing row: {row} from {csv_file}. Error: {e}'))
                    continue

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))