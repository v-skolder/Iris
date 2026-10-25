# HTML Runtime

`IrisRuntimeSDK` is distributed through a CDN. Iris loads it in dashboards, which use the SDK to access their data. The SDK checks whether a `webview` bridge is available: inside the desktop app it uses the bridge; otherwise it looks for published partitions in the file system.

The SDK exposes `IrisRuntimeSDK.<dashboard_id>.<cube_name>` for reading data in both environments. In the desktop app it also offers cube cache deletion and `IrisRuntimeSDK.<dashboard_id>.publish`, mirroring the bridge's namespace. `IrisRuntimeSDK.isDesktop` indicates whether the bridge is available. The [example.html](../../project-example/src/dashboards/example.html) uses the SDK and hides refresh, cache deletion, and publishing controls outside the desktop app.

The desktop bridge exposes `webview.<dashboard_id>.<cube_name>` with `get_data`, `list_partitions`, and `delete_data`, plus `webview.<dashboard_id>.publish`. The `partitions` arguments are optional; omitting them or passing null selects all partitions. `get_data` also accepts `force_refresh`.

`list_partitions()` returns `{"partitions": [[ ["202609"], true ]]}`. Each entry contains the partition values and a boolean indicating whether it is cached. In the published runtime, available partition files are reported as present. See also [Cache](cache.md).

For the files created by `publish`, see [Published artifacts](publish-artifact.md).
