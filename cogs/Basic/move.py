# import nextcord
from nextcord.ext import commands
import random
import asyncio
from datetime import datetime
from cogs.Utils.checks import *
from test_database import *
from constants import *


class move(commands.Cog):
    """ Player uses this command to roll for movement points, and to move to a different position  """

    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command(aliases=["m","M","r","R","Move","moove","roll","Roll"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def move(self, ctx):
        
        MOVE_MIN = SETTINGS["movement_min"]
        MOVE_MAX = SETTINGS["movement_max"]

        now = datetime.datetime.today()
        discordID = ctx.author.id
        discordUser = ctx.author
        moveRoll = random.randint(MOVE_MIN, MOVE_MAX)
        
        # Get db info
        document = find_player(discordID)
        document = list(document)

        # Check if OK to move
        pre_checks = ["channel"]
        if not await all_checks(pre_checks, ctx, document, "move"):
            return
        
        # Check if in town
        pos = get_player(document, "pos")
        if pos == 0:
            await ctx.send(ctx.author.mention + " The TAXICRAB will take you where you want to go for free while you're in town. Use `!look` to see what's available.")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} Use `!bye` when you're done in town for a free return trip to where you were.")
            return
        
        # Checked looked positions
        looked = get_player(document, "info", "looked")
        remainingMoves = get_remaining_moves(document)
        
        # Check if rolled today, set points if not.
        resetTime = get_reset()
        moveTime = get_player(document, "time", "move")
        if moveTime < resetTime:
            moveRoll = await check_health_move(ctx, document, moveRoll)
            await ctx.send(f"{ctx.author.mention} {ROLL_EMOJI} You rolled for movement points! {ROLL_EMOJI}"
            f"\n**Daily Movement Point Roll**: {moveRoll}"
            f"\n**Current position**: {pos}")
            
            # Notify player to look if they haven't yet.
            if pos not in looked:
                await ctx.send(f"{ctx.author.mention} Take a `!look` around before you `!move`.")
            else:
                await ctx.send(f"{ctx.author.mention} Use `!move` again to move."
                "\nYou may move multiple times a day until you run out of moves."
                "\nThe map is a circle. Moving beyond position 20 will start you back on position 1."
                "\nMake sure you take a `!look` at each position once a week before you move on!")

            # Log roll
            print(f"{now} - {discordUser}: ROLLED {moveRoll}")
            
            # Save roll to DB
            db_roll(discordID, moveRoll, remainingMoves, now)
            ctx.command.reset_cooldown(ctx)
            return
               
        # Get remaining movement points
        time_until_reset = (resetTime - now).seconds   
        no_moves_msg = f"{ctx.author.mention} An AKU WORLDS day begins at <t:1587424800:t>."
        no_moves_msg += f"\n<a:hehe_aku:867940486395097148> : You are exhausted from all that traveling "
        no_moves_msg += f"and you must wait {time_until_reset} seconds before moving again!"

        # No movement points left
        if remainingMoves == 0:                         
            await ctx.send(f"{no_moves_msg}")
            return

        # Get number of positions to move from command; default to 1
        msg = ctx.message.content.split()
        if len(msg) == 2:
            if msg[1] and msg[1] != '' and msg[1].isdigit() and int(msg[1]) in range(0, (remainingMoves + 1)):
                move = int(msg[1])
            else:
                await ctx.send(f"{ctx.message.author.mention} Try a valid number, or just use `!move`")
                ctx.command.reset_cooldown(ctx)
                return
        else:        
            move = 1    
            if pos not in looked:
                await ctx.send(f"{ctx.message.author.mention} You haven't taken a `!look` here yet! Use `!move 1` to move on anyway.")
                ctx.command.reset_cooldown(ctx)
                return
        
        # Get remaining movement points
        remainingMoves -= move

        # Not enough points to move that far
        if remainingMoves < 0:           
            await ctx.send(f"{no_moves_msg}")
            return

        # Player doesn't want to move
        if move == 0:
            await ctx.send(f"{ctx.author.mention} You looked at the journey ahead and decided. . . nah.")
            ctx.command.reset_cooldown(ctx)
            return
 
        # Log
        print(f"{now} - {discordUser}: MOVE {move}")

        # Moved past the last board space
        pos = await check_cross_border(ctx, discordID, pos, move)

        # Submit Movement to db
        db_move(discordID, pos, move)
        ctx.command.reset_cooldown(ctx)
        
        # Success msg
        await ctx.send(f"{ctx.author.mention} You moved to position {pos}. "
        f"\n**Remaining Moves**: {remainingMoves}"
        "\nUse `!p` to see your progress at any time.")
        await asyncio.sleep(1)

        # Check moves left
        if remainingMoves > 0:
            await ctx.send(f"{ctx.author.mention} Try taking a `!look` around!")
        else:
            await ctx.send(f"{ctx.author.mention} You don't have any moves left to `!look` around today.")

        # Notify player if they can play the guessing game
        await check_hovel(ctx, document, discordID, pos)

        
        # # Position special event
        # if pos == 14:            
        #     heart_coin = 0
        #     try:
        #         inv = [ sub['inv'] for sub in document]
        #         inv = inv[0]
        #         heart_coin = inv['heart_coin']
        #     except (KeyError, IndexError):
        #         pass
        #     if heart_coin == 0:
        #         await asyncio.sleep(1)
        #         await ctx.send(f"{ctx.author.mention} As you arrive, you see a large barrel next to the path that resembles a giant open vitamin with a \"TAKE ONE\" sign next to it.")
        #         await asyncio.sleep(1)
        #         await ctx.send(f"{ctx.author.mention} You pull out a pink, heart-shaped Vitamin Coin from the chest. ")
        #         await asyncio.sleep(1)
        #         await ctx.send(f"{ctx.author.mention} On one side of the coin, you see an inscription: ")
        #         await asyncio.sleep(1)
        #         await ctx.send(f"{ctx.author.mention} Happy Valentine's Day from the VITC Team!")
        #         add_item_amt(discordID, "heart_coin", 1)
        
def setup(bot: commands.bot):
    bot.add_cog(move(bot))