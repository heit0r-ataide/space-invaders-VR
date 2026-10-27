import pygame
import random
import sys

# Inicialização do Pygame e Joystick
pygame.init()
pygame.joystick.init()

# Detecta o joystick
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# Definir cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)

# Definir tamanho da tela
LARGURA_TELA = 1300
ALTURA_TELA = 550
largura_vr = LARGURA_TELA // 2
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Space Invaders VR")
modo_tela = "vr"
largura_jogo = largura_vr

# Definir fontes
fonte = pygame.font.Font(None, 36)

# Definir imagens e redimensioná-las
nave_jogador_img = pygame.image.load('nave_jogador.png')
nave_jogador = pygame.transform.scale(nave_jogador_img, (50, 50))

inimigo_img = pygame.image.load('inimigo.png')
inimigo_sprite = pygame.transform.scale(inimigo_img, (40, 40))

boss_img = pygame.image.load('boss.png')
boss_sprite = pygame.transform.scale(boss_img, (100, 100))

# Definir imagem de fundo
imagem_de_fundo_img = pygame.image.load('background.png')

# Definir música de fundo
pygame.mixer.music.load('trilha_sonora.mp3')
pygame.mixer.music.play(-1)  # Toca em loop

# Definir sons
som_disparo = pygame.mixer.Sound('som_disparo.wav')
som_explosao = pygame.mixer.Sound('som_explosao.wav')

# Definir variáveis
velocidade_jogador = 5
velocidade_inimigo = 2
velocidade_boss = 2  # Boss se move em zigue-zague
velocidade_projeteis = 7
projeteis_jogador = []
projeteis_inimigos = []
inimigos = []
boss_na_tela = False
boss_vidas = 10  # Boss tem 10 vidas
rodada_atual = 1
max_rodadas = 5
pontuacao = 0
vidas = 3  # 3 vidas para o jogador
tempo_recarga = 500
ultimo_disparo = 0
inimigos_destruidos = 0
especial_disponivel = False

# Função para criar inimigos
def criar_inimigos():
    for i in range(5):
        x_inimigo = random.randint(50, largura_jogo - 100)
        y_inimigo = random.randint(50, 150)
        inimigos.append([x_inimigo, y_inimigo, random.choice([-1, 1])])  # Adicionar direção inicial

# Função para mover projéteis
def mover_projeteis(projeteis):
    for projetil in projeteis[:]:
        projetil[1] -= velocidade_projeteis
        if projetil[1] < 0:
            projeteis.remove(projetil)

def mover_projeteis_inimigos():
    for projetil in projeteis_inimigos[:]:
        projetil[1] += velocidade_projeteis
        if projetil[1] > ALTURA_TELA:
            projeteis_inimigos.remove(projetil)

# Função para mover inimigos em zigue-zague
def mover_inimigos():
    for inimigo in inimigos[:]:
        inimigo[0] += inimigo[2] * velocidade_inimigo
        if inimigo[0] <= 0 or inimigo[0] >= largura_jogo - 40:
            inimigo[2] *= -1  # Mudar direção horizontal
        if random.randint(1, frequencia_disparos) == 1:
            projeteis_inimigos.append([inimigo[0] + 20, inimigo[1] + 20])
            som_disparo.play()

# Função para mover o boss em zigue-zague
def mover_boss():
    global boss_vidas, boss_na_tela, pontuacao
    if boss_na_tela:
        boss[0] += boss[2] * velocidade_boss
        if boss[0] <= 0 or boss[0] >= largura_jogo - 100:
            boss[2] *= -1  # Mudar direção do boss
        if random.randint(0, 100) < 5:  # Chance de disparo do boss
            projeteis_inimigos.append([boss[0] + 50, boss[1] + 50])
        # Verificar se o boss foi atingido
        for projetil in projeteis_jogador[:]:
            if verificar_colisao(projetil, boss, 100, 100):
                projeteis_jogador.remove(projetil)
                boss_vidas -= 1
                print(f"Boss atingido! Vidas restantes: {boss_vidas}")
                som_explosao.play()
                if boss_vidas == 0:
                    print("Boss derrotado!")
                    pontuacao += 200
                    return True  # Boss foi derrotado
    return False  # Boss ainda não foi derrotado

# Função para verificar se todos os inimigos foram destruídos
def verificar_inimigos_derrotados():
    return not inimigos and not boss_na_tela

# Função para verificar colisão
def verificar_colisao(projetil, objeto, largura, altura):
    return objeto[0] < projetil[0] < objeto[0] + largura and objeto[1] < projetil[1] < objeto[1] + altura

