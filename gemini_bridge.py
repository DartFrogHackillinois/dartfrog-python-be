# FIREBASE.PY RUNS FIRST
# GEMINI_BRIDGE RUNS SECOND

import pathlib
import textwrap
import google.generativeai as genai

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from IPython.display import display
from IPython.display import Markdown
import csv


'''def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))'''


cred = credentials.Certificate('json_creds/dartfrog-ecb02-firebase-adminsdk-tt4ph-fe4cf40a97.json') # cert from firebase

app = firebase_admin.initialize_app(cred) # init for firebase client

db = firestore.client()

GOOGLE_API_KEY = ('AIzaSyBaoV9kl3p8wEo0yXB89AosAfdVynkzpDY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

with open('txt_ref/combined_content.txt', 'r') as input_file: # pulling user placed, firebase uploaded content
    content = input_file.read()

query = content

try:
    response = model.generate_content(query) # response from gemini
    print(response.text)
    #print(type(response.text)) # prints type string
    updateData = { # working with python dictionary to post to Firestore
        "generated_response": response.text  # Use a field name to store the response
    } # dictionary and json data were mismatched

    responseDart = db.collection("responseMessages").document("7H5hzZUGr7jRMV69yjyp").update(updateData)



except Exception as e:
    print(f"An error occurred: {e}")  # error 500 is due to limit
