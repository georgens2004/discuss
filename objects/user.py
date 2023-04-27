from sql.base import db_create_pool

from objects.topic import Topic, topics
from loguru import logger

from random import choice as random_choice

users = {}
class User:

    def __init__(self, user):
        self.id = user["id"]
        self.topics = user["topics"] if user["topics"] is not None else []
        self.companion = user["companion"]
        self.active_topic = user["active_topic"]
    
    async def create_topic(self, text):
        idx = 0
        while idx < len(text):
            if text[idx] == "'":
                text = text[:idx] + "'" + text[idx:]
                idx += 1
            idx += 1
        
        db = await db_create_pool()
        topic_id = await db.fetchval("SELECT nextval('topics_id_sequence')")
        topic_id -= 1
        await db.execute(f"INSERT INTO topics (id, author, text) VALUES ({topic_id}, {self.id}, '{text}')")
        await db.execute(f"UPDATE users SET topics = array_append(topics, {topic_id}) WHERE id = {self.id}")
        self.topics.append(topic_id)
        topics[topic_id] = Topic(await db.fetchrow(f"SELECT * FROM topics WHERE id = {topic_id}"))
        await db.close()
    
    async def delete_topic(self, topic_id):
        db = await db_create_pool()
        await db.execute(f"DELETE FROM topics WHERE id = {topic_id}")
        self.topics.remove(topic_id)
        del topics[topic_id]
        await db.execute(f"UPDATE users SET topics = array_remove(topics, {topic_id}) WHERE id = {self.id}")
        await db.close()

    async def open_topic(self, topic_id):
        db = await db_create_pool()
        await db.execute(f"UPDATE topics SET opened = TRUE WHERE id = {topic_id}")
        topics[topic_id].opened = True
        await db.close()

    async def close_topic(self, topic_id):
        db = await db_create_pool()
        await db.execute(f"UPDATE topics SET opened = FALSE WHERE id = {topic_id}")
        topics[topic_id].opened = False
        await db.close()
    
    async def get_random_topic(self):
        ids = []
        for id in topics:
            if topics[id].author != self.id and topics[id].opened and topics[id].companion == -1:
                ids.append(id)
        if len(ids) == 0:
            return -1
        return await random_choice(ids)
    