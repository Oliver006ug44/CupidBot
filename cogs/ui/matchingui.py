from discord.ui import Select, View, Modal, TextInput, button, DynamicItem
from discord import Button, ButtonStyle, Interaction, TextStyle, Embed, SelectOption, User
from discord.ext.commands import Bot
from database.matchingdb import get_profile
import random
from asyncio import sleep



class SwipeView(View):
    def __init__(self, user:User, bot):
        super().__init__(timeout=None)
        self.user = user
        self.bot:Bot = bot
    
    @button(label='Swipe Left', emoji="⬅️")
    async def swipe_left(self, interaction:Interaction, button:Button):
        await interaction.response.defer()
        
        profile = get_profile(interaction.user, self.bot)
        profile.edit({'$push': {'rejected_pairs': self.user.id}})
        

        random_profile = profile.get_random_profile()
        random_profile_embed = random_profile.generate_embed()


        await interaction.edit_original_response(embed=random_profile_embed, view=SwipeView(self.user, self.bot))
        
    
    @button(label='Swipe Right', emoji="➡️")
    async def swipe_right(self, interaction:Interaction, button:Button):
        await interaction.response.defer()

        profile = get_profile(interaction.user, self.bot)
        profile.edit({'$push': {'selected_pairs': self.user.id}})

        their_profile = get_profile(self.user, self.bot)
        their_profile.edit({"$push": {'paired_with_us':interaction.user.id}})

        
        if interaction.user.id in their_profile.selected_pairs:
            await interaction.followup.send(f"Congrats! you and {self.user.mention} matched! Feel free to dm each other or smth... idfk", ephemeral=True)
            try:
                await self.user.send(f"You matched with {interaction.user.mention}! Feel free to dm each other")
            except: await interaction.followup.send("I couldnt dm them! you'll have to find a way to reach them!", ephemeral=True)
            await sleep(3)


        random_profile = profile.get_random_profile()
        random_profile_embed = random_profile.generate_embed()


        await interaction.edit_original_response(embed=random_profile_embed, view=SwipeView(self.user, self.bot))