# HTML Runtime

`IrisRuntimeSDK` is loaded through a version-pinned CDN `<script src="https://cdn.jsdelivr.net/gh/v-skolder/Iris@v0.1.0/runtime/iris-runtime.js"></script>` before dashboard scripts run. Dashboards may use a single HTML file or keep CSS, JavaScript, images and other static assets in an `assets/` directory beside that HTML. HTML references such as `assets/style.css` and `assets/dashboard.js` work in the desktop app. Iris packages the HTML and assets as read-only application resources in a desktop build. See the [example HTML](../../project-example/src/dashboards/example/index.html), [CSS](../../project-example/src/dashboards/example/assets/style.css) and [JavaScript](../../project-example/src/dashboards/example/assets/dashboard.js).

On publication, Iris embeds supported local assets into the generated dashboard HTML and preserves the SDK's CDN script reference. The published dashboard still reads partition data from its separate `.js` files; "one HTML" refers to the dashboard presentation, not the partition payloads or its CDN dependency.

The SDK checks whether a `webview` bridge is available: inside the desktop app it uses the bridge; otherwise it reads the published `partitions.json` and dynamically imports the selected `.js` partition modules. The partition list also lets the dashboard build its selectors.

The SDK exposes `IrisRuntimeSDK.<dashboard_id>.<cube_name>` for reading data in both environments. In the desktop app it also offers cube cache deletion and `IrisRuntimeSDK.<dashboard_id>.publish`, mirroring the bridge's namespace. `IrisRuntimeSDK.isDesktop` indicates whether the bridge is available. The example dashboard uses the SDK and hides refresh, cache deletion, and publishing controls outside the desktop app.

The desktop bridge exposes `webview.<dashboard_id>.<cube_name>` with `get_data`, `list_partitions`, and `delete_data`, plus `webview.<dashboard_id>.publish`. For `get_data` and `publish`, omitted or null `partitions` selects cached partitions by default (`cache_only: true`); `cache_only: false` discovers all source partitions. An explicit partition selection is independent of `cache_only`. `get_data` also accepts `force_refresh`; `delete_data` without partitions deletes all cached partitions. Calling `publish({ partitions })` without an environment opens the desktop environment selector; the desktop app passes the selected registered environment to the publishing operation. Published dashboards do not offer publication actions.

`list_partitions()` returns `{"partitions": [[ ["202609"], true ]]}`. Each entry contains the partition values and a boolean indicating whether it is cached. In the published runtime, available partition files are reported as present. See also [Cache](cache.md).

In published mode, the available partitions are the ones in `partitions.json`; there is no source Cube to discover. Consequently, `get_data` without `partitions` reads all published partitions, and `cache_only: false` cannot discover additional partitions in this mode.

For the files created by `publish`, see [Published artifacts](publish-artifact.md).
