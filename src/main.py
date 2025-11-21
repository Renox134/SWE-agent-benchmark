import subprocess
import shutil
import json
import sys
import os
from datasets import load_dataset
from pathlib import Path

num_workers = 5

dataset_url: str = "SWE-bench/SWE-bench_Verified"
agent_model: str = "openrouter/openai/gpt-4o"
tasks_base = Path(f"tasks/{agent_model.replace('/', '_')}")
tasks_base.mkdir(parents=True, exist_ok=True)
pred_dir = str(tasks_base) + f"/predictions_{dataset_url.replace('/', '_')}.jsonl"

def main() -> None:
    run_agent_batch()
    run_bench()

def run_agent_single() -> None:

    def __has_patch(task_folder) -> str | None:
        folders = os.listdir(str(task_folder))
        if len(folders) > 0:
            skip = os.listdir(str(task_folder))[0]
            patch_path = str(task_folder) + f"/{skip}/{skip}.patch"

            if os.path.exists(patch_path):
                return patch_path
        return None

    dataset = load_dataset(dataset_url, split="test")
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
            with open(patch_path, "r", newline="\n") as f:
                patch_content = f.read()

                patch_dict = {
                    "instance_id": instance_id,
                    "model_name_or_path": agent_model.replace('/', '_'),
                    "model_patch": patch_content
                }

                patches.append(patch_dict)

    # dump patches into a jsonl file
    with open(pred_dir, "w", newline="\n") as o:
        for patch in patches:
            o.write(json.dumps(patch) + "\n")

def run_agent_batch() -> None:
    # run swe agent
    cmd = [
        "sweagent", "run-batch",
        f"--agent.model.name={agent_model}",
        "--instances.type=swe_bench",
        "--instances.subset=verified",
        "--instances.split=test",
        "--instances.slice=:10",
        "--agent.model.per_instance_cost_limit=2.00",
        f"--output_dir={str(tasks_base)}",
        f"--num_workers={num_workers}"
    ]
    subprocess.run(cmd)

    with open(str(tasks_base) + "/preds.json", "r", newline="\n") as f, open(pred_dir, "a", newline="\n") as o:
        preds = json.load(f)

        for key, value in preds.items():
            if value["model_name_or_path"] == agent_model.replace('/', '_'):
                o.write(json.dumps({"model_name_or_path": agent_model.replace('/', '_'),
                                    "instance_id": value["instance_id"],
                                    "model_patch": value["model_patch"]}) + "\n")

def run_bench() -> None:
    # verify with swebench
    cmd = [
        sys.executable, "-m", "swebench.harness.run_evaluation",
        f"--dataset_name={dataset_url}",
        f"--predictions_path={pred_dir}",
        f"--max_workers={num_workers}",
        f"--run_id={dataset_url.replace('/', '_')}"
    ]
    subprocess.run(cmd)

    # move result file into correct task folder
    result_file = f"{agent_model.replace('/', '_')}.{dataset_url.replace('/', '_')}.json"
    shutil.move(result_file, str(tasks_base))


if __name__ == "__main__":
    main()
