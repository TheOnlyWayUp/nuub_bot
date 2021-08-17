import discord
from discord.ext import commands
from helpers.logHelper import logger
import os
import logging
from pymongo import MongoClient
from helpers.getPrefix import getPrefix
import ast
from helpers.getWeather import getLocationKey, getWeather

logging.basicConfig(level=logging.INFO)
os.sys.path.append('/ffmpeg/bin')

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", None)

bot = commands.Bot(command_prefix="nb.", help_command=None)

MONGODB = os.environ.get("MONGODB", None)

bot = commands.Bot(command_prefix='*', help_command=None)

client = MongoClient(MONGODB)

db = client["discord"]
collection = db["bot"]


@bot.event
async def on_ready():
    print("Ready..")
    print("Logged in as: ", bot.user)
    print("Prefix: ", bot.command_prefix)
    print("Latency: ", round(bot.latency * 1000), "ms")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")
        else:
            print(f"Unable to load {filename}")
            logger.warning(
                f"Unable to load {filename}, is it suppose to be in cog directory?"
            )
    try:
        bot.run(DISCORD_TOKEN)
        logger.info(
            "Bot Is Off\n----------------------------------- END OF SESSION")
    except Exception as e:
        logger.warning(f"Unable to load cog: {e}")


@bot.event
async def on_guild_join(guild):
    guild_id = guild.id
    collection.insert_one({"_id": guild_id, "prefix": ","})
    print("done")


@bot.command(help="Chage prefix command, Refactor into base cog?")
async def prefix(ctx, prefix):
    collection.update_one({"_id": ctx.guild.id}, {"$set": {"prefix": prefix}})
    await ctx.send(embed=discord.Embed(title="Updated Prefix: ",
                                       description=f"New prefix: {prefix}"))


@bot.command("Help command in bot.py file, refactor into help cog?")
async def helpv1(ctx):
    docstring_values = await __parse_docstrings()
    caller_message = ctx.message.content
    if len(caller_message.split()) == 1:
        # The message which called the help command has no params
        message_text = "Available Commands:\n```\n"
        for cog in docstring_values.keys():
            message_text += f"* {cog}"
        message_text += "\n```"
        await ctx.send(message_text)
    else:
        # The command has parameters, search for cog with required name
        cog = caller_message.split()[1]
        try:
            em = discord.Embed()
            em.add_field(name="name", value=cog, inline=False)
            for key, value in docstring_values[cog].items():
                em.add_field(name=key, value=value, inline=False)
            await ctx.send(embed=em)
        except:
            em = discord.Embed(title="Error",
                               description=f"Could not find command {cog}")
            await ctx.send(embed=em)


async def __parse_docstring(filename):
    with open(filename, "r") as f:
        contents = f.read()
    module = ast.parse(contents)
    docstring = ast.get_docstring(module)
    if not docstring:
        docstring = "description: <Unknown>\n" + "syntax: <Unknown>"
    return {
        line.split(": ")[0]: "".join(line.split(": ")[1:])
        for line in docstring.split("\n") if line.strip()
    }


async def __parse_docstrings():
    values = {}
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            values[filename.strip(".py")] = await __parse_docstring(
                os.path.join("cogs", filename))
    return values


try:
    bot.run(DISCORD_TOKEN)
    logger.info(
        "Bot Is Off\n----------------------------------- END OF SESSION")
except Exception as e:
    logger.warning(f"Bot Failed to initialise: {e}")
