from sql.base import db_create_pool

topics = {}
class Topic:

    def __init__(self, topic):
        self.id = topic["id"]
        self.author = topic["author"]
        self.text = topic["text"]
        self.companion = topic["companion"]

        self.opened = topic["opened"]
        self.discussed_times = topic["discussed_times"]
        self.rating = topic["rating"]
        self.reports = topic["reports"]
    
    async def report(self):
        db = await db_create_pool()
        self.reports += 1
        await db.execute(f"UPDATE topics SET reports = {self.reports} WHERE id = {self.id}")
        await db.close()
    
    async def change_rating(self, diff):
        db = await db_create_pool()
        self.rating += diff
        await db.execute(f"UPDATE topics SET rating = {self.rating} WHERE id = {self.id}")
        await db.close()
