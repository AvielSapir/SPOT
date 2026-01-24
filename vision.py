import cv2
import numpy as np
from ultralytics import YOLO
model = YOLO('yolov8n.pt')

CameraURL="http://192.168.1.42:8080/video"
cap=cv2.VideoCapture(CameraURL)
if(not cap.isOpened()):
    print("Error: couldn't open camera")
    exit()

def get_frame():
    for _ in range(5):
        cap.grab()
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read from camera")
        return None
    return frame 

def find_laser_center(frame):
   
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 20, 150])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    #mask = cv2.erode(mask, None, iterations=1)
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
    IsFoundLaser = False
    IsFoundObject = False
    center_x, center_y = -1, -1

    results = model.predict(frame,imgsz=320, verbose=False, conf=0.1)

    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        name = model.names[cls_id]
        conf = float(box.conf[0])

        if name in ['cup']:
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            IsFoundObject = True
            print("!")
            break

    laser_x, laser_y = find_laser_center(frame)

    if laser_x != -1 and laser_y != -1:
        IsFoundLaser = True
        print("->")

    return laser_x, laser_y, center_x, center_y, IsFoundLaser, IsFoundObject