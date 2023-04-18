import nextcord
from nextcord.ext import commands
import random
import asyncio
from datetime import datetime

from cogs.Utils.checks import *
from test_database import *
from constants import *


class gym(commands.Cog):
    """ (TOWN) - Visit the GYM to spend SALT and gain HEALTH  """

    def __init__(self, bot: commands.bot):
        self.bot = bot
    
    @commands.command(aliases=["sweat","Gym"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def gym(self, ctx):
        now = datetime.datetime.today()
        discordID = ctx.author.id
        discordUser = ctx.author

        GYM1_COST = SETTINGS["gym_moff_cost"]
        GYM2_COST = SETTINGS["gym_crab_cost"]
        GYM3_COST = SETTINGS["gym_dragum_cost"]
        GYM1_MIN = SETTINGS["gym_moff_health_min"]
        GYM1_MAX = SETTINGS["gym_moff_health_max"]
        GYM2_MIN = SETTINGS["gym_crab_health_min"]
        GYM2_MAX = SETTINGS["gym_crab_health_max"]
        GYM3_MIN = SETTINGS["gym_dragum_health_min"]
        GYM3_MAX = SETTINGS["gym_dragum_health_max"]
        
        
        def check(msg):
            return msg.author.id == discordID and msg.content.isdigit()


        # Get db info
        document = find_player(discordID)
        document = list(document)

        # Check if OK to move
        pre_checks = ["channel", "time", "not_town"]
        if not await all_checks(pre_checks, ctx, document, "gym"):
            return
           
        # Get SALT
        salt = get_player(document, "inv", "salt")
              
        # OK to enter Gym
        try:
            set_busy(discordID, True)
            await ctx.send(f"{ctx.author.mention} Welcome to the grand opening of the Gym. Thanks for staying healthy!")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} Your SALT: {salt}\nWhat type of workout are you interested in today?"
            "\nPlease choose one:"
            f"\n`{GYM1_COST}` - MOFF Workout - {GYM1_COST} SALT"
            f"\n`{GYM2_COST}` - CRAB Workout - {GYM2_COST} SALT"
            f"\n`{GYM2_COST}` - DRAGUMSLAYER Workout - {GYM2_COST} SALT"
            "\nUse `0` if you're feeling lazy and want to change your mind.")
            
            # Get response
            response = await self.bot.wait_for("message", check=check, timeout=40)
            purchase = int(response.content)
            
            # Wait for correct entry
            while purchase not in [0, GYM1_COST, GYM2_COST, GYM3_COST]:
                await response.add_reaction('❌')
                response = await self.bot.wait_for("message", check=check, timeout=30)
                purchase = int(response.content)
        
        # Timeout
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} Please come back when you're ready to sweat.")
            ctx.command.reset_cooldown(ctx)
            set_busy(discordID, False)
            return

        # No free lunch
        if purchase > salt:
            await ctx.send(ctx.author.mention + " <a:hehe_aku:867940486395097148> Sorry, it looks like you don't have enough SALT to pay for that.")
            ctx.command.reset_cooldown(ctx)
            set_busy(discordID, False)
            return     
        
        # Charge SALT
        if purchase > 0:
            await ctx.send(f"{ctx.author.mention} You paid {purchase} SALT.")
            # add_item_amt(discordID, "salt", -purchase)
        
        # Nada
        if purchase == 0:
            await ctx.send(f"{ctx.author.mention} I hope you'll put more effort than that into defeating the DRAGUM. . .")
        # MOFF
        elif purchase == GYM1_COST:
            await ctx.send(f"{ctx.author.mention} You chose the MOFF workout plan.")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You take a walk around the gym and marvel at all the training equipment.")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} Maybe you'll actually try to use it some day. . .")
            await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.mention} You start to feel healthier already!")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You finish your workout and leave the gym.")
            health = random.randint(GYM1_MIN, GYM1_MAX)

        # CRAB
        elif purchase == GYM2_COST:
            await ctx.send(f"{ctx.author.mention} You chose the CRAB workout plan")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You perform some light cardio.")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You do a couple pull-ups and push-ups.")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You bench-press the bar a few times.")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You finish your workout and leave the gym feeling healthy and strong!")
            health = random.randint(GYM2_MIN, GYM2_MAX)
            
        # DRAGUMSLAYER
        elif purchase == GYM3_COST:
            await ctx.send(f"{ctx.author.mention} You chose the DRAGUMSLAYER workout plan")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You do some HIIT around the track.")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You load up the weights and do some deadlifts, squats, and curls.")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You don't skip leg-day.")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You finish your workout sweaty and ready to take on the DRAGUM!")
            health = random.randint(GYM3_MIN, GYM3_MAX)

        # Finished workout
        if purchase > 0:            
            db_gym(discordID, health, purchase, now)
            print(f"{now} - {discordUser} - GYM Visit - Spent {purchase} SALT - Health +{health}")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} Use `!look` to see what else is in town, or use `!bye` to leave.")
        else:
            await ctx.send(f"{ctx.author.mention} Please come back when you're ready to sweat.")
            ctx.command.reset_cooldown(ctx)
            set_busy(discordID, False)
            return
        
        set_busy(discordID, False)


def setup(bot: commands.bot):
    bot.add_cog(gym(bot))


        #
        # Gym Membership NFT check
        #
        # try:
            # inv = [ sub['inv'] for sub in document]
            # inv = inv[0]
            # taxi_tokens = inv['taxicrab']
            # if taxi_tokens > 0:
                # FARE = 4
            # elif taxi_tokens > 4:
                # FARE = 3
            # await ctx.send(ctx.author.mention + " You show the TAXICRAB your TAXICRAB token(s).")
            # await asyncio.sleep(1)
            # await ctx.send(ctx.author.mention + " The TAXICRAB looks thankful, and adjusts your fare accordingly.")
            # await asyncio.sleep(1)
        # except (KeyError, IndexError):
            # await ctx.send(ctx.author.mention + " No TAXICRAB Tokens found, you'll have to pay full price!\nIf you have already purchased or found a TAXICRAB Token, run `!assets` to update your inventory.")
            # await asyncio.sleep(1)