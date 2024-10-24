import json
from typing import Any, Dict, List, Optional, Tuple, Type
from urllib.parse import urlparse

from .engine import AlloyDBEngine

from llama_index.core.storage.kvstore.types import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_COLLECTION,
    BaseKVStore,
)

IMPORT_ERROR_MSG = "`asyncpg` package not found, please run `pip install asyncpg`"


def get_data_model(
    base: Type,
    index_name: str,
    schema_name: str,
    use_jsonb: bool = False,
) -> Any:
    """
    This part create a dynamic sqlalchemy model with a new table.
    """
    from sqlalchemy import Column, Index, Integer, UniqueConstraint
    from sqlalchemy.dialects.postgresql import JSON, JSONB, VARCHAR

    tablename = "data_%s" % index_name  # dynamic table name
    class_name = "Data%s" % index_name  # dynamic class name

    metadata_dtype = JSONB if use_jsonb else JSON

    class AbstractData(base):  # type: ignore
        __abstract__ = True  # this line is necessary
        id = Column(Integer, primary_key=True, autoincrement=True)
        key = Column(VARCHAR, nullable=False)
        namespace = Column(VARCHAR, nullable=False)
        value = Column(metadata_dtype)

    return type(
        class_name,
        (AbstractData,),
        {
            "__tablename__": tablename,
            "__table_args__": (
                UniqueConstraint(
                    "key", "namespace", name=f"{tablename}:unique_key_namespace"
                ),
                Index(f"{tablename}:idx_key_namespace", "key", "namespace"),
                {"schema": schema_name},
            ),
        },
    )


class CloudSQLPostgresKVStore(BaseKVStore):
    """CloudSQL for Postgres Key-Value store.

    Args:
        connection_string (str): psycopg2 connection string
        async_connection_string (str): asyncpg connection string
        table_name (str): table name
        schema_name (Optional[str]): schema name
        perform_setup (Optional[bool]): perform table setup
        debug (Optional[bool]): debug mode
        use_jsonb (Optional[bool]): use JSONB data type for storage
    """

    engine: AlloyDBEngine
    table_name: str
    schema_name: str

    def __init__(
        self,
        engine: AlloyDBEngine,
        table_name: str,
        schema_name: str = "public",
    ):
        try:
            import asyncpg  # noqa
            import psycopg2  # type: ignore # noqa
            import sqlalchemy
            import sqlalchemy.ext.asyncio  # noqa
        except ImportError:
            raise ImportError(
                "`sqlalchemy[asyncio]`, `psycopg2-binary` and `asyncpg` "
                "packages should be pre installed"
            )

        self.engine = engine
        self.table_name = table_name
        self.schema_name = schema_name

    async def _initialize(self) -> None:
        await self._create_schema_if_not_exists()
        await self._create_table_if_not_exists()

    async def _create_schema_if_not_exists(self) -> None:
        create_schema_query = f"CREATE SCHEMA IF NOT EXISTS {self.schema_name}"
        await self.engine.aexecute_query(create_schema_query)

    async def _create_table_if_not_exists(self) -> None:
        create_query =  f"""CREATE TABLE IF NOT EXISTS {self.schema_name}.{self.table_name} (
        id SERIAL PRIMARY KEY,
        key VARCHAR NOT NULL,
        namespace VARCHAR NOT NULL,
        value JSON NOT NULL,
        CONSTRAINT {self.table_name}:unique_key_namespace UNIQUE (key, namespace),
        INDEX {self.table_name}:idx_key_namespace (key, namespace)
        );"""
        await self.engine.aexecute_query(create_query)

    def put(
        self,
        key: str,
        val: dict,
        collection: str = DEFAULT_COLLECTION,
    ) -> None:
        """Put a key-value pair into the store.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        self.put_all([(key, val)], collection=collection)

    async def aput(
        self,
        key: str,
        val: dict,
        collection: str = DEFAULT_COLLECTION,
    ) -> None:
        """Put a key-value pair into the store.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        await self.aput_all([(key, val)], collection=collection)

    def put_all(
        self,
        kv_pairs: List[Tuple[str, dict]],
        collection: str = DEFAULT_COLLECTION,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        self.engine._run_as_sync(self.aput_all(kv_pairs=kv_pairs,collection=collection, batch_size=batch_size))

    def aput_all(
        self,
        kv_pairs: List[Tuple[str, dict]],
        collection: str = DEFAULT_COLLECTION,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        self.engine._run_as_async(self.aput_all(kv_pairs=kv_pairs,collection=collection, batch_size=batch_size))

    async def _aput_all(
        self,
        kv_pairs: List[Tuple[str, dict]],
        collection: str = DEFAULT_COLLECTION,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        from sqlalchemy import text

        self._initialize()

        for i in range(0, len(kv_pairs), batch_size):

            batch = kv_pairs[i : i + batch_size]
            # Prepare the VALUES part of the SQL statement
            values_clause = ", ".join(
                f"({key}, collection, {value})"
                for key, value in batch
            )

            #Insert statement
            stmt = text(
                    f"""
                INSERT INTO {self.schema_name}.{self.table_name} (key, namespace, value)
                VALUES {values_clause}
                ON CONFLICT (key, namespace)
                DO UPDATE SET
                value = EXCLUDED.value;
                """
                )
            await self.engine.aexecute_query(stmt)

    def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]:
        """Get a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """

    async def aget(
        self, key: str, collection: str = DEFAULT_COLLECTION
    ) -> Optional[dict]:
        """Get a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """

    def get_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """Get all values from the store.

        Args:
            collection (str): collection name

        """

    async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """Get all values from the store.

        Args:
            collection (str): collection name

        """

    def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """Delete a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """

    async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """Delete a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
