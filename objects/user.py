from sql.base import db_create_pool
import time
from random import choice as random_choice

from objects.topic import Topic, topics
from loguru import logger

import config

users = {}
class User:

    def __init__(self, user):
        self.id = user["id"]
        self.topics = user["topics"] if user["topics"] is not None else []
        self.companion = user["companion"]
        self.active_topic = user["active_topic"]
        self.opened = user["opened"]

        self.last_event_time = time.time() - 10
    
    async def get_ready(self):
        self.opened = True
    
    async def get_busy(self):
        self.opened = False
    
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
    
    def get_random_topic(self):
        ids = []
        for id in topics:
            if topics[id].author != self.id and users[topics[id].author].opened and topics[id].opened and topics[id].companion == -1:
                ids.append(id)
        if len(ids) == 0:
            return -1
        return random_choice(ids)
    
    async def start_discussion(self, topic_id):
        db = await db_create_pool()
        topics[topic_id].companion = self.id
        await db.execute(f"UPDATE topics SET companion = {self.id}")
        author = topics[topic_id].author
        users[author].companion = self.id
        users[author].active_topic = topic_id
        self.companion = author
        self.active_topic = topic_id
        await db.close()
    
    async def stop_discussion(self):
        db = await db_create_pool()
        topic_id = self.active_topic
        companion = self.companion
        users[companion].active_topic = -1
        users[companion].companion = -1
        self.active_topic = -1
        self.companion = -1

        topics[topic_id].companion = -1
        await db.execute("UPDATE topics SET companion = -1")
        await db.close()
    
    def remember_moment(self):
        self.last_event_time = time.time()
    
    def is_event_will_be_handled(self):
        time_now = time.time()
        diff = time_now - self.last_event_time
        if diff < config.USER_MSG_MAX_RATE:
            return False
        return True
