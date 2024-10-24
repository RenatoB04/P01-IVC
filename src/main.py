import cv2
import numpy as np
import pygame
import sys

pygame.init()

width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Breakout')

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro ao abrir a câmera")
    sys.exit()

paddle_width = 80
paddle_height = 10
paddle_x = width // 2 - paddle_width // 2
paddle_y = height - 30

ball_radius = 10
ball_x = width // 2
ball_y = height // 2
ball_dx = 4
ball_dy = -4

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
        center_x, _ = position
        paddle_x = int(center_x * width // cap.get(3)) - paddle_width // 2

    ball_x += ball_dx
    ball_y += ball_dy

    if ball_x <= ball_radius or ball_x >= width - ball_radius:
        ball_dx *= -1
    if ball_y <= ball_radius:
        ball_dy *= -1
    if ball_y >= height - ball_radius:
        ball_x = width // 2
        ball_y = height // 2
        ball_dy *= -1

    if paddle_y <= ball_y + ball_radius <= paddle_y + paddle_height:
        if paddle_x <= ball_x <= paddle_x + paddle_width:
            ball_dy *= -1

    screen.fill((0, 0, 0))

    pygame.draw.rect(screen, (0, 255, 0), (paddle_x, paddle_y, paddle_width, paddle_height))

    pygame.draw.circle(screen, (255, 0, 0), (ball_x, ball_y), ball_radius)

    pygame.display.flip()

    pygame.time.delay(30)

cap.release()
cv2.destroyAllWindows()