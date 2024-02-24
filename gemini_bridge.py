import pathlib
import textwrap

import google.generativeai as genai
from google.colab import userdata
from IPython.display import display
from IPython.display import Markdown

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

GOOGLE_API_KEY=userdata.get('AIzaSyAV5Ee-abg_SrUP6MpoC60f3EpXysZc4N8')
