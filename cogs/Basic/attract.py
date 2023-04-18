import nextcord
from nextcord.ext import commands
import random
import asyncio
import datetime
from datetime import datetime, timedelta, time

from test_database import *
from constants import *
from cogs.Utils.checks import *



class attract(commands.Cog):
    """ Player uses this command to attract MOFFS  """

    def __init__(self, bot: commands.bot):
        self.bot = bot
    
    @commands.command(aliases=["a","A","moffs","fart","Attract"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def attract(self, ctx: commands.context):
        
        ATTRACT_MIN = SETTINGS["attract_min"]
        ATTRACT_MAX = SETTINGS["attract_max"]
        
        now = datetime.datetime.today()
        discordUser = ctx.author
        discordID = ctx.author.id

        # Get db info
        document = find_player(discordID)
        document = list(document)
        
        # # Check if OK to attract
        pre_checks = ["channel", "time"]        
        if not await all_checks(pre_checks, ctx, document, "attract"):
            return
        
        # Check if player in town
        pos = get_player(document, "pos")
        if pos == 0:
            await ctx.send(f"{ctx.author.mention}"
            "The MOFFS in town are all busy, please don't distract them with your silly dance."
            "\nTry again after you leave town with `!bye`.")            
            return
                
        #    
        # OK to run command
        #

        # Raise min if players have shoes
        pumps = get_player(document, "inv", "pumps")
        fire = get_player(document, "inv", "fire_pumps")
        if pumps or fire > 0:
            ATTRACT_MIN += 5
            await ctx.send(f"{ctx.author.mention} Nice shoes!")
            await asyncio.sleep(1)

        # Roll D20 for attract amount
        roll = random.randint(ATTRACT_MIN, ATTRACT_MAX)
         
        # Update database
        db_attract(discordID, roll, now)
        
        # Attract messages
        if roll == 1:
            moffString = "MOFF. You're not feeling very attractive today."
        elif roll < 10:
            moffString = "MOFFS today. I suppose it could be worse."
        elif roll < 19:
            moffString = "MOFFS today. You are very attractive!"
        elif roll < 21:
            moffString = "MOFFS today. WOW! What's your secret to being one of the most attractive players in the game?"
            
        await ctx.send(f"{ctx.author.mention} <:ban20:885223732614938646> - You attracted {roll} {moffString}"
        "\nDid you `!roll` for your daily movement points today?"
        "\nUse `!p` at any time to check your progress and daily commands.")
        
        # Log
        print(f"{now} - {discordUser} attracted {roll}")


def setup(bot: commands.bot):
    bot.add_cog(attract(bot))