import subprocess
import json
import sys
import os
from datasets import load_dataset
from pathlib import Path

dataset_url: str = "SWE-bench/SWE-bench_Verified"
agent_model: str = "openrouter/openai/gpt-4o"

def main() -> None:

    dataset = load_dataset(dataset_url, split="test")

    tasks_base = Path(f"tasks/{agent_model.replace('/', '_')}")
    tasks_base.mkdir(parents=True, exist_ok=True)

    patches = []

    for idx, task in enumerate(dataset):
        instance_id = task["instance_id"]
        repo = f"https://github.com/{task['repo']}"
        problem_text = task["problem_statement"]

        task_folder = tasks_base / f"task{idx}"
        task_folder.mkdir(exist_ok=True)

        cmd = [
            "sweagent", "run",
            f"--agent.model.name={agent_model}",
            "--agent.model.per_instance_cost_limit=2.00",
            f"--env.repo.github_url={repo}",
            f"--problem_statement.text={problem_text}",
            f"--output_dir={str(task_folder)}"
        ]
 
        subprocess.run(cmd)

        folders = os.listdir(str(task_folder))
        if len(folders) > 0:
            skip = os.listdir(str(task_folder))[0]
            patch_path = str(task_folder) + f"/{skip}/{skip}.patch"

            if os.path.exists(patch_path):
                with open(patch_path, "r") as f:
                    patch_content = f.read()

                    patch_dict = {
                        "instance_id": instance_id,
                        "model_name_or_path": agent_model,
                        "model_patch": patch_content
                    }

                    patches.append(patch_dict)

    with open(str(tasks_base) + f"/predictions.jsonl", "w") as o:
        for patch in patches:
            o.write(json.dumps(patch) + "\n")

    cmd = [
        sys.executable, "-m", "swebench.harness.run_evaluation",
        f"--dataset_name={dataset_url}",
        f"--predictions_path={str(tasks_base) + f"/predictions.jsonl"}",
        "--max_workers=1",
        f"--run_id=task{idx}"
    ]

    subprocess.run(cmd)

if __name__ == "__main__":
    main()
