import pymongo
from pymongo import MongoClient

class Mongo():
    def __init__(self):
        self.DOMAIN = 'localhost'
        self.PORT = 27017

    def getDatabase(self, database):
        client = MongoClient(self.DOMAIN, self.PORT)
        db = client[database]

        return db
