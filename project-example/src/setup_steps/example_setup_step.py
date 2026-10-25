
import json
import os
import subprocess
from pathlib import Path

from iris import SetupStep

__all__ = ["ExampleSetupStep"]


class ExampleSetupStep(SetupStep):
    def __init__(self, profile: str):
        self.profile = profile

    def generate_token(self) -> str:
        token_command = \
        [
            "databricks",
            "auth",
            "token",
            self.profile,
        ]
        result = subprocess.run(token_command, capture_output=True, text=True, check=True, timeout=30)
        return json.loads(result.stdout)["access_token"]

    def configure(self, config: dict) -> dict:
        drive_path = Path(config["drive_path"]).expanduser()
        if not drive_path.is_dir() or not os.access(drive_path, os.W_OK):
            raise ValueError("The configured Drive directory is unavailable")

        try:
            self.generate_token()
        except subprocess.CalledProcessError:
            login_command = \
            [
                "databricks",
                "auth",
                "login",
                "--profile",
                self.profile,
            ]
            subprocess.run(login_command, check=True)
            self.generate_token()
        config["drive_path"] = str(drive_path)
        config["generate_token"] = self.generate_token
        return config
