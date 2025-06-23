import os
import click
import subprocess
from pathlib import Path

@click.group()
def cli():
    pass

@cli.command()
def ls():
    tmuxp_dir = Path(os.path.expanduser('~'), ".config/tmuxp")
    cmd = fr"ls {tmuxp_dir} | sed 's/\.yaml$//' | fzf"
    selection = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
    if selection:
        tmuxp_file = tmuxp_dir / f"{selection}.yaml"
        subprocess.run(["tmuxp", "load", "-y", str(tmuxp_file)])

@cli.command()
@click.argument('name', type=click.STRING)
@click.argument('location_dir', default=os.getcwd(), type=click.Path(exists=True))
@click.option('--venv', is_flag=True, help='Activate a virtual environment named .venv in the workspace directory.')
def create(name, location_dir, venv):
    curdir = location_dir # if location_dir else os.getcwd()

    if not os.path.exists(curdir):
        raise click.ClickException(f"The directory '{curdir}' does not exist.")

    workspace_path = Path(curdir) / name
    if not workspace_path.exists():
        workspace_path.mkdir()

    user_home = os.path.expanduser("~")
    tmuxp_config_path = Path(user_home) / ".config/tmuxp" / f"{name}.yaml"

    tmuxp_content = f"""start_directory: {curdir}/{name}
session_name: {name}
windows:
  - window_name: editor
    focus: true
  - window_name: terminal
"""

    if venv:
        venv_activate_command = ".venv/bin/activate"
        tmuxp_content = f"""start_directory: {curdir}/{name}
session_name: {name}
shell_command_before:
- >
  [[ -e '{venv_activate_command}' ]] && source {venv_activate_command}
- reset
windows:
  - window_name: editor
    focus: true
  - window_name: terminal
"""

    with open(tmuxp_config_path, "w") as f:
        f.write(tmuxp_content)

    print(f"Workspace '{name}' created at: {curdir}")
    if venv:
        print(f"Virtual environment activation (source .venv/bin/activate) will be attempted on workspace load.")


@cli.command()
@click.argument('name', type=click.STRING)
def remove(name):
    """
    Remove an existing workspace.
    Args:
        name (str): The name of the workspace to be removed.
    """
    user_home = os.path.expanduser("~")
    config_file_path = f"{user_home}/.config/tmuxp/{name}.yaml"
    if Path(config_file_path).exists():
        os.remove(config_file_path)
        print(f"Worwskspace '{name}' removed.")
    else:
        print(f"Workspace '{name}' does not exist.")

if __name__ == "__main__":
    cli()
