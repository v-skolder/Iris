
import json

from iris.payload import BasePayloadFormatter

__all__ = ["ExamplePayloadFormatter"]


class ExamplePayloadFormatter(BasePayloadFormatter):
    def format(self, raw_data):
        return json.loads(raw_data.write_json())
