# IrisRuntimeSDK

## Responsibility

`IrisRuntimeSDK` is the JavaScript interface between Iris and its hub and dashboards. Its contract follows the publication unit: a dashboard owns data sources, and each data source binds a Cube to the PayloadFormatter that produces its payload. The SDK returns dashboard objects, which expose their data sources; each source exposes its own data, partition and cache operations.

The SDK is available to the hub and dashboard before their scripts run. In the desktop app, it delegates operations to the WebView bridge; in published mode, it reads the published dashboard registry, partition manifests and payload modules. It hides transport details without owning the source data, cache or publisher. `IrisRuntimeSDK.isDesktop` indicates whether the desktop bridge is available.

All methods return promises. Invalid arguments, unknown or unavailable identifiers, unsupported operations and I/O failures reject with an `Error` containing a descriptive `message`. Empty results are valid results, never substitutes for failures. Mutations resolve only after the underlying operation completes.

## Dashboard and data source

See the [Dashboard](Dashboard.md) and [DataSource](DataSource.md) class references for their full contracts.

Each dashboard has an application-wide unique `id`. A dashboard registers one or more data sources, each with an `id` unique **within that dashboard**, a Cube and a PayloadFormatter. The pair `(dashboardId, dataSourceId)` identifies the complete association; neither the Cube nor the formatter is addressed separately through this API. The same Cube can therefore be used by different dashboards with different formatters, without ambiguity.

The Cube owns source discovery and data retrieval. Its associated PayloadFormatter transforms the data into the payload consumed by that dashboard. Both desktop reads and publication use this same association. Published files contain the formatted payload, not the raw Cube or the formatter implementation.

A [Partition](Partition.md) object belongs to a data source and exposes its column values through `values` and its status through `isCached`. Obtain partitions with `source.listPartitions()` and pass those objects to `getData` and `cleanCache`. A selection is an array of Partition objects; an explicit empty selection selects nothing, while omitted or `null` selections use the operation's default.

## Registry and navigation

### `IrisRuntimeSDK.listDashboards()`

Returns Dashboard objects for the registered dashboards in desktop mode and the dashboards present in the published hub registry in published mode. Each object exposes the properties and operations described in [Dashboard](Dashboard.md).

### `IrisRuntimeSDK.getDashboard(id)`

Returns a dashboard object for a registered or published dashboard. Its `id`, `name`, `description`, `tags` and `navigateRelativeUrl` properties describe the dashboard; its methods operate in that dashboard's context. An unknown or unavailable ID rejects.

### `dashboard.getDataSource(id)`

Returns a data source object for an association registered on this dashboard. Its `id` and `cubeId` identify the association and Cube. It exposes `listPartitions`, `getData` and `cleanCache`; its associated PayloadFormatter is applied automatically. An unknown or unavailable source ID rejects.

```js
const dashboard = await IrisRuntimeSDK.getDashboard("example_dashboard");
const source = await dashboard.getDataSource("example_source");
const partitions = await source.listPartitions();
const data = await source.getData({ partitions: [partitions[0]] });
```
### `dashboard.listDataSources()`

Returns DataSource objects registered on this dashboard:

```js
await dashboard.listDataSources();
// [DataSource { id: "example_source", cubeId: "example_cube" }]
```

`id` identifies the Cube–PayloadFormatter association within the dashboard. `cubeId` identifies its Cube for inspection; the formatter is inseparable from the association and is applied automatically. The SDK does not expose implementation objects or credentials. A dashboard with no sources returns `[]`. In published mode, the result contains the sources recorded for that published dashboard, including sources with no published partitions.

### `IrisRuntimeSDK.listPublishEnvironments()`

Returns simple objects describing the environments registered in the desktop app:

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

On success, the promise resolves without a value. A failed publication rejects.

This operation is desktop-only. Refreshing or populating the cache is a separate operation.

## Partitions

### `source.listPartitions()`

Returns the available partitions for the specified dashboard data source and their cache status:

```js
await source.listPartitions();
// [
//   Partition { values: { month: "202609" }, isCached: true },
//   Partition { values: { month: "202610" }, isCached: false }
// ]
```

`values` maps the Cube's partition-column names to their values. `isCached` is a boolean, not a string. In desktop mode, the associated Cube discovers source partitions and `isCached` indicates whether each partition is present in SQLite. An empty source returns `[]`; a discovery failure rejects the promise.

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
const partitions = await source.listPartitions();
await source.getData({ partitions: [partitions[0]] });
// [{ partition: partitions[0], payload: /* formatted data */ }]
```

The formatter defines each payload's internal structure. No selected partitions produces an empty array. A failed read or formatting operation rejects rather than returning a partial result.

### `source.cleanCache(partitions = null)`

Deletes cached data for the source's Cube. `partitions` is an optional list of Partition objects returned by this source; omitted or `null` deletes all cached partitions for that Cube, while `[]` deletes nothing. Already absent partitions are ignored. Since the cache belongs to the Cube, other dashboard associations using that Cube are also affected. Source data and published artifacts are unchanged.

On success, the promise resolves without a value. A failed cleanup rejects. This operation is desktop-only.

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


