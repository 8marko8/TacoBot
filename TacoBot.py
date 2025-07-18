import discord
from discord.ext import commands
import json
import random
# data
def load_data_tacos(path="TacoBot/tacos.json"):
    with open(path, "r") as f:
        return json.load(f)
def save_data_tacos(data, path="TacoBot/tacos.json"):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
with open("TacoBot/menu.json", "r") as f:
    menu_data = json.load(f)
with open("TacoBot/cmds.json", "r") as f:
    cmd_data = json.load(f)
def load_inv(path="TacoBot/inv.json"):
    with open(path, "r") as f:
        return json.load(f)
def save_inv(data, path="TacoBot/inv.json"):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
# other
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=";", intents=discord.Intents.all())
botToken = "Hidden"
general_id = 0 # Replace this with the channel_id that you want the bot to send the message in.
def randomize():
    return random.randint(0, 1) == 1 
# script
@bot.event
async def on_ready():
    if general_id:
        general = bot.get_channel(general_id)
        await general.send(f"I'm online in #{general.name} ({general_id})")
    else:
        return
@bot.command()
async def bet(ctx, amount):
    tacos_data = load_data_tacos()
    uid = str(ctx.author.id)
    utacos = tacos_data.get(uid, 0)
    if uid not in tacos_data:
        tacos_data[uid] = 1000
    if amount.lower() == 'all':
        amount = utacos
    amount = int(amount)
    if amount > utacos:
        await ctx.send("Can't afford that. Brokie.")
        return
    tacos_data[uid] -= amount
    if randomize():
        winnings = amount + amount * 2
        tacos_data[uid] += winnings
        await ctx.send(f"You won! You now have **{tacos_data[uid]:}** tacos. 🌮")
    else:
        await ctx.send(f"You lost! You now have **{tacos_data[uid]:}** tacos. 🌮")
    save_data_tacos(tacos_data)
@bot.command()
async def balance(ctx, user: discord.User = None):
    tacos_data = load_data_tacos()
    if str(ctx.author.id) not in tacos_data:
        tacos_data[str(ctx.author.id)] = 1000
    if user is None:
        user = ctx.author
    uid = str(user.id)
    balance = tacos_data.get(uid, 0)
    await ctx.send(f"{user.mention} has **{balance:}** tacos. 🌮")
    save_data_tacos(tacos_data)
# you found an easter egg
@bot.command()
async def pay(ctx, user: discord.User, amount):
    tacos_data = load_data_tacos()
    sender_id = str(ctx.author.id)
    receiver_id = str(user.id)
    if sender_id not in tacos_data:
        tacos_data[sender_id] = 1000
    if receiver_id not in tacos_data:
        tacos_data[receiver_id] = 1000
    if amount.lower() == 'all':
        amount = tacos_data[sender_id]
    amount = int(amount)
    if amount < 1:
        await ctx.send("Invalid amount. Please enter a positive integer.")
        return
    if amount > tacos_data[sender_id]:
        await ctx.send("Can't afford that. Brokie.")
        return
    tacos_data[sender_id] -= amount
    tacos_data[receiver_id] += amount
    await ctx.send(f"<@{ctx.author.id}> just paid {user.mention} **{amount}** tacos(s)! 🌮")
    save_data_tacos(tacos_data)
@bot.command()
async def admingive(ctx, user: discord.User, amount: int):
    tacos_data = load_data_tacos()
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not an admin!")
        return
    receiver_id = str(user.id)
    if receiver_id not in tacos_data:
        tacos_data[receiver_id] = 1000
    if amount < 1:
        await ctx.send("Invalid amount. Please enter a positive integer.")
        return
    tacos_data[receiver_id] += amount
    await ctx.send(f"<@{ctx.author.id}> just gave {user.mention} **{amount}** tacos(s) as an admin! 🌮")
    save_data_tacos(tacos_data)
@bot.command()
async def lb(ctx):
    tacos_data = load_data_tacos()
    lb_tacos = sorted(tacos_data.items(), key=lambda x: x[1], reverse=True)
    lb_tacos = dict(lb_tacos)
    embed = discord.Embed(
        title="Leaderboard (tacos)"
    )
    for idx, (user, tacos) in enumerate(lb_tacos.items(), start=1):
        user = await bot.fetch_user(user)
        user = user.name
        name = "undefined"
        if idx == 1:
            name = f"🥇 {user}"
        elif idx == 2:
            name = f"🥈 {user}"
        elif idx == 3:
            name = f"🥉 {user}"
        else:
            name = f"{idx}. {user}"
        embed.add_field(name=name, value=f"`{tacos}` tacos", inline=False)
    await ctx.send(embed=embed, allowed_mentions=discord.AllowedMentions(users=True))
@bot.command()
async def shop(ctx):
    roleEmbed = discord.Embed(
        title="Role Shop",
        description=(
            "- <@&Role_id_here> - 200,000,000 🌮 " # Replace with role id
        ),
        color=discord.Color.gold()
    )
    itemEmbed = discord.Embed(
        title="Item Shop",
        description=(
            "- 1x Nacho - 100 🌮\n" +
            "- 1x Quesadilla - 1,000 🌮\n" +
            "- 1x Burrito - 2,500 🌮\n" +
            "- 1x Marko's Special Sauce - 1,000,000 🌮"
        ),
        color=discord.Color.gold()
    )
    await ctx.send(content="Welcome to the shop.", embeds=[itemEmbed, roleEmbed])
@bot.command()
async def buy(ctx, item: str, amount: int):
    tacos_data = load_data_tacos()
    inventory = load_inv()
    userid = str(ctx.author.id)
    if item not in list(menu_data.keys()):
        await ctx.send("Invalid item, choose one from the shop! (Case Sensitive)")
        return
    elif amount <= 0:
        await ctx.send("Invalid amount, please enter a positive integer!")
        return
    if userid not in inventory:
        inventory[userid] = {item: 0 for item in menu_data.keys()}
    inventory[userid][item] += amount
    tacos_data[userid] -= amount * menu_data.get(item)
    await ctx.send(f"Bought {amount}x {item}(s)! <@{userid}>")
    save_data_tacos(tacos_data)
    save_inv(inventory)
@bot.command()
async def showInv(ctx, user: discord.Member = None):
    tacos_data =load_data_tacos()
    if user is None:
        user = ctx.author
    inventory = load_inv()
    userid = str(user.id)
    invLine = []
    for item, amount in inventory[userid].items():
        invLine.append(f"**x{amount}** {item}(s)")
    invLine = '\n'.join(invLine)
    embed = discord.Embed(
        title=f"{user.name}'s inventory",
        description=invLine
    )
    embed.set_author(name=f"Tacos: {tacos_data[userid]:,}")
    await ctx.send(embed=embed)
@bot.command()
async def cmds(ctx):
    embed = discord.Embed(
        title="Taco Bot Commands"
    )
    for cmd, desc in cmd_data.items():
        embed.add_field(name=cmd, value=desc, inline=False)
    await ctx.send(embed=embed)
bot.run(botToken)
# Made by 98marko and obrules_ on Discord
# This is my first time publishing a Discord bot, that's why there's a lot of hard-coded variables
# Thank you