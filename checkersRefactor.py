"""
Jogo de Damas Brasileiro implementado com IA usando minimax e poda alfa-beta.
O jogo é jogado num tabuleiro 8x8 com peças 'x' e 'o'.
"""
import copy
import time
import random
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Set


class GamePhase(Enum):
    """Fases do jogo para ajustar estratégias."""
    OPENING = auto()
    MIDDLE = auto()
    ENDGAME = auto()


class Player(Enum):
    """Enumeração para os jogadores."""
    X = "x"  # Peças jogador X
    O = "o"  # Peças jogador O


@dataclass
class Position:
    """Representa uma posição no tabuleiro."""
    row: int
    col: int

    def is_valid(self) -> bool:
        """Verifica se a posição está dentro do tabuleiro."""
        return 0 <= self.row < 8 and 0 <= self.col < 8
    
    def __add__(self, other):
        """Permite somar posições para calcular movimentos."""
        return Position(self.row + other.row, self.col + other.col)
    
    def manhattan_distance(self, other) -> int:
        """Calcula a distância Manhattan até outra posição."""
        return abs(self.row - other.row) + abs(self.col - other.col)
    
    def euclidean_distance(self, other) -> float:
        """Calcula a distância euclidiana até outra posição."""
        return ((self.row - other.row) ** 2 + (self.col - other.col) ** 2) ** 0.5


@dataclass
class Move:
    """Representa um movimento no jogo."""
    start: Position
    end: Position
    is_capture: bool = False
    captured_position: Optional[Position] = None


class PieceType:
    """Constantes para os tipos de peças no tabuleiro."""
    EMPTY = '.'
    X = 'x'
    O = 'o'
    X_KING = 'D'
    O_KING = 'd'


class CheckersBoard:
    """Classe que gerencia o tabuleiro de damas."""
    
    def __init__(self):
        """Inicializa um novo tabuleiro de damas."""
        self.board = [[PieceType.EMPTY for _ in range(8)] for _ in range(8)]
        self._setup_board()
        
    def _setup_board(self):
        """Configura o tabuleiro inicial com as peças nas posições corretas."""
        # Posiciona peças do jogador O nas 3 primeiras linhas
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self.board[row][col] = PieceType.O
        
        # Posiciona peças do jogador X nas 3 últimas linhas
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self.board[row][col] = PieceType.X
    
    def get_piece(self, position: Position) -> str:
        """Retorna a peça na posição especificada."""
        return self.board[position.row][position.col]
    
    def set_piece(self, position: Position, piece_type: str):
        """Define uma peça na posição especificada."""
        self.board[position.row][position.col] = piece_type
    
    def remove_piece(self, position: Position):
        """Remove uma peça do tabuleiro (substitui por espaço vazio)."""
        self.board[position.row][position.col] = PieceType.EMPTY
    
    def is_empty(self, position: Position) -> bool:
        """Verifica se uma posição está vazia."""
        return self.get_piece(position) == PieceType.EMPTY
    
    def is_enemy_piece(self, position: Position, player: Player) -> bool:
        """Verifica se há uma peça inimiga na posição."""
        piece = self.get_piece(position)
        if player == Player.X:
            return piece in [PieceType.O, PieceType.O_KING]
        else:
            return piece in [PieceType.X, PieceType.X_KING]
    
    def is_player_piece(self, position: Position, player: Player) -> bool:
        """Verifica se há uma peça do jogador na posição."""
        piece = self.get_piece(position)
        if player == Player.X:
            return piece in [PieceType.X, PieceType.X_KING]
        else:
            return piece in [PieceType.O, PieceType.O_KING]
    
    def is_king(self, position: Position) -> bool:
        """Verifica se há uma dama na posição."""
        piece = self.get_piece(position)
        return piece in [PieceType.X_KING, PieceType.O_KING]
    
    def promote_if_needed(self, position: Position):
        """Promove uma peça para dama se ela chegar ao fim do tabuleiro."""
        piece = self.get_piece(position)
        
        # Promove peça X para dama se chegar à linha 0
        if piece == PieceType.X and position.row == 0:
            self.set_piece(position, PieceType.X_KING)
        
        # Promove peça O para dama se chegar à linha 7
        elif piece == PieceType.O and position.row == 7:
            self.set_piece(position, PieceType.O_KING)
    
    def apply_move(self, move: Move):
        """Aplica um movimento no tabuleiro."""
        # Guarda a peça que está se movendo
        piece = self.get_piece(move.start)
        
        # Remove a peça da posição inicial
        self.remove_piece(move.start)
        
        # Coloca a peça na posição final
        self.set_piece(move.end, piece)
        
        # Se for uma captura, remove a peça capturada
        if move.is_capture and move.captured_position:
            self.remove_piece(move.captured_position)
        
        # Verifica se a peça deve ser promovida a dama
        self.promote_if_needed(move.end)
    
    def count_pieces(self) -> Tuple[int, int]:
        """Conta as peças de cada jogador no tabuleiro."""
        x_pieces = 0
        o_pieces = 0
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece in [PieceType.X, PieceType.X_KING]:
                    x_pieces += 1
                elif piece in [PieceType.O, PieceType.O_KING]:
                    o_pieces += 1
        
        return x_pieces, o_pieces
    
    def hash_position(self) -> str:
        """Cria um hash da posição atual do tabuleiro."""
        return ''.join(''.join(row) for row in self.board)
    
    def print(self):
        """Imprime o tabuleiro atual."""
        print("  " + " ".join(str(i) for i in range(8)))
        for i in range(8):
            print(f"{i} " + " ".join(self.board[i]))
        print()
    
    def clone(self) -> 'CheckersBoard':
        """Cria uma cópia profunda do tabuleiro atual."""
        new_board = CheckersBoard()
        new_board.board = copy.deepcopy(self.board)
        return new_board


