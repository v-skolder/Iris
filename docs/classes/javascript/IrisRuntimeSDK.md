# IrisRuntimeSDK

## Responsibility

`IrisRuntimeSDK` is the JavaScript interface between Iris and its hub and dashboards. Its contract follows the publication unit: a dashboard owns data sources, and each data source binds a Cube to the PayloadFormatter that produces its payload. The SDK returns dashboard objects, which expose their data sources; each source exposes its own data, partition and cache operations.

The SDK is available to the hub and dashboard before their scripts run. In the desktop app, it delegates operations to the WebView bridge; in published mode, it reads the published dashboard registry, partition manifests and payload modules. It hides transport details without owning the source data, cache or publisher. `IrisRuntimeSDK.isDesktop` indicates whether the desktop bridge is available.

All methods return promises. Invalid arguments, unknown or unavailable identifiers, unsupported operations and I/O failures reject with an `Error` containing a descriptive `message`. Empty results are valid results, never substitutes for failures. Mutations resolve only after the underlying operation completes.

## Dashboard and data source

Each dashboard has an application-wide unique `id`. A dashboard registers one or more data sources, each with an `id` unique **within that dashboard**, a Cube and a PayloadFormatter. The pair `(dashboardId, dataSourceId)` identifies the complete association; neither the Cube nor the formatter is addressed separately through this API. The same Cube can therefore be used by different dashboards with different formatters, without ambiguity.

The Cube owns source discovery and data retrieval. Its associated PayloadFormatter transforms the data into the payload consumed by that dashboard. Both desktop reads and publication use this same association. Published files contain the formatted payload, not the raw Cube or the formatter implementation.

A partition is an object mapping each column named in the Cube's `PARTITION_BY` to its value, for example `{ month: "202609", product: "cartao" }`. A selection is an array of these objects, for example `[{ month: "202609" }, { month: "202610" }]`. Each object must contain exactly the Cube's partition columns; missing or unknown columns reject the operation. Values are strings and must not be converted to numbers. Object key order does not identify a partition: Iris uses the Cube's declared partition-column order when encoding artifact file names. An explicit empty selection selects nothing; omitted or `null` selections use the operation's default.

## Registry and navigation

### `IrisRuntimeSDK.listDashboards()`

Returns dashboard descriptors. Desktop mode lists registered dashboards; published mode lists dashboards present in the published hub registry.

```js
await IrisRuntimeSDK.listDashboards();
// [{
//   id: "example_dashboard",
//   name: "Exemple Dashboard",
//   tags: ["Example"],
//   description: "A simple dashboard just for example",
//   navigate_relative_url: "./example/index.html"
// }]
```

`navigate_relative_url` is resolved relative to the hub URL and can differ by runtime. It is a navigation address, not an access-control guarantee.

### `IrisRuntimeSDK.getDashboard(id)`

Returns a dashboard object for a registered or published dashboard. Its `id`, `name`, `description`, `tags` and `navigateRelativeUrl` properties describe the dashboard; its methods operate in that dashboard's context. An unknown or unavailable ID rejects.

### `dashboard.getDataSource(id)`

Returns a data source object for an association registered on this dashboard. Its `id` and `cubeId` identify the association and Cube. It exposes `listPartitions`, `getData` and `cleanCache`; its associated PayloadFormatter is applied automatically. An unknown or unavailable source ID rejects.

```js
const dashboard = await IrisRuntimeSDK.getDashboard("example_dashboard");
const source = await dashboard.getDataSource("example_source");
const partitions = await source.listPartitions();
const data = await source.getData({ partitions: [{ month: "202609" }] });
```
### `dashboard.listDataSources()`

Returns descriptors for the data sources registered on this dashboard:

```js
await dashboard.listDataSources();
// [{ id: "example_source", cube_id: "example_cube" }]
```

`id` identifies the Cube–PayloadFormatter association within the dashboard. `cube_id` identifies its Cube for inspection; the formatter is inseparable from the association and is applied automatically. The SDK does not expose implementation objects or credentials. A dashboard with no sources returns `[]`. In published mode, the result contains the sources recorded for that published dashboard, including sources with no published partitions.

### `IrisRuntimeSDK.listPublishEnvironments()`

Returns the registered publication environments in the desktop app:

```js
await IrisRuntimeSDK.listPublishEnvironments();
// [
//   { id: "hmg", description: "Use it for in validation artifacts." },
//   { id: "prod", description: "Use it for validated artifacts." }
// ]
```

When none are registered, it returns `[]`. The Downloads fallback is not a registered environment. This operation is desktop-only.

## Publication

### `dashboard.publish(environmentId = null, metadata = {})`

Publishes the specified dashboard and its data-source associations to one destination. If the environment is omitted or `null` and environments are configured, the desktop app asks the user to select one; cancellation rejects. With no configured environments, an omitted or `null` ID selects the user's Downloads folder. An unknown environment or failed configured destination is an error; Iris never silently switches destinations.

