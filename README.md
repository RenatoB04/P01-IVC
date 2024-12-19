
# P01-IVC

Este projeto foi desenvolvido para a unidade curricular de Introdução à Visão por Computador e utiliza **Python**, **OpenCV** e **Pygame** para implementar um sistema de rastreamento facial que permite controlar a plataforma de um jogo interativo em tempo real com movimentos do rosto.

## Tecnologias Utilizadas
- **Python 3.12**: Linguagem de desenvolvimento principal.
- **OpenCV**: Biblioteca para captura de frames, deteção de rostos e rastreamento.
- **Pygame**: Usado para lógica e renderização do jogo.
- **Sockets UDP**: Comunicação em tempo real entre os módulos do projeto.

## Estrutura do Projeto
- **`camera_control.py`**:
  - Captura frames da câmara.
  - Deteta rostos utilizando Haar Cascade.
  - Realiza rastreamento contínuo com o tracker CSRT.
  - Envia a posição do rosto para o jogo via sockets UDP.
- **`game.py`**:
  - Recebe os dados de posição enviados pelo `camera_control.py`.
  - Gere a lógica do jogo, incluindo o movimento da plataforma, colisões e pontuações.
  - Renderiza os elementos do jogo com Pygame.

## Como Executar
1. Certifique-se de que tem o Python 3.12 instalado.
2. Instale as bibliotecas necessárias:
   ```
   pip install opencv-python pygame
   ```
3. Execute o ficheiro `game.py`:
   ```
   python game.py
   ```

## Funcionalidades
- **Deteção Inicial**: Identifica o rosto utilizando Haar Cascade.
- **Rastreamento Contínuo**: Mantém o rastreamento do rosto com alta precisão usando CSRT.
- **Controlo Baseado em Movimento**: Move a plataforma no jogo com base nos movimentos faciais.
- **Feedback Visual**: Exibe um ponto vermelho no rosto para indicar que está a ser rastreado.

## Fases do Desenvolvimento
Este projeto foi implementado em 3 fases distintas, conforme os requisitos da unidade curricular:

### Fase 1
- **Técnica Utilizada**: Segmentação por cor.
- **Descrição**: O controlo baseou-se na posição de objetos segmentados por cores predefinidas na imagem, como a cara do jogador, utilizando a cor da pele como critério.

### Fase 2
- **Técnica Utilizada**: Detecção de objetos com Viola-Jones e Haar Cascade.
- **Descrição**: Implementámos deteção de rostos utilizando o classificador Haar Cascade, que permite localizar a posição do rosto para ser usada como base para o controlo.

### Fase 3
- **Técnica Utilizada**: Tracking com CSRT.
- **Descrição**: Utilizámos o tracker CSRT para rastrear o rosto detetado em tempo real após a deteção inicial. Este método oferece maior estabilidade e precisão em situações de movimento.

## Referências
- [OpenCV Documentation](https://opencv.org/)
- [Pygame Documentation](https://www.pygame.org/docs)
- [Haar Cascade Models](https://github.com/opencv/opencv/tree/master/data/haarcascades)
