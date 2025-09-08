import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

class CheckerJumpingVisualizer:
    @staticmethod
    def simulate_moves(initial_board: list, moves: list) -> list:
        """
        Simula la secuencia de movimientos en el tablero unidimensional.
        Retorna la lista de estados del tablero después de cada movimiento.
        """
        board = initial_board.copy()
        states = [board.copy()]
        
        for move in moves:
            color, from_pos, to_pos = move
            if board[from_pos] != color:
                raise ValueError(f"❌ Movimiento inválido: {color} no está en posición {from_pos}")
            if board[to_pos] != '_':
                raise ValueError(f"❌ Posición destino {to_pos} no está vacía")
            
            # Verificar movimiento
            if abs(from_pos - to_pos) == 1:
                # Slide
                pass
            elif abs(from_pos - to_pos) == 2:
                # Jump
                mid_pos = (from_pos + to_pos) // 2
                opposite = 'B' if color == 'R' else 'R'
                if board[mid_pos] != opposite:
                    raise ValueError(f"❌ Salto inválido: no hay {opposite} en posición {mid_pos}")
            else:
                raise ValueError(f"❌ Movimiento inválido: distancia {abs(from_pos - to_pos)} no permitida")
            
            # Ejecutar
            board[from_pos] = '_'
            board[to_pos] = color
            states.append(board.copy())
        
        return states

    @staticmethod
    def animate(initial_board: list, moves: list):
        """
        Crea una animación del tablero evolucionando con los movimientos.
        """
        states = CheckerJumpingVisualizer.simulate_moves(initial_board, moves)
        
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.set_xlim(-0.5, len(initial_board) - 0.5)
        ax.set_ylim(-0.5, 0.5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Colores
        color_map = {'R': 'red', '_': 'white', 'B': 'blue'}
        
        def update(frame):
            ax.clear()
            ax.set_xlim(-0.5, len(initial_board) - 0.5)
            ax.set_ylim(-0.5, 0.5)
            ax.set_aspect('equal')
            ax.axis('off')
            
            board = states[frame]
            for i, piece in enumerate(board):
                color = color_map.get(piece, 'black')
                ax.add_patch(plt.Rectangle((i-0.4, -0.4), 0.8, 0.8, color=color, ec='black'))
                if piece != '_':
                    ax.text(i, 0, piece, ha='center', va='center', fontsize=20, color='white')
            
            ax.set_title(f"Paso {frame}: {' '.join(board)}")
        
        ani = animation.FuncAnimation(fig, update, frames=len(states), interval=1000, repeat=False)
        plt.show()

    @staticmethod
    def print_board(board: list):
        """
        Imprime el tablero en texto.
        """
        print(' '.join(board))

# Ejemplo de uso
if __name__ == "__main__":
    N = 2
    initial_board = ['R'] * N + ['_'] + ['B'] * N
    # Ejemplo de movimientos (ajusta según necesidad)
    moves = [['R', 1, 2], ['B', 3, 1], ['B', 4, 3], ['R', 2, 4], ['R', 0, 2], ['B', 1, 0], ['B', 3, 1], ['R', 2, 3]]  # Ejemplo simple
    
    print("Tablero inicial:")
    CheckerJumpingVisualizer.print_board(initial_board)
    
    try:
        states = CheckerJumpingVisualizer.simulate_moves(initial_board, moves)
        print("\nEstados después de movimientos:")
        for i, state in enumerate(states):
            print(f"Paso {i}: {' '.join(state)}")
        
        # Animar
        CheckerJumpingVisualizer.animate(initial_board, moves)
    except ValueError as e:
        print(f"Error en simulación: {e}")
