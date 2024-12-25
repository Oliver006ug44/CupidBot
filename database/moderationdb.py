from database.databasev2 import MODERATION
from discord import User, Embed
from discord.ext.commands import Bot



class NoDataException(BaseException):
    def __init__(self):
        super().__init__("No data was provided! Data object was empty")



class Case():
    def __init__(self, bot:Bot, data:dict, resp_id:str=None):
        self.id = data.get("id")
        self._id = resp_id if resp_id else str(data.get('_id'))
        self.target = bot.get_user(data.get("target_id"))
        self.target_name = data.get("target_name")
        self.moderator = bot.get_user(data.get("moderator_id"))
        self.type = data.get("type")
        self.reason = data.get("reason")
        self.duration = data.get("duration")
        self.proof = data.get("proof")
        self.embed = self.create_embed()

    def create_embed(self) -> Embed:
        embed=Embed(color=0xffd5a6)
        embed.add_field(name="Case:",value=f"`{self.id}`", inline=True)
        embed.add_field(name="Type:",value=f"`{self.type}`", inline=True)
        embed.add_field(name="Moderator:",value=f"`{self.moderator.name}`", inline=True)
        embed.add_field(name="Target:",value=f"{self.target.mention} | `{self.target_name}`", inline=False)
        embed.add_field(name="Reason:",value=f"`{self.reason}`", inline=False)
        embed.set_footer(text=f"Case ID: {self._id}")
        return embed


        



def create_case(bot:Bot, type:str, target:User, moderator:User, reason:str, *, duration=None, proof=None) ->Case:
    all_cases = [case for case in MODERATION.find()]
    case_id = len(all_cases) +1
    base_case = {
        "id":case_id,
        "target_id":target.id,
        "target_name":target.name,
        "moderator_id": moderator.id,
        "type":type,
        "reason":reason,
        "duration": duration if duration else 'N/A',
        "proof": proof if proof else 'N/A'
    }
    resp = MODERATION.insert_one(base_case)
    return Case(bot, base_case, str(resp.inserted_id))


def get_cases(bot, user:User) -> list[Case]:
    cases = [Case(bot, case) for case in MODERATION.find({'target_id':user.id})]
    return cases