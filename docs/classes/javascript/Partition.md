# Partition

## Responsibility

A `Partition` represents one partition of a [DataSource](DataSource.md). It combines its column values with its availability status. Obtain these objects from `source.listPartitions()` and pass them directly to that source's `getData` or `cleanCache` methods.

```js
const partitions = await source.listPartitions();
const partition = partitions[0];

console.log(partition.values);   // { month: "202609" }
console.log(partition.isCached); // true or false

await source.getData({ partitions: [partition] });
await source.cleanCache([partition]);
```

## Properties

- `values`: an object mapping each column in the Cube's `PARTITION_BY` to its string value, for example `{ month: "202609" }`.
- `isCached`: a boolean. In desktop mode it indicates whether the Cube's partition is cached; in published mode it is `true` for a partition listed in the published manifest and does not describe the desktop cache.

A partition belongs to the source that returned it. Passing it to another source rejects. Its identity is determined by the column names and values, not the order of object keys or `isCached`. The status is a snapshot from listing, not a guarantee that the cache will remain unchanged.

The SDK serializes `values` when communicating with the bridge or reading published artifacts; the JavaScript object itself is not the file format. The Cube's declared partition-column order determines how values are encoded into file names. A failed discovery rejects; an empty partition list is valid.
