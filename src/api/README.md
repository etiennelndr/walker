# Walker API

An API for autonomous movements of bots in unknown locations.

## Requirements

Running the API requires an NVIDIA GPU with a driver compatible with CUDA 13.

## Usage

The API is configured from the `config.yaml` file of the directory set in `WALKERAPIDIR`, under
the section of the environment set in `WALKER_API_ENV`. Both variables are required:

```sh
export WALKERAPIDIR=config
export WALKER_API_ENV=dev
```

Any value of the configuration can be overridden with an environment variable prefixed with
`WALKER_API_`, using `__` to reach nested keys (e.g. `WALKER_API_ASGI__PORT=8080`).

Then, from this directory, run one of the following commands:

| Command                     | Description                                             |
|-----------------------------|---------------------------------------------------------|
| `uv run walker-api serve`   | Serves the generation of walker movements (`/walks`).   |
| `uv run walker-api collect` | Serves the collection of training records (`/records`). |

Collected training records are appended to the JSON Lines file set in the `training.path`
configuration value, one record per line.
