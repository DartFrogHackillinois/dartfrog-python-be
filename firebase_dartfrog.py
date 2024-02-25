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

userID = ''
fileID = ''


def infer_data_structure(rows, chart_type):
    """
    Infer the data structure required for the chart type from the CSV rows.
    This function aims to be adaptable to different CSV formats and chart requirements.
    """
    # Initialize containers for inferred data
    structured_data = defaultdict(list)
    labels = []

    # Infer structure based on chart type
    if chart_type in ['line', 'bar', 'radar']:
        # Assume first column as labels, remaining as datasets
        labels = [row[0] for row in rows]
        for row in rows:
            for i, value in enumerate(row[1:], start=1):
                structured_data[i].append(float(value) if value else None)
    elif chart_type in ['bubble', 'scatter']:
        # Assume columns represent x, y, (and r for bubble), each row is a point
        for row in rows:
            point = [float(value) for value in row]
            structured_data[1].append({'x': point[0], 'y': point[1], 'r': point[2]} if chart_type == 'bubble' else {'x': point[0], 'y': point[1]})
    else:
        # For pie, doughnut, and polarArea, assume single dataset with multiple segments
        labels = [row[0] for row in rows]
        structured_data[1] = [float(row[1]) for row in rows]

    return labels, dict(structured_data)

def chartParser(csv_content, chart_type):
    """
    Parses any given CSV to a JSON structure suitable for Chart.js, considering the chart type.
    This function is designed to adapt to various CSV structures.
    """
    # Split the CSV content into lines and parse
    lines = csv_content.splitlines()
    reader = csv.reader(lines)
    next(reader)  # Skip headers

    # Infer the data structure from rows
    rows = list(reader)
    labels, datasets = infer_data_structure(rows, chart_type)

    # Prepare the Chart.js data structure
    chart_data = {
        'type': chart_type,
        'data': {
            'labels': labels,
            'datasets': []
        }
    }

    for i, (dataset_label, data) in enumerate(datasets.items(), start=1):
        dataset = {
            'label': f'Dataset {i}',
            'data': data
        }
        chart_data['data']['datasets'].append(dataset)

    return chart_data

def on_snapshot(col_snapshot, changes, read_time):
    global userID
    global fileID
    for change in changes:
        if change.type.name == 'ADDED':
            latest_document = change.document.to_dict()
            latest_data = json.dumps(latest_document, indent=4, sort_keys=True, default=str)
            processed_data = json.loads(latest_data)
            content = processed_data['content']
            userID = processed_data['userID']
            fileID = processed_data['fileID']

            print(content)
            gemini_bridge.found_type(content)
            try:
                graphData = {  # working with python dictionary to post to Firestore
                    "graph_response": chartParser(content, found_type),  # Use a field name to store the response
                    "user_id": userID,
                    "file_id": fileID
                }  # dictionary and json data were mismatched

                dartfrog_data = db.collection("graphData").add(graphData)
                print(userID)



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


print(userID)
# Assuming 'timestamp' field for ordering
doc_ref = db.collection("csvUploads").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1)
query_watch = doc_ref.on_snapshot(on_snapshot)

# Wait for the callback to complete
callback_done.wait()
