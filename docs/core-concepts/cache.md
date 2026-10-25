# Cache

Iris stores Cube data in a local SQLite cache. Each Cube's `SCHEMA` defines the cached columns, their types, and the primary key. Columns named in `PARTITION_BY` are part of that schema and identify the cached partitions. The Cube returns Polars DataFrames with those columns; in the example, `month` identifies partitions such as `202609`.

Inside the desktop app, the HTML runtime SDK uses `webview.<dashboard_id>.<cube_name>` for cache operations:

- `get_data({ partitions, force_refresh })` reads data for the selected partitions. `force_refresh: true` fetches fresh data instead of reusing cached data.
- `list_partitions()` returns the available partition values and whether each one is cached: `{"partitions": [[ ["202609"], true ]]}`.
- `delete_data({ partitions })` removes cached data for the selected partitions.

For operations that accept `partitions`, omitting it or passing `null` addresses all partitions of that Cube. See the [Cube](cube.md) and [HTML runtime](html-runtime.md) documentation.
