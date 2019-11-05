from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, List, NamedTuple


class DataType(Enum):
    """
    Postgres DataTypes
    Since PG COPY requires data in exact format (eg. 2 bytes for smallint, 4
        bytes for integer) and python data types don't allow to set length, we
        describe schema that is used to remap types to binary forms
    """
    SMALLINT = auto()  # int
    INTEGER = auto()  # int
    BIGINT = auto()  # int
    DOUBLE_PRECISION = auto()  # float
    CHARACTER_VARYING = auto()  # str
    DATE = auto()  # datetime.date


class ColumnDefinition(NamedTuple):
    name: str
    data_type: DataType


@dataclass
class Schema:
    """
    Internal postgres table schema representation
    """
    columns: List[ColumnDefinition]

    @staticmethod
    def load_from_table(
        psycopg2_cursor: Any,
        table: str,  # Must have table_schema.table_name format
    ) -> Schema:
        """
        Retrives this schema from given table
        """
        table_schema, table_name = table.split(".")

        # Possible need to filter table_catalog
        psycopg2_cursor.execute('''
            SELECT
                column_name, data_type
            FROM
                information_schema.columns
            WHERE
                table_schema = %(table_schema)s AND
                table_name = %(table_name)s
            ORDER BY
                ordinal_position
        ''', {
            'table_schema': table_schema,
            'table_name': table_name,
        })

        return Schema(
            columns=[
                ColumnDefinition(
                    name=row[0],
                    data_type=_pg_data_type_to_py[row[1]]
                )
                for row in psycopg2_cursor
            ]
        )


_pg_data_type_to_py = {
    'smallint': DataType.SMALLINT,
    'integer': DataType.INTEGER,
    'bigint': DataType.BIGINT,
    'double precision': DataType.DOUBLE_PRECISION,
    'character varying': DataType.CHARACTER_VARYING,
    'date': DataType.DATE,
}