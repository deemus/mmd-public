# import nextcord
from nextcord.ext import commands
import random
import asyncio
from datetime import datetime

from cogs.Utils.checks import *
from test_database import *
from constants import *


class pump(commands.Cog):
    """ (ITEM) - Pump up your Pumps for bonus movement points, if you have them!  """

    def __init__(self, bot: commands.bot):
        self.bot = bot
    
    # @commands.cooldown(1, 20, commands.BucketType.user)
    @commands.command(aliases=["PUMP","Pump","pp","PP"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def pump(self, ctx):
        now = datetime.datetime.today()
        discordID = ctx.author.id
        discordUser = ctx.author      
        
        # Get db info
        document = find_player(discordID)
        document = list(document)

        # Check if OK to pump
        pre_checks = ["channel", "time"]
        if not await all_checks(pre_checks, ctx, document, "pump"):
            return   

        # Check for pumps
        fire_pumps = get_player(document, "inv", "fire_pumps")
        pumps = get_player(document, "inv", "pumps")
            
        if fire_pumps > 0:
            pump_style = "🔥Limited Edition Fired Up Pumps🔥"
            levelWeight = [45,45,10]
            # fired up
        elif pumps > 0:
            pump_style = "Pumped Up Pumps"
            levelWeight = [70,25,5]
            # pumped up
        else:
            await ctx.send(ctx.author.mention + "You look around for a button to pump up. . .")
            await asyncio.sleep(3)
            await ctx.send(ctx.author.mention + "You only found your belly!  It didn't gain you any points, but it felt pretty nice.")
            return
        
        # OK to pump
        
        # Already in town
        position = get_player(document, "pos")
        if position == 0:
            await ctx.send(f"{ctx.author.mention} Everyone in town stops what they're doing to check out your sweet kicks.")
            await asyncio.sleep(1)
        levels = [1,2,3]
        pump_amt = random.choices(levels, levelWeight, k=1)
        pump_amt = pump_amt[0]

        # Pluralize
        if pump_amt == 1:
            point_s = "point"
        else:
            point_s = "points"

        db_pump(discordID, pump_amt, now)
        
        await ctx.send(f"{ctx.author.mention} You start to pump up your {pump_style}")
        await asyncio.sleep(2)
        await ctx.send(f"{ctx.author.mention} You gained {pump_amt} movement {point_s}!")
        print(f"{now} - {discordUser} - {pump_style} gained {pump_amt} movement {point_s}")


def setup(bot: commands.bot):
    bot.add_cog(pump(bot))