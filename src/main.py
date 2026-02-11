import subprocess
import shutil
import json
import sys
import os
from datasets import load_dataset
from pathlib import Path
from argparse import ArgumentParser, RawTextHelpFormatter
from typing import Tuple
import re

from visualizer import Visualizer


model_keys = ["openrouter/openai/gpt-4o",
              "openrouter/anthropic/claude-sonnet-4",
              "openrouter/deepseek/deepseek-v3.2",
              "openrouter/qwen/qwen3-coder",
              "openrouter/meta-llama/llama-3-70b-instruct",
              "openrouter/mistralai/mistral-small-3.2-24b-instruct"]

model_names = {
    "gpt": 0,
    "claude-sonnet": 1,
    "deepseek": 2,
    "qwen3": 3,
    "llama": 4,
    "mistral": 5
}

dataset_dict = {
    0: "SWE-bench/SWE-bench",
    1: "SWE-bench/SWE-bench_Lite",
    2: "SWE-bench/SWE-bench_Verified",
    3: "SWE-bench/SWE-bench_Multimodal",
    4: "SWE-bench/SWE-bench_Multimodal",
    5: "SWE-bench/SWE-bench_Multilingual"
}

split_dict = {
    0: "",
    1: "",
    2: "test",
    3: "test",
    4: "dev",
    5: "test"
}

# dataset_url: str = "SWE-bench/SWE-bench_Verified"

def build_arg_parser() -> ArgumentParser:
    """
    Builds and returns the argument parser for the command line tool.
    """
    parser = ArgumentParser(
        description="This is a command line tool that helps launching SWE-agent and SWE-bench",
        formatter_class=RawTextHelpFormatter
    )

    # mode argument
    parser.add_argument(
        "-m", "--mode",
        default="agent",
        help="The mode that specifies which part of the program is launched. Allowed inputs are:\n"\
        "'agent'\n'bench'\n'vis'\n'agent_bench'\n'agent_vis'\n'bench_vis'\n'agent_bench_vis'"
        )
    # slice argument
    parser.add_argument(
        "-s", "--slice",
        default=(0, 500),
        nargs="+",
        help="The slice of the instances that will be run. Defaults to the entire dataset.\n"
        "Allowed inputs are either two numbers, which would set the range for batch mode "
        "(e.g., --s 0 100) "
        "or one number (e.g., --s 13) for testing one particular instance."
    )
    # num_workers
    parser.add_argument(
        "-nw", "--num_workers",
        default=1,
        help="The number of workers used by SWE-agent and SWE-bench. Allowed range is 1-50"
    )
    # agent
    parser.add_argument(
        "-a", "--agent",
        default="qwen3",
        help="The LLM used by SWE-agent. Allowed inputs are:\n" \
        "'gpt'\n'claude-sonnet'\n'deepseek'\n'llama'\n'qwen3'\n'mistral'."
    )
    # dataset
    parser.add_argument(
        "-d", "--dataset",
        default=2,
        help="An index that specifies which dataset will be used. The index mapping looks like this:\n" \
        "0: SWE-bench/SWE-bench\n1: SWE-bench/SWE-bench_Lite\n2: SWE-bench/SWE-bench_Verified (split=test)\n" \
        "3: SWE-bench/SWE-bench_Multimodal (split=test)\n4: SWE-bench/SWE-bench_Multimodal (split=dev)\n" \
        "5: SWE-bench/SWE-bench_Multilingual (split=test)"

    )

    return parser

def validate_args(mode: str, num_workers: int, test_slice: int | Tuple[int],
                  agent_model: str, dataset_idx: int) -> bool:
    legal_mode = False
    legal_number_of_workers = False
    legal_test_slice = False
    legal_model = False
    legal_dataset_idx = False

    # check mode
    mode_pattern = r"^(agent)?_?(bench)?_?(vis)?$"
    legal_mode = re.match(mode_pattern, mode)
    if not legal_mode:
        print("The provided mode couldn't be recognized. For more information, type '--help'")

    # check number of workers
    legal_number_of_workers = num_workers <= 50 and num_workers > 0
    if not legal_number_of_workers:
        print("Illegal number of workers. Must be between 1 and 50.")

    # check test slice
    if isinstance(test_slice, int):
        legal_test_slice = test_slice >= 0 and test_slice <= 500
    elif isinstance(test_slice, tuple):
        legal_test_slice = len(test_slice) == 2 and test_slice[0] >= 0 and test_slice[1] <= 500 and test_slice[0] <= test_slice[1]
    if not legal_test_slice:
        print("Illegal test slice. Must be either one number between 0 and 500 or two numbers " \
        "between 0 and 500 (with the first being smaller than the second)")

    # check model
    legal_model = agent_model in model_names.keys()
    if not legal_model:
        print("Illegal model name. Supported model names are: 'gpt', 'claude-sonnet', 'deepseek', 'llama', 'qwen3', 'mistral'")

    # check dataset idx
    legal_dataset_idx = dataset_idx in list(range(0, 6))
    if not legal_dataset_idx:
        print("The provided dataset index isn't supported.")

    return legal_mode and legal_number_of_workers and legal_test_slice and legal_model and legal_dataset_idx

