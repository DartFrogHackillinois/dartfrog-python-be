import pathlib
import textwrap

import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown


def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


GOOGLE_API_KEY = ('AIzaSyAV5Ee-abg_SrUP6MpoC60f3EpXysZc4N8')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Load files
with open('txt_ref/dartfrog_query.txt', 'r') as file:
    query_text = file.read()

with open('txt_ref/output_text_customers.txt', 'r') as text_file:
    additional_data = text_file.read()

# Combine content and write to 'combined_content.txt'
with open('txt_ref/combined_content.txt', 'w') as output_file:
    output_file.write(query_text)
    output_file.write('\n')  # Add a newline between the files
    output_file.write(additional_data)

# Read the combined content and send it to the AI model
with open('txt_ref/combined_content.txt', 'r') as input_file:
    content = input_file.read()

response = model.generate_content(content)
print(response.text)