`metadata` is an optional JSON-serializable object stored under a dedicated `metadata` key in the publication event. It cannot override framework-generated version, environment, timestamp, digests or verified identity. Callers must not include credentials, tokens or other secrets.

Publication uses cached partitions from each associated Cube, formats them with **that dashboard's associated formatter**, and writes the resulting payloads under the dashboard and data source. It does not discover or fetch uncached partitions. Publication is incremental: previously published partitions remain available. The dashboard HTML is created if absent; if it already exists, publishing data leaves it unchanged. The published hub is managed separately. Updates follow the ordering and failure limitations in [Published artifacts](../../core-concepts/publish-artifact.md); the whole destination is not a single transaction.

The result is `{ dashboard_id, environment, published_sources }`. `environment` is the selected ID or `null` for Downloads. `published_sources` is an array of `{ data_source_id, partitions }`, containing the partitions published for each source in this operation. Sources without cached partitions have an empty array.

This operation is desktop-only. Refreshing or populating the cache is a separate operation.

## Partitions

### `source.listPartitions()`

Returns the available partitions for the specified dashboard data source and their cache status:

```js
await source.listPartitions();
// [
//   { partition: { month: "202609" }, isCached: true },
//   { partition: { month: "202610" }, isCached: false }
// ]
```

`partition` maps the Cube's partition-column names to their values. `isCached` is a boolean, not a string. In desktop mode, the associated Cube discovers source partitions and `isCached` indicates whether each partition is present in SQLite. An empty source returns `[]`; a discovery failure rejects the promise.

In published mode, the manifest lists the available published partitions. Each is returned with `isCached: true`, meaning its published payload is available; it does not indicate the presence of a desktop cache.
## Data and cache

### `source.getData(options = {})`

Returns data from the associated Cube formatted by the **PayloadFormatter registered for this dashboard and source**. The SDK never selects a formatter independently.

`options` accepts:

- `partitions`: a selection, `null`, or omitted.
- `force_refresh`: boolean, default `false`.
- `cache_only`: boolean, default `true`.

In desktop mode, omitted or `null` partitions select cached partitions by default. With `cache_only: false`, Iris discovers all source partitions and fetches missing data. An explicit selection takes precedence over `cache_only` and fetches missing selected partitions. With `force_refresh: true`, Iris fetches and replaces the selected partitions in the Cube's cache. An explicit empty selection returns an empty result without fetching.

In published mode, omitted or `null` partitions select all published partitions for that dashboard and source. `cache_only: false` cannot discover source partitions; `force_refresh: true` rejects. A requested partition absent from the manifest rejects rather than silently returning incomplete data.

The result preserves partition boundaries:

```js
await source.getData({
  partitions: [{ month: "202609" }]
});
// { partitions: [{ values: { month: "202609" }, payload: /* formatted data */ }] }
```

The formatter defines each payload's internal structure. No selected partitions produces `{ partitions: [] }`. A failed read or formatting operation rejects rather than returning a partial result.

### `source.cleanCache(partitions = null)`

Deletes cached data for the source's Cube. `partitions` is an optional list of partition objects; omitted or `null` deletes all cached partitions for that Cube, while `[]` deletes nothing. Already absent partitions are ignored. Since the cache belongs to the Cube, other dashboard associations using that Cube are also affected. Source data and published artifacts are unchanged.

The result is `{ dashboard_id, data_source_id, deleted_partitions }`, with the partition objects actually removed. This operation is desktop-only.

## Published artifact contract

The artifact preserves the dashboard-to-source association so the same IDs work in both runtimes:

- The published hub registry contains dashboard descriptors and navigation URLs for the dashboards represented in that hub.
- Each published dashboard has a registry of its data source IDs and associated Cube IDs, including sources with no published partitions.
- Each source has its own partition manifest and payload files under that dashboard's publication directory. Its manifest maps partition objects to their published files; Iris encodes values in the Cube's declared partition-column order when constructing file names.
- Each partition module exports the payload produced by that source's associated formatter. A dashboard sharing a Cube with another dashboard reads its own formatted payload files.
- The SDK uses the dashboard and source IDs to resolve the manifest and selected payloads. It does not need the Python Cube or formatter in published mode.

These registries and manifests are part of the SDK's public contract and must be generated consistently with its version. Publication must reject identifiers or partition values that cannot be represented safely in the artifact paths. An unavailable manifest or payload rejects the read; an empty manifest is a valid empty source. The publication destination's permissions govern access to these files.

## Runtime availability

| Method | Desktop | Published |
| --- | --- | --- |
| `listDashboards`, `getDashboard`, `listDataSources`, `getDataSource`, `listPartitions`, `getData` | Registered resources | Published resources |
| `listPublishEnvironments`, `publish`, `cleanCache` | Available | Rejects as unavailable |

Published reads require access to the artifact files and the SDK CDN. See [Cache](../../core-concepts/cache.md) and [Published artifacts](../../core-concepts/publish-artifact.md).




