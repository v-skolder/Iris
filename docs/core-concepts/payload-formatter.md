# PayloadFormatter

A PayloadFormatter converts Cube data into a payload that can be serialized for the WebView's HTML. The example implements `format(raw_data)` and converts a Polars DataFrame into JSON-compatible values, including dates. See [ExamplePayloadFormatter](../../project-example/src/payload_formatters/example_payload_formatter.py).
