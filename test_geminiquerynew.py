import pathlib
import textwrap

import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

GOOGLE_API_KEY=('AIzaSyAV5Ee-abg_SrUP6MpoC60f3EpXysZc4N8')

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-pro')

with open('txt_ref/dartfrog_query.txt', 'r') as file:
  query_text = file.read()

text_file_path = 'txt_ref/output_text_customers.txt'
with open(text_file_path, 'r') as text_file:
  additional_data = text_file.read()

combined_content = query_text + '\n' + additional_data

with open('txt_ref/dartfrog_query.txt', 'w') as file:
  file.write(combined_content)

response = model.generate_content(combined_content)
print(response.text)