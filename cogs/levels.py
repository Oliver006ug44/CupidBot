# Level Features for the bot
from discord import Embed, Member, Message, Interaction, File
from discord.app_commands import command, Group
from discord.ext.commands import Cog, is_owner, Bot
from database.levelesdb import Level, get_level, create_level, LevelNotFoundException

from imagegen import generate_level, int_to_ordinal

import random

class Levels(Cog):
    def __init__(self, bot:Bot) -> None:
        self.bot = bot
        super().__init__()
    
    # event listener for level ups
    @Cog.listener('on_message')
    async def level_xp_gain(self, message:Message):
        return
        user = message.author
        if user.bot or not message.guild: return
        try: level = get_level(self.bot)
        except LevelNotFoundException: level = create_level(self.bot, user)
        multiplier = 1
        if user.premium_since: multiplier = 1.5


        state, msg = level.inc_xp(multiplier)
        

    @command()
    async def leaderboard(self, interaction:Interaction):
        await interaction.response.send_message('Under Construction!', ephemeral=True)



    levels = Group(name="level", description="A group of level based commands", default_permissions=None)
    



    @levels.command(name="edit", description="edits a users level data")
    async def level_set_xp(self, interaction:Interaction, member:Member, level:int, xp:int):
        await interaction.response.send_message('Under Construction!', ephemeral=True)
    


    

    
