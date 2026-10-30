# Dashboard

## Responsibility

A `Dashboard` is the JavaScript representation of one dashboard registered in Iris. It provides its descriptive information, access to its data sources, and the publication operation. It is the unit of publication: each source belongs to a dashboard and binds a Cube to the PayloadFormatter used for that dashboard's data.

Obtain a dashboard through [IrisRuntimeSDK](IrisRuntimeSDK.md):

```js
const dashboard = await IrisRuntimeSDK.getDashboard("example_dashboard");
```

The ID is unique within the Iris application. An unknown or unavailable dashboard causes `getDashboard` to reject. The SDK provides the object in both desktop and published modes; its methods return promises.

## Properties

| Property | Meaning |
| --- | --- |
| `id` | Dashboard identifier. |
| `name` | Display name. |
| `description` | Description of the dashboard. |
| `tags` | List of tags. |
| `navigateRelativeUrl` | Navigation URL relative to the hub; its value can differ between runtimes. |

The URL is not an access-control guarantee. `IrisRuntimeSDK.listDashboards()` returns Dashboard objects with these same properties and methods.

## Methods

### `listDataSources()`

Returns DataSource objects for the dashboard's sources:

```js
await dashboard.listDataSources();
// [DataSource { id: "example_source", cubeId: "example_cube" }]
```

A source ID is unique within its dashboard. Each object identifies the association and its Cube; the associated formatter is applied automatically and is not exposed as an implementation object. An empty dashboard returns `[]`. Published mode lists the sources recorded for that published dashboard, including sources with no published partitions.

### `getDataSource(id)`

Returns the [DataSource](DataSource.md) associated with the given ID in this dashboard. An unknown or unavailable ID rejects.

```js
const source = await dashboard.getDataSource("example_source");
const partitions = await source.listPartitions();
```

### `publish(environmentId = null, metadata = {})`

Publishes this dashboard and its source associations. The operation is available only in the desktop app; published mode rejects.

`environmentId` selects a registered publication environment. When it is omitted or `null`, the desktop app asks the user to choose if environments are configured; cancellation rejects. If none are configured, Iris uses Downloads. An unknown environment or a failed configured destination rejects without silently switching destinations.

`metadata` is an optional JSON-serializable object stored under a dedicated `metadata` key in the publication event. It cannot override framework-generated version, environment, timestamp, digests or verified identity. It must not include credentials, tokens or other secrets.

```js
await dashboard.publish("hmg", { note: "Monthly update" });
```

The operation publishes cached partitions for each associated Cube, formatting them with that dashboard's associated formatter. It does not fetch uncached partitions. Publication is incremental and retains previously published partitions. The dashboard HTML is created if absent; an existing HTML file is left unchanged. The published hub is managed separately.

On success the promise resolves without a value. A failed write rejects and must not create a successful publication event; updates across the destination are not a single transaction. See [Published artifacts](../../core-concepts/publish-artifact.md) for the publication model.



