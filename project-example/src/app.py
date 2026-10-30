
from pathlib import Path

from iris import DashboardDataSource, DirectoryPublisher, Iris, SetupField

from src.cubes import ExampleCube
from src.payload_formatters import ExamplePayloadFormatter
from src.setup_steps import ExampleSetupStep

__all__ = ["app"]


app = Iris(version="1.0.0")
app.config.html_base_directory = "./src/dashboards"

app.add_setup_step(
    message="Configuring Databricks and Google Drive...",
    implementation=ExampleSetupStep(profile="picpay-principal"),
    fields= \
    [
        SetupField(
            name="drive_path",
            description="Your Google Drive directory",
            placeholder="Enter the mounted Drive path",
        )
    ],
)

app.add_publish_environment(
    name="hmg",
    description="Use it for in validation artifacts.",
    publisher=DirectoryPublisher(path=lambda config: Path(config["drive_path"]) / "hmg"),
)

app.add_publish_environment(
    name="prod",
    description="Use it for validated artifacts.",
    publisher=DirectoryPublisher(path=lambda config: Path(config["drive_path"]) / "prod"),
)

app.add_dashboard(
    id="example_dashboard",
    name="Exemple Dashboard",
    description="A simple dashboard just for example",
    tags=["Example"],
    data=[
        DashboardDataSource(
            id="example_source",
            cube=ExampleCube(),
            payload_formatter=ExamplePayloadFormatter(),
        )
    ],
    html="example/index.html",
)


if __name__ == "__main__":
    app.run()
