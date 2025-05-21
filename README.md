Main.py file has Detection using Webcam. Below code is for detection using IP cam

import os -  File Handling.

import cv2 - Loading, processing, and manipulating images.

import pickle - Saving and loading the facial embeddings stored in the database dictionary (Common Purpose - Saving and Loading Python objects like dictionaries and NumPy arrays.)

import insightface - Provides pre-trained deep learning models for face detection and recognition.

import numpy as np - Helps with numerical operations on arrays and images.

import logging as log - tracking errors, warnings, and messages during execution.

import mysql.connector - connect and interact with a MySQL database

from datetime import datetime - handling date and time

from insightface.app import FaceAnalysis - Insightface package -> App Submodule -> FaceAnalysis Class, encapsulate face analysis operations like detection, recognition, feature extraction, etc,

from scipy.spatial.distance import cosine - Calculating similarity for face recognition.


1.SETUP LOGGING - It is not related to user login or authentication. It stores errors, warnings, and general info.

log.basicConfig(

    filename="log_file.log", # If the specified file exists, logging messages will be appended to it. If the file does not exist, Python will create a new file automatically.

    level=log.DEBUG, # What kind of messages should be logged. DEBUG(Lowest) - All logs & debugging info. INFO - General info logs. WARNING - Unexpected but not critical. ERROR -Functionality failure. CRITICAL(Highest) - Severe error & crash
		     # Eg: level=logging.WARNING means, only WARNING, ERROR, and CRITICAL will be logged (DEBUG & INFO will be ignored)

    format="%(asctime)s - %(levelname)s - %(message)s", # Specifying the structure and content of log messages. Since the values changes for each log entry, the format must define by using prefined log attributes.
		          				# %()Placeholder for log attributes, automatically replaced with actual values. s - typecasting to string(prevents errors when combining different log details) Python assigns values to predefined log attributes, based on their purpose.

    datefmt="%Y-%m-%d %H:%M:%S" # Customizing the format of the date and time in the asctime attribute. Works Only if the asctime attribute is declared in the format parameter
)


2.INITIALIZE ARCFACE MODEL

app = FaceAnalysis(name="buffalo_l") # Creating an object for FaceAnalysis class to make our work easier. By default it searches for the model in ...Insight/model dir. 
				     # If the dir has more than one model,  we need to specify like this. (Defining the Model)

app.prepare(ctx_id=-1) # Mandatory for using get(). Other required deep learning model and the defined model is loading by using the prepare(). It belongs to FaceAnalysis class in the insightface.app module. 
		       # ctx_id=-1 → Use CPU, ctx_id=0 → Use GPU. (#Initials / Loading the Model)


3. LOAD OR CREATE DATABASE

database = {} -  Dictionary to store embeddings

if os.path.exists("face_db.pkl"): #Loading the database if it is already created

    with open("face_db.pkl", "rb") as f: - rb Read Binary

        database = pickle.load(f)

image_list = [
    ("C:/Users/LIBS/Documents/A R C F A C E/DB/abdul.png", "ABDUL"),
    ("C:/Users/LIBS/Documents/A R C F A C E/DB/esakki.png", "ESAKKI"),
    ("C:/Users/LIBS/Documents/A R C F A C E/DB/madhan.png", "MADHAN"),
]

for image_path, person_name in image_list: # Extracting face embeddings from images and save to database
   
    image = cv2.imread(image_path) #The String "img_path" converts into numpy Array

    if image is None:
        print(f"Error loading image: {image_path}")
        continue
	
    else:  
    faces = app.get(image) # get() belongs to FaceAnalysis Class. It detects the faces and extracts embeddings from an image. It also returns bounding box (bbox) coordinates
			   # in this format by default X1,Y1,X2,Y2 (numpy array format) . Returns all these in List format.
  
  if faces: #If any facial embedding found means, it Save the embeddings in the database dictionary with respective keys and values   
        database[person_name] = faces[0].embedding
        print(person_name + " image loaded Successfully..")


with open("face_db.pkl", "wb") as f: # opens the file, if doesn't exists creates a new one. While working with pickle, the file type pkl is used. wb - Write Binary (Saving the updated database to a file)

    pickle.dump(database, f) - SYNTAX dump(The Object want to save, the file)

print("All face embeddings stored successfully!")


4. CONNECTING CODE TO MYSQL DATABASE

def connect_to_database(): 
    
    connection = mysql.connector.connect(  #mysql.connector.connect() is a built-in function that creates a connection between Python and MySQL.

        host="localhost",  # Database host - Running on own computer, so Local Host. If the DB is in another server, need to specify IP address instead of localhost

        user="root",       # Database username - Specify the username used to connect to MySQL. 

        password="",      # Database password (leave empty if none)

        database="demo"   # Database name
    )

    return connection # We can use the connection in multiple places for different tasks.


