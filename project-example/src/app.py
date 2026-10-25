
from iris import DashboardDataSource, DirectoryPublisher, Iris, SetupField

from src.cubes import ExampleCube
from src.payload_formatters import ExamplePayloadFormatter
from src.setup_steps import ExampleSetupStep

__all__ = ["app"]


app = Iris()
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

app.add_dashboard(
    id="example_dashboard",
    data=[
        DashboardDataSource(
            cube=ExampleCube(),
            payload_formatter=ExamplePayloadFormatter(),
        )
    ],
    html="example.html",
    publisher=DirectoryPublisher(),
)


if __name__ == "__main__":
    app.run()
