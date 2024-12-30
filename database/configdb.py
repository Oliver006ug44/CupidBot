from discord.ext.commands import Bot
from discord import Guild
from database.databasev2 import CONFIG


class ConfigNotFoundException(BaseException):
    def __init__(self, message="The users level data doesnt exists!"):
        self.message = message
        super().__init__(self.message)



class Reward():
    def __init__(self, data:dict, server:Guild):
        self.data = data
        self.add = [server.get_role(r) for r in data.get('add', [])]
        self.remove = [server.get_role(r) for r in data.get('remove', [])]
        

class LevelRewards():
    def __init__(self, bot:Bot, data:dict, server:Guild):
        self.bot = bot
        self.data = data
        self.server = server
    
    def get_closest_reward(self, level) -> Reward:
        current_key = None
        keys = [int(k) for k in self.data.keys()]
        remove_roles = []
        for key in keys:
            if level > int(key):
                current_key = key
                reward_data:dict = self.data.get(str(key), {})
                remove_roles += reward_data.get('remove', [])


        
        
        data = {
            "add": reward_data.get('add', []),
            "remove": reward_data.get('remove', []) + remove_roles
        }

        return Reward(data, self.server)



class Config():
    def __init__(self, bot:Bot, data:dict=None):
        self.bot = bot
        if not data: raise ConfigNotFoundException()
        self.server = bot.get_guild(data.get('server_id'))
        self.rewards = LevelRewards(self.bot, data.get('level_rewards'),self.server)
        self.level_up_channel = self.server.get_channel(data.get('levelup_chan'))
        self.data = data

    
    def edit(self, data, upsert=False):
        CONFIG.update_one(self.doc, data, upsert=upsert)
        data = CONFIG.find_one(self.doc)
        self.__init__(self.bot, data)

    





def get_config(bot:Bot, server_id:int) -> Config:
    return Config(bot, CONFIG.find_one({'server_id':server_id}))

        
def create_config(bot:Bot, server_id:int) -> Config:
    pass
