import cv2
import socket
import sys
import os
import threading
import numpy as np

server_ip = 'localhost'
server_port = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro: Câmara")
    sys.exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

running = True

lk_params = dict(winSize=(15, 15),
                 maxLevel=2,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict(maxCorners=100,
                      qualityLevel=0.3,
                      minDistance=7,
                      blockSize=7)

prev_gray = None
prev_points = None


def detect_motion():
    global running, prev_gray, prev_points

    while running:
        ret, frame = cap.read()
        if not ret:
            print("Erro: Frame")
            break

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is None:
            prev_gray = gray
            prev_points = cv2.goodFeaturesToTrack(gray, mask=None, **feature_params)
            continue

        if prev_points is not None:
            next_points, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_points, None, **lk_params)
            good_new = next_points[status == 1] if next_points is not None else []
            good_old = prev_points[status == 1] if prev_points is not None else []

            if len(good_new) > 0:
                avg_x_movement = np.mean(good_new[:, 0] - good_old[:, 0])
                center_x = int(frame.shape[1] // 2 + avg_x_movement * 5)
                center_x = max(0, min(frame.shape[1], center_x))

                message = str(center_x).encode()
                client_socket.sendto(message, (server_ip, server_port))

                for i, (new, old) in enumerate(zip(good_new, good_old)):
                    a, b = new.ravel()
                    c, d = old.ravel()
                    cv2.line(frame, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2)
                    cv2.circle(frame, (int(a), int(b)), 5, (0, 0, 255), -1)

            else:
                prev_points = cv2.goodFeaturesToTrack(gray, mask=None, **feature_params)
        else:
            prev_points = cv2.goodFeaturesToTrack(gray, mask=None, **feature_params)

        cv2.imshow('Camera', frame)

        if cv2.waitKey(1) == 27:
            running = False
            break

        prev_gray = gray.copy()
        prev_points = cv2.goodFeaturesToTrack(gray, mask=None, **feature_params)


detector_thread = threading.Thread(target=detect_motion)
detector_thread.start()

try:
    detector_thread.join()
except KeyboardInterrupt:
    running = False

cap.release()
cv2.destroyAllWindows()
client_socket.close()
