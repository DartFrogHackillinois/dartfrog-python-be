# app.py
from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
import firebase
import gemini_bridge

app = Flask(__name__)

# Firebase Initialization
cred = credentials.Certificate('json_creds/dartfrog-ecb02-firebase-adminsdk-tt4ph-fe4cf40a97.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Gemini Bridge Initialization
GOOGLE_API_KEY = 'AIzaSyBaoV9kl3p8wEo0yXB89AosAfdVynkzpDY'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    # Parse the JSON request body and extract userID
    if not request.json or 'userID' not in request.json:
        return jsonify({'error': 'Request must be JSON and include a userID field'}), 400

    user_id = request.json['userID']

    # Call functions in firebase.py and geminibridge.py with the extracted userID
    firebase.main_graph(user_id) # Replace some_function with the actual function name
    geminibridge.main_query(user_id) # Replace some_function with the actual function name

    return jsonify({'message': 'Function calls were successful', 'firebaseResponse': 'None', 'geminibridgeResponse': 'None'}), 200

def generate_content():
    try:
        # Read combined content
        with open('txt_ref/combined_content.txt', 'r') as input_file:
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
    app.run(debug=True)
