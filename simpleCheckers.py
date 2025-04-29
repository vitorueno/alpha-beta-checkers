import copy

# Constantes do jogo
BOARD_SIZE = 8
PLAYER_X = 'x'
PLAYER_O = 'o'
KING_X = 'X'
KING_O = 'O'
EMPTY = '.'
MAX_SEM_CAPTURA = 20  # Limite de jogadas sem captura para declarar empate

def inicializar_tabuleiro():
    """Cria o tabuleiro inicial de damas."""
    tabuleiro = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    for linha in range(BOARD_SIZE):
        for coluna in range(BOARD_SIZE):
            if (linha + coluna) % 2 == 1:
                if linha < 3:
                    tabuleiro[linha][coluna] = PLAYER_O
                elif linha > 4:
                    tabuleiro[linha][coluna] = PLAYER_X
    return tabuleiro

def imprimir_tabuleiro(tabuleiro):
    """Exibe o tabuleiro no terminal."""
    for linha in tabuleiro:
        print(' '.join(linha))
    print()

def movimentos_validos(tabuleiro, jogador):
    """Gera todos os movimentos válidos para o jogador atual."""
    movimentos = []
    direcao = -1 if jogador.lower() == PLAYER_X else 1
    inimigos = [PLAYER_O, KING_O] if jogador.lower() == PLAYER_X else [PLAYER_X, KING_X]

    for linha in range(BOARD_SIZE):
        for coluna in range(BOARD_SIZE):
            peca = tabuleiro[linha][coluna]
            if peca.lower() == jogador:
                movimentos.extend(movimentos_peca(tabuleiro, linha, coluna, peca, direcao, inimigos))
    return movimentos

def movimentos_peca(tabuleiro, linha, coluna, peca, direcao, inimigos):
    """Gera os movimentos válidos para uma única peça."""
    movimentos = []
    for desloc_coluna in [-1, 1]:
        nova_linha = linha + direcao
        nova_coluna = coluna + desloc_coluna
        if movimento_valido(tabuleiro, nova_linha, nova_coluna):
            movimentos.append(((linha, coluna), (nova_linha, nova_coluna)))
        nova_linha_salto = linha + 2 * direcao
        nova_coluna_salto = coluna + 2 * desloc_coluna
        if captura_valida(tabuleiro, linha, coluna, nova_linha, nova_coluna, nova_linha_salto, nova_coluna_salto, inimigos):
            movimentos.append(((linha, coluna), (nova_linha_salto, nova_coluna_salto)))
    if peca.isupper():
        movimentos.extend(movimentos_dama(tabuleiro, linha, coluna, inimigos))
    return movimentos

def movimentos_dama(tabuleiro, linha, coluna, inimigos):
    """Gera os movimentos válidos extras para uma dama."""
    movimentos = []
    for desloc_linha in [-1, 1]:
        for desloc_coluna in [-1, 1]:
            nova_linha = linha + desloc_linha
            nova_coluna = coluna + desloc_coluna
            if movimento_valido(tabuleiro, nova_linha, nova_coluna):
                movimentos.append(((linha, coluna), (nova_linha, nova_coluna)))
            nova_linha_salto = linha + 2 * desloc_linha
            nova_coluna_salto = coluna + 2 * desloc_coluna
            if captura_valida(tabuleiro, linha, coluna, nova_linha, nova_coluna, nova_linha_salto, nova_coluna_salto, inimigos):
                movimentos.append(((linha, coluna), (nova_linha_salto, nova_coluna_salto)))
    return movimentos

def movimento_valido(tabuleiro, linha, coluna):
    return 0 <= linha < BOARD_SIZE and 0 <= coluna < BOARD_SIZE and tabuleiro[linha][coluna] == EMPTY

def captura_valida(tabuleiro, linha, coluna, linha_meio, coluna_meio, linha_destino, coluna_destino, inimigos):
    return (0 <= linha_destino < BOARD_SIZE and 0 <= coluna_destino < BOARD_SIZE and
            tabuleiro[linha_meio][coluna_meio] in inimigos and tabuleiro[linha_destino][coluna_destino] == EMPTY)

