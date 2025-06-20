# Hanoi-Towers-LLM

A **Tower of Hanoi solver and visualizer powered by Large Language Models (LLMs)**.  
`HanoiTowersSolverSteps.py` prompts an LLM (tested with Google Gemini 2) to generate the optimal sequence of moves for *n* disks, breaks the solution into smaller chunks to avoid token limits, validates the output, and—optionally—plays the moves with a simple animated viewer.

> **Research inspiration**  
> This project is motivated by Apple’s paper *“The Illusion of Thinking”*, which argues that Large Reasoning Models (LRMs) fail on large-disk Hanoi instances due to fundamental reasoning flaws.  
> Here we **probe an alternative hypothesis**: that apparent failures stem primarily from **context-window/token limitations rather than true reasoning deficits**. Our “por partes” chunking strategy lets us disentangle the two factors empirically.


## Installation

```bash
git clone https://github.com/11inaki11/Hanoi-Towers-LLM.git
cd Hanoi-Towers-LLM
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # google-generativeai, rich, tqdm, matplotlib, etc.
```

Set your LLM key:

```bash
export GEMINI_API_KEY_HANOI="YOUR_KEY"
# or OPENAI_API_KEY if you adapt the provider
```

(Optional) Install ffmpeg if you want to capture the animation as a video/GIF.

---

## Quick Start

```bash
python HanoiTowersSolverSteps.py --disks 5
```

| Flag            | Default         | Description                       |
|-----------------|----------------|-----------------------------------|
| `--disks`, `-n` | 3              | Number of disks (≥ 3)             |
| `--model`       | gemini-2.0-pro | LLM model name                    |
| `--temperature` | 0.2            | Sampling temperature              |
| `--visual`      | true           | Disable with `--visual false`     |
| `--timeout`     | 30             | Seconds to wait for LLM           |

---

## Example

```text
$ python HanoiTowersSolverSteps.py -n 4

🧠 Prompting LLM for 4-disk solution… (chunk 1/1)
✅ Received 15 moves, validating…
🎬 Starting visualizer … FPS: 4
Move  1/15: peg 0 ➜ peg 2
...
🏁 Finished in 00:00:07.41
Result saved to runs/run_2025-06-20_14-22-05.json
```

---

## Project Layout

```
Hanoi-Towers-LLM/
├── HanoiTowersSolverSteps.py   # main CLI script
├── HanoiTowersViewer.py            # lightweight matplotlib animator
├── requirements.txt
├── runs/                           # auto-generated logs
└── docs/
    └── demo.gif
```

---

## Adapting to other LLM providers

The core prompt & parse logic is isolated in `llm_interface()`.  
To switch from Gemini to OpenAI or any local model:

- Replace the import (`google.generativeai` ➜ `openai` or other).
- Implement a minimal wrapper that returns `.text` with the move list.

---

## Roadmap

- ✅ JSON logging
- ⏳ Unit tests for the