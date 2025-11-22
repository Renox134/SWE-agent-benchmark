from typing import Dict, List

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import random

PATH_TO_FOLDER = "./tasks"
FILE_SUFFIX = ".SWE-bench_SWE-bench_Verified.json"

def main():
    models = {}
    for folder in os.listdir(PATH_TO_FOLDER):
        r = file_to_dict(PATH_TO_FOLDER + "/" + folder + "/" + folder + FILE_SUFFIX)
        visualize_single_performance(r, folder)
        model_dict = {}
        for task in r["resolved_ids"]:
            model_dict[task] = "resolved"
        for task in r["unresolved_ids"]:
            model_dict[task] = "unresolved"
        for task in r["error_ids"]:
            model_dict[task] = "error"
        for task in r["empty_patch_ids"]:
            model_dict[task] = "empty patch"
        for task in r["incomplete_ids"]:
            if task in r["submitted_ids"]:
                model_dict[task] = "incomplete"

        models[folder] = model_dict

    combined_chart("all")

def get_task_dict() -> List[str]:
    from datasets import load_dataset
    retorno = {}
    dataset_url: str = "SWE-bench/SWE-bench_Verified"
    dataset = load_dataset(dataset_url, split="test")
    ids = [d["instance_id"] for d in dataset]
    for i, id in enumerate(ids):
        retorno[i] = id
    return retorno

def file_to_dict(path: str) -> Dict[str, int | List[str]]:
    try:
        with open(path, "r") as file:
            results = json.load(file)
        return results
    except:
        print("An error occoured while trying to find: ", path)

def visualize_single_performance(performance_dict: Dict[str, int | List[str]], model_name: str):
    # performance_dict = {
    #     "total_instances": 500,
    #     "submitted_instances": 100,
    #     "completed_instances": 90,
    #     "resolved_instances": 50,
    #     "unresolved_instances": 20,
    #     "empty_patch_instances": 4,
    #     "error_instances": 16
    # }

    keys = ["resolved_instances", "unresolved_instances", "empty_patch_instances", "error_instances"]
    submitted = performance_dict["submitted_instances"]
    completed = performance_dict["completed_instances"]

    completion_rate_chart = go.Pie(
        labels=["Completed", "Not Completed"],
        values=[completed, submitted - completed],
        name="Completion Rate"
    )

    performance_rate = go.Pie(
        labels=["Resolved", "Unresoolved", "Empty Patch", "Error"],
        values=[performance_dict[key] for key in keys],
        name="Performance Chart"
    )

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=("Completion Rate", "Performance Chart")
    )

    fig.add_trace(completion_rate_chart, row=1, col=1)
    fig.add_trace(performance_rate, row=1, col=2)

    fig.update_layout(title_text=model_name, showlegend=True)

    fig.show()

def combined_chart(task_type: str):
    task_type_dict = {
        "astropy": (0, 21),
        "django": (22, 252),
        "matplotlib": (253, 286),
        "mwaskom": (287, 288),
        "pallets": (289, 289),
        "psf": (290, 297),
        "pydata": (298, 319),
        "pylint": (320, 329),
        "pytest": (330, 348),
        "scikit-learn": (349, 380),
        "sphinx-doc": (381, 424),
        "sympy": (425, 499)
    }
    task_id_dict = {}
    with open("task_ids.json", "r") as file:
        task_id_dict = json.load(file)

    range_tuple = (task_type_dict[task_type][0], task_type_dict[task_type][1]) if task_type != "all" else (0, len(task_id_dict.keys()) - 1)
    tasks = [task_id_dict[str(i)] for i in range(range_tuple[0], range_tuple[1] + 1)]
    outcomes = [
        "resolved",
        "incomplete",
        "error",
        "empty patch",
        "unresolved",
    ]
    agents = {}

    for i in range (3):
        agent_dict = {}
        for t in tasks:
            rand = random.randint(0, 99)
            o = "unresolved"
            if (rand < 50):
                o = "resolved"
            elif (rand < 55):
                o = "incomplete"
            elif (rand < 75):
                o = "error"
            elif (rand < 90):
                o = "empty patch"

            agent_dict[t] = o
        agents["Model " + str(i + 1)] = agent_dict

    counts = {outcome: {task: [] for task in tasks} for outcome in outcomes}

    for actor_name, results in agents.items():
        for task, value in results.items():
            if value in outcomes:
                counts[value][task].append(actor_name)

    fig = make_subplots(
        rows=1, cols=5,
        subplot_titles=outcomes,
        shared_yaxes=True,
        horizontal_spacing=0.05
    )

    actor_colors = {
        "Model 1": "steelblue",
        "Model 2": "indianred",
        "Model 3": "seagreen"
    }

    for col, outcome in enumerate(outcomes, start=1):
        for actor_name in agents.keys():
            values = [
                1 if actor_name in counts[outcome][task] else 0
                for task in tasks
            ]

            fig.add_trace(
                go.Bar(
                    x=values,
                    y=tasks,
                    name=actor_name,
                    orientation="h",
                    marker_color=actor_colors[actor_name],
                    showlegend=(col == 1),
                ),
                row=1, col=col
            )

        fig.update_xaxes(title_text="Count", row=1, col=col)

    fig.update_layout(
        title="Actor Performance by Outcome (Stacked per Actor)",
        barmode="stack"
    )

    fig.show()

if __name__ == "__main__":
    main()