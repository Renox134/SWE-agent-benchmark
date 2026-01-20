from typing import Dict, List

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import random
import re

PATH_TO_FOLDER = "./tasks"
FILE_SUFFIX = ".SWE-bench_SWE-bench_Verified.json"

def main():
    models = {}
    for folder in os.listdir(PATH_TO_FOLDER):
        files = os.listdir(PATH_TO_FOLDER + "/" + folder)

        # check if prediction file exists, skip folder otherwise
        has_prediction_file = False
        regex = r".*\.SWE-bench_SWE-bench_Verified\.json$"
        for filename in files:
            if re.search(regex, filename):
                has_prediction_file = True
                break
        if not has_prediction_file:
            continue
        
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

    combined_chart("all", models)
    line_chart_resolution("all", models)
    line_chart_binary_resolution("all", models)

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

def combined_chart(task_type: str, models: Dict[str, Dict[str, str]]):
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

    range_tuple = ()
    if task_type == "all":
        range_tuple = (0, len(task_id_dict.keys()) - 1)
    else:
        range_tuple = (task_type_dict[task_type][0], task_type_dict[task_type][1])
    
    tasks = [task_id_dict[str(i)] for i in range(range_tuple[0], range_tuple[1] + 1)]
    outcomes = [
        "resolved",
        "incomplete",
        "error",
        "empty patch",
        "unresolved",
    ]

    counts = {outcome: {task: [] for task in tasks} for outcome in outcomes}

    for model_name, results in models.items():
        for task, value in results.items():
            if value in outcomes:
                counts[value][task].append(model_name)

    fig = make_subplots(
        rows=1, cols=5,
        subplot_titles=outcomes,
        shared_yaxes=True,
        horizontal_spacing=0.05
    )

    color_list = ["steelblue", "indianred", "seagreen", "olive", "greenyellow", "violet", "gold"]
    color_dict = {}
    for i, key in enumerate(models.keys()):
        color_dict[key] = color_list[i % len(color_list)]

    for col, outcome in enumerate(outcomes, start=1):
        for model_name in models.keys():
            values = [
                1 if model_name in counts[outcome][task] else 0
                for task in tasks
            ]

            fig.add_trace(
                go.Bar(
                    x=values,
                    y=tasks,
                    name=model_name,
                    orientation="h",
                    marker_color=color_dict[model_name],
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

def line_chart_resolution(task_type: str, models: Dict[str, Dict[str, str]]):
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

    with open("task_ids.json", "r") as file:
        task_id_dict = json.load(file)

    if task_type == "all":
        range_tuple = (0, len(task_id_dict.keys()) - 1)
    else:
        range_tuple = task_type_dict[task_type]

    tasks = [task_id_dict[str(i)] for i in range(range_tuple[0], range_tuple[1] + 1)]

    fig = go.Figure()

    color_list = ["steelblue", "indianred", "seagreen", "olive", "greenyellow", "violet", "gold"]
    color_dict = {model: color_list[i % len(color_list)]
                  for i, model in enumerate(models.keys())}

    for model_name, results in models.items():
        y_values = []
        for task in tasks:
            outcome = results.get(task, None)
            to_assign = 0
            match outcome:
                case "resolved": to_assign = 4
                case "unresolved": to_assign = 3
                case "error": to_assign = 2
                case "empty patch": to_assign = 1
                case "incomplete": to_assign = 0

            y_values.append(to_assign)

        fig.add_trace(
            go.Scatter(
                x=tasks,
                y=y_values,
                mode="lines+markers",
                name=model_name,
                line=dict(color=color_dict[model_name])
            )
        )

    fig.update_layout(
        title="Resolution Line Graph (4 = resolved, 3 = unresolved, 2 = error, 1 = empty patch, 0 = incomplete)",
        xaxis_title="Tasks",
        yaxis_title="(Explained in title)",
        yaxis=dict(tickmode="array", tickvals=[0, 1, 2, 3, 4]),
        height=600
    )

    fig.show()

def line_chart_binary_resolution(task_type: str, models: Dict[str, Dict[str, str]]):
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

    with open("task_ids.json", "r") as file:
        task_id_dict = json.load(file)

    # Determine task range
    if task_type == "all":
        range_tuple = (0, len(task_id_dict.keys()) - 1)
    else:
        range_tuple = task_type_dict[task_type]

    tasks = [task_id_dict[str(i)] for i in range(range_tuple[0], range_tuple[1] + 1)]

    # Create figure
    fig = go.Figure()

    # Color palette (same as your bar chart)
    color_list = ["steelblue", "indianred", "seagreen", "olive", "greenyellow", "violet", "gold"]
    color_dict = {model: color_list[i % len(color_list)]
                  for i, model in enumerate(models.keys())}

    # Add one line per model
    for model_name, results in models.items():
        y_values = []
        for task in tasks:
            outcome = results.get(task, None)
            y_values.append(1 if outcome == "resolved" else 0)

        fig.add_trace(
            go.Scatter(
                x=tasks,
                y=y_values,
                mode="lines+markers",
                name=model_name,
                line=dict(color=color_dict[model_name])
            )
        )

    fig.update_layout(
        title="Binary Resolution Line Graph (1 = resolved, 0 = else)",
        xaxis_title="Tasks",
        yaxis_title="Resolved (1) / Not Resolved (0)",
        yaxis=dict(tickmode="array", tickvals=[0, 1]),
        height=600
    )

    fig.show()

def __get_example_model_dict():
    task_id_dict = {}
    with open("task_ids.json", "r") as file:
        task_id_dict = json.load(file)

    range_tuple = range_tuple = (0, len(task_id_dict.keys()) - 1)

    tasks = [task_id_dict[str(i)] for i in range(range_tuple[0], range_tuple[1] + 1)]
    models = {}

    for i in range (3):
        model_dict = {}
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

            model_dict[t] = o
        models["Model " + str(i + 1)] = model_dict

    return models

if __name__ == "__main__":
    main()