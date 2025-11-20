import subprocess
import os
import shlex
from pathlib import Path


def set_env_keys():
    """
    Sets the api keys to the values specified in the internal dictionary
    """
    api_key_dict = {
        "ANTHROPIC_API_KEY": "<your key>",
        "OPENAI_API_KEY": "<your key>"
    }
    with open("agent/.env", "w") as file:
        for key, val in api_key_dict.items():
            file.write(key + "=" + val + "\n")
        file.close()


def get_venv_python():
    """
    Find the python venv directory
    """
    venv_dir = Path("agent/venv")
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    else:
        return venv_dir / "bin" / "python"


def test_agent():
    venv_python = get_venv_python()
    subprocess.run([str(venv_python), "-m", "sweagent", "--help"], cwd="agent")


def run_agent(command: str, flags):
    venv_python = get_venv_python()

    flag_list = shlex.split(flags)

    subprocess.run(
        [str(venv_python), "-m", "sweagent", command, *flag_list],
        cwd="agent",
        check=True  # raise an error if sweagent fails
    )


if __name__ == "__main__":
    # set_env_keys()
    # test_agent()

    flags = (
        "--agent.model.name=openrouter/openai/gpt-4o "
        "--agent.model.per_instance_cost_limit=2.00 "
        "--env.repo.github_url=https://github.com/SWE-agent/test-repo "
        "--problem_statement.github_url=https://github.com/SWE-agent/test-repo/issues/1"
    )
    run_agent("run", flags)
