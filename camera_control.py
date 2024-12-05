import cv2
import socket
import sys
import os
import threading

# Definir o endereço do servidor e a porta para envio dos dados de posição do rosto
server_ip = 'localhost'
server_port = 5000

# Criação do socket para comunicação via UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Inicialização da câmara para captura de vídeo
cap = cv2.VideoCapture(0)
if not cap.isOpened():  # Verifica se a câmara foi aberta com sucesso
    print("Erro: Câmara")
    sys.exit()  # Encerra o programa se a câmara não abrir

# Define as dimensões do vídeo capturado
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Define o caminho para o classificador Haar para deteção de rostos
cascade_path = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")
if not os.path.exists(cascade_path):  # Verifica se o ficheiro XML existe
    print("Erro: Ficheiro .xml não encontrado.")
    sys.exit()  # Encerra o programa caso o ficheiro não seja encontrado

# Carrega o classificador Haar para deteção de rostos
face_cascade = cv2.CascadeClassifier(cascade_path)

# Inicialização do tracker CSRT (Channel and Spatial Reliability Tracking)
tracker = cv2.legacy.TrackerCSRT_create()

# Variáveis de controlo do estado do tracking
running = True  # Flag para controlar o loop principal
tracking = False  # Flag que indica se o tracker está a seguir o rosto
center_x = None  # Variável que armazenará a posição horizontal do centro do rosto


def detect_motion():
    global running, tracking, center_x, tracker

    while running:
        # Captura de um novo frame da câmara
        ret, frame = cap.read()
        if not ret:  # Se não conseguir capturar o frame, termina o loop
            print("Erro: Frame")
            break

        # Espelha a imagem para se alinhar com o movimento natural da face
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Converte o frame para escala de cinza

        if not tracking:
            # Detecção do rosto usando o classificador Haar
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:  # Se algum rosto for detectado
                (x, y, w, h) = faces[0]  # Pega as coordenadas do primeiro rosto detectado
                center_x = x + w // 2  # Calcula o centro do rosto
                bbox = (x, y, w, h)  # Define a caixa delimitadora do rosto
                tracker.init(frame, bbox)  # Inicializa o tracker com a caixa delimitadora
                tracking = True  # Marca que o rastreamento está ativo
                print("Rosto detectado e tracking iniciado.")
        else:
            # Atualiza a posição do rosto com o tracker CSRT
            success, bbox = tracker.update(frame)
            if success:  # Se o rastreamento for bem-sucedido
                (x, y, w, h) = [int(v) for v in bbox]  # Converte as coordenadas para inteiros
                center_x = int(x + w // 2)  # Recalcula o centro horizontal do rosto

                # Desenha um ponto no centro do rosto
                cv2.circle(frame, (center_x, y + h // 2), 5, (0, 0, 255), -1)

                # Envia a posição horizontal do centro do rosto para o servidor
                message = str(center_x).encode()
                client_socket.sendto(message, (server_ip, server_port))
            else:
                # Se o rastreamento falhar, reinicia o processo de deteção
                tracking = False
                print("Falha no tracking.")

        # Exibe o frame com a imagem processada
        cv2.imshow('Camera', frame)

        # Encerra o programa se a tecla 'Esc' for pressionada
        if cv2.waitKey(1) == 27:
            running = False
            break


# Criação de uma thread separada para realizar a deteção de movimento
detector_thread = threading.Thread(target=detect_motion)
detector_thread.start()

try:
    # Aguarda até a thread de deteção terminar
    detector_thread.join()
except KeyboardInterrupt:
    running = False

# Libera os recursos e encerra as janelas do OpenCV ao terminar o programa
cap.release()
cv2.destroyAllWindows()
client_socket.close()  # Fecha a conexão do socket