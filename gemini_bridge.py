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


with open('dartfrog_query.txt', 'r') as file:
  query_text = file.read()

response = model.generate_content(query_text)
print(response.text)


