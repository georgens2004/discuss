from sql.base import db_create_pool

Users = {}
class User:

    def __init__(self, user):
        self.id = user["id"]
        self.username = user["username"]
        self.topics = user["topics"]
        self.companion = user["companion"]
    
    async def create_topic(self, text):
        db = await db_create_pool()
        topic_id = await db.fetch("SELECT currval('topics_id_sequence')")
        topic_id += 1
        await db.execute(f"INSERT INTO topics (id, author, text) VALUES (nextval('topics_id_squence'), {self.id}, {text})")
        await db.execute(f"UPDATE users SET topics = array_append(topics, {topic_id}) WHERE id = {self.id}")
        self.topics.append(topic_id)
        await db.close()
        
