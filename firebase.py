import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("dartfrog-ecb02-firebase-adminsdk-tt4ph-fe4cf40a97.json") # local creds in project directory
firebase_admin.initialize_app(cred) # firebase_admin initializes creds

db = firestore.client() # creates a client for the python program

doc_ref = db.collection("csvUploads").document("3B3GXtkY61jCQ5381f8Y")
doc = doc_ref.get() # runs "get" command from gemini_bridge
data = doc.to_dict() # converts the fetched document into a legible format

# Print the data
print(data)
