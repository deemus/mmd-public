import nextcord
from nextcord.ext import commands

from datetime import datetime

from cogs.Utils.checks import *
from test_database import *
from constants import *

class progress(commands.Cog):
    """ Check daily progress, position, and available commands """

    def __init__(self, bot: commands.bot):
        self.bot = bot


    @commands.command(aliases=["p", "P"])
    @commands.cooldown(1, 25, commands.BucketType.user)
    async def progress(self, ctx: commands.context):                      
        BOARD_SIZE = SETTINGS["positions"]
        FARE = SETTINGS["taxi_fare"]

        notLooked = posList = list(range(1,BOARD_SIZE+1))

        healthStatus = 'You feel normal.'
        discordID = ctx.author.id
        
        # Get Player stats from db        
        submits = find_player(discordID)        
        document = list(submits)

        # Check if OK to run command
        pre_checks = ["skip_busy"]
        if not await all_checks(pre_checks, ctx, document, "progress"):
            return        

        pos = get_player(document, "pos")
        fakulty = get_player(document, "info", "fakulty")
        salt = get_player(document, "inv", "salt")
        moffs = get_player(document, "inv", "moffs")
        health = get_player(document, "week_stats", "totals", "health")

        usedPoints = get_player(document, "info", "used_points")
        points = get_player(document, "info", "points")
        remainingMoves = points - usedPoints

        looked = get_player(document, "info", "looked")

        guessWins = get_player(document, "week_stats", "counts", "guess_win")
        guessLosses = get_player(document, "week_stats", "counts", "guess_lose")
        guessTotal = guessWins + guessLosses

        attractTime = get_player(document, "time", "attract")
        moveTime = get_player(document, "time", "move")
        gymTime = get_player(document, "time", "gym")
        pumpTime = get_player(document, "time", "pump")
        heistTime = get_player(document, "time", "heist")
        spireTime = get_player(document, "time", "spire")
        krabertoTime = get_player(document, "time", "kraberto")

        pumps = get_player(document, "inv", "pumps")
        fire_pumps = get_player(document, "inv", "fire_pumps")
        taxi_tokens = get_player(document, "inv", "taxicrab")
    
        if len(looked) > 0:
            looked.sort()
            notLooked = set(posList) - set(looked)
            notLooked = sorted(notLooked)

        # Check for taxicrab token; apply fare discount
        if taxi_tokens:
            if taxi_tokens > 2:
                FARE -= 2
            elif taxi_tokens > 0:
                FARE -= 1        
        
        # Health status messages
        if health < -20:
            healthStatus = "You feel like a limp noodle..."
        elif health < 0:
            healthStatus = "You're not feeling that strong..."
        elif health > 0 and health < 20:
            healthStatus = "You are feeling healthy!"
        elif health >= 20 and health < 40:
            healthStatus = "You feel amazing!"
        elif health >= 40:
            healthStatus = "You feel like you could defeat the DRAGUM by yourself!"           

        # Check if in town
        if pos == 0:
            posString = "In Town"
        else:
            posString = str(pos)
        
        comString = ''
        resetTime = get_reset()
        
        guessRemain = 6 - guessTotal
        
        
        if (moveTime < resetTime) or (points > usedPoints):
            comString += " `!move` "
        if (fire_pumps > 0 or pumps > 0) and pumpTime < resetTime:
            comString += " `!pump` "
        if attractTime < resetTime:
            comString += " `!attract` "
        if len(notLooked) > 0 and remainingMoves > 0:
            comString += " `!look` "
        if heistTime < resetTime and moffs > 24:
            comString += " `!heist` "
        if spireTime < resetTime and salt > 19 and moffs > 5:
            comString += " `!spire` (in town) "
        if gymTime < resetTime and salt > 3 and moffs > 5:
            comString += " `!gym` (in town) "
        if guessRemain > 0:
            comString += " `!guess` (at a HOVEL)  "
        # if townTime < resetTime:
        #     comString += "`!taxicrab` (to town) "
        if comString == '':
            comString = "None! Try again after <t:1587424800:t>"
        
        if len(notLooked) == 0:
            notLooked = "You looked everywhere this week!"
            
        statMessage = "'s PROGRESS"

        statMessage +=f"\n\nStatus: {healthStatus}"
        statMessage +=f"\nF**aku**lty: {fakulty}"
        statMessage +=f"\nPosition: {posString}"
        statMessage +=f"\nMOFFS: {moffs}\nSALT: {salt}"

        statMessage +=f"\n\n**Daily movement points remaining**: {remainingMoves}"
        statMessage +=f"\nGuessing game attempts remaining: {guessRemain}"
        
        statMessage +=f"\n\nPositions not looked at: {notLooked}"
        
        statMessage +=f"\n\n**You can still use the following commands today**: {comString}"
        statMessage +=f"\n\nUse `!inv` to see your collected items & treasure."
        statMessage +=f"\nUse `!stats` to see your game statistics."
        statMessage +=f"\nUse `!taxi town` or `!t 0` to go to Town. Costs {FARE} MOFFS."
        
        
        if isinstance(ctx.channel, nextcord.channel.DMChannel):
            await ctx.send(f"{ctx.author.mention}{statMessage}")
            return

        await ctx.message.delete()
        await ctx.send(f"{ctx.author.mention}{statMessage}", delete_after=30)


def setup(bot: commands.bot):
    bot.add_cog(progress(bot))
