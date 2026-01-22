import cv2
import numpy as np
from ultralytics import YOLO
model = YOLO('yolov8n.pt')

CameraURL="http://192.168.182.102:8080/video"
cap=cv2.VideoCapture(CameraURL)
if(not cap.isOpened()):
    print("Error: couldn't open camera")
    exit()

def get_frame():
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read from camera")
        return None
    return frame 

def find_laser_center(frame):
   
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #calculating the green spectrum
    lower_green = np.array([40, 50, 100]) 
    upper_green = np.array([80, 255, 255])
    #remove noises
    mask = cv2.inRange(hsv, lower_green, upper_green)
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return cx, cy

    return -1, -1 

def find_target(frame):
    
    IsFoundLaser=False
    IsFoundObject=False
    results= model.predict(frame,verbose = False,conf = 0.6)
    center_x,center_y=-1,-1
    #look for cups in the objects the model found
    for box in results[0].boxes:
        id_class= box.cls[0]
        name= model.names[id_class]
        if name == 'cup':
            #find its cordinates
            x1,x2,y1,y2= box.xyxy[0].tolist()
            center_x= int((x1+x2)/2)
            center_y= int((y1+y2)/2)
            IsFoundObject=True
            break
    laser_x,laser_y=find_laser_center(frame)
    if(laser_x!=-1 and laser_y!=-1):
        l_b=True
    return laser_x,laser_y,center_x,center_y,IsFoundLaser,IsFoundObject     