def aplicar_movimento(tabuleiro, movimento):
    """Executa um movimento e retorna o novo tabuleiro e se houve captura."""
    novo_tabuleiro = copy.deepcopy(tabuleiro)
    (linha_origem, coluna_origem), (linha_destino, coluna_destino) = movimento
    peca = novo_tabuleiro[linha_origem][coluna_origem]
    novo_tabuleiro[linha_origem][coluna_origem] = EMPTY
    novo_tabuleiro[linha_destino][coluna_destino] = peca

    captura = False
    if abs(linha_destino - linha_origem) == 2:
        linha_captura = (linha_origem + linha_destino) // 2
        coluna_captura = (coluna_origem + coluna_destino) // 2
        novo_tabuleiro[linha_captura][coluna_captura] = EMPTY
        captura = True

    promover_dama(novo_tabuleiro, linha_destino, coluna_destino, peca)

    return novo_tabuleiro, captura

def promover_dama(tabuleiro, linha, coluna, peca):
    if peca == PLAYER_X and linha == 0:
        tabuleiro[linha][coluna] = KING_X
    elif peca == PLAYER_O and linha == BOARD_SIZE - 1:
        tabuleiro[linha][coluna] = KING_O

def avaliar(tabuleiro, jogador):
    """Avalia o tabuleiro para o jogador atual."""
    pontuacao = 0
    for linha in tabuleiro:
        for peca in linha:
            if peca.lower() == jogador:
                pontuacao += 3 if peca.isupper() else 1
            elif peca != EMPTY:
                pontuacao -= 3 if peca.isupper() else 1
    return pontuacao

def alpha_beta(tabuleiro, profundidade, alpha, beta, maximizando, jogador):
    """Algoritmo Alpha-Beta Pruning."""
    if profundidade == 0:
        return avaliar(tabuleiro, jogador), None

    movimentos = movimentos_validos(tabuleiro, jogador if maximizando else oponente(jogador))
    if not movimentos:
        return avaliar(tabuleiro, jogador), None

    melhor_movimento = None

    if maximizando:
        melhor_valor = float('-inf')
        for movimento in movimentos:
            novo_tabuleiro, _ = aplicar_movimento(tabuleiro, movimento)
            valor, _ = alpha_beta(novo_tabuleiro, profundidade - 1, alpha, beta, False, jogador)
            if valor > melhor_valor:
                melhor_valor = valor
                melhor_movimento = movimento
            alpha = max(alpha, valor)
            if beta <= alpha:
                break
        return melhor_valor, melhor_movimento
    else:
        pior_valor = float('inf')
        for movimento in movimentos:
            novo_tabuleiro, _ = aplicar_movimento(tabuleiro, movimento)
            valor, _ = alpha_beta(novo_tabuleiro, profundidade - 1, alpha, beta, True, jogador)
            if valor < pior_valor:
                pior_valor = valor
                melhor_movimento = movimento
            beta = min(beta, valor)
            if beta <= alpha:
                break
        return pior_valor, melhor_movimento

def oponente(jogador):
    """Retorna o jogador adversário."""
    return PLAYER_O if jogador == PLAYER_X else PLAYER_X

def jogo():
    """Função principal para executar o jogo IA vs IA."""
    tabuleiro = inicializar_tabuleiro()
    jogador_atual = PLAYER_X
    jogadas_sem_captura = 0

    while True:
        imprimir_tabuleiro(tabuleiro)

        movimentos = movimentos_validos(tabuleiro, jogador_atual)
        if not movimentos:
            print(f"Jogador {oponente(jogador_atual)} venceu!")
            break

        _, melhor_movimento = alpha_beta(tabuleiro, profundidade=5, alpha=float('-inf'), beta=float('inf'), maximizando=True, jogador=jogador_atual)
        if melhor_movimento:
            tabuleiro, captura = aplicar_movimento(tabuleiro, melhor_movimento)
            jogadas_sem_captura = 0 if captura else jogadas_sem_captura + 1

        if jogadas_sem_captura >= MAX_SEM_CAPTURA:
            print("Empate por excesso de jogadas sem captura!")
            break

        jogador_atual = oponente(jogador_atual)

if __name__ == "__main__":
    jogo()
