from typing import Dict, List

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import re

PATH_TO_FOLDER = "./tasks"
FILE_SUFFIX = ".SWE-bench_SWE-bench_Verified.json"

class Visualizer():
    @staticmethod
    def visualize():
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
            
            r = Visualizer.file_to_dict(PATH_TO_FOLDER + "/" + folder + "/" + folder + FILE_SUFFIX)
            Visualizer.visualize_single_performance(r, folder)
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

        Visualizer.combined_chart("all", models)

    @staticmethod
    def file_to_dict(path: str) -> Dict[str, int | List[str]]:
        try:
            with open(path, "r") as file:
                results = json.load(file)
            return results
        except:
            print("An error occoured while trying to find: ", path)

    @staticmethod
    def visualize_single_performance(performance_dict: Dict[str, int | List[str]], model_name: str):
        keys = ["resolved_instances", "unresolved_instances", "error_instances"]
        submitted = performance_dict["submitted_instances"]
        completed = performance_dict["completed_instances"]

        completion_rate_chart = go.Pie(
            labels=["Completed", "Not Completed"],
            values=[completed, submitted - completed],
            name="Completion Rate"
        )

        performance_rate = go.Pie(
            labels=["Resolved", "Unresoolved", "Error"],
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

    @staticmethod
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
