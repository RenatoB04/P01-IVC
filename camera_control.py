import cv2
import numpy as np
import socket
import sys
from ultralytics import YOLO

server_ip = 'localhost'
server_port = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmara")
    sys.exit()

model = YOLO("yolov8n.pt")  # Carrega o modelo YOLOv8 nano
model.fuse()  # Otimiza o modelo para inferência em CPU

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

def detect_objects(frame):
    resized_frame = cv2.resize(frame, (320, 240))
    results = model.predict(resized_frame, imgsz=320, conf=0.5, device="cpu")  # Usa CPU explicitamente
    detections = results[0].boxes
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    center_x = None

    for detection in detections:
        x1, y1, x2, y2 = detection.xyxy[0]
        cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
        radius = int(min(x2 - x1, y2 - y1) / 2)
        cx, cy = int(cx * frame.shape[1] / 320), int(cy * frame.shape[0] / 240)
        cv2.circle(mask, (cx, cy), radius, 255, -1)
        center_x = cx
        break

    return mask, center_x

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro: Não foi possível capturar o quadro")
        break

    frame = cv2.flip(frame, 1)
    mask, center_x = detect_objects(frame)

    if center_x is not None:
        message = str(center_x).encode()
        client_socket.sendto(message, (server_ip, server_port))

    masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow('Camera', frame)
    cv2.imshow('Mask', masked_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
client_socket.close()