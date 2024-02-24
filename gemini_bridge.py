import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
import textwrap
from IPython.display import Markdown

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def main_query(user_id):
    # Check if the app is already initialized
    if not firebase_admin._apps:
        # App not yet initialized, proceed with initialization
        cred = credentials.Certificate('json_creds/dartfrog-ecb02-firebase-adminsdk-tt4ph-fe4cf40a97.json')
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    else:
        # App already initialized, retrieve the existing app
        db = firestore.client()

    GOOGLE_API_KEY = 'AIzaSyBaoV9kl3p8wEo0yXB89AosAfdVynkzpDY'
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    with open('txt_ref/combined_content.txt', 'r') as input_file:
        content = input_file.read()

    query = content

    try:
        response = model.generate_content(query)
        generated_response = response.text

        # Update Firestore with the generated response
        update_data = {
            "generated_response": generated_response,
            "user_id": user_id
        }
        db.collection("responseMessages").add(update_data)

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == '__main__':
    # Replace 'example_user_id' with the actual user ID you want to use
    main_query('example_user_id')
