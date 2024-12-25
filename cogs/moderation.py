#Moderation Features for the bot
from discord import Embed, Member, Message, Interaction, Attachment, User
from discord.app_commands import command, describe, Group
from discord.ext.commands import Cog, Bot

from database.moderationdb import create_case, get_cases, Case

import time
from enum import Enum


class CaseType(Enum):
    warn = "warn"
    timeout = "timeout"
    kick = "kick"
    soft_ban = "soft_ban"
    ban = "ban"

    


class Moderation(Cog):
    def __init__(self, bot:Bot) -> None:
        super().__init__()
        self.bot = bot


    case = Group(name='case',description="A group of all case related commands")

    @case.command(name="create", description="creates a case against a user")
    @describe(
        user="The user to create a case on",
        type="The type of case to create",
        reason="The reason for this case's creation",
        duration="The duration in 1d 5h 3s format",
        proof="attached proof for this infraction"
    )
    async def case_create(self, interaction:Interaction, user:Member, type:CaseType, reason:str="None Provided", duration:str=None, proof:Attachment=None):
        case:Case = create_case(self.bot, type.value, user, interaction.user, reason)
        await interaction.response.send_message(embed=case.embed)
    

    @case.command(name='view', description="View all the cases a user has")
    async def case_view(self, interaction:Interaction, user:User):
        cases = get_cases(self.bot, user)
        data = {
            True: "...",
            False: ""
        }
        description = "\n".join(f"`{case.id}` | `{case.type}` | `{case.reason[0:20]}{data[len(case.reason) > 20]}`" for case in cases) if len(cases) > 0 else "No cases found!"
        cases_embed = Embed(title=f"All cases for {user.name}", description=description, color=0xffd5a6)
        await interaction.response.send_message(embed=cases_embed)


        
