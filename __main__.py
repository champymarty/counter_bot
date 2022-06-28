import pickle
import discord
import os
from dotenv import load_dotenv

from Comfirm import Confirm


guildIds = [787837042724700190] # kiki server
guildIds = None

# load .env variables
load_dotenv()
intents = discord.Intents.default()
intents.message_content = True

file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "members.txt")

member_to_points = { }

command_channel_id = {
    988476017901445220,
    988476135413256253,
}

role_to_points = {
    "<:no1:943876176835928085>": 1,
    "<:no2:943876198403014787>": 2,
    "<:no3:943876218837684237>": 3,
    "<:no5:943876257370746920>": 5,
}

listen_members_id = {
    493716749342998541
}

bot : discord.Bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    load_data()
    print("We have logged in as {0.user}".format(bot))
            
@bot.slash_command(guild_ids=guildIds,  description="Show ranking")
async def ranking(ctx: discord.ApplicationContext):
    global member_to_points
    await ctx.defer()
    current_points = 0
    if str(ctx.author.id) in member_to_points:
        current_points = member_to_points[str(ctx.author.id)]
    
    if len(member_to_points) == 0:
        description = "No one have participated yet"
    else:
        i = 1
        description = ""
        for member_id, points in {k: v for k, v in sorted(member_to_points.items(), key=lambda item: item[1], reverse=True)}.items():
            member = await discord.utils.get_or_fetch(ctx.guild, "member", int(member_id))
            description += "{}) {} with {} points \n".format(i, member.mention, points)
            i += 1
    embed = discord.Embed(title="You have {} points".format(current_points), description=description)
    await ctx.respond(embed=embed)
    
@bot.slash_command(guild_ids=guildIds,  description="Get my current points")
async def check_points(ctx: discord.ApplicationContext,
                       member: discord.Option(
                            discord.Member, 
                            description="The member to check his/her points", required=False, default=None)):
    global member_to_points
    await ctx.defer()
    current_points = 0
    if member is None:
        if str(ctx.author.id) in member_to_points:
            current_points = member_to_points[str(ctx.author.id)]
        await ctx.respond("You have now {} points".format(current_points))
    else:
        if str(member.id) in member_to_points:
            current_points = member_to_points[str(member.id)]
        await ctx.respond(embed=discord.Embed(description="The user {} now have {} points".format(
            member.mention, current_points)))
    
@bot.slash_command(guild_ids=guildIds,  description="Add points to a member")
@discord.default_permissions(administrator=True)
async def add_points(ctx: discord.ApplicationContext, member: discord.Member, points: discord.Option(int)):
    global member_to_points
    await ctx.defer()
    if not str(member.id) in member_to_points:
        member_to_points[str(member.id)] = points
    else:
        member_to_points[str(member.id)] += points
    save_data()
    await ctx.respond(embed = discord.Embed(description="{} points where added to {}. New total is {} points".format(
        points, member.mention, member_to_points[str(member.id)] )))
    
@bot.slash_command(guild_ids=guildIds,  description="Remove points to a member")
@discord.default_permissions(administrator=True)
async def remove_points(ctx: discord.ApplicationContext, member: discord.Member, points: discord.Option(int)):
    global member_to_points
    await ctx.defer()
    if not str(member.id) in member_to_points:
        await ctx.respond(embed = discord.Embed(description="No points where remove because {} dont have any yet".format(
            member.mention
        )))
    else:
        member_to_points[str(member.id)] -= points
        save_data()
        await ctx.respond(embed = discord.Embed(description="{} points where remove from {}. New total is {} points".format(
            points, member.mention, member_to_points[str(member.id)])))
    
@bot.slash_command(guild_ids=guildIds,  description="Set points to a member")
@discord.default_permissions(administrator=True)
async def set_points(ctx: discord.ApplicationContext, member: discord.Member, points: discord.Option(int, min_value=0)):
    global member_to_points
    await ctx.defer()
    member_to_points[str(member.id)] = points
    save_data()
    await ctx.respond(embed = discord.Embed(description="{} now have {} points".format(member.mention, points)))
    
@bot.slash_command(guild_ids=guildIds,  description="Delete all the points data")
@discord.default_permissions(administrator=True)
async def clear_all_points(ctx: discord.ApplicationContext):
    global member_to_points
    view = Confirm()
    await ctx.respond("Do you really want to delete all the points of EVERYONE ?", view=view)
    await view.wait()
    if view.value:
        member_to_points = {}
        save_data()
        await ctx.respond(embed = discord.Embed(description="All data reset !"))
    
@bot.event
async def on_message(message: discord.Message):
    if message.channel.id in command_channel_id and message.author.id in listen_members_id:
        await new_mimu_house_command(message)
        
async def new_mimu_house_command(message: discord.Message):
    text = build_text(message)
    if "@" in text:
        member_id = text.split("@")[1].split(">")[0].strip()
        sorted_dict = {k: v for k, v in sorted(member_to_points.items(), key=lambda item: item[1])}        
        point_to_add = None
        for key, points in role_to_points.items():
            if key in text:
                point_to_add = points
                break
        
        if point_to_add is not None:
            emoji = '\N{THUMBS UP SIGN}'
            if not member_id in member_to_points:
                member_to_points[member_id] = point_to_add
            else:
                member_to_points[member_id] += point_to_add
            print("addind {} points to {}".format(point_to_add, member_id))
            save_data()
            await message.add_reaction(emoji)
    
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

def save_data():
    global member_to_points
    with open(file, "wb") as handle:
        pickle.dump(member_to_points, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def load_data():
    global member_to_points
    if os.path.isfile(file):
        with open(file, "rb") as handle:
            member_to_points = pickle.load(handle)
            print(member_to_points)
    else:
        member_to_points = {}


bot.run(os.getenv("TOKEN"))