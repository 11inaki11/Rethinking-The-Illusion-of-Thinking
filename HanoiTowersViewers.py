import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import numpy as np
import time

class HanoiVisualizer:
    def __init__(self, initial_state, moves):
        self.state = [peg.copy() for peg in initial_state]  # copia profunda
        self.moves = moves
        self.num_pegs = 3
        self.colors = self._generate_pastel_colors()
        self.max_disk = max(disk for peg in initial_state for disk in peg)
        if len(self.colors) < self.max_disk + 1:
            raise ValueError(f"Not enough colors for {self.max_disk} disks.")
        self._validate_initial_state()

    def _generate_pastel_colors(self):
        pastel_colors = [c for name, c in mcolors.CSS4_COLORS.items()
                         if 'light' in name.lower() or 'lavender' in name.lower() or 'misty' in name.lower()]
        if not pastel_colors:
            raise RuntimeError("No pastel colors found in mcolors.CSS4_COLORS.")
        np.random.seed(42)
        np.random.shuffle(pastel_colors)
        return pastel_colors

    def _validate_initial_state(self):
        seen_disks = set()
        for peg in self.state:
            for j in range(len(peg) - 1):
                if peg[j] < peg[j + 1]:
                    raise ValueError("Invalid initial stack: larger disk on top of smaller")
            for disk in peg:
                if disk in seen_disks:
                    raise ValueError(f"Repeated disk in initial state: {disk}")
                seen_disks.add(disk)

    def _validate_and_apply_move(self, move, step):
        disk, from_peg, to_peg = move

        if not (0 <= from_peg < self.num_pegs) or not (0 <= to_peg < self.num_pegs):
            print(f"⛔ Invalid peg index at step {step}: {move}")
            self.failed_move = step
            self.failed_disk = disk
            return False

        if not self.state[from_peg] or self.state[from_peg][-1] != disk:
            print(f"⛔ Invalid move at step {step}: disk {disk} is not on top of peg {from_peg}")
            self.failed_move = step
            self.failed_disk = disk
            return False

        if self.state[to_peg] and self.state[to_peg][-1] < disk:
            print(f"⛔ Invalid move at step {step}: cannot place disk {disk} on smaller disk {self.state[to_peg][-1]}")
            self.failed_move = step
            self.failed_disk = disk
            return False

        self.state[from_peg].pop()
        self.state[to_peg].append(disk)
        return True


    def _draw_state(self, step):
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        if not hasattr(self, 'fig') or not plt.fignum_exists(self.fig.number):
            # Crear figura solo una vez
            self.fig, self.ax = plt.subplots(figsize=(14, 5))
            plt.ion()
            self.fig.show()
            self.fig.canvas.draw()

        self.ax.clear()

        # Parámetros
        disk_count = max(len(peg) for peg in self.state)
        peg_spacing = 14 / (self.num_pegs + 1)
        peg_x_positions = [(i + 1) * peg_spacing for i in range(self.num_pegs)]
        peg_width = peg_spacing * 0.05
        available_height = 5 * 0.7
        disk_height = available_height / (disk_count + 2)
        max_disk_width = peg_spacing * 0.85
        min_disk_width = peg_spacing * 0.3
        scale_factor = (max_disk_width - min_disk_width) / max(1, self.max_disk - 1)

        # Dibujar postes
        for x in peg_x_positions:
            self.ax.add_patch(patches.Rectangle(
                (x - peg_width / 2, 0),
                peg_width,
                available_height + 2 * disk_height,
                color='dimgray'
            ))

        # Dibujar discos
        for peg_idx, peg in enumerate(self.state):
            for level, disk in enumerate(peg):
                x_center = peg_x_positions[peg_idx]
                y_bottom = level * disk_height
                disk_width = min_disk_width + (disk - 1) * scale_factor
                if hasattr(self, 'failed_disk') and disk == self.failed_disk:
                    color = 'red'
                else:
                    color = self.colors[disk % len(self.colors)]

                self.ax.add_patch(patches.Rectangle(
                    (x_center - disk_width / 2, y_bottom),
                    disk_width,
                    disk_height * 0.8,
                    color=color,
                    edgecolor='black'
                ))
                self.ax.text(
                    x_center,
                    y_bottom + disk_height * 0.25,
                    str(disk),
                    ha='center',
                    va='center',
                    fontsize=10,
                    weight='bold'
                )

        self.ax.set_xlim(0, 14)
        self.ax.set_ylim(0, available_height + 2 * disk_height)
        self.ax.axis('off')
        self.ax.set_title(f"Step {step}", fontsize=16, pad=10)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        time.sleep(0.03) 

    def animate(self):
        import matplotlib.pyplot as plt

        plt.ion()
        self._draw_state(step=0)

        try:
            for i, move in enumerate(self.moves):
                valid = self._validate_and_apply_move(move, i + 1)
                self._draw_state(step=i + 1)
                if not valid:
                    print("\nLa figura muestra el estado justo antes del error. El disco problemático está en rojo.")
                    break

            plt.ioff()
            plt.show()


        except Exception as e:
            print("\n⛔ Error en la animación:\n", e)
            print("\nLa figura permanecerá abierta para que puedas analizar el estado actual.")
            plt.ioff()
            plt.show()  # Bloqueante: mantiene la figura abierta tras el error


    @staticmethod
    def simulate_moves(initial_state, moves):
        """
        Simula una secuencia de movimientos desde un estado inicial dado.
        Devuelve la configuración final de las torres sin mostrar nada.

        Parámetros:
        - initial_state: lista de listas representando las torres.
        - moves: lista de movimientos [disk, from_peg, to_peg].

        Retorna:
        - La configuración final de las torres.
        """
        num_pegs = 3
        state = [peg.copy() for peg in initial_state]

        for i, move in enumerate(moves):
            disk, from_peg, to_peg = move

            if not (0 <= from_peg < num_pegs) or not (0 <= to_peg < num_pegs):
                raise ValueError(f"Invalid peg index in move {i + 1}: {move}")

            if not state[from_peg] or state[from_peg][-1] != disk:
                raise ValueError(f"Invalid move at step {i + 1}: disk {disk} is not on top of peg {from_peg}")

            if state[to_peg] and state[to_peg][-1] < disk:
                raise ValueError(f"Invalid move at step {i + 1}: cannot place disk {disk} on smaller disk {state[to_peg][-1]}")

            state[from_peg].pop()
            state[to_peg].append(disk)

        print("Final state after simulation:")
        print(state)
        return state




