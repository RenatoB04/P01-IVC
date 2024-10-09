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

    return mask
while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro")
        break

    mask = segment_color(frame)

    cv2.imshow('Original', frame)
    cv2.imshow('Mask', mask)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))
    pygame.display.flip()

    pygame.time.delay(30)

cap.release()
cv2.destroyAllWindows()
