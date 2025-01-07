import asyncpg

class PostgreSQLBatchInserter:
    def __init__(self, db_config, table_name, batch_size=10000):
        self.db_config = db_config
        self.table_name = table_name
        self.batch_size = batch_size

    async def _connect(self):
        self.pool = await asyncpg.create_pool(**self.db_config)

    async def _close(self):
        await self.pool.close()

    async def insert_data(self, data):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                query = f"""
                INSERT INTO {self.table_name} (ip, ifindex, ontindex, capture, timecapture)
                VALUES ($1, $2, $3, $4, $5)
                """
                await connection.executemany(query, data)

    async def run(self, snmp_traffic):
        await self._connect()
        try:
            await snmp_traffic.main(self)
        finally:
            await self._close()