from discord.ui import View, Button, button, Modal, TextInput, Select
from discord import ButtonStyle, Member, Interaction, TextStyle, Embed, SelectOption
from database.matchingdb import get_profile, MATCHING
from cogs.ui.submissionui import SubmissionView
from discord.ext.commands import Bot


class TosConfirmationView(View):
    def __init__(self, user:Member, bot:Bot):
        self.responded = False
        self.bot = bot
        super().__init__(timeout=180)

    
    @button(label="Confirm",custom_id="confirm_tos_button", style = ButtonStyle.green)
    async def tos_confirm(self, interaction:Interaction, button:Button):
        if self.responded:
            return await interaction.response.send_message("You already responded to this!", ephemeral=True)
        
        self.responded = True
        MATCHING.insert_one({"user_id":interaction.user.id, "tos_agreed":True})
        await interaction.response.send_message("Done! Feel free to re-run the command", ephemeral=True)


# TODO
## 1.)  move to 1 select menu with custom name and stuff, just take in options as kwarg
class ProfileGenderSelect(Select):
    def __init__(self, bot:Bot):
        self.bot = bot
        options = [
            SelectOption(label="Male"),
            SelectOption(label="Female"),
            SelectOption(label="Other", description="Please specify in bio"),
        ]
        super().__init__(custom_id="profile_gender", placeholder="Select Your Gender", min_values=1, max_values=1, options=options)


    async def callback(self, interaction:Interaction):
        profile = get_profile(interaction.user, self.bot)
        profile.edit({"$set":{"gender":self.values[0]}})
        await interaction.response.edit_message(embed=profile.generate_embed())


class ProfileAgeSelect(Select):
    def __init__(self, bot:Bot):
        self.bot = bot
        options = [SelectOption(label=f"{age}") for age in range(13,24)]
        super().__init__(custom_id="profile_age", placeholder="Select Your Age", min_values=1, max_values=1, options=options)


    async def callback(self, interaction:Interaction):
        profile = get_profile(interaction.user, self.bot)
        profile.edit({"$set":{"age":int(self.values[0])}})
        await interaction.response.edit_message(embed=profile.generate_embed())
        

class ProfileSexualitySelect(Select):
    def __init__(self, bot:Bot):
        self.bot = bot
        options = [
            SelectOption(label="Heterosexual"),
            SelectOption(label="Homosexual"),
            SelectOption(label="Bisexual"),
            SelectOption(label="Other"),
        ]
        super().__init__(custom_id="profile_sexuality", placeholder="Select Your Sexuality", min_values=1, max_values=1, options=options)


    async def callback(self, interaction:Interaction):
        profile = get_profile(interaction.user, self.bot)
        profile.edit({"$set":{"sexuality":self.values[0]}})
        await interaction.response.edit_message(embed=profile.generate_embed())



class ProfileEditModal(Modal):
    def __init__(self, user:Member, bot:Bot):
        self.bot = bot
        super().__init__(title="Edit Profile", timeout=None, custom_id="edit_profile_modal")
        try:
            profile = get_profile(user, bot)
            
            self.name.default = profile.name
            self.pronouns.default = profile.pronouns
            self.bio.default = profile.bio
        except:pass
        

    
    name = TextInput(label="Name", style=TextStyle.short)
    pronouns = TextInput(label="Pronouns", style=TextStyle.short)
    bio = TextInput(label="Bio", style=TextStyle.paragraph)

    async def on_submit(self, interaction:Interaction):

        profile = get_profile(interaction.user, self.bot)
        profile.edit({"$set":{"name":self.name.value,"pronouns":self.pronouns.value,"bio":self.bio.value}})

        await interaction.response.edit_message(embed=profile.generate_embed())



class ProfileCreationView(View):
    def __init__(self, bot:Bot, editing=False):
        super().__init__(timeout=None)
        self.add_item(ProfileSexualitySelect(bot))
        self.add_item(ProfileAgeSelect(bot))
        self.add_item(ProfileGenderSelect(bot))
        self.edit = editing
        self.bot:Bot = bot
        if editing:
            self.children[1].label = "Resubmit"
    
    @button(label="Edit Profile", style=ButtonStyle.gray)
    async def edit_profile(self, interaction:Interaction, button:Button):
        await interaction.response.send_modal(ProfileEditModal(interaction.user, self.bot))

    
    @button(label="Submit Profile", style=ButtonStyle.green)
    async def submit_profile(self, interaction:Interaction, button:Button):
        # send profile to home server, and wait for verifcation
        profile = get_profile(interaction.user, self.bot)
        # delete the old profile message
        if profile.profile_message_id:
            channel = interaction.guild.get_channel(profile.profile_channel_id)
            message = await channel.fetch_message(profile.profile_message_id)
            await message.delete()
            profile.edit({"$unset": {"profile_message_id":"", "profile_channel_id":""}})
        
        if profile.approved == "waiting" or profile.approved == False and not self.edit:
            return await interaction.response.send_message('Your profile was already submitted!', ephemeral=True)
        
        guild = self.bot.get_guild(1282801630575595572)
        verifcation_channel = guild.get_channel(1307474634559459360)
        msg = await verifcation_channel.send("Waiting..")

        await msg.edit(content="", embed=profile.generate_embed(color=0xfffacd), view=SubmissionView(self.bot))
        profile.queue_profile(msg.id)
        profile.edit({"$set":{"approved":"waiting"}})
        await interaction.response.send_message("Submitted! it may take up to 24 hours to be approved!", ephemeral=True)

