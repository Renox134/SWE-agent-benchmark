import subprocess
import sys
from datasets import load_dataset
from pathlib import Path

dataset_url: str = "SWE-bench/SWE-bench_Verified"
agent_model: str = "openrouter/openai/gpt-4o"

def main() -> None:

    dataset = load_dataset(dataset_url, split="test")

    tasks_base = Path(f"tasks/{agent_model.replace('/', '_')}")
    tasks_base.mkdir(exist_ok=True)

    for idx, task in enumerate(dataset):
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

        cmd = [
            sys.executable, "-m", "swebench.harness.run_evaluation",
            f"--dataset_name={dataset_url}",
            f"--predictions_path={str(task_folder)}",
            "--max_workers=1",
            f"--run_id=task{idx}"
        ]

        subprocess.run(cmd)

if __name__ == "__main__":
    main()
