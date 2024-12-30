from discord.ext.commands import Bot
from discord import User
from database.databasev2 import LEVELS, UserNotFoundException

import random
import time

class LevelNotFoundException(BaseException):
    def __init__(self, message="The users level data doesnt exists!"):
        self.message = message
        super().__init__(self.message)


class Level():
    def __init__(self, bot:Bot, data:dict=None):
        self.bot = bot
        if not data: raise LevelNotFoundException()
        self.user_id = data.get('user_id')
        self.user = bot.get_user(data.get('user_id'))
        if not self.user: raise UserNotFoundException()
        self.level = data.get('level', 0)
        self.xp = data.get('xp', 0)
        self._id = data.get('_id')
        self.doc = {'_id':self._id}
        self.date = data.get('date', 0)
    
    def edit(self, data):
        LEVELS.update_one(self.doc, data)
        data = LEVELS.find_one(self.doc)
        self.__init__(self.bot, data)

    def inc_xp(self, mul:int=1) -> tuple[bool, str]:
        """Randomly increases the users xp between 1-45

        Args:
            mul (int, optional): a multiplier to apply to the xp gained. Defaults to 1.

        Returns:
            tuple[bool, str]: true if level up, with a message provided
        """
        state = False
        message = ""
        num = int(random.randint(0,45) * mul)
        xp_required = self.level * 100 if self.level != 0 else 50
        new_xp = self.xp + num

        if new_xp > xp_required:
            self.xp = new_xp%xp_required
            self.level += 1
            state = True
            message = f"Congrats {self.user.mention}! You have leveled up to `{self.level}`"

        self.edit({"$set":{"xp":self.xp,"level":self.level,"date":int(time.time())}})

        return state, message





def get_level(bot:Bot, user:User) -> Level:
    return Level(bot, LEVELS.find_one({"user_id":user.id}))

        
