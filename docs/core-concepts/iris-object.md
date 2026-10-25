# Iris Object

`Iris(version="1.0.0")` declares the application version and registers dashboards and publication environments. The example sets `html_base_directory`, registers `hmg` and `prod` with `add_publish_environment(name=..., publisher=...)`, registers `example_dashboard` with `add_dashboard(...)`, associates a `DashboardDataSource` with a Cube and a PayloadFormatter, specifies `example/index.html`, and calls `run()`. See [app.py](../../project-example/src/app.py).

The HTML file may reference separate CSS, JavaScript and other assets from a sibling `assets/` directory. See [HTML Runtime](html-runtime.md) and [Standalone Builder](standalone-builder.md).

`app.config` is the application's shared runtime configuration. Registered publishers resolve dynamic destinations only at publication time, after registered setup steps have populated that same object.

Publishers belong to the Iris application rather than individual dashboards. The desktop app selects an environment for each publication. The dashboard's `publish` operation produces [published artifacts](publish-artifact.md) in the selected environment. The declared application version is recorded in publication metadata; publishing data again under that version still creates a distinct publication event.
