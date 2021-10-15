import os
import json
SECRET_KEY = "hackathon_enjoin"

if os.environ.get('MONGODB_URL') is not None:
    url = os.environ.get('MONGODB_URL') 
else: 
    f = open('key.json', 'r')
    data = json.load(f)
    user = data["user"]
    password = data["password"]
    db = data["db"]
    url = "mongodb+srv://"+user+":"+password+db