#=== EJEMPLO USO ===
# initial_state = [[8,7,6,5,4,3, 2, 1], [], []]
# moves = [[1, 0, 1], [2, 0, 2], [1, 1, 2], [3, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [4, 0, 2], [1, 1, 2], [2, 1, 0], [1, 2, 0], [3, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2], [5, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [3, 2, 0], [1, 1, 2], [2, 1, 0], [1, 2, 0], [4, 2, 1], [1, 0, 1], [2, 0, 2], [1, 1, 2], [3, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [6, 0, 2], [1, 1, 2], [2, 1, 0], [1, 2, 0], [3, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2], [4, 1, 0], [1, 2, 0], [2, 2, 1], [1, 0, 1], [3, 2, 0], [1, 1, 2], [2, 1, 0], [1, 2, 0], [5, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2], [3, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [4, 0, 2], [1, 1, 2], [2, 1, 0], [1, 2, 0], [3, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2], [7, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [3, 2, 0], [1, 1, 2], [2, 1, 0], [1, 2, 0], [4, 2, 1], [1, 0, 1], [2, 0, 2], [1, 1, 2], [3, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [5, 2, 0], [1, 1, 2], [2, 1, 0], [1, 2, 0], [3, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2], [4, 1, 0], [1, 2, 0], [2, 2, 1], [1, 0, 1], [3, 2, 0], [1, 1, 2], [2, 1, 0], [1, 2, 0], [6, 2, 1], [1, 0, 1], [2, 0, 2], [1, 1, 2], [3, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [4, 0, 2], [1, 1, 2], [2, 1, 0], [1, 2, 0], [3, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2], [5, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [3, 2, 0], [1, 1, 2], [2, 1, 0], [1, 2, 0], [4, 2, 1], [1, 0, 1], [2, 0, 2], [1, 1, 2], [3, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [8, 0, 2], [1, 1, 2], [2, 1, 0], [1, 2, 0], [3, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2], [4, 1, 0], [1, 2, 0], [2, 2, 1], [1, 0, 1], [3, 2, 0], [1, 1, 2], [2, 1, 0], [1, 2, 0], [5, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2], [3, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [4, 0, 2], [1, 1, 2], [2, 1, 0], [1, 2, 0], [3, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2], [6, 1, 0], [1, 2, 0], [2, 2, 1], [1, 0, 1], [3, 2, 0], [1, 1, 2], [2, 1, 0], [1, 2, 0], [4, 2, 1], [1, 0, 1], [2, 0, 2], [1, 1, 2], [3, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [5, 2, 0], [1, 1, 2], [2, 1, 0], [1, 2, 0], [3, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2], [4, 1, 0], [1, 2, 0], [2, 2, 1], [1, 0, 1], [3, 2, 0], [1, 1, 2], [2, 1, 0], [1, 2, 0], [7, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2], [3, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [4, 0, 2], [1, 1, 2], [2, 1, 0], [1, 2, 0], [3, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2], [5, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [3, 2, 0], [1, 1, 2], [2, 1, 0], [1, 2, 0], [4, 2, 1], [1, 0, 1], [2, 0, 2], [1, 1, 2], [3, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [6, 0, 2], [1, 1, 2], [2, 1, 0], [1, 2, 0], [3, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2], [4, 1, 0], [1, 2, 0], [2, 2, 1], [1, 0, 1], [3, 2, 0], [1, 1, 2], [2, 1, 0], [1, 2, 0], [5, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2], [3, 0, 1], [1, 2, 0], [2, 2, 1], [1, 0, 1], [4, 0, 2], [1, 1, 2], [2, 1, 0], [1, 2, 0], [3, 1, 2], [1, 0, 1], [2, 0, 2], [1, 1, 2]]

# viz = HanoiVisualizer(initial_state, moves)
# viz.animate()
# final_state = HanoiVisualizer.simulate_moves(initial_state, moves)