# Level Features for the bot
from discord import Embed, Member, Message, Interaction, File
from discord.app_commands import command, Group
from discord.ext.commands import Cog, is_owner, Bot
from database.levelesdb import Level, get_level, create_level, LevelNotFoundException, LEVELS
from database.configdb import get_config

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
        try: level = get_level(self.bot, user)
        except LevelNotFoundException: level = create_level(self.bot, user)
        multiplier = 1
        if user.premium_since: multiplier = 1.5

        server_config = get_config(self.bot, message.guild.id)
        levels_chan = server_config.level_up_channel
        state, msg = level.inc_xp(multiplier)
        rewards = server_config.rewards.get_closest_reward(level.level) # get the closest reward

        
        user_roles = set(user.roles)
        new_roles = user_roles.difference(rewards.remove) | set(rewards.add) # the roles the user SHOULD have
        if user_roles != new_roles: await user.edit(roles=new_roles)

        if not state: return
        description = f"Congrats {user.mention}! you leveled up to `{level.level}`!"
        if rewards.level_rewards.data.get(str(level.level), None):
            description += f"""
            
            Roles Added: {", ".join(r.mention for r in rewards.add)}
            Roles Removed: {", ".join(r.mention for r in rewards.base_remove)}
            """

        level_up_embed = Embed(title="Level Up!", description=description)
        await levels_chan.send(embed=level_up_embed, content=f"{user.mention}")
        
        
        

    @command(description="A command to view all the top ranking members in a server")
    async def leaderboard(self, interaction:Interaction):
        users:list[Level] = []
        for base_data in LEVELS.find():
            user_id = base_data.get("user_id", None)
            if not user_id: continue
            try: users.append(get_level(self.bot, self.bot.get_user(int(user_id))))
            except: continue
            
        order = sorted(users, key=lambda x:x.level, reverse=True)

        description = "\n".join(f"{i+1} | Level `{level.level}` | Xp `{level.xp}` |  {level.user.mention}" for i, level in enumerate(order[0:10]))
        leaderboard_embed = Embed(title="Leaderboard", description=description, color=0xffa1dc)

        await interaction.response.send_message(embed=leaderboard_embed)



    levels = Group(name="level", description="A group of level based commands", default_permissions=None)
    
    


    @levels.command(name="edit", description="edits a users level data")
    async def level_set_xp(self, interaction:Interaction, member:Member, level:int=None, xp:int=None):
        if interaction.user.id != 1267552151454875751: return await interaction.response.send_message("Command is currently locked!")
        user_level = get_level(self.bot, member)
        old_level = user_level.level
        old_xp = user_level.xp

        new_level = old_level if level == None else level
        new_xp = old_xp if xp == None else xp
        
        user_level.edit({"$set":{"level":new_level,"xp":new_xp}})

        level_edit_embed = Embed(title="Level Edit", description=f"I have updated {member.mention}'s level to the following:\n\nlevel: `{old_level}` -> `{new_level}`\nxp: `{old_xp}` -> `{new_xp}`")
        await interaction.response.send_message(embed=level_edit_embed)

    


    

    
