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
        user = message.author
        if user.bot or not message.guild: return
        try: level = get_level(self.bot)
        except LevelNotFoundException: level = create_level(self.bot, user)
        multiplier = 1
        if user.premium_since: multiplier = 1.5


        state, msg = level.inc_xp(multiplier)
        
        

        
        



    @command(description="View the level of yourself or another user")
    async def view_level(self, interaction:Interaction, member:Member=None, hidden:bool=False):
        await interaction.response.defer()
        if not member: member = interaction.user
        data:dict = levels_data.find_one({"user_id":member.id})
        leaderboard:list = sorted(levels_data.find(), key=lambda x:x.get('level'), reverse=True)
        user_ids = [record.get('user_id') for record in leaderboard] # make it easier to grab the index


        if not data:
            xp = 0
            level = 1
        else:
            xp = data.get("xp")
            level = data.get("level")

        
        rank_place= int_to_ordinal(user_ids.index(member.id) + 1)
        rank = f"{rank_place} Place"
        
        
        generate_level(member.name, level,rank,xp,member.avatar.url)
        file = File('output.png', filename=f"output_card.png")
        
        await interaction.followup.send(ephemeral=hidden, file=file)
    


    @command()
    async def leaderboard(self, interaction:Interaction):
        data:list = sorted(levels_data.find(), key=lambda x:x.get('level'), reverse=True)
        description = "\n".join(f"{i+1} | Level `{record.get('level')}` | Xp `{record.get('xp')}` |  {interaction.guild.get_member(int(record.get('user_id'))).mention}" for i, record in enumerate(data[0:10]))
        leaderboard_embed = Embed(title="Leaderboard", description=description, color=0xffa1dc)
        await interaction.response.send_message(embed=leaderboard_embed)



    levels = Group(name="level", description="A group of level based commands", default_permissions=None)
    



    @levels.command(name="set_xp", description="sets a users xp")
    async def level_set_xp(self, interaction:Interaction, member:Member, xp:int):
        if interaction.user.id != 1267552151454875751: return await interaction.response.send_message("Fuck you for trying casties")
        levels_data.update_one({"user_id":member.id}, {"$set":{"xp":xp}}, upsert=True)
        await interaction.response.send_message(f"I have set {member.mention}'s xp to `{xp}`")
    


    @levels.command(name="set_level", description="sets a users level")
    async def level_set_level(self, interaction:Interaction, member:Member, level:int):
        if interaction.user.id != 1267552151454875751: return await interaction.response.send_message("Fuck you for trying casties")
        levels_data.update_one({"user_id":member.id}, {"$set":{"level":level}}, upsert=True)
        await interaction.response.send_message(f"I have set {member.mention}'s level to `{level}`")

    
