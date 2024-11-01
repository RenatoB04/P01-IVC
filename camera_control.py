import cv2
import numpy as np
import socket
import sys
from collections import deque

# Configuração do servidor para enviar dados ao jogo
server_ip = 'localhost'  # Endereço IP do servidor (jogo)
server_port = 5000  # Porta do servidor

# Inicia a captura de vídeo com a câmara
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error")
    sys.exit()  # Sai se a câmara não estiver disponível

# Define a faixa de cor em HSV para detecção de cor laranja
lower_orange = np.array([0, 50, 50], dtype=np.uint8)
upper_orange = np.array([50, 255, 255], dtype=np.uint8)

# Histórico de posições para suavizar o movimento
position_history = deque(maxlen=7)

# Configuração do socket UDP para enviar dados de posição ao jogo
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def segment_color(frame):
    """
    Função para segmentar a cor laranja na imagem.
    Converte a imagem para HSV, aplica uma máscara, e calcula o centroide do maior contorno.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # Converte o quadro para HSV
    mask = cv2.inRange(hsv, lower_orange, upper_orange)  # Cria uma máscara para a cor laranja
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Encontra contornos na máscara

    if contours:
        # Seleciona o maior contorno e verifica se é significativo
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) > 500:  # Ignora contornos pequenos
            moments = cv2.moments(largest_contour)  # Calcula os momentos do contorno
            center_x = int(moments["m10"] / moments["m00"])  # Calcula o centro X do contorno
            return mask, center_x
    return mask, None  # Retorna a máscara e None se nenhum contorno for detetado

while True:
    # Captura um quadro da câmara
    ret, frame = cap.read()
    if not ret:
        print("Error")
        break

    frame = cv2.flip(frame, 1)  # Espelha a imagem horizontalmente
    mask, position = segment_color(frame)  # Segmenta a cor e obtém a posição

    if position:
        # Adiciona a posição ao histórico e calcula a média
        position_history.append(position)
        average_x = int(np.mean(position_history))
        # Envia a posição média ao jogo via socket UDP
        message = str(average_x).encode()
        client_socket.sendto(message, (server_ip, server_port))

    # Exibe a imagem original e a máscara
    cv2.imshow('Original', frame)
    cv2.imshow('Mask', mask)

    # Sai do loop se a tecla 'q' for pressionada / to fix
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberta a câmara e fecha todas as janelas
cap.release()
cv2.destroyAllWindows()
client_socket.close()