def run_agent_single(agent_model: str, tasks_base: str, pred_dir: str, task_idx: int) -> None:

    def __has_patch(task_folder) -> str | None:
        folders = os.listdir(str(task_folder))
        if len(folders) > 0:
            skip = os.listdir(str(task_folder))[0]
            patch_path = str(task_folder) + f"/{skip}/{skip}.patch"

            if os.path.exists(patch_path):
                return patch_path
        return None

    dataset = load_dataset("SWE-bench/SWE-bench_Verified", split="test")

    task = dataset[task_idx]

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


    # dump patches into a jsonl file
    with open(pred_dir, "w", newline="\n") as o:
        o.write(json.dumps(patch_dict) + "\n")

def run_agent_batch(agent_model: str, tasks_base: str, num_workers: int,
                    pred_dir: str, slice: Tuple[int, int], subset: str, split: str) -> None:
    # run swe agent
    cmd = [
        "sweagent", "run-batch",
        f"--agent.model.name={agent_model}",
        "--instances.type=swe_bench",
        "--agent.model.per_instance_cost_limit=2.00",
        f"--instances.slice={':'.join(map(str, slice))}",
        f"--output_dir={str(tasks_base)}",
        f"--num_workers={num_workers}"
    ]
    if subset != "":
        cmd.append(f"--instances.subset={subset}")
    if split != "":
        cmd.append(f"--instances.split={split}")
    subprocess.run(cmd)

    with open(str(tasks_base) + "/preds.json", "r", newline="\n") as f, open(pred_dir, "a", newline="\n") as o:
        preds = json.load(f)

        for key, value in preds.items():
            if value["model_name_or_path"] == agent_model.replace('/', '_'):
                o.write(json.dumps({"model_name_or_path": agent_model.replace('/', '_'),
                                    "instance_id": value["instance_id"],
                                    "model_patch": value["model_patch"]}) + "\n")

def run_bench(agent_model: str, tasks_base: str, num_workers: int, pred_dir: str, dataset_url: str) -> None:
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
    result_file = Path(f"{agent_model.replace('/', '_')}.{dataset_url.replace('/', '_')}.json")
    destination = tasks_base / result_file.name

    if destination.exists():
        destination.unlink()

    shutil.move(str(result_file), str(tasks_base))

def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    mode: str = str(args.mode)
    num_workers: int = int(args.num_workers)
    test_slice: int | Tuple[int, int] = int(args.slice[0]) if len(args.slice) == 1 else (int(args.slice[0]), int(args.slice[1]))
    agent_model: str = str(args.agent)
    dataset_idx: int = int(args.dataset)

    # check the provided arguments
    if not validate_args(mode, num_workers, test_slice, agent_model, dataset_idx):
        return
    dataset_url: str = dataset_dict[dataset_idx]
    dataset_subset: str = dataset_url.split("_")[1].lower()
    split: str = split_dict[dataset_idx]
    agent_model = model_keys[model_names[agent_model]]

    tasks_base = Path(f"tasks/{agent_model.replace('/', '_')}")
    tasks_base.mkdir(parents=True, exist_ok=True)
    pred_dir = str(tasks_base) + f"/predictions_{dataset_url.replace('/', '_')}.jsonl"

    if "agent" in mode:
        if isinstance(test_slice, int):
            run_agent_single(agent_model, tasks_base, pred_dir, test_slice)
        elif isinstance(test_slice, tuple):
            run_agent_batch(agent_model, tasks_base, num_workers,
                            pred_dir, test_slice, dataset_subset, split)

    if "bench" in mode:
        run_bench(agent_model, tasks_base, num_workers, pred_dir, dataset_url)

    if "vis" in mode:
        Visualizer().visualize()

if __name__ == "__main__":
    main()
