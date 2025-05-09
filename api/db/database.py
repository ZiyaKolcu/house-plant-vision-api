import psycopg
from psycopg.rows import dict_row
from api.core.config import settings


class Database:
    _dsn: str = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

    @classmethod
    async def get_connection(cls):
        return await psycopg.AsyncConnection.connect(cls._dsn, row_factory=dict_row)

    @classmethod
    async def fetchrow(cls, query: str, *args):
        async with await cls.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                return await cur.fetchone()

    @classmethod
    async def execute(cls, query: str, *args):
        async with await cls.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
