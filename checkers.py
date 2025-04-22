import copy
import time
import random

def criar_tabuleiro():
    tabuleiro = [['.' for _ in range(8)] for _ in range(8)]
    for i in range(3):
        for j in range(8):
            if (i + j) % 2 == 1:
                tabuleiro[i][j] = 'o'
    for i in range(5, 8):
        for j in range(8):
            if (i + j) % 2 == 1:
                tabuleiro[i][j] = 'x'
    return tabuleiro

def imprimir_tabuleiro(tab):
    print("  " + " ".join(str(i) for i in range(8)))
    for i in range(8):
        print(str(i) + " " + " ".join(tab[i]))
    print()

def dentro(i, j):
    return 0 <= i < 8 and 0 <= j < 8

def eh_inimigo(peça, jogador):
    if jogador in ['x', 'D']:
        return peça in ['o', 'd']
    else:
        return peça in ['x', 'D']

def contar_peças(tab):
    """Conta peças de cada jogador para determinar fase do jogo"""
    peças_x = sum(1 for i in range(8) for j in range(8) if tab[i][j] in ['x', 'D'])
    peças_o = sum(1 for i in range(8) for j in range(8) if tab[i][j] in ['o', 'd'])
    return peças_x, peças_o

def fase_do_jogo(tab):
    """Determina a fase do jogo baseada no número de peças"""
    peças_x, peças_o = contar_peças(tab)
    total = peças_x + peças_o
    if total > 16:
        return "abertura"
    elif total > 8:
        return "meio"
    else:
        return "final"

