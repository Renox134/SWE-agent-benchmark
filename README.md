# SWE-agent-benchmark
A lightweight command-line utility for **benchmarking Large Language Models (LLMs)** using **SWE-agent** and **SWE-bench** together — with optional visualization support.

This project simplifies the full evaluation workflow:

1. Run SWE-agent to generate patches
2. Evaluate patches using SWE-bench
3. Visualize model performance

All from a **single CLI interface**.

---

# Supported Models

Short names can be used in the CLI:

| Alias           | Model                            |
| --------------- | -------------------------------- |
| `gpt`           | `gpt-4o`                         |
| `claude-sonnet` | `claude-sonnet-4`                |
| `deepseek`      | `deepseek-v3.2`                  |
| `qwen3`         | `qwen3-coder`                    |
| `llama`         | `llama-3-70b-instruct`           |
| `mistral`       | `mistral-small-3.2-24b-instruct` |

All models are accessed via **OpenRouter**. Other models could also be used, provided that the respective code is edited in the project.

---

# Dataset

The tool currently targets:

```
SWE-bench/SWE-bench_Verified
```

(Test split)

---

# Installation

## 1. Clone repository

```bash
git clone https://github.com/Renox134/SWE-agent-benchmark.git
cd SWE-agent-benchmark
```

## 2. Initial Build
Once the project is installed, everything must be build. For that, there are both a batch script for windows and a shell script for unix.
The scripts automatically:
- pull the latest verison of SWE-agent
- create a virtual python environment in the SWE-agent submodule
- install SWE-agent (in editable mode)
- create a virtual python environment in this projects working directory
- install the project dependencies into the virtual environment 
 
## 3. Adding the API key
To run SWE-agent properly, you have to **add your OpenRouter API key** to the agent. To do that, the key can either be exported into an evironment variable or entered into a **.env** file at the root of the agent directory. If using the file, the following lines should do the trick:
```bash
OPENROUTER_API_KEY=<your-key>
LITELLM_API_BASE=https://openrouter.ai/api/v1
```
For more information, see the [official SWE-agent documentation](https://swe-agent.com/latest/installation/keys/).


---

# Usage

Main entry point:

```bash
python src/main.py [OPTIONS]
```

## Modes

The **mode** determines which stages run:

| Mode              | Runs                      |
| ----------------- | ------------------------- |
| `agent`           | SWE-agent only            |
| `bench`           | SWE-bench evaluation only |
| `vis`             | Visualization only        |
| `agent_bench`     | Agent → Bench             |
| `agent_vis`       | Agent → Visualization     |
| `bench_vis`       | Bench → Visualization     |
| `agent_bench_vis` | Full pipeline             |

Default: `agent`

---

## Arguments

### `--mode` / `-m`

Select workflow stage(s).

Example:

```bash
python src/main.py -m agent_bench_vis
```

---

### `--slice` / `-s`

Choose SWE-bench test instances.

* **Single instance:**

```bash
-s 13
```

* **Range (batch mode):**

```bash
-s 0 100
```

Default:

```
0–500
```

---

### `--num_workers` / `-nw`

Parallel workers for agent + bench.

* Range: **1–50**
* Default: **1**

Example:

```bash
-nw 8
```

---

### `--agent` / `-a`

Select LLM alias.

Default:

```
qwen3
```

Example:

```bash
-a gpt
```

---

# Example Workflows

## Run full benchmark on first 50 tasks with GPT‑4o and 8 workers

```bash
python src/main.py -m agent_bench_vis -s 0 50 -a gpt -nw 8
```

---

## Run SWE-agent on a single SWE-bench test instance

```bash
python src/main.py -m agent -s 13 -a qwen3
```

---

## Only visualize existing results

```bash
python src/main.py -m vis
```

---

# Output Structure

Each model gets its own folder:

```
tasks/<model_name>/
```

Contains:

* Generated patches
* Prediction `.jsonl`
* SWE-bench evaluation results

---

# Visualization

The built‑in **Visualizer** reads benchmark outputs and produces:

* One performance chart for each model where results exist
* A joint performance chart displaying the performance of every model on each of the 500 tests

(Implementation located in `visualizer.py`.)

---

# Development Notes
We had trouble getting SWE-bench to work on Windows, so running the bench on a unix-based system is highly recommended, unless you know what you're doing.

---

# Limitations / TODO

* Visualization is not yet customizable
* Hard‑coded model list
* Fixed dataset target (Verified split only)
* Minimal error handling for subprocess failures

---

# License

MIT License

---

# Acknowledgements

* **SWE-agent**
* **SWE-bench**
* **OpenRouter**

For enabling reproducible evaluation of LLM software engineering ability.
