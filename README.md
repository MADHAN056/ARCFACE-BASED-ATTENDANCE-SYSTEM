## Project Overview
This project is a real-time attendance management system that leverages facial recognition for accurate and contactless attendance marking. Built using the ArcFace model from the InsightFace library, it detects and verifies faces from live camera feed and stores attendance logs into a MySQL database.

## Installation Requirements
Before installing Python dependencies, make sure you have the required system tools installed.
Run this command in PowerShell: winget install -e --id Microsoft.VisualStudio.2022.BuildTools \n
Load buffalo_l model in .insightface Folder (Create a New Folder named "Model" inside .insightface folder and move the arcface model into it)

## Imported Modules, Tools and Their Roles
FILE HANDLING AND UTILITIES
os -  File Handling.
pickle - Saving and loading the facial embeddings stored in the database dictionary (Common Purpose - Saving and Loading Python objects like dictionaries and NumPy arrays.)
logging as log - tracking errors, warnings, and messages during execution.

IMAGE PROCESSING
cv2 - Loading, processing, and manipulating images.
numpy - Helps with numerical operations on arrays and images.

FACE RECOGNITION AND ANALYSIS
insightface - Provides pre-trained deep learning models for face detection and recognition.
FaceAnalysis - Insightface package -> App Submodule -> FaceAnalysis Class, encapsulate face analysis operations like detection, recognition, feature extraction, etc,
cosine - Calculating similarity for face recognition.(from scipy.spatial.distance)

DATABASE AND TIME
mysql.connector - connect and interact with a MySQL database
import datetime - handling date and time
