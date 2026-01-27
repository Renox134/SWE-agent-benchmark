from typing import Dict, Any
from datasets import load_dataset
from pprint import pprint
import requests
import json


base_prompt: str = (
    "In the following, I will provide you with an entry from a dataset "
    "(SWE-bench verified) that is used to benchmark LLMs (such as claude, GPT, etc.). "
    "This entry is a dict, that has information on which repo the problem to solve is from, "
    "the base commit ID, what the actual patch looked like, a 'test_patch' and some other information. "
    "One crucial information is the 'problem_statement', as it's supposed to describe the problem, "
    "such that an LLM can produce the same, or a similar patch. However, I think the descriptions "
    "might be improvable. Here is your task: Given the information of the dataset entry, try to infer "
    "or refine a problem description that would naturally lead to that solution."
)

dataset_url: str = "SWE-bench/SWE-bench_Verified"
open_router_api_key = ""  # put your key here
entry_index: int = 292

model_keys = [
    "openrouter/openai/gpt-4o",
    "openrouter/anthropic/claude-sonnet-4",
    "openrouter/deepseek/deepseek-v3.2",
    "openrouter/qwen/qwen3-coder",
    "openrouter/meta-llama/llama-3-70b-instruct",
    "openrouter/mistralai/mistral-small-3.2-24b-instruct",
]


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def query_openrouter(prompt: str, model: str) -> str:
    headers = {
        "Authorization": f"Bearer {open_router_api_key}",
        "Content-Type": "application/json",
        # Optional but recommended by OpenRouter:
        "HTTP-Referer": "http://localhost",
        "X-Title": "swe-bench-prompt-refiner",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        data=json.dumps(payload),
        timeout=120,
    )

    response.raise_for_status()
    data = response.json()

    return data["choices"][0]["message"]["content"]


def main() -> None:
    dataset = load_dataset(dataset_url, split="test")
    tmp: Dict[str, Any] = dataset[entry_index]
    tmp.pop("problem_statement", None)

    final_prompt = base_prompt + "\n\nEntry:\n" + str(tmp)

    model = model_keys[1]
    print(f"\nUsing model: {model}\n")

    response = query_openrouter(final_prompt, model)

    print("=== MODEL RESPONSE ===")
    print(response)


if __name__ == "__main__":
    main()
