import nextcord
from nextcord.ext import commands
import random
import asyncio
from datetime import datetime

from cogs.Utils.checks import *
from test_database import *
import constants

class trader(commands.Cog):
	""" Trade for Crystals, or trade Crystals for SALT and MOFFS """

	def __init__(self, bot: commands.bot):
		self.bot = bot


	@commands.command(aliases=["swap", "trade", "ex", "exchange","Trader"])
	@commands.cooldown(1, 15, commands.BucketType.user)
	async def trader(self, ctx: commands.context):                      
		ITEMS = constants.ITEMS
		# SALT_EMOJI = EMOJIS["salt_crystal"]
		# DEF_EMOJI = EMOJIS["def_crystal"]
		# TIME_EMOJI = EMOJIS["time_crystal"]
		# SHARD_EMOJI = EMOJIS["crystal_shard"]
		

		now = datetime.datetime.today()
		discordID = ctx.author.id
		discordUser = ctx.author 

		def check_int(msg):
			return msg.author.id == discordID and msg.content.isdigit()	


		async def make_trade(inv_amt, gain_item, lose_item, required_amt, gain_amount):
			if required_amt > inv_amt:
				await ctx.send(f"{ctx.message.author.mention} You can't afford this!")
				return False
			
			elif gain_amount > 0:
				if gain_item in ["salt", "moffs"]:
					add_item_amt(discordID, gain_item, gain_amount)
					await ctx.send(f"{ctx.message.author.mention} You gained {gain_amount}  {gain_item.upper()}!")
				else:
					add_item_amt(discordID, gain_item, gain_amount)		
					await ctx.send(f"{ctx.message.author.mention} You gained {gain_amount}  {ITEMS[gain_item]['desc']}!")
			
				print(f"{now} - {discordUser} - Traded {required_amt} {lose_item} for {gain_amount} {gain_item}")
				inv_amt -= required_amt
				add_item_amt(discordID, lose_item, -required_amt)
				db_trade(discordID, lose_item, required_amt)
				return True

			else:
				await ctx.send(f"{ctx.message.author.mention} Invalid amount!")
				return False


		async def check_crystals(crystals):
			if crystals > 1:
				amount = await self.bot.wait_for("message", check=check_int, timeout=60)
				amount = int(amount.content)
				return amount	
			else:
				return 1

		
		# Get db info
		document = find_player(discordID)
		document = list(document)

		# Check if OK to Trade
		pre_checks = ["channel", "not_town"]
		if not await all_checks(pre_checks, ctx, document, "trader"):
			return

		#Get salt crystals
		salt_crystals = get_player(document, "inv","salt_crystal")
		shards = get_player(document, "inv","crystal_shard")

		# Start trader menu; wait for player input
		set_busy(discordID, True)

		# Loop menu until player leaves trader
		finished = False
		while not finished:     
			# Check available crystals
			if salt_crystals > 0:
				await ctx.send(f"{ctx.message.author.mention} You have **{salt_crystals} SALT Crystal(s)**💎 available to exchange.")
			else:
				await ctx.send(ctx.author.mention + " <a:hehe_aku:867940486395097148> No SALT Crystals💎 found.")
			await asyncio.sleep(1)
			if shards > 0:
				await ctx.send(f"{ctx.message.author.mention} You have **{shards} Crystal Shard(s)🔹** available to exchange.")
			else:
				await ctx.send(ctx.author.mention + " <a:hehe_aku:867940486395097148> No Crystal Shards🔹 found.")

			await asyncio.sleep(1)

			# Trader messaage
			await ctx.send(f"{ctx.message.author.mention} Welcome to the Crystal Exchange!"
			"\n`1` - Gain 15 - 20 SALT Instantly - COSTS 1 SALT Crystal💎"
			"\n`2` - Gain 15 - 25 MOFFS Instantly - COSTS 1 SALT Crystal💎"
			"\n`3` - Gain 1 TIME Crystal<:crystal:936472306224627753> (for Sparkly Spire) - COSTS 1 SALT Crystal💎"
			"\n`4` - Gain 1 MAJIC Defense Crystal<:crystal2:936476907376103475> (for Heists) - COSTS 1 SALT Crystal💎"
			"\n`5` - Gain 1 SALT Crystal💎 - COSTS 10 Crystal Shards🔹"
			"\n`0` - Leave"
			"\n\n Enter your selection: ")

			try:
				selection = await self.bot.wait_for("message", check=check_int, timeout=60)
				selection = int(selection.content)

				if selection in [0, 1, 2, 3, 4, 5]:
					if salt_crystals < 1 and selection in [1, 2, 3, 4]:
						await ctx.send(f"{ctx.message.author.mention} You have **{salt_crystals} SALT Crystals**💎 available to exchange.\nCome back when you get some more.")
						set_busy(discordID, False)
						return
					
					# Gain SALT
					if selection == 1:
						gainSalt = int(random.randint(15,20))
						if await make_trade(salt_crystals, "salt", "salt_crystal", 1, gainSalt):
							salt_crystals -= 1
					
					# Gain MOFFS
					elif selection == 2:
						gainMoffs = random.randint(15,25)
						if await make_trade(salt_crystals, "moffs", "salt_crystal", 1, gainMoffs):
							salt_crystals -= 1
					
					# TIME Crystal
					elif selection == 3:
						await ctx.send(f"{ctx.message.author.mention} How many TIME Crystals<:crystal:936472306224627753> do you want?")		
						amount = await check_crystals(salt_crystals)
						if await make_trade(salt_crystals, "time_crystal", "salt_crystal", amount, amount):
							salt_crystals -= amount

					# DEF Crystal
					elif selection == 4:
						await ctx.send(f"{ctx.message.author.mention} How many MAJIC Defense Crystals<:crystal2:936476907376103475> do you want?")		
						amount = await check_crystals(salt_crystals)
						if await make_trade(salt_crystals, "def_crystal", "salt_crystal", amount, amount):
							salt_crystals -= amount
						
					# Shards for SALT crystal
					elif selection == 5:
						if shards < 10:
							await ctx.send(f"{ctx.message.author.mention} You have **{shards} Crystal Shards🔹** \nCome back when you get some more.")
						else:
							amount = 1
							if shards > 20:
								await ctx.send(f"{ctx.message.author.mention} How many SALT Crystals💎 do you want?")
								amount = await check_crystals(shards)
							if await make_trade(shards, "salt_crystal", "crystal_shard", 10*amount, amount):
								shards -= 10*amount
								salt_crystals += amount
							
					# Exit trader
					elif selection == 0:
						await ctx.send(f"{ctx.message.author.mention} Thank you, come again.")
						finished = True
				
				# Invalid selection
				else:
					await ctx.send(f"{ctx.author.mention} Invalid Selection. Try again")

				await asyncio.sleep(1)
			# Time out
			except asyncio.TimeoutError:
				await ctx.send(f"{ctx.author.mention} Come back when you're ready to trade.")
				ctx.command.reset_cooldown(ctx)
				set_busy(discordID, False)
				return

		ctx.command.reset_cooldown(ctx)
		set_busy(discordID, False)

def setup(bot: commands.bot):
	bot.add_cog(trader(bot))
