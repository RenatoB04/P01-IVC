import cv2
import numpy as np
import pygame
import sys

pygame.init()

width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Visao')

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro")
    sys.exit()

def segment_color(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_color = np.array([0, 20, 70], dtype=np.uint8)
    upper_color = np.array([20, 255, 255], dtype=np.uint8)

    mask = cv2.inRange(hsv, lower_color, upper_color)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        center_x = x + w // 2
        center_y = y + h // 2
        return mask, (center_x, center_y)

    return mask, None

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro")
        break

    mask, position = segment_color(frame)

    cv2.imshow('Original', frame)
    cv2.imshow('Mask', mask)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()

    if position:
        center_x, center_y = position

        pygame.draw.circle(screen, (255, 0, 0), (center_x * width // cap.get(3), center_y * height // cap.get(4)), 10)

    pygame.display.flip()

    screen.fill((0, 0, 0))

    pygame.time.delay(30)

cap.release()
cv2.destroyAllWindows()