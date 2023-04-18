from nextcord.ext import commands
import asyncio
from datetime import datetime
from cogs.Utils.checks import *
from test_database import *
from constants import *

from cogs.Basic.look import look
from cogs.Basic.move import move


class movelook(commands.Cog):
    """ (ITEM) Use Deemaku's Hacker Glasses to automate the moving and looking commands """

    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command(aliases=["ml", "ML", "Ml"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def movelook(self, ctx):

        now = datetime.datetime.today()
        discordID = ctx.author.id
        discordUser = ctx.author

        # Get db info
        document = find_player(discordID)
        document = list(document)

        # Check if OK to movelook
        pre_checks = ["channel", "town"]
        if not await all_checks(pre_checks, ctx, document, "move"):
            return
        
        # Check for hacker glasses
        hacker = get_player(document, "inv", "hacker")
        if hacker == 0:
            await ctx.send(f"{ctx.author.mention} <a:hehe_aku:867940486395097148> You have not learned the secret technique required to use this command!")
            return
        
        # Check valid usage
        msg = ctx.message.content.split()
        if len(msg) == 2:
            # Valid search type
            if msg[1] and msg[1] != '' and msg[1].isdigit() and int(msg[1]) in [1,3]:
                search = int(msg[1])
            else:
                await ctx.send(f"{ctx.message.author.mention} <a:hehe_aku:867940486395097148> Usage: `!ml 1` or `!ml 3`")
                ctx.command.reset_cooldown(ctx)
                return
        elif len(msg) == 1:
            search = 3
        else: 
            await ctx.send(f"{ctx.message.author.mention} <a:hehe_aku:867940486395097148> Usage: `!ml 1` or `!ml 3`")
            ctx.command.reset_cooldown(ctx)
            return
        
        # Check already moved today and if any moves are left     
        moveTime = get_player(document, "time", "move")
        resetTime = get_reset()
        remainingMoves = get_remaining_moves(document)
        
        # Auto roll if necessary
        if moveTime < resetTime or remainingMoves == 0:
            await move.move(self, ctx)
            return                
            
        # Checked looked positions
        pos = get_player(document, "pos")
        posLooked = get_player(document, "info", "looked")
        
        # Check already looked at current position
        if pos not in posLooked:
            places_moved = 0
            alreadyLooked = False
        else:
            nextPos = pos + 1
            places_moved = 1
            alreadyLooked = True
            if nextPos in posLooked:
                await ctx.send(f"{ctx.message.author.mention} <a:hehe_aku:867940486395097148> "
                f"You have already looked at the current position ({pos}) and the next position ({nextPos})."
                "\nIf you still want to move there, use `!m`, otherwise use `!p` to decide where to go."
                f"\n**Remaining Moves**: {remainingMoves}")
                ctx.command.reset_cooldown(ctx)
                return            
    
        if (remainingMoves < 4 and alreadyLooked) or remainingMoves < 3:
            search = 1
        
        # OK To look/move
        
        # Update remaining moves
        remainingMoves -= places_moved

        await ctx.send("` Hackermode: Activated `")        
        # Log
        print(f"{now} - {discordUser}: MOVELOOK {places_moved}")

        # Plural check
        if search == 1:
            pointText = "point"
        else:
            pointText = "points"

        if places_moved > 0:
            pos = await check_cross_border(ctx, discordID, pos, places_moved)

            # Check if enough points to perform search after move
            if remainingMoves == 0 or (remainingMoves - search < 0):
                # Set quick search
                newRemainingMoves = remainingMoves - 1
                
                await ctx.send(f"{ctx.author.mention} <a:hehe_aku:867940486395097148> You moved to position {pos}, "
                "but you don't have enough movement points left to look around!"
                f"\n**Remaining Moves**: {remainingMoves}")
                db_move(discordID, pos, 1)
                return
            
            else:
                # Set thorough search
                newRemainingMoves = remainingMoves - search                
               
                await ctx.send(f"{ctx.author.mention} You used **1 point** to move to position {pos} and then **{search} {pointText}** to look around."
                f"\n**Remaining Moves**: {newRemainingMoves}")
                await asyncio.sleep(1)
            
            # Notify player if they can play the guessing game
            await check_hovel(ctx, document, discordID, pos)
            
            # Submit Movement to db
            db_move(discordID, pos, 1)
        
        else:
            # Look without moving
            newRemainingMoves = remainingMoves - search
            await ctx.send(f"{ctx.author.mention} You haven't looked at this position yet. Using **{search} {pointText}** to look now!"
            f"\n**Remaining Moves**: {newRemainingMoves}")
            await asyncio.sleep(1)
        
        # START LOOK #
        
        # Determine event type
        if search == 1:
            await ctx.send(f"` Hackermode: Automating Quick Search `\n")
            await asyncio.sleep(1)
        elif search == 3:
            await ctx.send(f"` Hackermode: Automating Thorough Search `\n")
            await asyncio.sleep(2)
        else:
            await ctx.send(f"{ctx.message.author.mention} Invalid usage. Use `!look` for more details")
            ctx.command.reset_cooldown(ctx)
            return
        
        await look.look(self, ctx, search)
        ctx.command.reset_cooldown(ctx)

def setup(bot: commands.bot):
    bot.add_cog(movelook(bot))