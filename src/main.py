import cv2
import numpy as np
import pygame
import sys

pygame.init()

width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Breakout - Controle por Visão Computadorizada')

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

paddle_width = 100
paddle_height = 20
paddle_x = (width // 2) - (paddle_width // 2)
paddle_y = height - 30
paddle_speed = 10

ball_radius = 10
ball_x = width // 2
ball_y = height // 2
ball_speed_x = 4
ball_speed_y = -4

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro ao acessar a câmera")
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
        print("Erro ao capturar frame")
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
        paddle_x = int(center_x * width / cap.get(3)) - (paddle_width // 2)

    if paddle_x < 0:
        paddle_x = 0
    if paddle_x > width - paddle_width:
        paddle_x = width - paddle_width

    ball_x += ball_speed_x
    ball_y += ball_speed_y

    if ball_x - ball_radius <= 0 or ball_x + ball_radius >= width:
        ball_speed_x = -ball_speed_x
    if ball_y - ball_radius <= 0:
        ball_speed_y = -ball_speed_y

    if (paddle_y <= ball_y + ball_radius <= paddle_y + paddle_height) and (paddle_x <= ball_x <= paddle_x + paddle_width):
        ball_speed_y = -ball_speed_y

    if ball_y > height:
        ball_x = width // 2
        ball_y = height // 2
        ball_speed_y = -ball_speed_y

    screen.fill(BLACK)
    pygame.draw.rect(screen, BLUE, (paddle_x, paddle_y, paddle_width, paddle_height))
    pygame.draw.circle(screen, RED, (ball_x, ball_y), ball_radius)

    pygame.display.flip()

    pygame.time.delay(30)

cap.release()
cv2.destroyAllWindows()