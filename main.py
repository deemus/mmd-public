import nextcord
from nextcord.ext import commands
from pretty_help import PrettyHelp
import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

import cogs.Utils.checks as checks
from cogs.Utils.checks import *

intents = nextcord.Intents.default()
intents.members = True
intents.messages = True

cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n-------")


bot = commands.Bot(
    command_prefix=";",
    help_command=PrettyHelp(),
    intents=intents
    )



@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

# load,reload and unload commands for the cogs
@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'extension {extension} loaded')

@bot.command()
async def reload(ctx, extension):
    bot.reload_extension(f'cogs.{extension}')
    await ctx.send(f'extension {extension} reloaded')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f'extension {extension} unloaded')




@bot.event
async def on_command_error(ctx, error):
    message = ''
    if isinstance(error, commands.CommandNotFound):
        message = "Command not recognized. Use `!help` for valid commands."
        await ctx.send(f"{ctx.author.mention} {message}", delete_after=5)
        await ctx.message.delete(delay=5)  

    elif isinstance(error, commands.CommandOnCooldown):
        message = "Relax. . . Take a breath. . . "
        await ctx.send(f"{ctx.author.mention} {message} {error}", delete_after=5)
        await ctx.message.delete(delay=5) 

    # elif isinstance(error, commands.JSONDecodeError):
    #     message = "There's a problem connecting to the WAX API right now. Try again later, or message @Deemaku if the problem continues.\n"
    #     message += "If you have **not** purchased or won a TAXICRAB Token, then you do **not** need to run this command."
    #     await ctx.send(f"{ctx.author.mention} {message}", delete_after=5)
    #     await ctx.message.delete(delay=15) 

    else:
        message = "An error occurred, Alerting <@274656402721472512>"
        await ctx.send(f"{ctx.author.mention} {message}")
        checks.BUSY = False
        print(error)

for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("__pycache"):
            bot.load_extension(f"cogs.{file[:-3]}")

#load cogs at the start of the bot
# bot.load_extension('cogs.oldhelp')
# bot.load_extension('cogs.attract')
# bot.load_extension('cogs.move')
# bot.load_extension('cogs.movelook')
# bot.load_extension('cogs.guess')
# bot.load_extension('cogs.register')
# bot.load_extension('cogs.progress')
# bot.load_extension('cogs.dragum')
# bot.load_extension('cogs.look')
# bot.load_extension('cogs.heist')
# bot.load_extension('cogs.taxi')
# bot.load_extension('cogs.inventory')
# bot.load_extension('cogs.dealer')
# bot.load_extension('cogs.gym')
# bot.load_extension('cogs.spire')
# bot.load_extension('cogs.trader')
# bot.load_extension('cogs.stats')
# bot.load_extension('cogs.pump')
# bot.load_extension('cogs.spear')
# bot.load_extension('cogs.power')


# # Testing
# bot.load_extension('cogs.mom')
# bot.load_extension('cogs.garden')

# # BETA ONLY COMMANDS
# bot.load_extension('cogs.reset')


#old
#bot.load_extension('cogs.assets')
#bot.load_extension('cogs.gib')
#bot.load_extension('cogs.ping')
#bot.load_extension('cogs.daily_reset')
#bot.load_extension('cogs.submit')



bot.run(os.getenv("TOKEN"))