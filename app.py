from flask import Flask, render_template, request,redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image 
import os
import json
from ultralytics import YOLO
import requests

app = Flask(__name__)
allowed_extensions = ["jpg", "png", "jpeg", "jfif", "webp"]

# Initialize YOLO model
yolo = YOLO("best2.pt")

#predefined functions 
def allowed_file(filename):    
    return "." in filename and filename.split(".")[-1].lower() in allowed_extensions

def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]

def get_location():
    ip_address = get_ip()
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    print(response)
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }
    return location_data

@app.route("/location")
def home():
    data = get_location()
    return data

@app.route("/", methods=["GET", "POST"])
def predict_image():
    if request.method == "POST":
        if "file" in request.files:
            f = request.files["file"]
            if f.filename == "":
                return "No file selected"
            if not allowed_file(f.filename):
                return "Invalid file format"
            basepath = os.path.dirname(__file__)
            filepath = os.path.join(basepath, "uploads", secure_filename(f.filename))
            f.save(filepath)
            image = Image.open(filepath)
            detections=yolo.predict(image, save=True)
            detection=detections[0]
            output = []
            for box in detection.boxes:
                x1, y1, x2, y2 = [round(x) for x in box.xyxy[0].tolist()]
                class_id = box.cls[0].item()
                prob = round(box.conf[0].item(), 2)
                output.append([x1, y1, x2, y2, detection.names[class_id], prob])
            print(output)
            print(detections)
            folder_path = 'runs/detect'
            subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
            latest_subfolder = max(subfolders, key=lambda x: os.path.getctime (os.path.join(folder_path, x)))
            directory = folder_path+"/"+latest_subfolder
            #print("printing directory: ", directory)
            files = os.listdir(directory)
            latest_file = files[0]
            #print(latest_file)
            filename = directory+ "/" +latest_file
            print(filename)
            # return send_from_directory('runs/detect/predict3', latest_file)
            return send_from_directory(directory,latest_file)
    else:
        return render_template("index.html")
    
if __name__ == "__main__":
    app.run()




