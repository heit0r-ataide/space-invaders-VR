import pygame
import sys

# Inicializa o pygame
pygame.init()

# Define a resolução da tela e cria a janela principal
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Invaders - VR 2D")

# Define as configurações de VR (offset para os olhos)
eye_offset = 20  # Ajuste para definir o ângulo de visão entre os olhos

# Carrega a imagem do fundo e dos objetos (exemplo)
background = pygame.Surface((width, height))  # Substitua com a imagem de fundo real
background.fill((0, 0, 0))  # Exemplo: fundo preto


# Função para renderizar a tela estereoscópica
def render_stereoscopic():
    # Renderiza a imagem do "olho esquerdo"
    screen.blit(background, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Simula o deslocamento da câmera para o olho esquerdo
    pygame.draw.rect(screen, (0, 128, 255),
                     (150 - eye_offset, 150, 50, 50))  # Exemplo de objeto renderizado para o olho esquerdo

    # Renderiza a imagem do "olho direito"
    screen.blit(background, (width // 2, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Simula o deslocamento da câmera para o olho direito
    pygame.draw.rect(screen, (255, 0, 128),
                     (150 + eye_offset + width // 2, 150, 50, 50))  # Exemplo de objeto renderizado para o olho direito


# Loop principal do jogo
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Atualiza a tela estereoscópica
    render_stereoscopic()

    # Atualiza o display
    pygame.display.flip()

    # Define a taxa de quadros por segundo
    clock.tick(60)

pygame.quit()
sys.exit()
