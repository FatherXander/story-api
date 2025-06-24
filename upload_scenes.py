import requests
import os

api_url = "https://story-api-jjmo.onrender.com/upload/"
scene_folder = "scenes"  # Change this if your scene files are in a different folder

files = []
for filename in os.listdir(scene_folder):
    if filename.endswith(".txt"):
        filepath = os.path.join(scene_folder, filename)
        files.append(('files', (filename, open(filepath, 'rb'), 'text/plain')))

response = requests.post(api_url, files=files)

print("Status:", response.status_code)
print("Raw response text:", response.text)