import os
import google.generativeai as genai, types
import time
import re, json
from HanoiTowersViewers import HanoiVisualizer
from HanoiTowersViewers import HanoiVisualizer
import ast


# Configura la API con tu clave
genai.configure(api_key=os.getenv("GEMINI_API_KEY_HANOI"))

# Inicializa los modelos generativos con instrucciones de sistema
model_a = genai.GenerativeModel(
    model_name="gemini-2.5-pro-preview-06-05",
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
    model_name="gemini-2.5-pro-preview-06-05",
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

"""
This function builds a prompt for the Tower of Hanoi puzzle, including the current configuration of pegs and the goal configuration.
It formats the pegs and the goal in a readable way, ensuring that the disks are described with their positions and sizes.
The prompt also includes the rules of the game and the number of moves
"""
def build_hanoi_prompt(N: int, k: list[list[int]], p: int) -> str:
    def format_peg(peg_index: int, peg: list[int]) -> str:
        if not peg:
            return f"    • Peg {peg_index}: (empty)"
        elif len(peg) == 1:
            return f"    • Peg {peg_index}: {peg[0]} (top)"
        else:
            elements = ",".join(str(d) for d in peg[:-1])
            return f"    • Peg {peg_index}: {peg[0]} (bottom)," + ",".join(str(d) for d in peg[1:-1]) + f",{peg[-1]} (top)"

    peg_descriptions = "\n".join(format_peg(i, peg) for i, peg in enumerate(k))
    goal_list = list(range(N, 0, -1))
    goal_str = f"    • Peg 0: (empty)\n    • Peg 1: (empty)\n    • Peg 2: $" + f"{goal_list[0]}$ (bottom), ..." + f" {goal_list[-1]} (top)"

    prompt = f"""
    I have a puzzle with ${N}$ disks of different sizes with configuration k={k} and I want to make ${p}$ moves to bring us closer to the solution:
{peg_descriptions}

    Goal configuration k=[[],[],{goal_list}]:
{goal_str}

    Rules:
    • Only one disk can be moved at a time.
    • Only the top disk from any stack can be moved.
    • A larger disk may not be placed on top of a smaller disk. Find the sequence of moves to transform the initial configuration into the goal configuration.
    """
    return prompt


######FUNCTION FOR ASKING THE AGENT#####
"""
This function interacts with the Gemini AI model to solve the Tower of Hanoi puzzle.
It sends a prompt with the current configuration and the number of moves to make, and processes the response.
The response includes the thought process and the final answer, which is a list of moves to be made.
"""

def ask_hanoi_agent(contents: str) -> str:
    # Configura el cliente
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY_HANOI"))

    # Solicita respuesta del modelo
    response = client.models.generate_content(
        model="gemini-2.5-pro-preview-06-05",
        config=types.GenerateContentConfig(
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

        The current configuration of the problem k, since it may be in the initial state or in an intermediate state.
        • The current configuration of the problem k, since it may be in the initial state or in an intermediate state.
        • The desired number of moves p. This parameter indicates how many moves I want you to make to bring us closer to the solution. This is because when the number of disks N is very large, solving the entire problem becomes very complex. Therefore, I don't want you to provide the complete solution, but rather the next p moves that move us toward the goal.

        Your response should be just a vector of moves, without any additional text or explanations.
        """,
            thinking_config=types.ThinkingConfig(include_thoughts=True)
        ),
        contents=contents
    )

    # Procesamiento de respuesta
    final_answer = ""
    for part in response.candidates[0].content.parts:
        if not part.text:
            continue
        if part.thought:
            print("Thought summary:")
            print(part.text)
            print()
        else:
            print("Answer:")
            print(part.text)
            print()
            final_answer += part.text  # Almacena respuesta útil

    return final_answer

#####FUNCTION FOR EXTRACTING MOVES VECTOR#####
"""This function extracts the moves vector from the response text of the LLM.
It uses regular expressions to find the first occurrence of a list formatted as [[...]] and converts it to a Python list.
"""

def extract_moves_vector(response_text: str) -> list[list[int]]:
    """
    Extrae el bloque de movimientos tipo [[1, 2, 3], ...] desde una salida ruidosa del LLM.
    Solo mantiene números, comas y corchetes dentro del primer [ y el último ].
    
    Args:
        response_text (str): Texto completo devuelto por el modelo.

    Returns:
        list[list[int]]: Lista limpia de movimientos como objetos Python.
    """
    start = response_text.find('[')
    end = response_text.rfind(']')

    if start == -1 or end == -1 or end <= start:
        raise ValueError("❌ No se encontró un bloque válido delimitado por [ y ].")

    # Extraer contenido bruto
    raw_block = response_text[start:end+1]

    # Limpiar: solo permitir dígitos, comas, corchetes y espacios mínimos
    cleaned_block = re.sub(r"[^\d\[\],]", "", raw_block)

    try:
        moves = ast.literal_eval(cleaned_block)
    except Exception as e:
        raise ValueError(f"❌ Error al convertir el bloque limpio a lista: {e}")
    
    # Validar estructura
    if not (isinstance(moves, list) and all(isinstance(m, list) and len(m) == 3 for m in moves)):
        raise ValueError("❌ El contenido extraído no es una lista válida de movimientos.")

    return moves


########################################### Example usage ###################################################
# Parámetros iniciales
N = 7
p = 100
k_actual = [list(range(N, 0, -1)), [], []]
k_objetivo = [[], [], list(range(N, 0, -1))]
total_moves = []
turn = 0  # 0: chat_a, 1: chat_b

# Enviar mensaje inicial al primer agente usando el prompt completo
prompt_inicial = build_hanoi_prompt(N=N, k=k_actual, p=p)
chat_a.send_message(prompt_inicial)

# Bucle de interacción por turnos
while True:
    print(f"\n🔁 Turno del modelo {'A' if turn == 0 else 'B'}")

    # Construir mensaje corto con el estado actual
    msg_turno = f"""
The current configuration is: {k_actual}
Please provide the next {p} moves to bring us closer to the solution.
Just answer with the list of moves.
"""

    # Enviar mensaje al modelo correspondiente
    # Enviar mensaje al modelo correspondiente
    try:
        response = (chat_a if turn == 0 else chat_b).send_message(msg_turno)
        print(f"\n🧠 Respuesta cruda del modelo {'A' if turn == 0 else 'B'}:\n{response.text}\n")
    except Exception as e:
        print(f"❌ Error al invocar al modelo: {e}")
        break


    # Extraer movimientos del texto
    try:
        moves = extract_moves_vector(response.text)
    except Exception as e:
        print(f"❌ Error al extraer movimientos: {e}")
        break

    # Aplicar movimientos y actualizar estado
    try:
        k_actual = HanoiVisualizer.simulate_moves(k_actual, moves)
    except Exception as e:
        print(f"⚠️ Movimiento inválido detectado: {e}")
        break

    # Acumular movimientos
    total_moves.extend(moves)
    print(f"✔️ Movimientos aplicados. Estado actual: {k_actual}")

    # Verificar si se ha alcanzado el objetivo
    if k_actual == k_objetivo:
        print("🎯 ¡Objetivo alcanzado!")
        break

    # Cambiar turno
    turn = 1 - turn

# Visualización final
print(f"\n✅ Total de movimientos realizados: {len(total_moves)}")
viz = HanoiVisualizer([[i for i in range(N, 0, -1)], [], []], total_moves)
viz.animate()