def gerar_movimentos(tab, jogador):
    movimentos = []
    capturas = []

    for i in range(8):
        for j in range(8):
            p = tab[i][j]
            if p != jogador and not (jogador == 'x' and p == 'D') and not (jogador == 'o' and p == 'd'):
                continue

            if p in ['x', 'D']:
                direcoes = [(-1, -1), (-1, 1)] if p == 'x' else [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            elif p in ['o', 'd']:
                direcoes = [(1, -1), (1, 1)] if p == 'o' else [(-1, -1), (-1, 1), (1, -1), (1, 1)]

            for d in direcoes:
                ni, nj = i + d[0], j + d[1]
                ci, cj = i + 2*d[0], j + 2*d[1]

                if dentro(ci, cj) and tab[ni][nj] != '.' and tab[ci][cj] == '.' and eh_inimigo(tab[ni][nj], jogador):
                    novo = copy.deepcopy(tab)
                    novo[ci][cj] = p
                    novo[i][j] = '.'
                    novo[ni][nj] = '.'
                    if jogador == 'x' and ci == 0:
                        novo[ci][cj] = 'D'
                    elif jogador == 'o' and ci == 7:
                        novo[ci][cj] = 'd'
                    capturas.append((novo, (i, j, ci, cj)))  # Guardamos os índices para análise
                elif dentro(ni, nj) and tab[ni][nj] == '.':
                    novo = copy.deepcopy(tab)
                    novo[ni][nj] = p
                    novo[i][j] = '.'
                    if jogador == 'x' and ni == 0:
                        novo[ni][nj] = 'D'
                    elif jogador == 'o' and ni == 7:
                        novo[ni][nj] = 'd'
                    movimentos.append((novo, (i, j, ni, nj)))  # Guardamos os índices para análise

    return capturas if capturas else movimentos

def distancia_ao_centro(i, j):
    """Calcula a distância de uma casa ao centro do tabuleiro"""
    centro_i, centro_j = 3.5, 3.5
    return ((i - centro_i) ** 2 + (j - centro_j) ** 2) ** 0.5

def distancia_ao_inimigo_mais_proximo(tab, i, j):
    """Calcula a distância à peça inimiga mais próxima"""
    peça = tab[i][j]
    min_dist = float('inf')
    
    for ni in range(8):
        for nj in range(8):
            if tab[ni][nj] != '.' and eh_inimigo(tab[ni][nj], peça):
                dist = abs(i - ni) + abs(j - nj)  # Distância Manhattan
                min_dist = min(min_dist, dist)
                
    return min_dist if min_dist != float('inf') else 8  # Se não há inimigos, retorna 8 (valor máximo possível)

def avaliar(tab, fase=None):
    """Função de avaliação melhorada que considera a fase do jogo"""
    if fase is None:
        fase = fase_do_jogo(tab)
    
    # Pesos para diferentes aspectos do jogo
    peso_peça = 10.0
    peso_dama = 25.0
    peso_avanço = 0.3 if fase == "abertura" else 0.1
    peso_centro = 0.5 if fase == "meio" else 0.2
    peso_aproximação = 0.0 if fase == "abertura" else (1.0 if fase == "final" else 0.3)
    
    valor = 0
    
    # Contagem e avaliação de peças
    for i in range(8):
        for j in range(8):
            p = tab[i][j]
            if p == 'x':
                # Peça básica + bônus pelo avanço
                valor += peso_peça + peso_avanço * (7 - i)
                # Bônus pelo controle do centro
                valor += peso_centro * (4 - distancia_ao_centro(i, j))
                # No final do jogo, incentiva aproximação das peças inimigas
                if fase == "final":
                    dist_inimigo = distancia_ao_inimigo_mais_proximo(tab, i, j)
                    valor += peso_aproximação * (8 - dist_inimigo)
            elif p == 'D':
                valor += peso_dama
                # Damas também ganham bônus pelo controle do centro
                valor += peso_centro * (4 - distancia_ao_centro(i, j))
            elif p == 'o':
                # Mesma lógica para peças 'o'
                valor -= peso_peça + peso_avanço * i
                valor -= peso_centro * (4 - distancia_ao_centro(i, j))
                if fase == "final":
                    dist_inimigo = distancia_ao_inimigo_mais_proximo(tab, i, j)
                    valor -= peso_aproximação * (8 - dist_inimigo)
            elif p == 'd':
                valor -= peso_dama
                valor -= peso_centro * (4 - distancia_ao_centro(i, j))
    
    # Adicionar um pequeno valor aleatório no final do jogo para evitar ciclos
    if fase == "final":
        valor += random.uniform(-0.1, 0.1)
    
    return valor

def alfa_beta(tab, prof, alfa, beta, maximizando, fase):
    if prof == 0 or jogo_terminou(tab):
        return avaliar(tab, fase), tab, None

    jogador = 'o' if maximizando else 'x'
    movimentos = gerar_movimentos(tab, jogador)

    if not movimentos:
        return avaliar(tab, fase), tab, None

    melhor_mov = None
    melhor_info = None

    if maximizando:
        max_eval = float('-inf')
        for mov, info in movimentos:
            eval, _, _ = alfa_beta(mov, prof - 1, alfa, beta, False, fase)
            if eval > max_eval:
                max_eval = eval
                melhor_mov = mov
                melhor_info = info
            alfa = max(alfa, eval)
            if beta <= alfa:
                break
        return max_eval, melhor_mov, melhor_info
    else:
        min_eval = float('inf')
        for mov, info in movimentos:
            eval, _, _ = alfa_beta(mov, prof - 1, alfa, beta, True, fase)
            if eval < min_eval:
                min_eval = eval
                melhor_mov = mov
                melhor_info = info
            beta = min(beta, eval)
            if beta <= alfa:
                break
        return min_eval, melhor_mov, melhor_info

def jogo_terminou(tab):
    return not gerar_movimentos(tab, 'x') or not gerar_movimentos(tab, 'o')

def calcular_hash_tabuleiro(tab):
    """Cria um hash do tabuleiro para detectar posições repetidas"""
    return ''.join(''.join(linha) for linha in tab)

def jogar():
    tab = criar_tabuleiro()
    turno_ia = True  # IA 'o' começa
    sem_progresso = 0
    max_turnos = 200
    
    # Guardar histórico de posições para detectar ciclos
    historico_posicoes = {}
    
    for turno in range(max_turnos):
        imprimir_tabuleiro(tab)
        jogador = 'o' if turno_ia else 'x'
        print(f"Turno {turno+1}: Vez da IA ({jogador})")

        # Determinar a fase do jogo
        fase = fase_do_jogo(tab)
        print(f"Fase do jogo: {fase}")
        
        # Ajustar profundidade com base na fase do jogo
        profundidade = 4 if fase == "abertura" else (5 if fase == "meio" else 6)
        
        # Registrar a posição atual
        hash_atual = calcular_hash_tabuleiro(tab)
        historico_posicoes[hash_atual] = historico_posicoes.get(hash_atual, 0) + 1
        
        # Detectar ciclos
        if historico_posicoes[hash_atual] > 2:
            print(f"Posição repetida {historico_posicoes[hash_atual]} vezes!")
            # No caso de ciclo, introduzir mais aleatoriedade
            _, novo_tab, mov_info = alfa_beta(tab, 2, float('-inf'), float('inf'), turno_ia, fase)
            
            # Se ainda temos ciclo, escolher um movimento aleatório
            if historico_posicoes[hash_atual] > 4:
                movimentos = gerar_movimentos(tab, jogador)
                if movimentos:
                    novo_tab, mov_info = random.choice(movimentos)
                    print("Movimento aleatório aplicado para quebrar ciclo!")
        else:
            # Movimento normal
            _, novo_tab, mov_info = alfa_beta(tab, profundidade, float('-inf'), float('inf'), turno_ia, fase)

        # Se temos informações do movimento, mostramos
        if mov_info:
            i, j, ni, nj = mov_info
            print(f"Movimento: ({i},{j}) -> ({ni},{nj})")
            
            # Verificar se foi uma captura
            if abs(i - ni) == 2:  # Movimento de captura
                sem_progresso = 0
                print("Captura realizada!")
            else:
                sem_progresso += 1
        else:
            sem_progresso += 1
            
        print(f"Turnos sem captura: {sem_progresso//2}")  # Dividimos por 2 pois contamos por jogador
        
        if sem_progresso >= 40:
            imprimir_tabuleiro(novo_tab)
            print("Empate por 20 jogadas consecutivas de cada jogador sem captura!")
            return
            
        # Avaliar o tabuleiro atual para o feedback
        valor = avaliar(novo_tab, fase)
        if turno_ia:
            print(f"Avaliação do tabuleiro: {-valor:.2f} (favorável ao 'x' se negativo)")
        else:
            print(f"Avaliação do tabuleiro: {valor:.2f} (favorável ao 'x' se positivo)")

        tab = novo_tab
        if jogo_terminou(tab):
            break
        turno_ia = not turno_ia
        print("-" * 30)
        time.sleep(0.5)  # Tempo para visualizar o movimento

    imprimir_tabuleiro(tab)
    peças_x, peças_o = contar_peças(tab)
    print(f"Final do jogo - Peças x: {peças_x}, Peças o: {peças_o}")
    
    if not gerar_movimentos(tab, 'o'):
        print("IA 'x' venceu!")
    elif not gerar_movimentos(tab, 'x'):
        print("IA 'o' venceu!")
    else:
        print("Limite de turnos atingido! Avaliando vencedor...")
        valor = avaliar(tab)
        if valor > 0:
            print("IA 'x' venceu por avaliação!")
        elif valor < 0:
            print("IA 'o' venceu por avaliação!")
        else:
            print("Empate!")

if __name__ == "__main__":
    jogar()