# Função para verificar colisão entre projéteis do jogador e inimigos
def verificar_colisao_inimigos():
    global pontuacao, inimigos_destruidos, especial_disponivel
    for projetil in projeteis_jogador[:]:
        for inimigo in inimigos[:]:
            if verificar_colisao(projetil, inimigo, 40, 40):
                projeteis_jogador.remove(projetil)
                inimigos.remove(inimigo)
                pontuacao += 50  # Adicionar pontos ao acertar um inimigo
                print(f"Inimigo atingido! Pontuação: {pontuacao}")
                som_explosao.play()
                inimigos_destruidos += 1  # Aumentar a contagem de inimigos destruídos
                if inimigos_destruidos >= 5:
                    especial_disponivel = True  # Liberar o tiro especial
                    inimigos_destruidos = 0  # Resetar a contagem
                break

def disparar_tiro_especial(jogador_x, jogador_y):
    # O tiro especial pode ser um projétil maior ou mais rápido
    projeteis_jogador.append([jogador_x + 25, jogador_y - 20])  # Primeiro projétil
    projeteis_jogador.append([jogador_x + 10, jogador_y - 20])  # Segundo projétil, à esquerda
    projeteis_jogador.append([jogador_x + 40, jogador_y - 20])  # Terceiro projétil, à direita
    som_disparo.play()  # Reproduzir som de disparo especial

def desenhar_cena(jogador_x, jogador_y):
    def desenhar_olho(superficie, deslocamento_x):
        fundo = pygame.transform.scale(imagem_de_fundo_img, superficie.get_size())
        superficie.blit(fundo, (0, 0))
        superficie.blit(nave_jogador, (jogador_x + deslocamento_x, jogador_y))

        for inimigo in inimigos:
            superficie.blit(inimigo_sprite, (inimigo[0] + deslocamento_x, inimigo[1]))
        for projetil in projeteis_jogador:
            pygame.draw.rect(superficie, BRANCO, (projetil[0] + deslocamento_x, projetil[1], 5, 10))
        for projetil in projeteis_inimigos:
            pygame.draw.rect(superficie, VERMELHO, (projetil[0] + deslocamento_x, projetil[1], 5, 10))
        if boss_na_tela:
            superficie.blit(boss_sprite, (boss[0] + deslocamento_x, boss[1]))

        textos = (
            f"Pontuação: {pontuacao}",
            f"Vidas: {vidas}",
            f"Rodadas: {rodada_atual}/{max_rodadas}",
            f"Especial: {inimigos_destruidos}/5",
        )
        for indice, texto in enumerate(textos):
            superficie.blit(fonte.render(texto, True, BRANCO), (10, 10 + indice * 40))

    if modo_tela == "vr":
        olho = pygame.Surface((largura_vr, ALTURA_TELA))
        tela.fill(PRETO)
        desenhar_olho(olho, -10)
        largura_metade = tela.get_width() // 2
        tela.blit(pygame.transform.scale(olho, (largura_metade, tela.get_height())), (0, 0))
        desenhar_olho(olho, 10)
        tela.blit(pygame.transform.scale(olho, (tela.get_width() - largura_metade, tela.get_height())),
                  (largura_metade, 0))
    else:
        cena = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        desenhar_olho(cena, 0)
        tela.blit(pygame.transform.scale(cena, tela.get_size()), (0, 0))

    pygame.display.flip()
