# app.py
from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
import firebase
import gemini_bridge
import os

flask_app = Flask(__name__)

# Check if the app is already initialized
if not firebase_admin._apps:
    # App not yet initialized, proceed with initialization
    cred = credentials.Certificate('json_creds/dartfrog-ecb02-firebase-adminsdk-tt4ph-fe4cf40a97.json')
    firebase_app = firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    # App already initialized, retrieve the existing app
    firebase_app = firebase_admin.get_app()
    db = firestore.client()

# Gemini Bridge Initialization
GOOGLE_API_KEY = 'AIzaSyBaoV9kl3p8wEo0yXB89AosAfdVynkzpDY'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/generate', methods=['POST'])
def generate():
    # Parse the JSON request body and extract userID
    if not request.json or 'userID' not in request.json:
        return jsonify({'error': 'Request must be JSON and include a userID field'}), 400

    user_id = request.json['userID']

    # Call functions in firebase.py and geminibridge.py with the extracted userID
    firebase.main_graph(user_id) # Replace some_function with the actual function name
    gemini_bridge.main_query(user_id) # Replace some_function with the actual function name

    return jsonify({'message': 'Function calls were successful', 'firebaseResponse': 'None', 'geminibridgeResponse': 'None'}), 200

@flask_app.route('/generate_content', methods=['POST'])
def generate_content():
    try:
        # Read combined content
        file_path = os.path.join(os.path.dirname(__file__), 'txt_ref', 'combined_content.txt')
        with open(file_path, 'r') as input_file:
            content = input_file.read()

        # Gemini Content Generation
        response = model.generate_content(content)
        generated_content = response.text

        # Update Firebase
        update_data = {"generated_response": generated_content}
        db.collection("responseMessages").document("7H5hzZUGr7jRMV69yjyp").update(update_data)

        return render_template('index.html', generated_content=generated_content)

    except Exception as e:
        error_message = f"An error occurred: {e}"
        return render_template('index.html', error_message=error_message)

if __name__ == '__main__':
    flask_app.run(debug=True)
