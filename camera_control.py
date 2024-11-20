import cv2
import socket
import sys
import os
import threading

# Configuração do servidor para envio dos dados da posição do rosto
server_ip = 'localhost'  # Endereço IP do servidor que irá receber os dados
server_port = 5000  # Porta de comunicação do servidor

# Criação do socket UDP para envio dos dados
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Inicialização da câmara
cap = cv2.VideoCapture(0)  # Abre a câmara padrão (índice 0)
if not cap.isOpened():  # Verifica se a câmara foi aberta com sucesso
    print("Erro: Não foi possível abrir a câmara")
    sys.exit()  # Termina o programa caso a câmara não funcione

# Define a resolução da câmara
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Largura do frame
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Altura do frame

# Verifica e obtém o caminho do ficheiro de cascata para detecção de rostos
cascade_path = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")
if not os.path.exists(cascade_path):  # Garante que o ficheiro existe no diretório
    print("Erro: O ficheiro 'haarcascade_frontalface_default.xml' não foi encontrado. "
          "Certifique-se de que está no mesmo diretório deste script.")
    sys.exit()  # Termina o programa se o ficheiro não estiver presente

# Carrega o classificador Viola-Jones utilizando o ficheiro de cascata
face_cascade = cv2.CascadeClassifier(cascade_path)

# Variável global para encerrar o programa
running = True


def detect_faces():
    """Função que processa frames e envia a posição do rosto detetado."""
    global running

    while running:
        ret, frame = cap.read()  # Captura um frame da câmara
        if not ret:  # Verifica se o frame foi capturado com sucesso
            print("Erro: Não foi possível capturar o frame da câmara")
            break  # Termina o loop caso não seja possível capturar frames

        # Espelha horizontalmente a imagem para corresponder ao movimento natural
        frame = cv2.flip(frame, 1)

        # Converte o frame capturado para escala de cinza, necessário para a detecção de rostos
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Realiza a detecção de rostos no frame em escala de cinza
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        center_x = None  # Inicializa a variável para armazenar o centro do rosto detectado

        # Itera sobre os rostos detectados (caso existam)
        for (x, y, w, h) in faces:
            center_x = x + w // 2  # Calcula o centro horizontal do rosto
            # Desenha um retângulo em torno do rosto detectado
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            break  # Considera apenas o primeiro rosto detectado

        if center_x is not None:  # Verifica se um rosto foi detectado
            # Envia a posição horizontal do centro do rosto através do socket UDP
            message = str(center_x).encode()
            client_socket.sendto(message, (server_ip, server_port))

        # Mostra a imagem capturada e processada com o retângulo em tempo real
        cv2.imshow('Camera', frame)

        # Aguarda brevemente para permitir o processamento suave
        if cv2.waitKey(1) == 27:  # Esc encerra o programa
            running = False
            break


# Inicia a detecção de rostos numa thread separada
detector_thread = threading.Thread(target=detect_faces)
detector_thread.start()

try:
    # Aguarda que a thread principal continue enquanto o programa corre
    detector_thread.join()
except KeyboardInterrupt:
    running = False

# Liberta os recursos da câmara e fecha todas as janelas ao terminar o programa
cap.release()  # Liberta a câmara
cv2.destroyAllWindows()  # Fecha todas as janelas abertas pelo OpenCV
client_socket.close()  # Fecha o socket UDP