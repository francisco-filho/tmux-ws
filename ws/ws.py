import os
import click
import subprocess
from pathlib import Path

@click.group()
def cli():
    pass

@cli.command()
def list():
    tmuxp_dir = Path(os.path.expanduser('~'), ".config/tmuxp")
    cmd = f"ls {tmuxp_dir} | sed 's/\.yaml$//' | fzf"
    selection = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
    if selection:
        tmuxp_file = tmuxp_dir / f"{selection}.yaml"
        subprocess.run(["tmuxp", "load", "-y", str(tmuxp_file)])

@cli.command()
@click.argument('name', type=click.STRING)
@click.argument('location_dir', type=click.Path(exists=True))
def create(name, location_dir):
    if not os.path.exists(location_dir):
        raise click.ClickException(f"The directory '{location_dir}' does not exist.")

    workspace_path = Path(location_dir) / name
    if not workspace_path.exists():
        workspace_path.mkdir()

    user_home = os.path.expanduser("~")
    with open(f"{user_home}/.config/tmuxp/" + name + ".yaml", "w") as f:
        f.write(f"""start_directory: {location_dir}/{name}
session_name: {name}
windows:
  - window_name: terminal
  - window_name: editor
""")

    print(f"Workspace '{name}' created at: {location_dir}")

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