class MoveGenerator:
    """Classe responsável por gerar todos os movimentos possíveis."""
    
    def __init__(self, board: CheckersBoard):
        self.board = board
    
    def get_piece_directions(self, position: Position) -> List[Position]:
        """Retorna as direções possíveis para uma peça se mover."""
        piece = self.board.get_piece(position)
        
        # Define as direções de movimento com base no tipo da peça
        if piece == PieceType.X:
            # Peça X só pode ir para cima (índices menores)
            return [Position(-1, -1), Position(-1, 1)]
        elif piece == PieceType.O:
            # Peça O só pode ir para baixo (índices maiores)
            return [Position(1, -1), Position(1, 1)]
        elif piece in [PieceType.X_KING, PieceType.O_KING]:
            # Damas podem ir em todas as direções
            return [Position(-1, -1), Position(-1, 1), Position(1, -1), Position(1, 1)]
        
        return []
    
    def generate_moves(self, player: Player) -> Tuple[List[Tuple[CheckersBoard, Move]], bool]:
        """Gera todos os movimentos válidos para um jogador."""
        capture_moves = []
        regular_moves = []
        
        # Verifica todas as posições do tabuleiro
        for row in range(8):
            for col in range(8):
                position = Position(row, col)
                
                # Pula se não for uma peça do jogador atual
                if not self.board.is_player_piece(position, player):
                    continue
                
                # Obtém as direções possíveis para a peça atual
                directions = self.get_piece_directions(position)
                
                # Verifica cada direção para movimentos possíveis
                for direction in directions:
                    # Verifica se é possível capturar
                    captures = self._check_capture(position, direction, player)
                    if captures:
                        capture_moves.extend(captures)
                    
                    # Se não houver capturas, verifica movimentos regulares
                    else:
                        new_position = position + direction
                        if (new_position.is_valid() and 
                            self.board.is_empty(new_position)):
                            # Cria novo tabuleiro com o movimento aplicado
                            new_board = self.board.clone()
                            move = Move(position, new_position)
                            new_board.apply_move(move)
                            regular_moves.append((new_board, move))
        
        # Retorna capturas se houver, caso contrário retorna movimentos regulares
        has_captures = len(capture_moves) > 0
        return capture_moves if has_captures else regular_moves, has_captures
    
    def _check_capture(self, position: Position, direction: Position, player: Player) -> List[Tuple[CheckersBoard, Move]]:
        """Verifica se é possível capturar na direção especificada."""
        captures = []
        
        # Posição da peça adversária (adjacente)
        enemy_pos = position + direction
        
        # Posição após a captura (2 casas na direção)
        landing_pos = enemy_pos + direction
        
        # Verifica se a captura é válida
        if (enemy_pos.is_valid() and landing_pos.is_valid() and
            self.board.is_enemy_piece(enemy_pos, player) and
            self.board.is_empty(landing_pos)):
            
            # Cria novo tabuleiro com a captura aplicada
            new_board = self.board.clone()
            move = Move(position, landing_pos, True, enemy_pos)
            new_board.apply_move(move)
            captures.append((new_board, move))
        
        return captures


