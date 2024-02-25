import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore, threading
import json
import csv
import os
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


def found_type(content, model):
    if len(content)>10000:
        content = content[:10000]+"..."
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
    return model.generate_content(context_str).text


cred = credentials.Certificate(
    "json_creds/dartfrog-ecb02-firebase-adminsdk-tt4ph-fe4cf40a97.json")  # local creds in project directory
firebase_admin.initialize_app(cred)  # firebase_admin initializes creds

db = firestore.client()  # creates a client for the python program

callback_done = threading.Event()

userID = ''
fileID = ''


def safe_float(value):
    try:
        return float(value)
    except ValueError:
        return None


def infer_data_structure(rows, chart_type):
    structured_data = defaultdict(list)
    labels = []

    for row in rows:
        # For line, bar, radar: assume first column as labels, remaining as datasets.
        # For bubble, scatter: need at least 2 elements (x and y; r is optional for scatter).
        # For pie, doughnut, polar area: need at least 2 elements (label and value).

        if chart_type in ['line', 'bar', 'radar']:
            if len(row) > 1:  # Ensure there's at least one data point beyond the label
                labels.append(row[0])
                for i, value in enumerate(row[1:], start=1):
                    numeric_value = safe_float(value)
                    if numeric_value is not None:  # Only append if the value could be converted
                        structured_data[i].append(numeric_value)
            # Else: Consider logging this case as a data row without enough columns for these chart types

        elif chart_type in ['bubble', 'scatter']:
            # Try to handle rows with missing values gracefully for scatter; bubble requires 3 values
            point = [safe_float(value) for value in row]
            if all(v is not None for v in point[:2]):  # Ensure at least x and y are valid
                if chart_type == 'bubble' and len(point) >= 3:
                    structured_data[1].append({'x': point[0], 'y': point[1], 'r': point[2]})
                elif chart_type == 'scatter':
                    # For scatter, r is not required
                    structured_data[1].append({'x': point[0], 'y': point[1]})
            # Else: Consider logging this case as a data row without enough valid columns/values

        else:
            # Pie, doughnut, and polar area charts: handle with single dataset with labels and values
            if len(row) > 1:
                label = row[0]
                value = safe_float(row[1])
                if value is not None:
                    labels.append(label)
                    structured_data[1].append(value)
            # Else: Consider logging this case as a data row without enough columns for these chart types

    return labels, dict(structured_data)
def chartParser(csv_content, chart_type):
    """
    Parses any given CSV to a JSON structure suitable for Chart.js, considering the chart type.
    This function is designed to adapt to various CSV structures.
    """
    lines = csv_content.splitlines()
    reader = csv.reader(lines)
    next(reader)  # Skip headers

    rows = list(reader)
    labels, datasets = infer_data_structure(rows, chart_type)

    chart_data = {
        'type': chart_type,
        'data': {
            'labels': labels,
            'datasets': [{
                'label': f'Dataset {i}',
                'data': data,
            } for i, (dataset_label, data) in enumerate(datasets.items())],
        }
    }

    return chart_data if datasets else None  # Only return if datasets are not empty

# Modified infer_data_structure function as provided remains unchanged

def find_best_chart_type(csv_content, ideal_chart_type):
    # List of chart types to iterate over
    chart_types = [ideal_chart_type,'line', 'bar', 'radar', 'doughnut', 'pie', 'polarArea', 'bubble', 'scatter']

    for chart_type in chart_types:
        chart_data = chartParser(csv_content, chart_type)
        if chart_data:  # Check if chart_data is not None (i.e., datasets are not empty)
            print(f"Found suitable chart type: {chart_type}")
            return chart_type, chart_data  # Return the type and data of the first suitable chart

    return None, None  # Return None if no suitable chart type is found

def on_snapshot(col_snapshot, changes, read_time):
    GOOGLE_API_KEY = 'AIzaSyBaoV9kl3p8wEo0yXB89AosAfdVynkzpDY'
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    global userID
    global fileID
    for change in changes:
        if change.type.name == 'ADDED':
            latest_document = change.document.to_dict()
            latest_data = json.dumps(latest_document, indent=4, sort_keys=True, default=str)
            processed_data = json.loads(latest_data)
            content = processed_data['content']
            userID = processed_data['userID']
            fileID = processed_data['file_id']

            print(content)
            # found_type(content)

            print(content)
            # found_type(content)

            print(content)
            # found_type(content)

            with open('txt_analysis/dartfrog_query.txt', 'r') as file:
                query_text = file.read()  # opens query prompt for reading

            with open('txt_analysis/data.txt', 'w') as text_file:
                text_file.write(content)  # opens and writes firebase provided data

            with open('txt_analysis/data.txt', 'r') as data_file:
                data = data_file.read()  # opens firebase provided data for reading by gemini in combined_content

            with open('txt_analysis/combined_content.txt', 'w') as output_file:
                output_file.write(query_text)  # connects both query and supplied data
                output_file.write('\n')  # Add a newline between the files
                output_file.write(data)

                # Read combined content
                file_path = os.path.join(os.path.dirname(__file__), 'txt_analysis', 'combined_content.txt')
                with open(file_path, 'r') as input_file:
                    user_content = input_file.read()

                # Gemini Content Generation
                if len(user_content) > 20000:
                    user_content = user_content[:20000] + "..."
                response = model.generate_content(user_content)
                generated_content = response.text
                analysis = {  # working with python dictionary to post to Firestore
                    "response": generated_content,
                    "user_id": userID,
                    "file_id": fileID
                }  # dictionary and json data were mismatched

                db.collection("responseMessages").add(analysis)

            print("Success")

            # gemini_analysis(userID, changes, content, fileID) # gemini analysis function


            graph_type = found_type(content, model)
            new_data = find_best_chart_type(content,graph_type)
            (graph_type, graph_r) = new_data

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
doc_ref = db.collection("csvUploads")

query_watch = doc_ref.on_snapshot(on_snapshot)

# Wait for the callback to complete
callback_done.wait()
