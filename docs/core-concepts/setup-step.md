# Setup step

Iris accepts a `SetupStep` implementation through `add_setup_step(...)`. The desktop app collects any `SetupField` values and passes them in a `config` mapping to `configure(config)`. The implementation validates the environment, adds values needed by later operations, and returns the resulting configuration.

The [example implementation](../../project-example/src/setup_steps/example_setup_step.py) checks `drive_path` and verifies Databricks authentication. It returns a mapping containing the validated path and a `generate_token` callable. A remote Cube calls `config["generate_token"]()` when it needs a token in `get_data(partitions, config)` or `list_partitions(config)`. A publisher receives the configuration when publishing. This removes the need to share a mutable dictionary between objects created before the user fills in fields.

The returned configuration is runtime state in the desktop process. Credentials and tokens must not be logged, written to the SQLite data cache, passed to dashboard HTML, or included in published artifacts. The Databricks CLI handles token refresh when the callable requests a token. If interactive login is required again, the failed operation must trigger the setup flow rather than exposing the token error to the HTML.
