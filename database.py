# Database Features for the bot
from pymongo import MongoClient
from discord import Member

client = MongoClient("mongodb://localhost:27017/")
cupid = client.get_database("cupid")
levels = cupid.get_collection('levels')
infractions = cupid.get_collection('infractions')
config = cupid.get_collection('config')
matching = cupid.get_collection('matching')



def generate_profile_description(user_id:int):
    data:dict = matching.find_one({'user_id':user_id})
    name = data.get('name', None) if data else None
    age = data.get('age', None) if data else None
    gender = data.get('gender', None) if data else None
    pronouns = data.get('pronouns', None) if data else None
    sexuality = data.get('sexuality', None) if data else None 
    bio = data.get('bio', None) if data else None
    resp_id = str(data.get('_id')) if data else None

    return f"❥﹒Name: `{name}`\n❥﹒Pronouns: `{pronouns}`\n❥﹒Gender: `{gender}`\n❥﹒Age: `{age}`\n❥﹒Sexuality: `{sexuality}`\n❥﹒Bio:\n```{bio}```", resp_id



def find_compatible_profiles(user_id: int, members: list[Member]):
    data: dict = matching.find_one({'user_id': user_id})
    if not data:
        return False, "You have no profile! Create one using `/matching profile create`"
    if not data.get('approved'):
        return False, "You haven't been approved! Please wait for it to be approved/denied."

    age = int(data.get('age'))
    user_ids = [member.id for member in members]
    rejected_ids = data.get('rejected_pairs', [])
    selected_ids = data.get('selected_pairs', [])

    profiles = []

    for profile in matching.find({'approved': True}):
        if (
            int(profile['user_id']) == user_id
            or profile['user_id'] not in user_ids
            or int(profile['age']) > age + 2
            or int(profile['age']) < age - 2
            or profile.get('paired') is True
            or profile['user_id'] in rejected_ids
            or profile['user_id'] in selected_ids
        ):
            continue
        
        profiles.append(profile)

    if not profiles:
        return False, "their is no one for you to match with, sorry!"
    
    return True, profiles