class GameEvaluator:
    """Classe responsável por avaliar a posição do jogo."""
    
    # Constantes para pesos na avaliação
    PIECE_WEIGHT = 10.0
    KING_WEIGHT = 25.0
    
    def __init__(self, board: CheckersBoard):
        self.board = board
        self.board_center = Position(3.5, 3.5)
    
    def determine_game_phase(self) -> GamePhase:
        """Determina a fase atual do jogo com base no número de peças."""
        x_pieces, o_pieces = self.board.count_pieces()
        total_pieces = x_pieces + o_pieces
        
        if total_pieces > 16:
            return GamePhase.OPENING
        elif total_pieces > 8:
            return GamePhase.MIDDLE
        else:
            return GamePhase.ENDGAME
    
    def evaluate(self, game_phase: Optional[GamePhase] = None) -> float:
        """Avalia o tabuleiro do ponto de vista do jogador X."""
        if game_phase is None:
            game_phase = self.determine_game_phase()
        
        # Ajusta pesos com base na fase do jogo
        advance_weight = 0.3 if game_phase == GamePhase.OPENING else 0.1
        center_weight = 0.5 if game_phase == GamePhase.MIDDLE else 0.2
        proximity_weight = (0.0 if game_phase == GamePhase.OPENING else 
                           (1.0 if game_phase == GamePhase.ENDGAME else 0.3))
        
        score = 0.0
        
        # Avalia cada posição do tabuleiro
        for row in range(8):
            for col in range(8):
                position = Position(row, col)
                piece = self.board.get_piece(position)
                
                if piece == PieceType.X:
                    # Peça básica + bônus pelo avanço (mais perto da linha 0)
                    score += self.PIECE_WEIGHT + advance_weight * (7 - row)
                    # Bônus pelo controle do centro
                    score += center_weight * (4 - self._distance_to_center(position))
                    # Incentiva aproximação das peças inimigas no final do jogo
                    if game_phase == GamePhase.ENDGAME:
                        enemy_dist = self._distance_to_nearest_enemy(position)
                        score += proximity_weight * (8 - enemy_dist)
                
                elif piece == PieceType.X_KING:
                    score += self.KING_WEIGHT
                    # Damas também ganham bônus pelo controle do centro
                    score += center_weight * (4 - self._distance_to_center(position))
                
                elif piece == PieceType.O:
                    # Mesma lógica para peças O (valor negativo)
                    score -= self.PIECE_WEIGHT + advance_weight * row
                    score -= center_weight * (4 - self._distance_to_center(position))
                    if game_phase == GamePhase.ENDGAME:
                        enemy_dist = self._distance_to_nearest_enemy(position)
                        score -= proximity_weight * (8 - enemy_dist)
                
                elif piece == PieceType.O_KING:
                    score -= self.KING_WEIGHT
                    score -= center_weight * (4 - self._distance_to_center(position))
        
        # Adiciona um pequeno valor aleatório no final do jogo para evitar ciclos
        if game_phase == GamePhase.ENDGAME:
            score += random.uniform(-0.1, 0.1)
        
        return score
    
    def _distance_to_center(self, position: Position) -> float:
        """Calcula a distância de uma posição ao centro do tabuleiro."""
        return position.euclidean_distance(self.board_center)
    
    def _distance_to_nearest_enemy(self, position: Position) -> float:
        """Calcula a distância à peça inimiga mais próxima."""
        piece = self.board.get_piece(position)
        min_dist = float('inf')
        
        # Determina quais peças são inimigas
        enemy_pieces = ([PieceType.O, PieceType.O_KING] if piece in [PieceType.X, PieceType.X_KING] 
                        else [PieceType.X, PieceType.X_KING])
        
        # Verifica todas as posições do tabuleiro
        for row in range(8):
            for col in range(8):
                other_position = Position(row, col)
                other_piece = self.board.get_piece(other_position)
                
                if other_piece in enemy_pieces:
                    dist = position.manhattan_distance(other_position)
                    min_dist = min(min_dist, dist)
        
        return min_dist if min_dist != float('inf') else 8  # Se não há inimigos, retorna 8


