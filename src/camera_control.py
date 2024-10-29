import cv2
import numpy as np
import socket
import sys
from collections import deque
import time

server_ip = 'localhost'
server_port = 5000

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error")
    sys.exit()

lower_orange = np.array([0, 50, 50], dtype=np.uint8)
upper_orange = np.array([50, 255, 255], dtype=np.uint8)
position_history = deque(maxlen=7)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

last_time = time.time()
frame_rate = 15


def segment_color(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_orange, upper_orange)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) > 500:
            x, y, w, h = cv2.boundingRect(largest_contour)
            center_x = x + w // 2
            return mask, center_x
    return mask, None


while True:
    ret, frame = cap.read()
    if not ret:
        print("Error")
        break

    if (time.time() - last_time) > (1.0 / frame_rate):
        frame = cv2.flip(frame, 1)
        mask, position = segment_color(frame)

        if position:
            position_history.append(position)
            average_x = int(np.mean(position_history))
            message = str(average_x).encode()
            client_socket.sendto(message, (server_ip, server_port))

        cv2.imshow('Original', frame)
        cv2.imshow('Mask', mask)

        last_time = time.time()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
client_socket.close()