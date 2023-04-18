import nextcord
from nextcord.ext import commands
import random
import asyncio

import cogs.Utils.checks as checks
from cogs.Utils.checks import *
from test_database import *
import constants


class inventory(commands.Cog):
    """ View your current items, crystals, consumables, etc. """

    def __init__(self, bot: commands.bot):
        self.bot = bot


    @commands.command(aliases=["inv","i","Inv","I"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def inventory(self, ctx: commands.context):                      

        itemCount = 0
        message = consumable_inv = crystal_inv = item_inv = basic_inv = ''        
        consumable = ["vit_bronze", "vit_silver", "vit_gold", "ban_bronze", "ban_silver", "ban_gold"]
        items = ["moff_token", "taxicrab", "fire_pumps", "pumps", "hacker"]
        crystals = ["salt_crystal", "time_crystal", "def_crystal", "crystal_shard"]
        basics = ["moffs", "salt", "seeds"]

        discordID = ctx.author.id

        # Get db info
        document = find_player(discordID)
        document = list(document)

        # Check if OK to run command
        pre_checks = ["skip_busy"]
        if not await all_checks(pre_checks, ctx, document, "inv"):
            return

        # Get player's items
        inv = get_player(document, "inv")
        inv = dict(sorted(inv.items()))
        if len(inv) > 0:                
            for item in inv:
                if inv[item] > 0:
                    itemCount += 1
                    if item in consumable:
                        consumable_inv+=(f"{ITEMS[item]['desc']}: {inv[item]}\n")
                    elif item in items:
                        item_inv+=(f"{ITEMS[item]['desc']}: {inv[item]}\n")
                    elif item in crystals:
                        crystal_inv+=(f"{ITEMS[item]['desc']}: {inv[item]}\n")
                    elif item in basics:
                        basic_inv+=(f"{ITEMS[item]['desc']}: {inv[item]}\n")

        
        # All 0s in db inventory
        if itemCount == 0:
            message = no_item_msg()
            await ctx.send(f"{ctx.author.mention} {message}")
            return
        
        # Create inventory message
        message= "\n**Basics**:"
        message+= f"\n{basic_inv}"
        message+= "\n**Items**:"
        message+= f"\n{item_inv}"
        message+= "\n**Crystals**:"
        message+= f"\n{crystal_inv}"
        message+= "\n**Consumables**:"
        message+= f"\n{consumable_inv}"
        
        # Don't delete in DM
        if isinstance(ctx.channel, nextcord.channel.DMChannel):
            await ctx.send(f"{ctx.author.mention}'s INVENTORY: {message}")
            return
        # Display inventory, delete after 20 seconds
        await ctx.send(f"{ctx.author.mention}'s INVENTORY: {message}", delete_after=20)


    def no_item_msg():
            message = "Your inventory is empty!"
            message+= "\nTry looking around more.\n If you have purchased an in-game item with WAX, use `~assets` to update your inventory."
            return message
        
		
def setup(bot: commands.bot):
    bot.add_cog(inventory(bot))
