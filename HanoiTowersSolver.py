from google import genai
from google.genai import types
import os
import json # Sigue siendo útil para inspeccionar la respuesta completa si es necesario

# Configura la API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY_HANOI")) # Asegúrate de que la variable de entorno esté configurada

response = client.models.generate_content(
    model="gemini-2.5-pro-preview-06-05", # O "gemini-2.5-flash-preview-06-05" para el modelo Flash
    config=types.GenerateContentConfig(
        system_instruction=f"""
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

        Your response should be just a vector of moves, without any additional text or explanations.
    """,
        # ¡Esta es la forma correcta de solicitar las trazas de pensamiento!
        thinking_config=types.ThinkingConfig(
            include_thoughts=True
        )
    ),
    contents=f"""
    I have a puzzle with $10$ disks of different sizes with Initial configuration:
    • Peg 0: $10$ (bottom), ... 2, 1 (top)
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
    """
)

# Ahora, itera sobre las partes de la respuesta para imprimir el razonamiento y la respuesta.
for part in response.candidates[0].content.parts:
    if not part.text: # Salta partes vacías
        continue
    if part.thought:
        print("Thought summary:")
        print(part.text) # El texto asociado con el pensamiento
        print()
    else:
        print("Answer:")
        print(part.text) # La parte de la respuesta final
        print()