class AIPlayer:
    """Classe de IA para jogar damas usando minimax com poda alfa-beta."""
    
    def __init__(self, player: Player):
        self.player = player
        self.maximizing = player == Player.O  # O é maximizador, X é minimizador
    
    def choose_move(self, board: CheckersBoard, depth: int) -> Tuple[CheckersBoard, Move]:
        """Escolhe o melhor movimento usando o algoritmo minimax com poda alfa-beta."""
        evaluator = GameEvaluator(board)
        game_phase = evaluator.determine_game_phase()
        
        # Executa algoritmo alfa-beta
        _, best_board, best_move = self._alpha_beta(
            board, depth, float('-inf'), float('inf'), 
            self.maximizing, game_phase
        )
        
        return best_board, best_move
    
    def _alpha_beta(self, board: CheckersBoard, depth: int, alpha: float, beta: float, 
                   maximizing: bool, game_phase: GamePhase) -> Tuple[float, CheckersBoard, Move]:
        """Implementa o algoritmo minimax com poda alfa-beta."""
        # Critério de parada: profundidade zero ou fim de jogo
        if depth == 0 or self._is_game_over(board):
            evaluator = GameEvaluator(board)
            return evaluator.evaluate(game_phase), board, None
        
        # Gera movimentos para o jogador atual
        current_player = Player.O if maximizing else Player.X
        move_generator = MoveGenerator(board)
        moves, _ = move_generator.generate_moves(current_player)
        
        # Se não há movimentos, o jogo acabou
        if not moves:
            evaluator = GameEvaluator(board)
            return evaluator.evaluate(game_phase), board, None
        
        best_board = None
        best_move = None
        
        if maximizing:
            max_eval = float('-inf')
            for new_board, move in moves:
                eval_score, _, _ = self._alpha_beta(
                    new_board, depth - 1, alpha, beta, False, game_phase
                )
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_board = new_board
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Poda beta
            
            return max_eval, best_board, best_move
        else:
            min_eval = float('inf')
            for new_board, move in moves:
                eval_score, _, _ = self._alpha_beta(
                    new_board, depth - 1, alpha, beta, True, game_phase
                )
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_board = new_board
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Poda alfa
            
            return min_eval, best_board, best_move
    
    def _is_game_over(self, board: CheckersBoard) -> bool:
        """Verifica se o jogo acabou (um jogador não tem movimentos)."""
        # Verifica se algum jogador não tem movimentos disponíveis
        for player in [Player.X, Player.O]:
            move_generator = MoveGenerator(board)
            moves, _ = move_generator.generate_moves(player)
            if not moves:
                return True
        
        return False


