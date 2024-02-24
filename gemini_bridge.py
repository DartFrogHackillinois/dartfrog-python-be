import pathlib
import textwrap

import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
import csv

with open('customers-1000.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    with open('txt_ref/output_text.txt', 'w') as text_file:
        for row in csv_reader:
            text_file.write(','.join(row) + '\n')


def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


GOOGLE_API_KEY = ('AIzaSyBaoV9kl3p8wEo0yXB89AosAfdVynkzpDY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

with open('txt_ref/dartfrog_query.txt', 'r') as file:
    query_text = file.read()

with open('txt_ref/data.txt', 'r') as text_file:
    additional_data = text_file.read()

with open('txt_ref/combined_content.txt', 'w') as output_file:
    output_file.write(query_text)
    output_file.write('\n')  # Add a newline between the files
    output_file.write(additional_data)


with open('txt_ref/combined_content.txt', 'r') as input_file:
    content = input_file.read()

query = content


try:
    response = model.generate_content(query)
    print(response.text)
except Exception as e:
    print(f"An error occurred: {e}")  # error 500 is due to limit