#5. FETCHING CAMERA DETAILS FROM THE DATABASE

def fetch_all_cameras():  

        connection = connect_to_database()
						# Connecting the Database
        cursor = connection.cursor()

        query = "SELECT camera, mode, ip, username, password FROM cameras" #SELECT - retrieve data from the DB.  FROM cameras(Table name). %s placeholder doesn't hold any value( Act as a Marker)

        cursor.execute(query)  # Sends the query to the database to fetch data. 

        cameras = cursor.fetchall() #fetchall() retrieves all rows returned by the query.

        cursor.close()

        connection.close()

        return cameras


6. LOG ATTENDANCE IN DATABASE
def log_attendance(person_name, camera):
    try:
        connection = connect_to_database() # Connect to the database

        cursor = connection.cursor() #Required to execute SQL queries. Without cursor(), we cannot fetch data or modify the database in the code.

        current_time = datetime.now() # Get current date and time. datetime.now() returns a full datetime object

        date = current_time.strftime("%Y-%m-%d") 
						#strftime() - Formats the date and time in a way that MySQL understands. Date - YYYY-MM-DD, Time - HH:MM:SS
        time = current_time.strftime("%H:%M:%S")  

        # Insert attendance record into the database
        query = """
        INSERT INTO attendance (person_name, camera, date, time) 

        VALUES (%s, %s, %s, %s) # Since the values are dynamic, we are using placeholders. Based On requirements, python will automatically mark values to the %s(Till it doesn't store any values in the %s). 
				# Makes the query safe, flexible, and efficient. It is a SQL Command Structure. 

        """
        cursor.execute(query, (person_name, camera, date, time))  # On calling them in execute(), The Values in %s was storing the values to the corresponding parameters.

        connection.commit()  # Save changes to the database

        print(f"Attendance logged for {person_name} at {time} on {date}")

    except Exception as e:

        print(f"Error logging attendance: {e}")

    finally: # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()


#7. PROCESS CAMERA FEED

def process_camera(camera, ip, username, password):

    print(f"Starting camera: {camera} ({ip})")

    url = f"rtsp://{username}:{password}@{ip}/cam/realmonitor?channel=1&subtype=0"

    video_stream = cv2.VideoCapture(url)

    try:

        while True: #Runs Continuoulsy to capture frames from the cam.

            ret, frame = video_stream.read() #read() return two values ret and frame. frame contains the single image data(read() returns the data in numpy array format). ret contains true, if frame reads the single frame successfully orelse false.
            
	    if not ret: #If ret contains false, the code ends with this block

                print(f"Failed to capture image from camera {camera}")

                break
            
            faces = app.get(frame)  

            for face in faces: #Using Loop to detect multiple faces

                new_embedding = face.embedding

                recognized = False #Initially assigned as False, when the similarity is more than the threshold, it is changed into True

                best_match_name = "Unknown" #Initialising as Unknown

                best_similarity = 0 #Initialising as Zero

                for name, stored_embedding in database.items():

                    similarity = 1 - cosine(new_embedding, stored_embedding)

                    threshold = 0.4

                    if similarity > threshold and similarity > best_similarity:

                        best_similarity = similarity

                        best_match_name = name

                        recognized = True

                bbox = face.bbox.astype(int) # OpenCV requires Integer Co-ordinate. "app.get(frame)" returns numpy array, which may comtain float values. So converting it  

                x1, y1, x2, y2 = bbox #Just Assigning variables to the values

                if recognized:

                    color = (0, 255, 0) # If recognised GREEN

                    log_attendance(best_match_name, camera) 

                else:

                    color = (0, 0, 255) #Else RED

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2) #SYNTAX - cv2.rectangle(image, pt1, pt2, color, thickness=None, lineType=None, shift=None). Used to draw rectangle on the image/video

                cv2.putText(frame, f"{best_match_name} ({round(best_similarity, 2)})", 

                            (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 2)

            cv2.imshow("Window Title", frame) #Display the video frame with detected faces in the window

            if cv2.waitKey(1) & 0xFF == ord('q'): #Break the loop, when 'q' is used

                break

    except Exception as e:

        print(f"Error in camera {camera}: {e}")

    finally:

        print(f"Closing camera: {camera}")

        video_stream.release() #Releases the webcam/video file so other programs can use it

        cv2.destroyAllWindows() #closes all openCV created Windows


# 8. MAIN FUNCTION TO PROCESS MULTIPLE CAMERAS
def main():
    cameras = fetch_all_cameras()
    
    if not cameras:
        print("⚠️ No cameras found in the database.")
        return

    threads = [] - List to store thread objects

    for camera, ip, username, password in cameras: 
        t = threading.Thread(target=process_camera, args=(camera, ip, username, password))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

        
# 9. RUN THE PROGRAM
if __name__ == "__main__":
    main()