from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")

cupid = client.get_database("cupid")
LEVELS = cupid.get_collection('levels')
INFRACTIONS = cupid.get_collection('infractions')
MODERATION = cupid.get_collection('moderation')
CONFIG = cupid.get_collection('config')
MATCHING = cupid.get_collection('matching')



class UserNotFoundException(BaseException):
    def __init__(self, message="The discord user is out of scope of the bot"):
        self.message = message
        super().__init__(self.message)