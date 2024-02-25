import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
import textwrap
from IPython.display import Markdown
import firebase_dartfrog

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
        
        ONE WORD ANSWER REQUIRED!!!!!!!
        """
    GOOGLE_API_KEY = 'AIzaSyBaoV9kl3p8wEo0yXB89AosAfdVynkzpDY'
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    return model.generate_content(context_str).text

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

user_id = firebase_dartfrog.userID
file_id = firebase_dartfrog.fileID

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
            "user_id": user_id,
            "file_id": file_id
        }
        db.collection("responseMessages").add(update_data)

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == '__main__':
    # Replace 'example_user_id' with the actual user ID you want to use
    main_query(f'{firebase_dartfrog.userID}')
