import pygame
import socket
import sys
import subprocess
import threading

camera_process = subprocess.Popen(["python", "camera_control.py"])

pygame.init()
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('P01-IVC!')
font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 5000))
server_socket.setblocking(False)

paddle_width, paddle_height = 100, 10
paddle_x, paddle_y = width // 2 - paddle_width // 2, height - 30
ball_radius, ball_x, ball_y = 10, width // 2, height // 2
ball_dx, ball_dy = 4, -4
lives, game_started = 3, False

brick_rows, brick_cols = 3, 10
brick_width, brick_height = width // brick_cols, 20
bricks = [pygame.Rect(col * brick_width, row * brick_height + 50, brick_width, brick_height)
          for row in range(brick_rows) for col in range(brick_cols)]

awaiting_input_text = font.render("Waiting for camera control", True, (255, 255, 255))
start_game_text = font.render("Press SPACE to start", True, (255, 255, 255))

camera_position = paddle_x

def receive_camera_data():
    global camera_position
    while True:
        try:
            data, _ = server_socket.recvfrom(1024)
            camera_position = int(data.decode())
        except BlockingIOError:
            continue

thread = threading.Thread(target=receive_camera_data, daemon=True)
thread.start()

while True:
    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            camera_process.terminate()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_started = True

    paddle_x = camera_position - paddle_width // 2

    if game_started:
        screen.fill((200, 200, 255))
        ball_x += ball_dx
        ball_y += ball_dy

        if ball_x <= ball_radius or ball_x >= width - ball_radius:
            ball_dx *= -1
        if ball_y <= ball_radius:
            ball_dy *= -1
        if ball_y >= height - ball_radius:
            ball_x, ball_y = width // 2, height // 2
            lives -= 1
            if lives <= 0:
                game_started, lives = False, 3

        if paddle_y <= ball_y + ball_radius <= paddle_y + paddle_height:
            if paddle_x <= ball_x <= paddle_x + paddle_width:
                ball_dy *= -1

        bricks = [brick for brick in bricks if not brick.collidepoint(ball_x, ball_y)]

        if len(bricks) == 0:
            game_started = False

        for brick in bricks:
            pygame.draw.rect(screen, (255, 100, 100), brick)
        pygame.draw.rect(screen, (0, 255, 0), (paddle_x, paddle_y, paddle_width, paddle_height))
        pygame.draw.circle(screen, (255, 255, 255), (ball_x, ball_y), ball_radius)

        lives_text = font.render(f"Lives: {lives}", True, (0, 0, 0))
        screen.blit(lives_text, (10, 10))
    else:
        screen.fill((0, 0, 0))
        screen.blit(start_game_text, (width // 2 - start_game_text.get_width() // 2, height // 2))

    pygame.display.flip()