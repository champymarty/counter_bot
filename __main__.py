import discord
import os
from dotenv import load_dotenv


# load .env variables
load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
file_separator = " "

file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "houses.txt")

channels_to_house = {
    966687401672069150: {"house": "Gryffindor", "score": 0},
    966687678630338630: {"house": "Slytherin", "score": 0},
    966687711962484766: {"house": "Ravenclaw", "score": 0},
    966687717427642378: {"house": "Hufflepuff", "score": 0},
}

leaderboard_channel_id =  969205890701987850

role_to_points = {
    "<:no1:943876176835928085>": 1,
    "<:no2:943876198403014787>": 2,
    "<:no3:943876218837684237>": 3,
    "<:no5:943876257370746920>": 5,
}

points_to_claim = None

listen_members_id = {
    493716749342998541
}

bot : discord.Bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))
    if os.path.isfile(file):
        with open(file, "r") as houseFile:
            lines = houseFile.readlines()
            scores = lines[0].strip().split(file_separator)
            i = 0
            for info in channels_to_house.values():
                info["score"] = int(scores[i])
                i += 1
            
    
@bot.event
async def on_message(message: discord.Message):
    global points_to_claim
    if message.content.startswith(".point"):
        await points_command(message)
    if message.channel.id == leaderboard_channel_id:
        await leaderboard_claim_point(message)
    elif message.channel.id in channels_to_house and message.author.id in listen_members_id:
        await new_mimu_house_command(message)
        
async def leaderboard_claim_point(message: discord.Message):
    global points_to_claim
    text = build_text(message)
    print(text)
    try:
        if points_to_claim is not None and "𝐂𝐥𝐚𝐢𝐦𝐞𝐝 𝐏𝐨𝐢𝐧𝐭!" in text:
            if add_points_leaderboard(text):
                emoji = '\N{THUMBS UP SIGN}'
                await message.add_reaction(emoji)
        elif points_to_claim is None and "𝐑𝐚𝐧𝐝𝐨𝐦 𝐏𝐨𝐢𝐧𝐭 𝐃𝐫𝐨𝐩" in text:
            for role, points in role_to_points.items():
                if role in text:
                    points_to_claim = points
                    break
            emoji = '\N{THUMBS UP SIGN}'
            await message.add_reaction(emoji)
    except TypeError:
        pass 
        
async def points_command(message: discord.Message):
    desceription = ""
    i = 1
    for info in channels_to_house.values():
        if info["house"] is not None:
            desceription += "{}) {} with {} points ! \n".format(i, info["house"], info["score"])
        i += 1
    embed = discord.Embed(title="points !!!!!", description=desceription)
    embed.set_footer(text="Ps: Fini and nezuko are the best princesses")
    await message.channel.send(embed=embed)
        
async def new_mimu_house_command(message: discord.Message):
    text = ""
    text += message.content
    try:
        for embed in message.embeds:
            text += embed.description
            for field in embed.fields:
                text +=  field.name
                text +=  field.value
        if add_points(text, channels_to_house[message.channel.id]):
            emoji = '\N{THUMBS UP SIGN}'
            await message.add_reaction(emoji)
    except TypeError:
        pass
    
def build_text(message: discord.Message):
    text = ""
    text += message.content
    try:
        for embed in message.embeds:
            text += embed.description
            for field in embed.fields:
                text +=  field.name
                text +=  field.value
    except TypeError:
        pass
    return text
        
def add_points_leaderboard(text: str):
    house = text.strip().split("**")[1]
    for houseInfo in channels_to_house.values():
        if houseInfo["house"].lower() == house.lower():
            houseInfo["score"] += points_to_claim
            write_houses()
            points_to_claim = None
            return True
    return False
        
def add_points(text: str, info):
    for key, points in role_to_points.items():
        if key in text:
            info["score"] += points
            print("{} point added to {}".format(points, info["house"]))
            write_houses()
            return True
    return False
        
def write_houses():
    with open(file, "w") as fileWrite:
        line = ""
        for info in channels_to_house.values():
            line += "{} ".format(info["score"])
        fileWrite.write(line)

bot.run(os.getenv("TOKEN"))