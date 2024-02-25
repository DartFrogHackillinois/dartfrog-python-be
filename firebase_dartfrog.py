import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore, threading
import json
import csv

import pathlib
import textwrap
import google.generativeai as genai
from collections import defaultdict

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from IPython.display import display
from IPython.display import Markdown
import csv
# import gemini_bridge
def found_type(content):
    context_str = """
    Given a CSV dataset, your task is to recommend the best Chart.js chart type to visually represent the data. The available Chart.js chart types are Line, Bar, Radar, Doughnut, Pie, Polar Area, Bubble, and Scatter. Consider the dataset's structure, the relationships it may contain, and how effectively each chart type could convey those relationships or data patterns. Your recommendation should be based on the following dataset characteristics:
    Column Count: The total number of columns in the dataset, which includes one column for labels or categories and others for data values.
    Data Nature: Whether the data values represent categories, sequential time points, or relationships between numerical variables.
    Data Homogeneity: If the dataset contains uniformly distributed data across all columns or if there are significant variances.
    Potential for Aggregation: Whether the dataset's data points could be aggregated into meaningful groups or summaries.
    Based on these considerations, provide your recommendation for the most suitable Chart.js chart type as a single word answer from the list provided. This will ensure clarity and precision in communication. Your analysis and decision-making process should prioritize how well the data's story can be told visually through the selected chart type.
    
    Here is the content: {
    """
    context_str += content
    context_str += """
        } That was the end of the content.
        
        Remember, your task is that given a CSV dataset, your task is to recommend the best Chart.js chart type to visually represent the data. The available Chart.js chart types are Line, Bar, Radar, Doughnut, Pie, Polar Area, Bubble, and Scatter. Consider the dataset's structure, the relationships it may contain, and how effectively each chart type could convey those relationships or data patterns. Your recommendation should be based on the following dataset characteristics:
        Column Count: The total number of columns in the dataset, which includes one column for labels or categories and others for data values.
        Data Nature: Whether the data values represent categories, sequential time points, or relationships between numerical variables.
        Data Homogeneity: If the dataset contains uniformly distributed data across all columns or if there are significant variances.
        Potential for Aggregation: Whether the dataset's data points could be aggregated into meaningful groups or summaries.
        Based on these considerations, provide your recommendation for the most suitable Chart.js chart type as a single word answer from the list provided. This will ensure clarity and precision in communication. Your analysis and decision-making process should prioritize how well the data's story can be told visually through the selected chart type.
        
        ONE WORD ANSWER REQUIRED ALL LOWERCASE!!!!!!!
        """
    GOOGLE_API_KEY = 'AIzaSyBaoV9kl3p8wEo0yXB89AosAfdVynkzpDY'
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    return model.generate_content(context_str).text


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
    This function aims to be adaptable to different CSV formats and chart requirements,
    specifically avoiding treating strings as data points unless they are labels.
    """
    # Initialize containers for inferred data
    structured_data = defaultdict(list)
    labels = []

    # Define a helper function to safely convert values
    def safe_float(value):
        try:
            return float(value)
        except ValueError:
            return None

    # Infer structure based on chart type
    if chart_type in ['line', 'bar', 'radar']:
        # Assume first column as labels, remaining as datasets
        labels = [row[0] for row in rows]
        for row in rows:
            # Convert values to floats, skipping non-numeric data
            for i, value in enumerate(row[1:], start=1):
                numeric_value = safe_float(value)
                if numeric_value is not None:  # Only append if the value could be converted
                    structured_data[i].append(numeric_value)
    elif chart_type in ['bubble', 'scatter']:
        # Process each row, ensuring all required values are numeric
        for row in rows:
            # Try converting all values, skip rows with non-numeric data
            try:
                point = [safe_float(value) for value in row]
                if all(v is not None for v in point):  # Check all values were successfully converted
                    if chart_type == 'bubble' and len(point) == 3:
                        structured_data[1].append({'x': point[0], 'y': point[1], 'r': point[2]})
                    elif chart_type == 'scatter' and len(point) >= 2:
                        structured_data[1].append({'x': point[0], 'y': point[1]})
            except ValueError:
                continue  # Skip rows with invalid data
    else:
        # For pie, doughnut, and polar area charts, assume single dataset with labels and values
        for row in rows:
            label = row[0]
            value = safe_float(row[1])
            if value is not None:  # Only use rows where the value is numeric
                labels.append(label)
                structured_data[1].append(value)

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

    print(chart_data)
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
            # found_type(content)
            graph_type = found_type(content)
            graph_r = chartParser(content, graph_type)
            try:
                graphData = {  # working with python dictionary to post to Firestore
                    "graph_response": graph_r,  # Use a field name to store the response
                    "graph_type": graph_type,
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
