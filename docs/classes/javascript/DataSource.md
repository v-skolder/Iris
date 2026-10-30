# DataSource

## Responsibility

A `DataSource` represents a dashboard's association between a Cube and a PayloadFormatter. It provides access to that Cube's partitions, formatted data and cache operations. The source automatically uses the formatter registered for its dashboard; dashboard code does not select the Cube or formatter independently.

Obtain it from a [Dashboard](Dashboard.md):

```js
const dashboard = await IrisRuntimeSDK.getDashboard("example_dashboard");
const source = await dashboard.getDataSource("example_source");
```

Its `id` identifies the association within the dashboard, and `cubeId` identifies the Cube. Two dashboards can associate the same Cube with different formatters. Desktop reads and publication use the association belonging to the selected dashboard; published files contain formatted payloads, not the Python Cube or formatter.

All methods return promises. Invalid arguments, unknown or unavailable resources, unsupported operations and I/O failures reject with a descriptive `Error`; empty results are not errors.

## Partitions

A [Partition](Partition.md) object belongs to this source and exposes `values`, an object containing the Cube's partition-column names and their string values, and `isCached`, its availability status. Obtain partitions through `listPartitions()` and pass them directly to this source. A selection is an array of Partition objects; omitted or `null` selections use the operation's default, and `[]` selects nothing.

### `listPartitions()`

```js
await source.listPartitions();
// [
//   Partition { values: { month: "202609" }, isCached: true },
//   Partition { values: { month: "202610" }, isCached: false }
// ]
```

In desktop mode, the Cube discovers source partitions and `isCached` indicates whether each is in SQLite. An empty source returns `[]`; discovery failures reject. In published mode, the list comes from the published manifest and `isCached` is `true` for each listed partition, indicating published availability rather than desktop cache presence.

## Data

### `getData(options = {})`

Returns the Cube's data formatted with this source's associated PayloadFormatter. The result preserves partition boundaries:

```js
const partitions = await source.listPartitions();
await source.getData({ partitions: [partitions[0]] });
// [{ partition: partitions[0], payload: /* formatted data */ }]
```

The formatter defines the payload's structure. No selected partitions returns an empty array; a read or formatting failure rejects instead of returning partial data.

Options are passed as an object:

| Option | Default | Meaning |
| --- | --- | --- |
| `partitions` | `null` | Partition selection; omitted or `null` uses the runtime default. |
| `force_refresh` | `false` | Fetch and replace selected cached partitions in desktop mode. |
| `cache_only` | `true` | With no selection in desktop mode, use cached partitions only. |

In desktop mode, an omitted or `null` selection uses cached partitions. Setting `cache_only: false` discovers all source partitions and fetches missing data. An explicit selection takes precedence over `cache_only` and fetches selected partitions missing from the cache. `force_refresh: true` fetches and replaces the selected cached partitions. An explicit empty selection performs no fetch.

In published mode, an omitted or `null` selection reads all published partitions for this source. `cache_only: false` cannot discover source partitions, and `force_refresh: true` rejects. Requesting a partition absent from the manifest rejects.

## Cache

### `cleanCache(partitions = null)`

Deletes cached data for the associated Cube in desktop mode. Pass a list of Partition objects returned by this source to select partitions, omit it or pass `null` to delete all cached partitions for that Cube, or pass `[]` to delete nothing. Already absent partitions are ignored.

```js
const partitions = await source.listPartitions();
await source.cleanCache([partitions[0]]);
```

On success the promise resolves without a value; a failure rejects. Cache belongs to the Cube, so other dashboard associations using that Cube are also affected. This operation does not delete source data or published artifacts and rejects in published mode. See [Cache](../../core-concepts/cache.md).




