import pygame
import socket
import sys
import subprocess
import threading

# Inicia o processo do controlo da câmara (camera_control.py)
camera_process = subprocess.Popen(["python", "camera_control.py"])

# Inicializa o Pygame e configura a janela do jogo
pygame.init()
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('P01-IVC')  # Define o título da janela
font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

# Configuração do socket UDP para receber dados de posição da câmara
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 5000))
server_socket.setblocking(False)  # Define o socket como não bloqueante

# Dimensões e posição inicial da plataforma
paddle_width, paddle_height = 100, 10
paddle_x, paddle_y = width // 2 - paddle_width // 2, height - 30

# Propriedades da bola
ball_radius, ball_x, ball_y = 10, width // 2, height // 2
ball_dx, ball_dy = 4, -4

# Variáveis de estado do jogo
lives, game_started, level = 3, False, 1

# Dimensões dos blocos
brick_width, brick_height = width // 10, 20
bricks = []  # Lista para armazenar as coordenadas dos blocos

# Textos informativos
awaiting_input_text = font.render("Waiting for camera", True, (255, 255, 255))
start_game_text = font.render("Press SPACE", True, (255, 255, 255))

# Posição da plataforma com base no controlo da câmara
camera_position = paddle_x

def setup_level(level):
    """
    Configura os blocos para o nível atual, ajustando a velocidade da bola.
    """
    global ball_dx, ball_dy, bricks
    bricks = []  # Limpa a lista de blocos
    ball_dx = 4 + (level - 1) * 1.5  # Aumenta a velocidade horizontal
    ball_dy = -4 - (level - 1) * 1.5  # Aumenta a velocidade vertical
    rows = level + 2  # Número de linhas de blocos aumenta com o nível
    for row in range(rows):
        for col in range(10):
            # Calcula as coordenadas de cada bloco e adiciona à lista
            x = col * brick_width
            y = row * brick_height + 50
            bricks.append((x, y))

def receive_camera_data():
    """
    Recebe dados de posição da câmara e atualiza a posição da plataforma.
    """
    global camera_position
    while True:
        try:
            # Recebe dados do socket e atualiza a posição da plataforma
            data, _ = server_socket.recvfrom(1024)
            camera_position = int(data.decode())
        except BlockingIOError:
            continue  # Continua se não houver dados disponíveis

# Inicia uma thread para receber dados da câmara sem bloquear o jogo
thread = threading.Thread(target=receive_camera_data, daemon=True)
thread.start()

# Configura o primeiro nível
setup_level(level)

# Loop principal do jogo
while True:
    clock.tick(30)  # Define a taxa de atualização para 30 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Fecha o jogo se a janela for fechada
            camera_process.terminate()  # Termina o processo da câmara
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Inicia o jogo com a tecla SPACE
                game_started = True

    # Atualiza a posição da plataforma com base nos dados da câmara
    paddle_x = camera_position - paddle_width // 2

    if game_started:
        # Limpa o ecrã e atualiza a posição da bola
        screen.fill((200, 200, 255))
        ball_x += ball_dx
        ball_y += ball_dy

        # Verifica colisões com as bordas da janela
        if ball_x <= ball_radius or ball_x >= width - ball_radius:
            ball_dx *= -1  # Inverte a direção horizontal da bola
        if ball_y <= ball_radius:
            ball_dy *= -1  # Inverte a direção vertical da bola
        if ball_y >= height - ball_radius:
            # Reinicia a bola e diminui uma vida
            ball_x, ball_y = width // 2, height // 2
            lives -= 1
            if lives <= 0:  # Reinicia o jogo se as vidas chegarem a zero
                game_started, lives, level = False, 3, 1
                setup_level(level)

        # Verifica colisão da bola com a plataforma
        if paddle_y <= ball_y + ball_radius <= paddle_y + paddle_height:
            if paddle_x <= ball_x <= paddle_x + paddle_width:
                ball_dy *= -1  # Inverte a direção vertical da bola

        # Verifica colisões da bola com os blocos
        for brick in bricks[:]:
            brick_x, brick_y = brick
            if (brick_x <= ball_x <= brick_x + brick_width and
                    brick_y <= ball_y <= brick_y + brick_height):
                bricks.remove(brick)  # Remove o bloco ao colidir
                # Inverte a direção da bola com base na colisão
                if abs(ball_x - (brick_x + brick_width // 2)) > abs(ball_y - (brick_y + brick_height // 2)):
                    ball_dx *= -1
                else:
                    ball_dy *= -1

        # Avança para o próximo nível se todos os blocos forem destruídos
        if len(bricks) == 0:
            level += 1
            setup_level(level)

        # Desenha os blocos, a plataforma e a bola
        for brick_x, brick_y in bricks:
            pygame.draw.rect(screen, (0, 0, 0), (brick_x - 1, brick_y - 1, brick_width + 2, brick_height + 2))  # Contorno
            pygame.draw.rect(screen, (255, 100, 100), (brick_x, brick_y, brick_width, brick_height))  # Bloco

        pygame.draw.rect(screen, (0, 255, 0), (paddle_x, paddle_y, paddle_width, paddle_height))
        pygame.draw.circle(screen, (255, 255, 255), (ball_x, ball_y), ball_radius)

        # Exibe o número de vidas e o nível atual
        lives_text = font.render(f"Lives: {lives} | Level: {level}", True, (0, 0, 0))
        screen.blit(lives_text, (10, 10))
    else:
        # Exibe o texto de início quando o jogo não está a decorrer
        screen.fill((0, 0, 0))
        screen.blit(start_game_text, (width // 2 - start_game_text.get_width() // 2, height // 2))

    # Atualiza o ecrã
    pygame.display.flip()