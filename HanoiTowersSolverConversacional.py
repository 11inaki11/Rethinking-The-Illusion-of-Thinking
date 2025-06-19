import os
import google.generativeai as genai
import time
import re, json
from HanoiTowersViewers import HanoiVisualizer


# Configura la API con tu clave
genai.configure(api_key=os.getenv("GEMINI_API_KEY_2"))

# Inicializa los modelos generativos con instrucciones de sistema
model_a = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction="""
        You are a helpful assistant. Solve this puzzle for me.
        There are three pegs and n disks of different sizes stacked on the first peg. The disks are numbered from 1 (smallest) to n (largest). Disk moves in this puzzle should follow:
        1. Only one disk can be moved at a time.
        2. Each move consists of taking the upper disk from one stack and placing it on top of another stack.
        3. A larger disk may not be placed on top of a smaller disk.

        The goal is to move the entire stack to the third peg.

        Example:
        With 3 disks numbered 1 (smallest), 2, and 3 (largest), the initial state is [[3, 2, 1], [], []], and a solution might be: moves = [[1, 0, 2], [2, 0, 1], [1, 2, 1], [3, 0, 2], [1, 1, 0], [2, 1, 2], [1, 0, 2]]
        This means: Move disk 1 from peg 0 to peg 2, then move disk 2 from peg 0 to peg 1, and so on.
        Requirements:
        • When exploring potential solutions in your thinking process, always include the corresponding complete list of moves.
        • The positions are 0-indexed (the leftmost peg is 0).
        • Ensure your final answer includes the complete list of moves in the format: moves = [[disk id, from peg, to peg], ...]

        Since the puzzle is complex when the number of disks N is very large, you will collaborate with another agent to solve it. Every time is your turn to interact, you will receive the following information:
        • The current configuration of the problem k, since it may be in the initial state or in an intermediate state.
        • The desired number of moves p. This parameter indicates how many moves I want you to make to bring us closer to the solution. This is because when the number of disks N is very large, solving the entire problem becomes very complex. Therefore, I don't want you to provide the complete solution, but rather the next p moves that move us toward the goal.


        Your response should be just a vector of moves, without any additional text or explanations. Example response:
        moves = [[1, 0, 2], [2, 0, 1], [1, 2, 1], [3, 0, 2], [1, 1, 0], [2, 1, 2]]
        """
)

model_b = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction="""
        You are a helpful assistant. Solve this puzzle for me.
        There are three pegs and n disks of different sizes stacked on the first peg. The disks are numbered from 1 (smallest) to n (largest). Disk moves in this puzzle should follow:
        1. Only one disk can be moved at a time.
        2. Each move consists of taking the upper disk from one stack and placing it on top of another stack.
        3. A larger disk may not be placed on top of a smaller disk.

        The goal is to move the entire stack to the third peg.

        Example:
        With 3 disks numbered 1 (smallest), 2, and 3 (largest), the initial state is [[3, 2, 1], [], []], and a solution might be: moves = [[1, 0, 2], [2, 0, 1], [1, 2, 1], [3, 0, 2], [1, 1, 0], [2, 1, 2], [1, 0, 2]]
        This means: Move disk 1 from peg 0 to peg 2, then move disk 2 from peg 0 to peg 1, and so on.
        Requirements:
        • When exploring potential solutions in your thinking process, always include the corresponding complete list of moves.
        • The positions are 0-indexed (the leftmost peg is 0).
        • Ensure your final answer includes the complete list of moves in the format: moves = [[disk id, from peg, to peg], ...]

        Since the puzzle is complex when the number of disks N is very large, you will collaborate with another agent to solve it. Every time is your turn to interact, you will receive the following information:
        • The current configuration of the problem k, since it may be in the initial state or in an intermediate state.
        • The desired number of moves p. This parameter indicates how many moves I want you to make to bring us closer to the solution. This is because when the number of disks N is very large, solving the entire problem becomes very complex. Therefore, I don't want you to provide the complete solution, but rather the next p moves that move us toward the goal.


        Your response should be just a vector of moves, without any additional text or explanations. Example response:
        moves = [[1, 0, 2], [2, 0, 1], [1, 2, 1], [3, 0, 2], [1, 1, 0], [2, 1, 2]]
        """
)

# Inicia las sesiones de chat para ambos modelos
chat_a = model_a.start_chat(history=[])
chat_b = model_b.start_chat(history=[])

# Mensaje inicial para comenzar la conversación
mensaje_actual = """
I have a puzzle with $5$ disks of different sizes with Initial configuration:
    • Peg 0: $5$ (bottom), ... 2, 1 (top)
    • Peg 1: (empty)
    • Peg 2: (empty)

    Goal configuration:
    • Peg 0: (empty)
    • Peg 1: (empty)
    • Peg 2: $10$ (bottom), ... 2, 1 (top)

    Rules:
    • Only one disk can be moved at a time.
    • Only the top disk from any stack can be moved.
    • A larger disk may not be placed on top of a smaller disk. Find the sequence of moves to transform the initial configuration into the goal configuration.
    • Everytime is your turn to interact, you should provide the next $p=20$ moves that move us toward the goal.
    • If we reach the goal, you should inform me that the goal has been reached.
"""

# Variable para alternar entre los modelos
turno = 0
moves = []  # Lista para almacenar los movimientos
initial_state = [[5, 4, 3, 2, 1], [], []]  
actual_state= initial_state

try:
    while True:
        time.sleep(5)
        if turno % 2 == 0:
            respuesta = chat_a.send_message(mensaje_actual)
        else:
            respuesta = chat_b.send_message(mensaje_actual)

        texto = respuesta.text.strip()
        print(f"\n 🤖Bot {'A' if turno%2==0 else 'B'}: {texto}")

        # 1. extrae el vector
        m = re.search(r"\[\[.*\]\]", texto, re.DOTALL)
        if m:
            moves.extend(json.loads(m.group(0)))
            print(f"✅ Updated moves variable with {len(moves)} entries.")
        else:
            moves = []
            print("⚠️ No se encontró vector moves en la respuesta.")

        # 2. actualiza mensaje_actual para el siguiente turno
        mensaje_actual = texto
        print(f"Lista de movimientos actualizada: {moves}")
        actual_state = HanoiVisualizer.simulate_moves(initial_state, moves)

        turno += 1
except KeyboardInterrupt:
    print("\nConversación interrumpida por el usuario.")

