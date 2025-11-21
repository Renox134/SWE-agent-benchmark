import subprocess
import shutil
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

        task_folder = tasks_base / str(instance_id)
        task_folder.mkdir(exist_ok=True)

        # check if task is already solved
        patch_path = __has_patch(task_folder)
        if patch_path is None:
            # run swe agent
            cmd = [
                "sweagent", "run",
                f"--agent.model.name={agent_model}",
                "--agent.model.per_instance_cost_limit=2.00",
                f"--env.repo.github_url={repo}",
                f"--problem_statement.text={problem_text}",
                f"--output_dir={str(task_folder)}"
            ]
            subprocess.run(cmd)

        # modify patch for swebench
        patch_path = __has_patch(task_folder)
        if patch_path is not None:
            with open(patch_path, "r") as f:
                patch_content = f.read()

                patch_dict = {
                    "instance_id": instance_id,
                    "model_name_or_path": agent_model.replace('/', '_'),
                    "model_patch": patch_content
                }

                patches.append(patch_dict)

    # dump patches into a jsonl file
    pred_dir = str(tasks_base) + f"/predictions_{dataset_url.replace('/', '_')}.jsonl"
    with open(pred_dir, "w") as o:
        for patch in patches:
            o.write(json.dumps(patch) + "\n")

    # verify with swebench
    cmd = [
        sys.executable, "-m", "swebench.harness.run_evaluation",
        f"--dataset_name={dataset_url}",
        f"--predictions_path={pred_dir}",
        "--max_workers=1",
        f"--run_id={dataset_url.replace('/', '_')}"
    ]
    subprocess.run(cmd)

    # move result file into correct task folder
    result_file = f"{agent_model.replace('/', '_')}.{dataset_url.replace('/', '_')}.json"
    shutil.move(result_file, str(tasks_base))

def __has_patch(task_folder) -> str | None:
    folders = os.listdir(str(task_folder))
    if len(folders) > 0:
        skip = os.listdir(str(task_folder))[0]
        patch_path = str(task_folder) + f"/{skip}/{skip}.patch"

        if os.path.exists(patch_path):
            return patch_path
    return None

if __name__ == "__main__":
    main()
