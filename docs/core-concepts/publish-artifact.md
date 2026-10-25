# Published artifacts

`Iris(version=...)` declares the application version. `add_publish_environment(name=..., publisher=...)` registers named destinations such as `hmg` and `prod` for all dashboards. The desktop app presents these names when publishing and shows the selected destination and version before writing. Each environment has an independent publication root with the same layout. When no environments are configured, Iris saves artifacts in the user's Downloads folder. A failed configured destination never falls back to Downloads.

`DirectoryPublisher(path=...)` accepts a fixed path or a callable that receives the application's runtime `config` and returns a path. Iris holds that configuration in `app.config`; setup populates it before publication, and the selected publisher receives the same object when its path is resolved. In the example, the callables build `hmg` and `prod` paths from the validated `config["drive_path"]`. Iris checks the selected destination again when writing and reports a failure if it becomes unavailable. Runtime tokens and credentials are never copied into artifacts or metadata.

```text
index.html
<dash_id>.html
<dash_id>-data/publications.json
<dash_id>-data/<cube_id>/partitions.json
<dash_id>-data/<cube_id>/<partition_value>__+__<another_value>.js
```

Iris generates `index.html` as a web navigation hub. Each dashboard has one `<dash_id>.html` file. Source dashboards may keep separate assets for desktop use; the [Standalone Builder](standalone-builder.md) embeds those local assets into the published HTML and preserves the pinned SDK CDN script reference. There is no published dashboard assets directory. A source dashboard without an assets directory continues to work. Each cube has a data directory under its dashboard.

`<dash_id>-data/publications.json` records publication events for that dashboard in this environment. Each event records `version` from `Iris`, `environment`, `published_at` in UTC, and SHA-256 digests for the generated dashboard HTML and the currently published partition files. The HTML digest covers its local inline assets and SDK URL, not the remote SDK bytes. `published_by` is included only when the desktop process has a trustworthy identity; the user does not type an unverified identity into the manifest. The manifest does not contain a `source_revision`. For example:

```json
{
  "dashboard_id": "example_dashboard",
  "publications": [
    {
      "version": "1.0.0",
      "environment": "hmg",
      "published_at": "2026-10-25T18:00:00Z",
      "html": {"sha256": "<digest>"},
      "partitions": {"example_cube/202609.js": {"sha256": "<digest>"}}
    }
  ]
}
```

Every successful dashboard publication appends an event, including another publication under the same application version. Each event describes the resulting dashboard HTML and partition files; republishing HTML rebuilds it from current source assets without changing partition files, and publishing only data leaves HTML unchanged. Republishing the web `index.html` independently does not publish dashboard data. The digests describe file contents, but metadata alone does not authorize access or prove its own integrity. Access to published static files depends on the permissions of the selected destination. Keeping older events does not preserve older file contents or promise rollback.

The cube's `partitions.json` lists published partition names without the `.js` extension. For example:

```json
{"partitions": ["202609__+__cartao"]}
```

The corresponding `202609__+__cartao.js` is a JavaScript module that exports only that partition's formatted data payload as its default export (`export default <payload>;`). The SDK dynamically imports selected modules by their names in `partitions.json`. Partition values in file names are joined with `__+__` in partition column order. Iris rejects values that contain the separator or cannot be represented safely as a single file name, keeping ordinary partition names readable without silently mapping distinct values to the same file.

Publication is incremental. With omitted `partitions`, it publishes cached partitions by default; `cache_only: false` discovers all source partitions and fetches missing data. Explicit partition values are published regardless of `cache_only`. Publishing a new partition adds its `.js` file and updates `partitions.json` to include it, while retaining previously published partitions. Iris prepares files before replacing live files, then replaces partition payloads, `partitions.json`, and finally `publications.json`. A failed write must not add a successful publication event. This ordered update limits partial visibility but is not a transaction across the whole directory. For example, publishing `202610__+__cartao` after the partition above results in:

```json
{"partitions": ["202609__+__cartao", "202610__+__cartao"]}
```

When a dashboard runs without the desktop `webview` bridge, the CDN-loaded `IrisRuntimeSDK` looks for partitions in these published files.
