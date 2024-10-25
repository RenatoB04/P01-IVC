import cv2
import numpy as np
import pygame
import sys

pygame.init()

width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Break those Bricks!')

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro ao abrir a câmera")
    sys.exit()

paddle_width = 100
paddle_height = 10
paddle_x = width // 2 - paddle_width // 2
paddle_y = height - 30

ball_radius = 10
ball_x = width // 2
ball_y = height // 2
ball_dx = 4
ball_dy = -4

lives = 3
font = pygame.font.SysFont("Arial", 24)
game_started = False

brick_rows = 3
brick_cols = 10
brick_width = width // brick_cols
brick_height = 20

bricks = []
for row in range(brick_rows):
    for col in range(brick_cols):
        brick_rect = pygame.Rect(col * brick_width, row * brick_height + 50, brick_width, brick_height)
        bricks.append(brick_rect)

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
        return mask, (center_x, y + h // 2)
    return mask, None

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro ao capturar o frame")
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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_started = True

    if position:
        center_x, _ = position
        paddle_x = int(center_x * width // cap.get(3)) - paddle_width // 2

    if game_started:
        ball_x += ball_dx
        ball_y += ball_dy

        if ball_x <= ball_radius or ball_x >= width - ball_radius:
            ball_dx *= -1
        if ball_y <= ball_radius:
            ball_dy *= -1
        if ball_y >= height - ball_radius:
            ball_x = width // 2
            ball_y = height // 2
            lives -= 1
            if lives <= 0:
                game_started = False
                lives = 3

        if paddle_y <= ball_y + ball_radius <= paddle_y + paddle_height:
            if paddle_x <= ball_x <= paddle_x + paddle_width:
                ball_dy *= -1

        bricks = [brick for brick in bricks if not (brick.collidepoint(ball_x, ball_y))]

        if len(bricks) == 0:
            game_started = False

    screen.fill((200, 200, 255))

    if not game_started:
        text = font.render("Press Space to start", True, (0, 0, 0))
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
    else:
        for brick in bricks:
            pygame.draw.rect(screen, (255, 100, 100), brick)

        pygame.draw.rect(screen, (0, 255, 0), (paddle_x, paddle_y, paddle_width, paddle_height))
        pygame.draw.circle(screen, (255, 255, 255), (ball_x, ball_y), ball_radius)

    lives_text = font.render(f"Lives: {lives}", True, (0, 0, 0))
    screen.blit(lives_text, (10, 10))

    pygame.display.flip()
    pygame.time.delay(30)

cap.release()
cv2.destroyAllWindows()