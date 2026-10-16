# Walker config

Configuration of Walker's Python projects.

An application named `WALKER_API` is configured from:

- the `config.yaml` file of the directory set in `WALKERAPIDIR`, under the section of the
  environment set in `WALKER_API_ENV` (required);
- environment variables prefixed with `WALKER_API_`, which take precedence over the file. Use
  `__` to reach nested keys (e.g. `WALKER_API_ASGI__PORT`).
