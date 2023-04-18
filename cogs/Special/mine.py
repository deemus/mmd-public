from test_database import *
from nextcord.ext import commands
from nextcord.ext.commands import context
from cogs.Utils.checks import *
import constants
import random
import asyncio
from datetime import datetime

api_index = 0  #Index to keep track of what API we last queried -- having this as a global variable is probably easiest even if not pretty...

class mine(commands.Cog):
    """ Calculate AKU SCORE  """
    # api_list = constants.API_LIST
    
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command(aliases=["AKUTOT"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def akutot(self, ctx: commands.context):
        discordID = ctx.author.id
        discordUser = ctx.author
        document = find_player(discordID)
        document = list(document)
        TOT_TEMPLATES = []
        
        # Check if player completed spire
        pre_checks = []
        if not await all_checks(pre_checks, ctx, document):
            return
        
        await ctx.send(f"{ctx.author.mention} Please wait. . . Looking for your latest unrecorded NFT transfers to `akutreasures`.")
        
        
        now = datetime.today()
        player_wax = get_player(document, "wax")
        last_sent_time = get_player(document, "transfers", "last_sent_moff")
        moff_history = get_player(document, "transfers", "history", "moff")
        new_transfers = {}
        shard_amt = 0
        data = check_transfer(player_wax, TOT_TEMPLATES, last_sent_time)        
        try:
            trans_time = int(data[0]['created_at_time'])
            if last_sent_time > trans_time:
                await ctx.send(f"{ctx.author.mention} No new transfers found!")
                return
        except IndexError:
            await ctx.send(f"{ctx.author.mention} No recent transfers found!")
            return
        except:
            await ctx.send(f"{ctx.author.mention} Something went wrong, Alerting <@274656402721472512>!")
            return
        
        if not moff_history:
            moff_history = []
        for transfer in data:
            tx_id = transfer["transfer_id"]
            if tx_id not in moff_history:
                amt = len(transfer['assets'])
                new_transfers[tx_id] = amt
                shard_amt += amt * 20
                msg_amt = amt * 20
                await ctx.send(f"{ctx.author.mention} Found new transfer of {amt} MOFF Token(s)! Adding {msg_amt} Crystal Shards!")
                await asyncio.sleep(1)
                
        add_item_amt(discordID, "crystal_shard", shard_amt)
        db_transfer_history(discordID, "moff", new_transfers, trans_time)
        print(f"{now} - {discordUser} - TRANSFER {amt} MOFF Token(s). Added {shard_amt} Crystal Shards 🔹")
        
def setup(bot: commands.bot):
    bot.add_cog(mine(bot))   