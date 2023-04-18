import nextcord
from nextcord.ext import commands
import random
import asyncio
from datetime import datetime

from cogs.Utils.checks import *
from test_database import *
from constants import *




class taxi(commands.Cog):
    """ Pay MOFFS to take the TAXICRAB to Town, or further along the map """

    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command(aliases=["peace","return"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def bye(self, ctx):
        """ When you're finished in Town, use !bye to return back to where you were, for free. """
        """ Usage Restrictions: Must be in Town. """
        discordID = ctx.author.id

        # Get db info
        document = find_player(discordID)
        document = list(document) 
        
        # Check if OK to call Taxi
        pre_checks = ["channel"]
        if not await all_checks(pre_checks, ctx, document, "taxi"):
            return
                       
        # Get old position
        pos = get_player(document, "pos")
        oldPos = get_player(document, "info", "oldPos")
        # If in town, return to old position
        if pos == 0:
            await ctx.send(ctx.author.mention + " You let the TAXICRAB know you are done in town.")
            await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.mention} You are safely returned back to position {oldPos}.")
            move_player(discordID, oldPos)
            return
        # Not in town
        else:
            await ctx.send(ctx.author.mention + " Hi!")
            return

    @commands.command(aliases=["taxicrab", "crab", "crabi", "T", "t","Taxicrab","Taxi"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def taxi(self, ctx):
        """ 
        Shortcuts: !t, !t #, !t 0 (for Town)
        Standard Fare: 5 MOFFS
        Discount Fare: 4 MOFFS - Requires 1 TAXICRAB Token NFT
        Discount Fare: 3 MOFFS - Requires 3 TAXICRAB Token NFTs 
        Usage Restriction: Cannot be in Town
        """

        BOARD_SIZE = SETTINGS["positions"]
        FARE = SETTINGS["taxi_fare"]

        now = datetime.datetime.today()
        discordID = ctx.author.id
        discordUser = ctx.author
        move = ride_fare = 0

        # Validate input
        def check(msg):
            return msg.author.id == discordID and msg.content.isdigit()
            
            
        def check_string(msg):
            return msg.author.id == discordID and isinstance(msg.content, str) and (msg.content).upper() in ["YES","NO","Y","N"]


        def check_dest(response):
            if response in ["town", "TOWN", "t", "T"]:
                dest = 0
            else:
                dest = int(response)
            return dest

        
        # Get db info
        document = find_player(discordID)
        document = list(document)

        # Check if OK to call Taxi
        pre_checks = ["channel"]
        if not await all_checks(pre_checks, ctx, document, "taxi"):
            return

        #Get player info
        position = get_player(document, "pos")
        moffs = get_player(document, "week_stats", "totals", "moffs")
        salt = get_player(document, "week_stats", "totals", "salt")
        taxi_tokens = get_player(document, "inv", "taxicrab")

        # Already in town
        if position == 0:
            await ctx.send(f"{ctx.author.mention} Use `!bye` when you're done in town for a free return trip to where you were.")
            await ctx.send(f"{ctx.author.mention} Use `!look` to see what's available.")
            ctx.command.reset_cooldown(ctx)
            return
        
        # Check for taxicrab token; apply fare discount
        if taxi_tokens:
            if taxi_tokens > 2:
                FARE -= 2
            elif taxi_tokens > 0:
                FARE -= 1
            await ctx.send(ctx.author.mention + " You show the TAXICRAB your TAXICRAB token(s)."
            "\nThe TAXICRAB looks thankful, and adjusts your fare accordingly.")
            await asyncio.sleep(1)
        else:
            await ctx.send(ctx.author.mention + " No TAXICRAB Tokens found: Fare set to 5 MOFFS.\nIf you have already purchased or found a TAXICRAB Token, run `~assets` to update your inventory.")
            await asyncio.sleep(1)
        
        # Too broke to ride        
        if moffs < FARE:
            await ctx.send(f"{ctx.author.mention} <a:hehe_aku:867940486395097148> There's a {FARE} MOFF minimum to ride in a TAXICRAB!")
            ctx.command.reset_cooldown(ctx)
            return
                
        # Let player use a shortcut to use the taxi
        msg = ctx.message.content.split()
        if len(msg) == 2:
            if msg[1] and (msg[1] != '' and msg[1].isdigit() and int(msg[1]) in range(0, (BOARD_SIZE + 1))) or msg[1] in ["town", "TOWN", "t", "T"]:
                dest = check_dest(msg[1])
            else:
                await ctx.send(f"{ctx.message.author.mention} Try a valid number, or just use `!taxi`")
                ctx.command.reset_cooldown(ctx)
                return
        else:        
            # Taxi message
            try:
                set_busy(discordID, True)
                
                # Request destination
                await ctx.send(f"{ctx.author.mention} The price to ride the TAXICRAB is **{FARE} MOFFS** per position traveled."
                f"\n**MOFFS**: {moffs}\n**POSITION**: {position}"
                f"\nWhich position would you like travel to?\nEnter a **position** between `1` and `{BOARD_SIZE}`."
                f"\nEnter `0` to go to **Town**. The fare to Town is {FARE} MOFFS"
                f"\n\nNote: TAXICRABS are able to travel around AKU WORLDS in either direction.")
                
                response = await self.bot.wait_for("message", check=check, timeout=30)
                dest = check_dest(response.content)
                
                # Allow multiple attempts for correct position
                while dest not in range(0, BOARD_SIZE+1) and str(dest) not in ["town", "TOWN", "t", "T"]:
                    await response.add_reaction('❌')
                    response = await self.bot.wait_for("message", check=check, timeout=20)
                    dest = check_dest(response.content)
            # Timeout
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.message.author.mention} The TAXICRAB got tired of waiting for you and scurried away.")
                set_busy(discordID, False)
                return        
        
        # Get shortest path to destinatino
        if position < dest:
            moves_left = (position + BOARD_SIZE) - dest
            moves_right = dest - position
        elif position > dest:
            moves_left = position - dest
            moves_right = (BOARD_SIZE - position) + dest
        else:
            await ctx.send(ctx.author.mention + " <a:hehe_aku:867940486395097148> Is this a game to you? Come back when you're serious!")
            ctx.command.reset_cooldown(ctx)
            set_busy(discordID, False)
            return
        
        # Set shortest path
        if moves_left < moves_right:
            move = moves_left
        else:
            move = moves_right

        # Travel to town
        if dest == 0:
            ride_fare = FARE       
            # Warning if no SALT
            if salt < 3:
                await ctx.send(ctx.author.mention + " WARNING: Your trip to town may be wasted if you don't have at least 3 SALT, **or** if you're not planning to visit the `!trader`.")
        else:
            # Calc fare
            ride_fare = move * FARE
        
        # No free lunch
        if ride_fare > moffs:
            await ctx.send(ctx.author.mention + " <a:hehe_aku:867940486395097148> Does this look like a charity to you?! Come back when you can afford the fare!")
            ctx.command.reset_cooldown(ctx)
            set_busy(discordID, False)
            return
        
        # Traveling to town; save position as oldPos in db
        # Subtract moff fare; record time
        if dest == 0:
            await ctx.send(f"{ctx.author.mention} You pay {ride_fare} MOFFS to the TAXICRAB to bring you to town."
            f"\nUse `!look` to see what's available."
            f"\nUse `!bye` when you're done in town for a free return trip to where you were.")
            db_taxi(discordID, position, dest, 1, ride_fare)                
            print(f"{now} - {discordUser} - Taxi ride - TOWN")
            ctx.command.reset_cooldown(ctx)
            set_busy(discordID, False)
            return
        # Player traveling along map
        else:
            try:
                if ride_fare > FARE:
                    # Confirm payment
                    await ctx.send(f"{ctx.author.mention} **TAXICRAB Fare**: {ride_fare} MOFFS\nDo you accept? Enter: `YES` or `NO`")
                    confirm = await self.bot.wait_for("message", check=check_string, timeout=10)
                    confirm = (confirm.content).upper()

                    if confirm in ["NO", "N"]:
                        # Did not confirm ride
                        await ctx.send(ctx.author.mention + " <a:hehe_aku:867940486395097148> Is this a game to you? Come back when you're serious!")
                        ctx.command.reset_cooldown(ctx)
                        set_busy(discordID, False)
                        return

                # Moved past the last board space
                if (position + move) > BOARD_SIZE:
                    position = (position + move) % BOARD_SIZE
                else:
                    position = position + move
                await ctx.send(f"{ctx.author.mention} You paid {ride_fare} MOFFS to the TAXICRAB to travel to position {dest}."
                "\nWe appreciate your business!") 

                #Submit to DB
                db_taxi(discordID, position, dest, move, ride_fare)                
                print(f"{now} - {discordUser} - Taxi ride - {ride_fare} MOFFS - Pos: {position}")

                # Notify player if they can play the guessing game
                await check_hovel(ctx, document, discordID, dest)

                ctx.command.reset_cooldown(ctx)

            # Too long to respond
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.message.author.mention} The TAXICRAB got tired of waiting for you and scurried away.")
                set_busy(discordID, False)
                return
            
        set_busy(discordID, False)
        
        
           
			
        
def setup(bot: commands.bot):
    bot.add_cog(taxi(bot))
