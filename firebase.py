import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore, threading
import json
import csv

import pathlib
import textwrap
import google.generativeai as genai

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from IPython.display import display
from IPython.display import Markdown
import csv


cred = credentials.Certificate(
    "json_creds/dartfrog-ecb02-firebase-adminsdk-tt4ph-fe4cf40a97.json")  # local creds in project directory
firebase_admin.initialize_app(cred)  # firebase_admin initializes creds

db = firestore.client()  # creates a client for the python program

callback_done = threading.Event()


def on_snapshot(col_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            latest_document = change.document.to_dict()
            latest_data = json.dumps(latest_document, indent=4, sort_keys=True, default=str)
            processed_data = json.loads(latest_data)
            content = processed_data['content']
            user_id = processed_data['userID']

            print(content)
            try:
                graphData = {  # working with python dictionary to post to Firestore
                    "graph_response": content, # Use a field name to store the response
                    "user_id": user_id
                }  # dictionary and json data were mismatched

                dartfrog_data = db.collection("graphData").document("iRoqnCqgAYzgOmbeGdG1").update(graphData)



            except Exception as e:
                print("Failed to upload graph data")



            with open('txt_ref/dartfrog_query.txt', 'r') as file:
                query_text = file.read()  # opens query prompt for reading

            with open('txt_ref/data.txt', 'w') as text_file:
                text_file.write(content)  # opens and writes firebase provided data

            with open('txt_ref/data.txt', 'r') as data_file:
                data = data_file.read()  # opens firebase provided data for reading by gemini in combined_content

            with open('txt_ref/combined_content.txt', 'w') as output_file:
                output_file.write(query_text)  # connects both query and supplied data
                output_file.write('\n')  # Add a newline between the files
                output_file.write(data)

            print("Success")  # success lol

    callback_done.set()


# Assuming 'timestamp' field for ordering
doc_ref = db.collection("csvUploads").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1)
query_watch = doc_ref.on_snapshot(on_snapshot)

# Wait for the callback to complete
callback_done.wait()