# Função para mostrar o menu inicial
def mostrar_menu_inicial():
    tela.fill(PRETO)
    titulo = fonte.render("Space Invaders", True, BRANCO)
    instrucao = fonte.render("Pressione ENTER ou A no controle para iniciar", True, BRANCO)
    tela.blit(titulo, (tela.get_width() // 2 - titulo.get_width() // 2, tela.get_height() // 2 - 100))
    tela.blit(instrucao, (tela.get_width() // 2 - instrucao.get_width() // 2, tela.get_height() // 2))
    pygame.display.flip()
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:  # Iniciar o jogo com ENTER
                    esperando = False
            if pygame.joystick.get_count() > 0:
                if joystick.get_button(0):  # Iniciar o jogo com botão "A" do joystick
                    esperando = False

def selecionar_modo_tela():
    global tela, modo_tela, largura_jogo

    fonte_opcoes = pygame.font.Font(None, 32)
    opcoes = [
        "1 - Tela cheia (uma imagem)",
        "2 - Tela duplicada para oculos VR",
        "ENTER para confirmar | A/B no controle",
    ]
    selecao = 0
    esperando = True

    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_1, pygame.K_LEFT, pygame.K_RIGHT):
                    selecao = 0 if evento.key != pygame.K_RIGHT else 1
                    if evento.key == pygame.K_1:
                        esperando = False
                elif evento.key == pygame.K_2:
                    selecao = 1
                    esperando = False
                elif evento.key == pygame.K_RETURN:
                    esperando = False
            if evento.type == pygame.JOYBUTTONDOWN:
                if evento.button == 0:
                    selecao = 1
                    esperando = False
                elif evento.button == 1:
                    selecao = 0
                    esperando = False

        tela.fill(PRETO)
        titulo = fonte.render("Modo de exibicao", True, BRANCO)
        tela.blit(titulo, (tela.get_width() // 2 - titulo.get_width() // 2, 170))
        for indice, texto in enumerate(opcoes):
            cor = (255, 220, 80) if indice == selecao else BRANCO
            imagem = fonte_opcoes.render(texto, True, cor)
            tela.blit(imagem, (tela.get_width() // 2 - imagem.get_width() // 2, 250 + indice * 45))
        pygame.display.flip()

    modo_tela = "vr" if selecao == 1 else "tela_cheia"
    largura_jogo = largura_vr if modo_tela == "vr" else LARGURA_TELA
    info_tela = pygame.display.Info()
    tela = pygame.display.set_mode((info_tela.current_w, info_tela.current_h), pygame.FULLSCREEN)

def selecionar_dificuldade():
    tela.fill(PRETO)
    titulo = fonte.render("Escolha a Dificuldade", True, BRANCO)
    opcao_normal = fonte.render("1 ou Y no controle: Normal", True, BRANCO)
    opcao_dificil = fonte.render("2 ou A no controle: Dificil", True, BRANCO)

    # Desenhar opções na tela
    tela.blit(titulo, (tela.get_width() // 2 - titulo.get_width() // 2, tela.get_height() // 2 - 100))
    tela.blit(opcao_normal, (tela.get_width() // 2 - opcao_normal.get_width() // 2, tela.get_height() // 2 - 20))
    tela.blit(opcao_dificil, (tela.get_width() // 2 - opcao_dificil.get_width() // 2, tela.get_height() // 2 + 20))
    pygame.display.flip()

    # Loop de espera pela seleção de dificuldade
    dificuldade = "normal"  # Padrão
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:  # Tecla '1' para Normal
                    dificuldade = "normal"
                    esperando = False
                elif evento.key == pygame.K_2:  # Tecla '2' para Difícil
                    dificuldade = "dificil"
                    esperando = False
            if pygame.joystick.get_count() > 0:
                if joystick.get_button(3):
                    dificuldade = "normal"
                    esperando = False
                elif joystick.get_button(0):
                    dificuldade = "dificil"
                    esperando = False

    return dificuldade


# Função para mostrar o menu final
def mostrar_menu_final():
    tela.fill(PRETO)
    if boss_vidas == 0:
        resultado = fonte.render("Você venceu!", True, BRANCO)
        tela.blit(resultado, (tela.get_width() // 2 - resultado.get_width() // 2, tela.get_height() // 2 - 100))
    else:
        resultado1 = fonte.render("Você perdeu!", True, BRANCO)
        tela.blit(resultado1, (tela.get_width() // 2 - resultado1.get_width() // 2, tela.get_height() // 2 - 100))
    pontuacao_final = fonte.render(f"Sua pontuação: {pontuacao}", True, BRANCO)
    instrucao = fonte.render("R ou X no controle: reiniciar | Q ou B: sair", True, BRANCO)

    tela.blit(pontuacao_final, (tela.get_width() // 2 - pontuacao_final.get_width() // 2, tela.get_height() // 2))
    tela.blit(instrucao, (tela.get_width() // 2 - instrucao.get_width() // 2, tela.get_height() // 2 + 50))
    pygame.display.flip()

    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:  # Reiniciar com R
                    return True
                if evento.key == pygame.K_q:  # Sair com Q
                    pygame.quit()
                    sys.exit()
            if pygame.joystick.get_count() > 0:
                if joystick.get_button(2):
                    return True
                if joystick.get_button(1):
                    pygame.quit()
                    sys.exit()

# Função para rodar o loop principal do jogo
def loop_jogo():
    global rodada_atual, boss_na_tela, boss, pontuacao, vidas, inimigos, boss_vidas, ultimo_disparo, tempo_recarga, especial_disponivel, velocidade_inimigo, velocidade_projeteis, frequencia_disparos
    # Posição inicial do jogador
    jogador_x = largura_jogo // 2 - 25
    jogador_y = ALTURA_TELA - 60

    boss = [largura_jogo // 2 - 50, 50, 1]  # Posição inicial e direção do boss
    criar_inimigos()  # Cria inimigos para a rodada

    dificuldade = selecionar_dificuldade()

    # Ajustar parâmetros de dificuldade
    if dificuldade == "normal":
        velocidade_inimigo = 3.5
        velocidade_projeteis = 7
        frequencia_disparos = 100  # Inimigos disparam com menos frequência
    elif dificuldade == "dificil":
        velocidade_inimigo = 5
        velocidade_projeteis = 7
        frequencia_disparos = 60  # Inimigos disparam mais frequentemente

    clock = pygame.time.Clock()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        tempo_atual = pygame.time.get_ticks()

        # Controle do jogador
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] and jogador_x > 0:
            jogador_x -= velocidade_jogador
        if teclas[pygame.K_RIGHT] and jogador_x < largura_jogo - 50:
            jogador_x += velocidade_jogador
        if teclas[pygame.K_SPACE]:  # Disparo do jogador
            if len(projeteis_jogador) < 5 and tempo_atual - ultimo_disparo > tempo_recarga:
                projeteis_jogador.append([jogador_x + 25, jogador_y])
                som_disparo.play()
                ultimo_disparo = tempo_atual

        # Controle do joystick
        pygame.joystick.get_init()
        if pygame.joystick.get_count() > 0:
            if joystick.get_button(0):
                if len(projeteis_jogador) < 5 and tempo_atual - ultimo_disparo > tempo_recarga:
                    projeteis_jogador.append([jogador_x + 25, jogador_y])
                    som_disparo.play()
                    ultimo_disparo = tempo_atual

        if pygame.joystick.get_count() > 0:
            eixo_horizontal = joystick.get_axis(0)
            if eixo_horizontal < -0.1:
                jogador_x -= velocidade_jogador
            if eixo_horizontal > 0.1:
                jogador_x += velocidade_jogador

        if especial_disponivel:
            if teclas[pygame.K_e]:  # Por exemplo, a tecla 'E' para o tiro especial
                disparar_tiro_especial(jogador_x, jogador_y)
                especial_disponivel = False  # Usar o tiro especial consome ele
            if pygame.joystick.get_count() > 0:
                if joystick.get_button(1):  # Botão "B" no joystick, por exemplo
                    disparar_tiro_especial(jogador_x, jogador_y)
                    especial_disponivel = False

        # Atualizar a posição dos projéteis
        mover_projeteis(projeteis_jogador)
        mover_projeteis_inimigos()
        verificar_colisao_inimigos()  # Verifica colisões com inimigos

        # Mover inimigos e disparar projéteis
        mover_inimigos()

        jogador_x = max(0, min(largura_jogo - 50, jogador_x))

        # Se o boss estiver na tela, mover o boss
        if boss_na_tela:
            if mover_boss():
                return mostrar_menu_final()

        # Verificar se todos os inimigos foram derrotados
        if verificar_inimigos_derrotados():
            if rodada_atual < max_rodadas:
                print(f"Rodada {rodada_atual} completa!")
                rodada_atual += 1
                pontuacao += 100  # Adiciona pontos ao completar a rodada
                print(f"Pontuação: {pontuacao}")
                inimigos.clear()  # Limpa os inimigos para a próxima rodada
                criar_inimigos()  # Cria novos inimigos
                if rodada_atual == max_rodadas:
                    boss_na_tela = True  # Iniciar a batalha contra o boss

        # Verificar se o jogador foi atingido
        for projetil in projeteis_inimigos[:]:
            if verificar_colisao(projetil, [jogador_x, jogador_y], 50, 50):
                vidas -= 1
                print(f"Vida perdida! Vidas restantes: {vidas}")
                som_explosao.play()
                projeteis_inimigos.remove(projetil)
                if vidas == 0:
                    print("Game Over! Sua pontuação final: ", pontuacao)
                    return mostrar_menu_final()
        desenhar_cena(jogador_x, jogador_y)
        clock.tick(60)  # Limitar a 60 FPS

# Função para reiniciar o jogo
def reiniciar_jogo():
    global rodada_atual, pontuacao, vidas, boss_vidas, boss_na_tela
    global inimigos_destruidos, especial_disponivel, ultimo_disparo

    rodada_atual = 1
    pontuacao = 0
    vidas = 3
    boss_vidas = 10
    boss_na_tela = False
    inimigos.clear()
    projeteis_jogador.clear()
    projeteis_inimigos.clear()
    inimigos_destruidos = 0
    especial_disponivel = False
    ultimo_disparo = 0

def main():
    selecionar_modo_tela()
    while True:
        mostrar_menu_inicial()
        if not loop_jogo():
            break
        reiniciar_jogo()

    pygame.quit()

if __name__ == "__main__":
    main()
