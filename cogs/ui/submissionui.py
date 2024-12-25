from discord import ButtonStyle, Interaction, TextStyle
from discord.ext.commands import Bot
from discord.ui import View, Button, button, Modal, TextInput
from database.matchingdb import qet_queued, get_profile


 


class SubmissionView(View):
    def __init__(self, bot:Bot):
        self.bot = bot
        super().__init__(timeout=None)
        
    

    @button(label="Approve", style=ButtonStyle.green, custom_id="approved_id")
    async def approve(self, interaction:Interaction, button:Button):
        await interaction.response.defer()
        profile = qet_queued(interaction.message.id, self.bot)
        profile.edit({"$set": {"approved":True}, "$unset": {"message_id":"","date":""}})
        profile_embed = profile.generate_embed(color=0xb2f2bb)


        profile_embed.add_field(name="Approved", value=f"Approved by: {interaction.user.mention}")

        self.children[0].disabled = True
        self.children[1].disabled = True
        await interaction.edit_original_response(embed=profile_embed, view=self)
        try:
            await profile.user.send("Your profile was approved! use `/matching match` to start matching with people")
        except: await interaction.followup.send(f"I cant Dm {profile.user.mention}")
        gender = profile.gender
        if gender == 'Male':
            channel = interaction.guild.get_channel(1307474580008599663)
        elif gender == 'Female':
            channel = interaction.guild.get_channel(1307474598060883968)
        else:
            channel = interaction.guild.get_channel(1307480874119462952)
        
        
        msg = await channel.send(embed=profile.generate_embed())
        profile.edit({"$set":{"profile_message_id":msg.id, "profile_channel_id":msg.channel.id}}) # store the message just in case we re-submit

            

        




        


    @button(label="Deny", style=ButtonStyle.red, custom_id="deny_id")
    async def deny(self, interaction:Interaction, button:Button):
        profile = qet_queued(interaction.message.id, self.bot)
        profile.edit({"$set": {"approved":False}, "$unset": {"message_id":"","date":""}})
        

        profile_embed = profile.generate_embed(color=0xff8d8d)
        profile_embed.add_field(name="Denied", value=f"Denied by: {interaction.user.mention}")
        self.children[0].disabled = True
        self.children[1].disabled = True
        await interaction.response.edit_message(embed=profile_embed, view=self)
        try:
            await profile.user.send("Your profile was denied! this is usually because ur bio sucks and you should add more detail to it :)\n\nRun `/matching profile edit` to edit & resubmit your profiile`")
        except: await interaction.followup.send(f"I cant Dm {profile.user.mention}")
    

