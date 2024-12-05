import cv2
import socket
import sys
import os
import threading

server_ip = 'localhost'
server_port = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro: Câmara")
    sys.exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

cascade_path = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")
if not os.path.exists(cascade_path):
    print("Erro: Ficheiro .xml não encontrado.")
    sys.exit()

face_cascade = cv2.CascadeClassifier(cascade_path)

tracker = cv2.legacy.TrackerCSRT_create()

running = True
tracking = False
center_x = None

def detect_motion():
    global running, tracking, center_x, tracker

    while running:
        ret, frame = cap.read()
        if not ret:
            print("Erro: Frame")
            break

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if not tracking:
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                center_x = x + w // 2
                bbox = (x, y, w, h)
                tracker.init(frame, bbox)
                tracking = True
                print("Rosto detectado e tracking iniciado.")
        else:
            success, bbox = tracker.update(frame)
            if success:
                (x, y, w, h) = [int(v) for v in bbox]
                center_x = int(x + w // 2)

                cv2.circle(frame, (center_x, y + h // 2), 5, (0, 0, 255), -1)
                message = str(center_x).encode()
                client_socket.sendto(message, (server_ip, server_port))
            else:
                tracking = False
                print("Falha no tracking.")

        cv2.imshow('Camera', frame)

        if cv2.waitKey(1) == 27:
            running = False
            break

detector_thread = threading.Thread(target=detect_motion)
detector_thread.start()

try:
    detector_thread.join()
except KeyboardInterrupt:
    running = False

cap.release()
cv2.destroyAllWindows()
client_socket.close()