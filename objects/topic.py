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
    
        