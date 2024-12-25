from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")

cupid = client.get_database("cupid")
LEVELS = cupid.get_collection('levels')
INFRACTIONS = cupid.get_collection('infractions')
MODERATION = cupid.get_collection('moderation')
CONFIG = cupid.get_collection('config')
MATCHING = cupid.get_collection('matching')


class NoProfileException(Exception):
    """
    Custom exception raised when a user profile is not found.

    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="No profile found for the user."):
        self.message = message
        super().__init__(self.message)
