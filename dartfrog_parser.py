import csv

csv_file_path = 'annual-enterprise-survey-2021-financial-year-provisional.csv'
text_file_path = 'txt_ref/data.txt'

with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    with open(text_file_path, 'w') as text_file:
        for row in csv_reader:
            text_file.write(','.join(row) + '\n')
