import nextcord
from nextcord.ext import commands
import random
import asyncio
from datetime import datetime

from cogs.Utils.events import *
from cogs.Utils.checks import *
from test_database import *
from constants import *

class look(commands.Cog):
    """ Use movement points to perform a search on each position """

    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command(aliases=["Look","l","L","<:akueyes:862540568004788245>",":akueyes:","gander","search"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def look(self, ctx, search=''):
        taxi_tokens = 0
        discordID = ctx.author.id
        discordUser = ctx.author
        now = datetime.datetime.today()
        emojis = "💎<:crystal:936472306224627753><:crystal2:936476907376103475>"

        
        # Verify correct command usage
        if search:
            try:
                search = int(search)
            except ValueError:
                await ctx.send(f"{ctx.message.author.mention} Invalid usage. Use `!look` for more details")
                ctx.command.reset_cooldown(ctx)
                return

        # Get db info
        document = find_player(discordID)
        document = list(document)

        # Check if OK to look
        pre_checks = ["channel"]
        if not await all_checks(pre_checks, ctx, document, "look"):
            return
        
        # Get position
        pos = get_player(document, "pos")
        
        # Check in town
        if pos == 0:
            # Check if player has taxi token
            taxi_tokens = get_player(document, "inv", "taxicrab")
            if taxi_tokens > 0:
                await ctx.message.author.send(" *Psst. . Hey. .*"
                "\n*I see you're a collector, so I'll give you some secret advice. . .*"
                "\n*My friend* `!kraberto` *can help you out. . . Just say the word. . .*"
                "\n*But keep this between us, OK?*")                
                await ctx.send(ctx.author.mention + " The TAXICRAB whispers something to you. . .")
           
            # Town look message
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You pass a `!trader` behind a table with many colorful Crystals {emojis} scattered around."
            "\nNext to the trader, a strange looking kiosk displaying `!MOFF-O-MATIC` has been installed."
            "\nYou see a very sparkly `!spire` rising from the edge of town."
            "\nA mysterious hooded figure peeks around a corner in a dark alley. "
            "\nA mid-sized, slightly run-down 24 hour `!gym` is open on your right."
            "\nOn your left, a community MOFF `!garden` is being established."
            "\nWhere do you want to go?  Use `!bye` to leave town if you're finished.")
            return
        
        # Get remaining movement points
        remainingMoves = get_remaining_moves(document)
        if remainingMoves == 0:
            await ctx.send(ctx.author.mention + " You're out of movement points, so you don't have the energy to look around."
            "\nTry again after <t:1587424800:t>"
            "\nDid you use `!roll` today?"
            "\nCheck your progress and daily commands with `!p`")
            return
        
        # Check if player has looked at this pos already
        looked = get_player(document, "info", "looked")
        for x in looked:
            if x == pos:
                await ctx.send(f"{ctx.message.author.mention} You already looked here this week."
                "\nCheck `!p` to see where you have not looked yet."
                "\nUse `!move` to go to the next position.")
                await asyncio.sleep(1)
                
                if remainingMoves == 0:
                    await ctx.send(f"{ctx.message.author.mention} You're out of movement points! Did you already `!roll` for points today?")
                ctx.command.reset_cooldown(ctx)
                return

        
        def check(msg):
            return msg.author.id == discordID and msg.content.isdigit() 
            

        # Wait 45sec for Look response
        msg = ctx.message.content.split()
        
        if len(msg) == 2:
            if int(msg[1]) in range(0, (remainingMoves + 1)) and int(msg[1]) in [1,3]:
                search = int(msg[1])
            else:
                await ctx.send(f"{ctx.message.author.mention} Invalid usage. Use `!look` for more details")
                ctx.command.reset_cooldown(ctx)
                return        
        # elif len(msg) == 1 and search > 0:
        #     pass
        else:        
            try:
                # Request look type
                set_busy(discordID, True)

                await ctx.send(f"{ctx.author.mention} **Remaining Moves**: {remainingMoves}"
                "\nHow much effort do you want to put into the search?"
                "\nEnter `3` for a THOROUGH search. Costs 3 movement points."
                "\nEnter `1` for a QUICK search. Costs 1 movement point.")
                
                response = await self.bot.wait_for("message", check=check, timeout=45)
                search = int(response.content)                
                
                while search not in [1,3] and search not in range(0, (remainingMoves + 1)):
                    await response.add_reaction('❌')
                    response = await self.bot.wait_for("message", check=check, timeout=20)
                    search = int(response.content)                    
            
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.message.author.mention} Command timed out. Did you fall asleep? Try `!look` again!")
                ctx.command.reset_cooldown(ctx)
                set_busy(discordID, False)
                return
        # Not enough points
        if search > remainingMoves:
            await ctx.send(f"{ctx.message.author.mention} <a:hehe_aku:867940486395097148> "
            "You don't have enough energy left for this type of search today!")
            return        

        # Determine event type
        if search == 1:
            lookRoll = random.randint(1, 5)
            await ctx.send(f"{ctx.message.author.mention} You decide to take a quick look around. . .")
            await asyncio.sleep(1)
        elif search == 3:
            lookRoll = random.randint(1, 5)
            # lookRoll = 5
            await ctx.send(f"{ctx.message.author.mention} You begin to look around to the best of your abilities. . .")
            await asyncio.sleep(2)
        else:
            await ctx.send(f"{ctx.message.author.mention} Invalid usage. Use `!look` for more details")
            ctx.command.reset_cooldown(ctx)
            set_busy(discordID, False)
            return

        # Owning a hovel does not cost movement points.
        try:
            if str(discordID) == HOVEL_OWNERS[pos]:
                await ctx.send(f"{ctx.message.author.mention} This place looks familiar. . .")
                await asyncio.sleep(1)
                await ctx.send(f"{ctx.message.author.mention} Welcome home, HOVEL owner! "
                "Searching your owned HOVEL will not cost you any movement points!")
                add_stat(discordID, "points", search)
        except KeyError:
            pass
        
        # Add look to db and log
        db_look(discordID, pos, search)
        print(f"{now} - {discordUser}: LOOK {search}")
        
        # Get event based on look roll
        
        await get_event(self, ctx, lookRoll, search)
        
        # Finished searching
        await ctx.send(f"{ctx.message.author.mention} You finished your search at this location.")
        await asyncio.sleep(1)
        if remainingMoves - search > 0:
            await ctx.send(f"{ctx.message.author.mention} Use `!move` to travel to a new location if you want to `!look` again.")
        elif remainingMoves < 1:
            await ctx.send(f"{ctx.message.author.mention} You are exhausted! Better get some rest before moving or searching again.")

        set_busy(discordID, False)
        ctx.command.reset_cooldown(ctx)


def setup(bot: commands.bot):
    bot.add_cog(look(bot))