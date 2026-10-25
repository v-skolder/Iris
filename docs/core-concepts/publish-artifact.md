# Published artifacts

Every publisher saves dashboards using the same layout. If no publisher is configured, Iris saves the artifacts in the user's Downloads folder. A configured publisher may choose another destination.

For the example `DirectoryPublisher`, Iris passes the runtime configuration returned by `SetupStep.configure(config)` when publishing. The publisher uses `config["drive_path"]` as its destination and handles a write failure if that directory becomes unavailable.

```text
index.html
<dash_id>.html
<dash_id>-data/<cube_id>/partitions.json
<dash_id>-data/<cube_id>/<partition_value>__+__<another_value>.js
```

Iris generates `index.html` as a web navigation hub. Each dashboard has its own `<dash_id>.html` file. Each cube has a data directory under its dashboard.

The cube's `partitions.json` lists published partition names without the `.js` extension. For example:

```json
{"partitions": ["202609__+__cartao"]}
```

The corresponding `202609__+__cartao.js` contains only the data payload for that partition. Partition values in file names are joined with `__+__` in partition column order.

Publication is incremental. Publishing a new partition adds its `.js` file and updates `partitions.json` to include its name, while retaining previously published partitions. For example, publishing `202610__+__cartao` after the partition above results in:

```json
{"partitions": ["202609__+__cartao", "202610__+__cartao"]}
```

When a dashboard runs without the desktop `webview` bridge, its injected `IrisRuntimeSDK` looks for partitions in these published files.
