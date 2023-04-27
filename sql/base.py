import asyncpg

from loguru import logger

from config import HOST, PG_USER, PG_PASSWORD, PG_DATABASE

async def db_create():
    # Recreating database tables
    create_db_command = open("sql/db_init.sql", 'r').read()

    logger.info("Connecting to db")
    conn: asyncpg.Connection = await asyncpg.connect (
        host = HOST,
        user = PG_USER,
        password = PG_PASSWORD,
        database = PG_DATABASE,
    )
    await conn.execute(create_db_command)
    logger.info("Created database tables")
    await conn.close()


async def db_create_pool():
    # Creating database connection pool
    return await asyncpg.create_pool (   
        host = HOST,
        user = PG_USER,
        password = PG_PASSWORD,
        database = PG_DATABASE,
    )

from objects.user import users
from objects.topic import Topic, topics

async def db_load_all_topics():
    global topics
    global opened_topics
    db = await db_create_pool()
    all_topics = await db.fetch("SELECT * FROM topics")
    for topic in all_topics:
        topics[topic["id"]] = Topic(topic)
    await db.close()
