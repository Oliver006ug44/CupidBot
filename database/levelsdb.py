from discord.ext.commands import Bot
from discord import User
from database.databasev2 import LEVELS, UserNotFoundException

import random
import time
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO



class LevelNotFoundException(BaseException):
    def __init__(self, message="The users level data doesnt exists!"):
        self.message = message
        super().__init__(self.message)


class Level():
    def __init__(self, bot:Bot, data:dict=None):
        self.bot = bot
        if not data: raise LevelNotFoundException()
        self.user_id = data.get('user_id')
        self.user = bot.get_user(data.get('user_id'))
        if not self.user: raise UserNotFoundException()
        self.level = data.get('level', 0)
        self.xp = data.get('xp', 0)
        self._id = data.get('_id')
        self.doc = {'_id':self._id}
        self.date = data.get('date', 0)
    
    def edit(self, data, upsert=False):
        LEVELS.update_one(self.doc, data, upsert=upsert)
        data = LEVELS.find_one(self.doc)
        self.__init__(self.bot, data)

    def inc_xp(self, mul:int=1) -> tuple[bool, str]:
        """Randomly increases the users xp between 1-45

        Args:
            mul (int, optional): a multiplier to apply to the xp gained. Defaults to 1.

        Returns:
            tuple[bool, str]: true if level up, with a message provided
        """
        state = False
        message = ""
        num = int(random.randint(0,45) * mul)
        xp_required = self.level * 100 if self.level != 0 else 50
        new_xp = self.xp + num

        if new_xp > xp_required:
            self.xp = new_xp%xp_required
            self.level += 1
            state = True
            message = f"Congrats {self.user.mention}! You have leveled up to `{self.level}`"
        else:
            self.xp = new_xp

        self.edit({"$set":{"xp":self.xp,"level":self.level,"date":int(time.time())}})

        return state, message
    
    def get_rank(self):
        all_users = [u for u in LEVELS.find()]
        parsed_levels:list[Level] = [get_level(self.bot, self.bot.get_user(u.get('user_id'))) for u in all_users if self.bot.get_user(u.get('user_id'))]
        sorted_levels = sorted(parsed_levels, key=lambda rank:rank.level, reverse=True)
        for i, level in enumerate(sorted_levels):
            if level.user == self.user:
                return i+1
        
        return 1000
    
    def make_rounded_image(self, image:Image, size=(96, 96)):
        image = image.resize((96,96))
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        rounded_image = ImageOps.fit(image, size, centering=(0.5, 0.5))
        rounded_image.putalpha(mask)
        return rounded_image, mask


    def generate_rank_card(self):
        level_data = self
        user = level_data.user
        level = level_data.level
        xp = level_data.xp

        background = Image.open('images/rank_bg.png')
        avatar_data = BytesIO(requests.get(user.avatar.url).content)
        avatar_image =  Image.open(avatar_data)

        username_font = ImageFont.truetype("font/Inter_28pt-Bold.ttf", 40)
        level_font = ImageFont.truetype("font/Inter_24pt-Bold.ttf", 36)
        rank_font = ImageFont.truetype("font/Inter_24pt-Bold.ttf", 24)
        xp_font = ImageFont.truetype("font/Inter_24pt-Bold.ttf", 20)

        rounded_avatar, mask = self.make_rounded_image(avatar_image)
        background.paste(rounded_avatar, (10,10), mask)
        draw = ImageDraw.Draw(background)

        draw.text((118, 19), f"{user.name}", font=username_font)
        draw.text((118, 67), f"Level: {level}", font=level_font, fill=0xffC5C5C5)

        draw.text((10, 113), f"Rank: {level_data.get_rank()}", font=rank_font, fill=0xffC5C5C5)
        draw.text((10, 142), f"Messages: N/A", font=rank_font, fill=0xffC5C5C5)

        width, heigth = 460, 24
        rect_x, rect_y = 10, 236
        percentage = xp/(level*100)

        draw.rounded_rectangle((rect_x, rect_y,rect_x+width, rect_y+heigth),3,0xffffffff, outline=0xffffffff, width=3) # bg rect
        draw.rounded_rectangle((rect_x, rect_y,rect_x+width*percentage, rect_y+heigth-1),3,0xffffa1dc) # bg rect

        xp_text = f"{xp}/{level*100}"
        text_bbox  = draw.textbbox((0,0), xp_text, font=xp_font)
        text_width = text_bbox[2] - text_bbox[0]
        image_width = background.width
        x = (image_width - text_width) // 2  # Center horizontally
        draw.text((x,236), xp_text, font=xp_font, fill=0xff7E7E7E)



        background.save("images/output.png")






def get_level(bot:Bot, user:User) -> Level:
    """gets the level of a user

    Args:
        bot (Bot): the bot to be able to do the .get_user() call
        user (User): user user to get the level of

    Returns:
        Level: the level object of the user
    """
    return Level(bot, LEVELS.find_one({"user_id":user.id}))

        
def create_level(bot:Bot, user:User) -> Level:
    """Creates a level for a user

    Args:
        bot (Bot): the bot to be able to do the .get_user() call
        user (User): the user for the level to be created from

    Returns:
        Level: the level object of the user
    """
    data = {
        "user_id":user.id,
        "level":0,
        "xp":0
    }
    level = Level(bot, data)
    level.edit({"$set":data}, upsert=True)
    return level
