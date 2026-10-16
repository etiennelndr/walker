# Walker

An autonomous agent in unfamiliar environments.

A walker is simulated in Unity. It perceives its surroundings by casting rays, and learns to move
from the states it goes through.

## Projects

| Project                      | Description                                                            |
|------------------------------|------------------------------------------------------------------------|
| [`src/config`](src/config)   | Library to configure the Python projects.                              |
| [`src/api`](src/api)         | API which collects the states of a walker and generates its movements. |
| [`src/trainer`](src/trainer) | Training of the models which generate the movements of a walker.       |
| [`src/ui`](src/ui)           | Unity project in which a walker is simulated.                          |

The Python projects (`config`, `api` and `trainer`) are the members of a single
[uv](https://docs.astral.sh/uv/) workspace.

## Requirements

- [uv](https://docs.astral.sh/uv/), which installs the required version of Python (at least 3.14).
- An NVIDIA GPU with a driver compatible with CUDA 13.
- [Unity](https://unity.com/) (at least 6000.6.2f1), for the simulation.

## Installation

Install the Python projects and their dependencies from the root of the repository:

```sh
uv sync --all-packages
```

Then install the git hooks, which lint, type-check and test the code on each commit:

```sh
uv run pre-commit install
```

## Usage

### API

The API is configured from [`src/api/config/config.yaml`](src/api/config/config.yaml). From the
`src/api` directory, set the directory of this file and the environment to use, then run one of
the commands of the API:

```sh
export WALKERAPIDIR=config
export WALKER_API_ENV=dev

# Serve the generation of walker movements
uv run walker-api serve
# Or serve the collection of training states
uv run walker-api collect
```

See the [README of the API](src/api/README.md) for more details.

### Trainer

The trainer is not implemented yet.

### Simulation

Open the `src/ui/walker-ui` directory with Unity, load the `Assets/scene.unity` scene and enter
the Play mode.

With the `Training` behaviour, the walker moves between the target points of the scene and sends
its states to the API at the configured server URL (`http://127.0.0.1:8000` by default). Start the
collection of training states (`uv run walker-api collect`) before entering the Play mode. The
walker stops as soon as a state can't be sent.

The `Patrolling` behaviour is not implemented yet.

## Development

Run the following commands from the root of the repository:

| Command                                   | Description                                  |
|-------------------------------------------|----------------------------------------------|
| `uv run ruff check`                       | Lints the Python projects.                   |
| `uv run ruff format`                      | Formats the Python projects.                 |
| `uv run mypy`                             | Type-checks the Python projects.             |
| `uv run --directory src/<project> pytest` | Runs the tests of a Python project.          |
| `uv run pre-commit run --all-files`       | Runs all the checks above, as a commit does. |

The version of the Python projects is computed from the git tags of the repository.
