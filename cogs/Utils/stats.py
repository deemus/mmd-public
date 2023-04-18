from nextcord.ext import commands, tasks
from database import *
from datetime import datetime, time, timedelta
from statistics import mean, median, mode
import sys
import asyncio
import nextcord
from cogs.Utils.checks import *
from test_database import *
from constants import *

#test guild:
guildID = 873294705373347881
roleID = 944824407719804929


#AKU guild:
#guildID = 859187679698092032
#roleID = healthyroleid

class stats(commands.Cog):
    """ See a variety of statistics about your MMD performance """
    def __init__(self, bot: commands.bot):
        self.bot = bot        

    @commands.command()
    async def stats(self, ctx):
        await ctx.message.add_reaction('✉️')
        # Get Player stats from db 
        discordID = ctx.author.id
        discordUser = ctx.author       
        submits = find_player(discordID)        
        document = list(submits)

        # Check if OK to run command
        pre_checks = []
        if not await all_checks(pre_checks, ctx, document, "progress"):
            return        

        guessWins = get_player(document, "week_stats", "counts", "guess_win")
        guessLosses = get_player(document, "week_stats", "counts", "guess_lose")
        guessTotal = guessWins + guessLosses

        heistWins = get_player(document, "week_stats", "counts", "heist_win")
        heistLosses = get_player(document, "week_stats", "counts", "heist_lose")
        heistTotal = heistWins + heistLosses

        spireBest = get_player(document, "all_stats", "totals", "spire_score")
        spireScore = get_player(document, "week_stats", "totals", "spire_score")
        spireCrystals = get_player(document, "week_stats", "counts", "spire_crystals")
        spireWins = get_player(document, "week_stats", "counts", "spire_win")
            
        statMessage = f"**{discordUser}'s MMD STATISTICS**"
        statMessage +=f"\n\nHeist Wins: {heistWins}"
        statMessage +=f"\nSuccessful Guesses: {guessWins}"        
        statMessage +=f"\n\nSpire Completions: {spireWins}"
        statMessage +=f"\nSpire Best Score (All-Time): {spireBest}"
        statMessage +=f"\nSpire Best Score (This Week): {spireScore}"
        statMessage +=f"\nTIME Crystals Used: {spireCrystals}"        
        
        if isinstance(ctx.channel, nextcord.channel.DMChannel):
            await ctx.send(f"{ctx.author.mention}{statMessage}")
            return

        await ctx.message.author.send(f"{statMessage}")


def setup(bot: commands.bot):
    bot.add_cog(stats(bot))