#Importing necessary Libraries
import os
import cv2
import pickle
import numpy as np
import insightface
import logging as log
import mysql.connector
from datetime import datetime
from insightface.app import FaceAnalysis
from scipy.spatial.distance import cosine


#SETUP LOGGING
log.basicConfig(
    filename="log_file.log",  
    level=log.DEBUG,          
    format="%(asctime)s - %(levelname)s - %(message)s",  
    datefmt="%Y-%m-%d %H:%M:%S" )


#INITIALIZE ARCFACE MODEL
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=-1)


#LOAD OR CREATE DATABASE
database = {}
if os.path.exists("face_db.pkl"):
    with open("face_db.pkl", "rb") as f:
        database = pickle.load(f)


#ADD IMAGES TO DATABASE
image_list = [
    ("C:/Users/mrmad/OneDrive/Documents/L I B S/A R C F A C E/DB/abdul.png", "ABDUL"),
    ("C:/Users/mrmad/OneDrive/Documents/L I B S/A R C F A C E/DB/esakki.png", "ESAKKI"),
    ("C:/Users/mrmad/OneDrive/Documents/L I B S/A R C F A C E/DB/madhan.png", "MADHAN"),
    ("C:/Users/mrmad/OneDrive/Documents/L I B S/A R C F A C E/DB/senthil.png", "SENTHIL"),
    ("C:/Users/mrmad/OneDrive/Documents/L I B S/A R C F A C E/DB/tanasaker.png", "DHANSEKAR"),
    ("C:/Users/mrmad/OneDrive/Documents/L I B S/A R C F A C E/DB/vishnu.png", "VISHNU"),
    ("C:/Users/mrmad/OneDrive/Documents/L I B S/A R C F A C E/DB/genesis.png", "GENESIS SIR"),
    ("C:/Users/mrmad/OneDrive/Documents/L I B S/A R C F A C E/DB/sathish.png", "SATHISH")
]
for img_path, person_name in image_list: 
    img = cv2.imread(img_path)
    if img is None:
        print("Error Loading Image " + img_path)
        continue
    else:
        faces = app.get(img) 

    if faces: 
        face = faces[0]
        x1, y1, x2, y2 = map(int, face.bbox)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, person_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.imshow(person_name, img)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()
        
with open("face_db.pkl", "wb") as f:
    pickle.dump(database, f)
print("All face embeddings stored successfully!")


#CONNECT TO MYSQL DATABASE
def connect_to_database():
    connection = mysql.connector.connect(
        host="localhost", 
        user="root",       
        password="12345",      
        database="register",
        auth_plugin="mysql_native_password"
    )
    return connection


#LOG ATTENDANCE IN DATABASE
def log_attendance(person_name):
    connection = None
        
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        current_time = datetime.now()
        date = current_time.strftime("%Y-%m-%d")  
        time = current_time.strftime("%H:%M:%S")  

        query = """
        INSERT INTO attendance (PERSON_NAME, ATTENDANCE_DATE, ATTENDANCE_TIME)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (person_name, date, time)) 
        connection.commit()  
        print(f"Attendance logged for {person_name} at {time} on {date}")

    except Exception as e:
        print(f"Error logging attendance: {e}")
        
    finally:
        if connection and connection.is_connected():  
            cursor.close()
            connection.close()

            
#Main Function
def main():
    cap = cv2.VideoCapture(0)    

    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    print("Webcam is running. Press 'q' to exit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break

            faces = app.get(frame)
            for face in faces:  
                new_embedding = face.embedding
                recognized = False 
                best_match_name = "Unknown" 
                best_similarity = 0 

                for name, stored_embedding in database.items():
                    similarity = 1 - cosine(new_embedding, stored_embedding)
                    threshold = 0.4
                    if similarity > threshold and similarity > best_similarity:
                        best_similarity = similarity
                        best_match_name = name
                        recognized = True

                bbox = face.bbox.astype(int)   
                x1, y1, x2, y2 = bbox

                if recognized:
                    color = (0, 255, 0)
                    log_attendance(best_match_name)
                else:
                    color = (0, 0, 255) 

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                cv2.putText(frame, best_match_name + " ( " + str(round(best_similarity, 2)) + " )", 
                            (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 2)

            cv2.imshow("Window Title", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break  

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Webcam Closed")

#Running the Program

if __name__ == "__main__":
    main()
