# Cache

Iris stores Cube data in a local SQLite cache. Each Cube's `SCHEMA` defines the cached columns, their types, and the primary key. Columns named in `PARTITION_BY` are part of that schema and identify the cached partitions. The Cube returns Polars DataFrames with those columns; in the example, `month` identifies partitions such as `202609`.

Inside the desktop app, the HTML runtime SDK uses `webview.<dashboard_id>.<cube_name>` for cache operations:

- `get_data({ partitions, force_refresh, cache_only })` reads data for the selected partitions. `force_refresh: true` replaces the selected cached partitions with fresh data. When `partitions` is omitted, `cache_only` defaults to `true` and selects cached partitions; `false` selects every partition listed by the Cube, fetching missing data.
- `list_partitions()` returns the available partition values and whether each one is cached: `{"partitions": [[ ["202609"], true ]]}`.
- `delete_data({ partitions })` removes cached data for the selected partitions.

Explicit `partitions` select those values regardless of `cache_only` and fetch any missing partitions from the Cube. `delete_data` without `partitions` deletes all cached partitions. The Cube's source partition listing identifies available partitions; a returned DataFrame without rows is not evidence that a partition was cached. See the [Cube](cube.md) and [HTML runtime](html-runtime.md) documentation.