class CheckersGame:
    """Classe principal para gerenciar o jogo de damas."""
    
    def __init__(self):
        self.board = CheckersBoard()
        self.ai_x = AIPlayer(Player.X)
        self.ai_o = AIPlayer(Player.O)
        self.position_history = {}  # Para detectar posições repetidas
        self.turns_without_capture = 0
        self.max_turns = 200
    
    def start_game(self):
        """Inicia o jogo de damas."""
        current_player = Player.O  # O começa
        turn_count = 0
        
        while turn_count < self.max_turns:
            # Imprime estado atual
            self.board.print()
            turn_count += 1
            print(f"Turno {turn_count}: Vez da IA ({current_player.value})")
            
            # Determina a fase do jogo
            evaluator = GameEvaluator(self.board)
            game_phase = evaluator.determine_game_phase()
            print(f"Fase do jogo: {game_phase.name.lower()}")
            
            # Ajusta profundidade com base na fase do jogo
            depth = self._determine_search_depth(game_phase)
            
            # Registra a posição atual para detectar ciclos
            self._track_position()
            
            # Escolhe e aplica o próximo movimento
            new_board, move = self._select_next_move(current_player, game_phase, depth)
            
            # Atualiza contagem de turnos sem captura
            self._update_progress_tracking(move)
            
            # Verifica por empate por turnos sem captura
            if self.turns_without_capture >= 40:  # 20 jogadas de cada lado
                self.board.print()
                print("Empate! 20 jogadas consecutivas de cada jogador sem captura.")
                return
            
            # Avalia e mostra o estado do tabuleiro
            self._show_evaluation(new_board, current_player)
            
            # Atualiza o tabuleiro
            self.board = new_board
            
            # Verifica se o jogo terminou
            if self._check_game_over():
                break
            
            # Alterna o jogador
            current_player = Player.X if current_player == Player.O else Player.O
            
            print("-" * 30)
            time.sleep(0.5)  # Tempo para visualizar o movimento
        
        # Fim do jogo
        self._show_game_result()
    
    def _determine_search_depth(self, game_phase: GamePhase) -> int:
        """Determina a profundidade de busca com base na fase do jogo."""
        if game_phase == GamePhase.OPENING:
            return 4
        elif game_phase == GamePhase.MIDDLE:
            return 5
        else:  # ENDGAME
            return 6
    
    def _track_position(self):
        """Registra a posição atual para detectar ciclos."""
        current_hash = self.board.hash_position()
        self.position_history[current_hash] = self.position_history.get(current_hash, 0) + 1
    
    def _select_next_move(self, player: Player, game_phase: GamePhase, depth: int) -> Tuple[CheckersBoard, Move]:
        """Seleciona o próximo movimento, lidando com ciclos se necessário."""
        current_hash = self.board.hash_position()
        
        # Se a posição está se repetindo, tenta quebrar o ciclo
        if self.position_history[current_hash] > 2:
            print(f"Posição repetida {self.position_history[current_hash]} vezes!")
            
            # Reduz profundidade para aumentar variabilidade
            depth = 2
            
            # Se ainda estamos em ciclo, escolhe movimento aleatório
            if self.position_history[current_hash] > 4:
                return self._choose_random_move(player)
        
        # Escolhe movimento normal
        ai = self.ai_o if player == Player.O else self.ai_x
        return ai.choose_move(self.board, depth)
    
    def _choose_random_move(self, player: Player) -> Tuple[CheckersBoard, Move]:
        """Escolhe um movimento aleatório para quebrar ciclos."""
        move_generator = MoveGenerator(self.board)
        moves, _ = move_generator.generate_moves(player)
        
        if moves:
            print("Movimento aleatório aplicado para quebrar ciclo!")
            return random.choice(moves)
        
        # Se não houver movimentos, retorna o estado atual (fim de jogo)
        return self.board, None
    
    def _update_progress_tracking(self, move: Optional[Move]):
        """Atualiza contagem de turnos sem captura."""
        if move:
            if move.is_capture:
                self.turns_without_capture = 0
                print("Captura realizada!")
                if move.start and move.end:
                    print(f"Movimento: ({move.start.row},{move.start.col}) -> "
                          f"({move.end.row},{move.end.col})")
            else:
                self.turns_without_capture += 1
                if move.start and move.end:
                    print(f"Movimento: ({move.start.row},{move.start.col}) -> "
                          f"({move.end.row},{move.end.col})")
        else:
            self.turns_without_capture += 1
        
        print(f"Turnos sem captura: {self.turns_without_capture // 2}")  # Dividimos por 2 pois contamos por jogador
    
    def _show_evaluation(self, board: CheckersBoard, current_player: Player):
        """Mostra avaliação do tabuleiro atual."""
        evaluator = GameEvaluator(board)
        value = evaluator.evaluate()
        
        if current_player == Player.O:
            print(f"Avaliação do tabuleiro: {-value:.2f} (favorável ao 'x' se negativo)")
        else:
            print(f"Avaliação do tabuleiro: {value:.2f} (favorável ao 'x' se positivo)")
    
    def _check_game_over(self) -> bool:
        """Verifica se o jogo acabou."""
        for player in [Player.X, Player.O]:
            move_generator = MoveGenerator(self.board)
            moves, _ = move_generator.generate_moves(player)
            if not moves:
                return True
        
        return False
    
    def _show_game_result(self):
        """Mostra o resultado final do jogo."""
        self.board.print()
        x_pieces, o_pieces = self.board.count_pieces()
        print(f"Final do jogo - Peças x: {x_pieces}, Peças o: {o_pieces}")
        
        # Verifica qual jogador não tem mais movimentos
        move_generator_x = MoveGenerator(self.board)
        moves_x, _ = move_generator_x.generate_moves(Player.X)
        
        move_generator_o = MoveGenerator(self.board)
        moves_o, _ = move_generator_o.generate_moves(Player.O)
        
        if not moves_o:
            print("IA 'x' venceu!")
        elif not moves_x:
            print("IA 'o' venceu!")
        else:
            print("Limite de turnos atingido! Avaliando vencedor...")
            evaluator = GameEvaluator(self.board)
            value = evaluator.evaluate()
            
            if value > 0:
                print("IA 'x' venceu por avaliação!")
            elif value < 0:
                print("IA 'o' venceu por avaliação!")
            else:
                print("Empate!")


def main():
    """Função principal para iniciar o jogo."""
    game = CheckersGame()
    game.start_game()


if __name__ == "__main__":
    main()