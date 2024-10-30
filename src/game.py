import pygame
import socket
import sys
import subprocess
import threading

camera_process = subprocess.Popen(["python", "camera_control.py"])

pygame.init()
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('P01-IVC')
font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 5000))
server_socket.setblocking(False)

paddle_width, paddle_height = 100, 10
paddle_x, paddle_y = width // 2 - paddle_width // 2, height - 30
ball_radius, ball_x, ball_y = 10, width // 2, height // 2
ball_dx, ball_dy = 4, -4
lives, game_started, level = 3, False, 1

brick_width, brick_height = width // 10, 20
bricks = []

awaiting_input_text = font.render("Waiting for camera control", True, (255, 255, 255))
start_game_text = font.render("Press SPACE to start", True, (255, 255, 255))

camera_position = paddle_x


def setup_level(level):
    global ball_dx, ball_dy, bricks
    bricks = []
    ball_dx = 4 + (level - 1) * 1.5
    ball_dy = -4 - (level - 1) * 1.5
    rows = level + 2
    for row in range(rows):
        for col in range(10):
            brick_rect = pygame.Rect(col * brick_width, row * brick_height + 50, brick_width, brick_height)
            bricks.append(brick_rect)


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

setup_level(level)

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
                game_started, lives, level = False, 3, 1
                setup_level(level)

        if paddle_y <= ball_y + ball_radius <= paddle_y + paddle_height:
            if paddle_x <= ball_x <= paddle_x + paddle_width:
                ball_dy *= -1

        for brick in bricks[:]:
            if brick.collidepoint(ball_x, ball_y):
                bricks.remove(brick)

                if abs(ball_x - (brick.x + brick.width // 2)) > abs(ball_y - (brick.y + brick.height // 2)):
                    ball_dx *= -1
                else:
                    ball_dy *= -1

        if len(bricks) == 0:
            level += 1
            setup_level(level)

        for brick in bricks:
            pygame.draw.rect(screen, (255, 100, 100), brick)
        pygame.draw.rect(screen, (0, 255, 0), (paddle_x, paddle_y, paddle_width, paddle_height))
        pygame.draw.circle(screen, (255, 255, 255), (ball_x, ball_y), ball_radius)

        lives_text = font.render(f"Lives: {lives} | Level: {level}", True, (0, 0, 0))
        screen.blit(lives_text, (10, 10))
    else:
        screen.fill((0, 0, 0))
        screen.blit(start_game_text, (width // 2 - start_game_text.get_width() // 2, height // 2))

    pygame.display.flip()