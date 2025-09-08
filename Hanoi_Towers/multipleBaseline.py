from google import genai
from google.genai import types
import os
import json
from HanoiTowersViewers import HanoiVisualizer
import re
import ast
import csv
from datetime import datetime
import time

# Configura la API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY_HANOI"))

#####FUNCTION FOR EXTRACTING MOVES VECTOR#####
def extract_moves_vector(response_text: str) -> list[list[int]]:
    start = response_text.find('[')
    end = response_text.rfind(']')

    if start == -1 or end == -1 or end <= start:
        raise ValueError("❌ No se encontró un bloque válido delimitado por [ y ].")

    raw_block = response_text[start:end+1]
    cleaned_block = re.sub(r"[^\d\[\],]", "", raw_block)

    try:
        moves = ast.literal_eval(cleaned_block)
    except Exception as e:
        raise ValueError(f"❌ Error al convertir el bloque limpio a lista: {e}")
    
    if not (isinstance(moves, list) and all(isinstance(m, list) and len(m) == 3 and all(isinstance(x, int) for x in m) for m in moves)):
        raise ValueError("❌ El contenido extraído no es una lista válida de movimientos.")

    return moves

#####FUNCTION FOR BUILDING PROMPT#####
def build_prompt(N: int) -> str:
    return f"""
    I have a puzzle with {N}$ disks of different sizes with Initial configuration:
    • Peg 0: ${N}$ (bottom), ... 2, 1 (top)
    • Peg 1: (empty)
    • Peg 2: (empty)

    Goal configuration:
    • Peg 0: (empty)
    • Peg 1: (empty)
    • Peg 2: ${N}$ (bottom), ... 2, 1 (top)

    Rules:
    • Only one disk can be moved at a time.
    • Only the top disk from any stack can be moved.
    • A larger disk may not be placed on top of a smaller disk. Find the sequence of moves to transform the initial configuration into the goal configuration.
    """

#####FUNCTION FOR RUNNING A SINGLE TEST#####
def run_single_test(N: int):
    system_instruction = f"""
    You are a helpful assistant. Solve this puzzle for me.
    There are three pegs and {N} disks of different sizes stacked on the first peg. The disks are numbered from 1 (smallest) to {N} (largest). Disk moves in this puzzle should follow:
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

    Your response should be just a vector of moves, without any additional text or explanations.
    """

    contents = build_prompt(N)

    response = client.models.generate_content(
        model="gemini-2.5-pro-preview-06-05",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(include_thoughts=True)
        ),
        contents=contents
    )

    final_answer = ""
    for part in response.candidates[0].content.parts:
        if not part.text:
            continue
        if part.thought:
            print(f"N={N} - Thought summary: {part.text}")
        else:
            final_answer += part.text

    # Validación
    k_init = [list(range(N, 0, -1)), [], []]
    goal_config = [[], [], list(range(N, 0, -1))]
    success = False

    try:
        moves = extract_moves_vector(final_answer)
        final_config = HanoiVisualizer.simulate_moves(k_init, moves)
        if final_config == goal_config:
            success = True
    except ValueError as e:
        print(f"N={N} - Error: {e}")

    # Tokens
    usage = response.usage_metadata
    prompt_tokens = usage.prompt_token_count
    output_tokens = usage.candidates_token_count
    total_tokens = usage.total_token_count

    return {
        'N': N,
        'success': success,
        'prompt_tokens': prompt_tokens,
        'output_tokens': output_tokens,
        'total_tokens': total_tokens
    }

#####MAIN EXECUTION#####
os.makedirs("results", exist_ok=True)
csv_path = os.path.join("results", "baseline_Hanoi_Towers.csv")

headers = ['Name', 'N', 'tokens_prompt', 'tokens_candidates', 'tokens_total', 'results']

file_exists = os.path.exists(csv_path)
with open(csv_path, mode='a', newline='') as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow(headers)
        file.flush()  # Forzar escritura inmediata

    for N in range(4, 11):  # N=3 to 10
        print(f"\n🚀 Ejecutando 10 pruebas para N={N}")
        for i in range(10):
            print(f"  Prueba {i+1}/10 para N={N}")
            try:
                result = run_single_test(N)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                experiment_name = f"N{result['N']}_{timestamp}_test{i+1}"
                results_value = 'ok' if result['success'] else 'fail'
                row = [
                    experiment_name,
                    result['N'],
                    result['prompt_tokens'],
                    result['output_tokens'],
                    result['total_tokens'],
                    results_value
                ]
                writer.writerow(row)
                file.flush()  # Forzar escritura inmediata después de cada fila
                print(f"    ✅ Guardado: {experiment_name} - Resultado: {results_value}")
            except Exception as e:
                print(f"    ❌ Error en prueba {i+1} para N={N}: {e}")
                # Opcional: guardar fila con error
                row = [f"N{N}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_test{i+1}_error", N, 0, 0, 0, 'error']
                writer.writerow(row)
                file.flush()
            time.sleep(1)  # Pequeña pausa para evitar rate limits

print(f"\n✅ Todas las pruebas completadas. Resultados guardados en: {csv_path}")
