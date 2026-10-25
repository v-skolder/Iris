
import polars as pl

from iris.cube import BaseCube, ColumnConfig, ColumnType

__all__ = ["ExampleCube"]


class ExampleCube(BaseCube):
    NAME = "example_cube"

    SCHEMA = [
        ColumnConfig(name="id", type=ColumnType.TEXT, primary_key=True),
        ColumnConfig(name="date", type=ColumnType.DATE),
        ColumnConfig(name="month", type=ColumnType.TEXT),
        ColumnConfig(name="product", type=ColumnType.TEXT),
        ColumnConfig(name="balance", type=ColumnType.NUMERIC),
    ]

    PARTITION_BY = ["month"]

    def get_data(self, partitions=None, config=None) -> pl.DataFrame:
        # Replace this sample with a query to Databricks or another data source.
        data = pl.DataFrame(
            [
                {"id": "1", "date": "2026-09-01", "product": "A", "balance": 125.5},
                {"id": "2", "date": "2026-09-15", "product": "B", "balance": 80.0},
                {"id": "3", "date": "2026-10-01", "product": "A", "balance": 140.0},
            ]
        ).with_columns(
            pl.col("date").str.to_date(),
            pl.col("date").str.to_date().dt.strftime("%Y%m").alias("month"),
        )

        if partitions is None:
            return data

        return data.filter(pl.col("month").is_in([values[0] for values in partitions]))

    def list_partitions(self, config=None) -> pl.DataFrame:
        return self.get_data(config=config).select("month").unique().sort("month")
