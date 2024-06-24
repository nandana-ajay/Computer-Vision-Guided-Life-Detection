from flask import Flask, render_template, request,redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from PIL import Image 
import json
from ultralytics import YOLO
import requests
import os
from flask_sqlalchemy import SQLAlchemy 
from travelling import calculate_shortest_path

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///alerts.db' # SQLite database in the current directory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)

#Database to store the location, severity and link of the image
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(30))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    humans_detected = db.Column(db.Integer)
    image_link = db.Column(db.String(255))  

    def __repr__(self):
        return f"Alert(id={self.id}, location={self.location},latitude={self.latitude}, longitude={self.longitude}, humans_detected={self.humans_detected}, image_link={self.image_link})"

allowed_extensions = ["jpg", "png", "jpeg"]

# Initialize YOLO model
yolo = YOLO("best2.pt")

#predefined functions 
def allowed_file(filename):    
    return "." in filename and filename.split(".")[-1].lower() in allowed_extensions


@app.route("/home", methods=["GET", "POST"])
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
            output=getting_bounding_box(detections)
            # print(output)
            folder_path = 'runs/detect'
            subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
            latest_subfolder = max(subfolders, key=lambda x: os.path.getctime (os.path.join(folder_path, x)))
            directory = folder_path+"/"+latest_subfolder
            files = os.listdir(directory)
            latest_file = files[0]
            filename = directory+ "/" +latest_file
            print(filename)
            if(len(output)>0):
                # print("Should be inserted into table")
                location= request.form['loc']
                latitude = request.form['lat']
                longitude = request.form['long']
                insert_alert(location,latitude, longitude, len(output), latest_file)
                return render_template("index1.html")
                # coordinates_array=get_coordinates_array()
                # calculate_shortest_path(coordinates_array)
            else:
                print("No humans detected so no alert is generated.")
            return send_from_directory(directory,latest_file)
    else:
        return render_template("index.html")
    
@app.route('/alerts')
def display_alerts():
    alerts = Alert.query.all()
    coordinates_array=get_coordinates_array()
    print(coordinates_array)
    returnedArray=calculate_shortest_path(coordinates_array)
    ordered_locations=convert_id_array_to_locations(returnedArray)
    return render_template('alerts.html', alerts=alerts,ordered_locations=ordered_locations)

@app.route('/clearAllAlerts')
def clear_all_alerts():
    try:
        db.session.query(Alert).delete()
        db.session.commit()
        return jsonify({"Message":"Successful"})
    except Exception as e:
        db.session.rollback()
        print("An error occurred:", str(e))
        return jsonify({"Message":"Not successful"})
    finally:
        db.session.close()

def getting_bounding_box(detections):
    detection=detections[0]
    output = []
    for box in detection.boxes:
        x1, y1, x2, y2 = [round(x) for x in box.xyxy[0].tolist()]
        class_id = box.cls[0].item()
        prob = round(box.conf[0].item(), 2)
        output.append([x1, y1, x2, y2, detection.names[class_id], prob])
    return output

def insert_alert(location, latitude, longitude,  humans_detected, image_link,):
    new_alert = Alert(location=location,latitude=latitude, longitude=longitude,  humans_detected=humans_detected, image_link=image_link)
    db.session.add(new_alert)
    db.session.commit()


def get_coordinates_array():
    coordinates_array=[[10.553772, 76.223585]]  #Coordinates of hub(GEC Thrissur)
    try:
        alerts = Alert.query.all()
        for alert in alerts:
            coordinates_array.append((alert.latitude, alert.longitude))
        return coordinates_array
    except Exception as e:
        print("An error occurred:", str(e))
        return None
    
def convert_id_array_to_locations(returnedArray):
    ordered_locations = ["Hub"]
    for alert_id in returnedArray:
        alert = Alert.query.get(alert_id)
        if alert:
            ordered_locations.append(alert.location)
    ordered_locations.append("Hub")
    return '--> '.join(ordered_locations)
    
# @app.route('/test')
# def travelling_test():
#     coordinates_array=get_coordinates_array()
#     print(coordinates_array)
#     calculate_shortest_path(coordinates_array)
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        clear_all_alerts()
        app.run()




