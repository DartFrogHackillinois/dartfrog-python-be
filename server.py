# app.py
from flask import Flask, render_template, request
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai

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

@app.route('/generate', methods=['GET','POST'])
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
