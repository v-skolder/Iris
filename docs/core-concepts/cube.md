# Cube

A Cube provides data as a Polars DataFrame. Its `NAME` identifies the cube. `SCHEMA` describes the columns stored in the SQLite cache, including the primary key. `PARTITION_BY` identifies the columns used to partition that cache. In the example, `month` contains values in `YYYYMM` format.

The Cube implements `get_data(partitions=None, config=None)` and `list_partitions(config=None)`. Iris supplies the runtime configuration returned by a [setup step](setup-step.md) when fetching data or discovering partitions. See [ExampleCube](../../project-example/src/cubes/example_cube.py) and [Cache](cache.md).
