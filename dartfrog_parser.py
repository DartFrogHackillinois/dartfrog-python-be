import csv

with open('annual-enterprise-survey-2021-financial-year-provisional.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)

    for row in reader:
        print(row)