import nextcord
from nextcord.ext import commands
import random
import asyncio
from datetime import datetime

from cogs.Utils.checks import *
from test_database import *
import constants

class garden(commands.Cog):
	""" (TOWN) - Unlock plots to plant seeds that will grow into useful plants to be harvested. """

	def __init__(self, bot: commands.bot):
		self.bot = bot


	@commands.command(aliases=["mg", "MG", "Garden", "GARDEN", "moffgarden",])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def garden(self, ctx: commands.context):                      
		ITEMS = constants.ITEMS
		# COST = SETTINGS["garden_fert_cost"]
		MAX_PLOTS = SETTINGS["garden_max_plots"]
		token = EMOJIS["moff_token"]
		hehe = EMOJIS["hehe"]

		now = datetime.datetime.today()
		discordID = ctx.author.id
		discordUser = ctx.author 

		def check_int(msg):
			return msg.author.id == discordID and msg.content.isdigit()	

        # Get db info
		document = find_player(discordID)
		document = list(document)

        # Check if OK to Garden
		pre_checks = ["channel", "not_town"]
		if not await all_checks(pre_checks, ctx, document, "garden"):
			return

		
		# Function to unlock a new plot in the Garden
		async def buy_plot(moff_tokens, plots_opened, cost):
			if moff_tokens >= cost:
				if cost == 1:
					await ctx.send(f"{ctx.author.mention} You spent {cost} MOFF Token{token} to unlock a plot in the MOFF Garden!")
				else:
					await ctx.send(f"{ctx.author.mention} You spent {cost} MOFF Tokens{token} to unlock a plot in the MOFF Garden!")
				db_buy_plot(discordID, plots_opened, cost)
				print(f"{now} - {discordUser} - GARDEN - Spent {cost} MOFF Tokens - Unlocked Plot")
			else:
				await ctx.send(f"{ctx.author.mention} {hehe} Not enough MOFF Tokens{token} available to open a new plot!")

		
		def pick_seed(akumen):
			if akumen < 10:
				available_plants = [k for k, v in PLANTS.items() if v.get("akumen") < 3]
			elif akumen < 25:
				available_plants = [k for k, v in PLANTS.items() if v.get("akumen") < 6]
			elif akumen < 75:
				available_plants = [k for k, v in PLANTS.items() if v.get("akumen") < 8]
			elif akumen < 150:
				available_plants = [k for k, v in PLANTS.items() if v.get("akumen") < 11]
			else:
				available_plants = list(PLANTS.keys())

			seed = random.choice(available_plants)

			return seed

		
		# Function to plant seed in a free plot in the garden
		async def plant_seed(seeds, plots, plots_available, akumen):
			
			# Check player has seeds and available plot
			if not seeds:
				await ctx.send(f"{ctx.author.mention} {hehe} You don't have any Seeds to plant!")
				return
				
			if not plots_available:
				await ctx.send(f"{ctx.author.mention} {hehe} You don't have any available Plots!")
				return
			
			# Let player choose if multiple plots are available
			if seeds and plots_available:
				plots = sorted([eval(i) for i in plots])
				selected_plot = plots[0]
				rand_seed = pick_seed(akumen)
				if plots_available > 1:
					selected_plot = 0

					while selected_plot not in plots:
						await ctx.send(f"{ctx.author.mention} Select empty Plot from `{plots}` to plant a Seed:beans::"
							f"\nEnter `0` to go back.")	
						selected_plot = await self.bot.wait_for("message", check=check_int, timeout=60)
						selected_plot = int(selected_plot.content)
			
						# Player changes mind
						if selected_plot == 0:
							await ctx.send(f"{ctx.author.mention} You decide not to plant anything right now.")
							return

				# Sets plant/harvest time; fills plot with chosen seed, removes seed.
				db_plant(discordID, selected_plot, rand_seed, now)
				await ctx.send(f"{ctx.author.mention} You planted a Seed:beans: in Plot {selected_plot}!")
				print(f"{now} - {discordUser} - GARDEN - Planted {rand_seed} in Plot {selected_plot}")
		
		
		# Function to use crystal shards to shorten harvest time (once per day)
		async def fertilize(shards, cost):
			selected_plot = 99
			fertable = check_plot(document, "fertable")
			if fertable:
				chosen = []
				# Check shards
				if shards < cost:
					await ctx.send(f"{ctx.author.mention} {hehe} Not enough Crystal Shards 🔹! Needed: {cost}")
					return
					
				# Allow choice or multiple fertilization
				if len(fertable) > 1:
					new_cost = cost * len(fertable)
					await ctx.send(f"{ctx.author.mention} Select Plot to fertilize from: `{fertable}`!"
						f"\nEnter `10` to use {new_cost} Crystal Shards 🔹 to fertilize all Plots at once."
						f"\nEnter `0` to go back.")
					
					while selected_plot not in fertable:
						selected_plot = await self.bot.wait_for("message", check=check_int, timeout=60)					
						selected_plot = int(selected_plot.content)
						# Player changes mind
						if selected_plot == 0:
							await ctx.send(f"{ctx.author.mention} You decide not to Fertilize anything right now.")
							return
						# Fertilize all
						if selected_plot == 10:
							chosen = fertable
							cost = new_cost
							if shards < new_cost:
								await ctx.send(f"{ctx.author.mention} {hehe} Not enough Crystal Shards 🔹! Needed: {new_cost}")
								return
							break
						elif selected_plot in fertable:
							chosen.append(selected_plot)
				else:
					chosen.append(fertable[0])

				# OK to fertilize
				db_fert(discordID, chosen, cost,  now)
				print(f"{now} - {discordUser} - GARDEN - Spent {cost} shards to fertilize Plot: {chosen}")					
				if len(chosen) > 1:
					await ctx.send(f"{ctx.author.mention} You used {cost} Crystal Shards 🔹 and fertilized Plots: `{chosen}`!")
				elif len(chosen) == 1:
					chosen = chosen[0]
					await ctx.send(f"{ctx.author.mention} You used {cost} Crystal Shards 🔹 and fertilized Plot {chosen}!")
				return
			else:
				await ctx.send(f"{ctx.author.mention} {hehe} No Plots are ready to be fertilized!"
					"\nYou may only fertilize each Plot once per day!")
				return

		# Function to display status of each Plot in the Garden
		def check_plot(document, check):
			reset_time = get_reset()
			status_msg = "'s Garden Overview:"
			fertable_plots = []
			harvestable_plots = []
			daily = []
			opened_plots = get_player(document, "garden", "unlocked_plots")
			d = {
				0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
				6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
			}

			garden = get_player(document, "garden")
			plots = range(1, opened_plots+1)
			for i in plots:
				plot_num = f"plot_{i}"
				plot_text = f"Plot {i}"				
				plot = garden.get(plot_num)

				# Build message if there's a seed planted
				if plot["seed"]:
					# Get planted time
					plant_time = plot.get("plant_time")
					seed_name = plot.get("seed")
					plant_name = PLANTS[seed_name]["plant_name"]
					plant_epoch = int(plant_time.timestamp())				
					remaining = plot.get("harvests_remaining")
					daily_harvest = plot.get("daily_harvest")
					
					# Check harvestable
					harvest_msg = "❌"
					fert_msg = "❌"
					daily_msg = "❌"
					harvestable = check_garden_time(plot, "harvest_time", now)
									
					if harvestable and remaining > 0:
						harvest_msg = f"**{plant_name}** "
						harvest_msg += f"✅ - Harvests Remaining: :{d[remaining]}:"
						harvestable_plots.append(i)
						if daily_harvest < reset_time:
							daily_msg = "✅"
							daily.append(i)
					else:
						fertable = check_garden_time(plot, "fert_time", reset_time)
						if fertable:
							fert_msg = "✅"
							fertable_plots.append(i)

					# Build status	
					status_msg += f"\n **{plot_text}**: Planted <t:{plant_epoch}:R> - "
					status_msg += f"Can Harvest: {harvest_msg} - "
					if not harvestable:
						status_msg += f"Can Fertilize: {fert_msg}"
					else:
						status_msg += f"Today?: {daily_msg}"
				else:
					status_msg += f"\n **{plot_text}**: Empty"
				
			if check == "status":
				print(f"{now} - {discordUser} - GARDEN - Status Check")
				
				return status_msg
			elif check == "fertable":
				return list(set(fertable_plots))
			elif check == "harvestable":
				return list(set(daily))
			elif check == "daily":
				return list(set(daily))
			else:
				return
				
		# Function to harvest plants that are ready
		async def harvest():
			selected_plot = 99
			harvestable = check_plot(document, "harvestable")

			if harvestable:
				chosen = []
				harvest_msg = ""				
				garden = get_player(document, "garden")
				# Allow choice or multiple harvesting
				for num in harvestable:
					plot_num = f"plot_{num}"
					plot = garden.get(plot_num)
					seed_name = plot.get("seed")
					plant_name = PLANTS[seed_name]["plant_name"]
					desc = PLANTS[seed_name]["desc"]
					harvest_akl = PLANTS[seed_name]["akumen"]

					harvest_msg += f"`{num}` - {plant_name} - {desc}.\n"
				
				if len(harvestable) > 1:
					harvest_msg += f"\n`10` to Harvest all Plots at once."

				await ctx.send(f"{ctx.author.mention} Select Plot to Harvest: "
					f"\n{harvest_msg}"					
					f"\n`0` to go back.")

				while selected_plot not in harvestable:
					selected_plot = await self.bot.wait_for("message", check=check_int, timeout=60)					
					selected_plot = int(selected_plot.content)
					# Player changes mind
					if selected_plot == 0:
						await ctx.send(f"{ctx.author.mention} You decide not to Harvest anything right now.")
						return
					# Fertilize all
					if selected_plot == 10:
						chosen = harvestable
						break
					elif selected_plot in harvestable:
						chosen.append(selected_plot)
					
				for num in chosen:
					plot_num = f"plot_{num}"
					plot = garden.get(plot_num)
					seed_name = plot.get("seed")
					plant_name = PLANTS[seed_name]["plant_name"]
					bonus = PLANTS[seed_name]["bonus"]
					min = PLANTS[seed_name]["bonus_min"]
					max = PLANTS[seed_name]["bonus_max"]
					akumen = PLANTS[seed_name]["akumen"]
					
					if bonus == "points":
						bonus_desc = "movement points"
					else:
						bonus_desc = ITEMS[bonus]["desc"]
					remaining = plot.get("harvests_remaining")
					
					
					if bonus != "quest":
						bonus_amt = random.randint(min, max)
						if bonus_amt == max:
							await ctx.send(f"{ctx.author.mention} Nice! You got a perfect Harvest!")
							await asyncio.sleep(1)
						elif bonus_amt == min:
							await ctx.send(f"{ctx.author.mention} Dang! Your hand slipped and you ruined some of the harvest!")
							await asyncio.sleep(1)

					double_chance = random.randint(0, 100)
					if double_chance == 69:
						await ctx.send(f"{ctx.author.mention} **BONUS!** You got lucky and doubled your harvest!!")
						bonus_amt *= 2
						await asyncio.sleep(1)
					
					db_harvest(discordID, plot_num, bonus, bonus_amt, akumen, now)
					print(f"{now} - {discordUser} - GARDEN - Harvested a {plant_name} and gained {bonus_desc}: {bonus_amt}")	
					await ctx.send(f"{ctx.author.mention} You Harvested a **{plant_name}** and gained {bonus_desc}: {bonus_amt} !")
					await asyncio.sleep(1)

					if remaining == 1:
						db_clear_plot(discordID, plot_num, num, 0)
						print(f"{now} - {discordUser} - GARDEN - Harvest cleared Plot {num}")
						await ctx.send(f"{ctx.author.mention} Your **{plant_name}** from **Plot {num}** can no longer be Harvested!"
							f"\n**Plot {num}** is now Empty!")
			else:
				await ctx.send(f"{ctx.author.mention} {hehe} No Plots are ready to Harvest!")
				return

		# Destroy plant and make Plot able to be planted again
		async def salt_plot():
			CLEAR_COST = SETTINGS["garden_clear_cost"]
			opened_plots = get_player(document, "garden", "unlocked_plots")
			free_plots = get_player(document, "garden", "free_plots")
			free_plots = sorted([eval(i) for i in free_plots])
			print(free_plots)
			plots = list(range(1,opened_plots+1))
			num = 99
			if opened_plots == 0:
				await ctx.send(f"{ctx.author.mention} {hehe} No open Plots!")
				return
			
			salt = get_player(document, "inv", "salt")
			if salt < CLEAR_COST:
				await ctx.send(f"{ctx.author.mention} {hehe} Not enough SALT!")
				return
			
			while num not in plots:
				await ctx.send(f"{ctx.author.mention} Select Plot to SALT: `{plots}`"
					f"\nEnter `0` to go back.")
						
				selected_plot = await self.bot.wait_for("message", check=check_int, timeout=60)
				selected_plot = selected_plot.content
				num = int(selected_plot)
				if num == 0:
					await ctx.send(f"{ctx.author.mention} You're not feeling that SALTy right now.")
					return
				elif num in free_plots:
					await ctx.send(f"{ctx.author.mention} Plot {num} is already empty!")
					return

			plot_num = f"plot_{num}"
			db_clear_plot(discordID, plot_num, num, CLEAR_COST)
			print(f"{now} - {discordUser} - GARDEN - Spent {CLEAR_COST} salt to clear Plot: {num}")
			await ctx.send(f"{ctx.author.mention} You spent {CLEAR_COST} SALT to clear **Plot {num}**")
			await asyncio.sleep(1)	
			await ctx.send(f"{ctx.author.mention} **Plot {num}** is now empty and ready for a new Seed :beans:!")

		
		# Start garden  menu; wait for player input
		set_busy(discordID, True)
		finished = False
		FERT_COST = SETTINGS["garden_fert_cost"]	
		await ctx.send(f"{ctx.author.mention} Welcome to the MOFF Garden!"
			f"\nHere you can unlock Plots to plant Seeds:beans: you have collected to grow a variety of plants with unique effects or bonuses."
			f"\nWhat you get is a mystery until the plant is ready for Harvest!"
			f"\nRare plants take the longest to grow, but have the strongest effects and provide the most akumen once Harvested!"
			f"\nYou can speed up plant growth once per day per Plot."
			f"\nEach plant has a set amount of times it can be Harvested, and you may only Harvest once per day.")
		
		while not finished:
			
			# Get player garden info
			
			moff_tokens = get_player(document, "inv","moff_token")
			plots = get_player(document, "garden","free_plots")
			plots_available = len(plots)
			plots_opened = get_player(document, "garden","unlocked_plots")			
			seeds = get_player(document, "inv","seeds")
			shards = get_player(document, "inv","crystal_shard")
			akumen = get_player(document, "garden","akumen")
			plot_cost = plots_opened + 1
			

			#check if player can access garden
			if plots_opened < 1 and moff_tokens < 1:
				await ctx.send(f"{ctx.author.mention} {hehe} You need a MOFF Token{token} to use the MOFF Garden!")
				await ctx.send(f"{ctx.author.mention} You may find them while searching, or attempt to synthesize one using the MOFF-O-MATIC 6900.")
				finished = True
				set_busy(discordID, False)
				return

			# Garden messaage
			await ctx.send(f"{ctx.author.mention}"
				f"\n**Unlocked Plots**: {plots_opened}"
				f"\n**MOFF Tokens**{token}: {moff_tokens}"
				f"\n**Seeds :beans:**: {seeds}"
				f"\n**Crystal Shards** 🔹: {shards}")
				
			if plots_opened == MAX_PLOTS:
				plot_msg = f"`2` - Maximum number of Plots reached!"
			else:
				plot_msg = f"`2` - Purchase a new Plot (**COST**: {plot_cost} MOFF Token(s){token})"

			await ctx.send(f"{ctx.author.mention} Choose your action:"
				"\n`1` - See current Plot status"
				f"\n{plot_msg}"
				"\n`3` - Plant a Seed (**COST**: 1 Seed:beans:)"
				"\n`4` - Fertilize a Plot (**COST**: 5 Crystal Shards 🔹 per Plot)"
				"\n`5` - Reap what you sow (Harvest)"
				"\n`6` - SALT a Plot (**COST**: 10 SALT)"
				"\n`0` - Leave"
				"\n\n Enter your selection: ")

			try:
				selection = await self.bot.wait_for("message", check=check_int, timeout=60)
				selection = int(selection.content)

				if selection in [1, 3, 4, 5, 6] and plots_opened == 0:
					await ctx.send(f"{ctx.author.mention} {hehe} No open Plots!  Purchase your first Plot (`2`) using Moff Tokens {token}!")
					continue
				
				if selection in [0, 1, 2, 3, 4, 5, 6]:
					# Check Plot status
					if selection == 1:
						# await ctx.send(f"{ctx.author.mention} Plot Status:")	
						status_msg = check_plot(document, "status")
						await ctx.send(f"{ctx.author.mention}{status_msg}")
					
					# Buy Plot
					elif selection == 2:
						if plots_opened < MAX_PLOTS:								
							#OK To buy
							await buy_plot(moff_tokens, plots_opened, plot_cost)
						else:
							await ctx.send(f"{ctx.author.mention} {hehe} You have already opened the maximum number of Plots!")
					
					# Plant Seed
					elif selection == 3:						
						# DB Plant
						await plant_seed(seeds, plots, plots_available, akumen)

					# Fertilize
					elif selection == 4:										
						# Auto fertilize single plot, 
						# Or display which plots are fertilizable and ask player to choose
						await fertilize(shards, FERT_COST)
						
					# Harvest
					elif selection == 5:
						# Display which plots are harvestable and ask player to choose
						await harvest()
							
					# SALT earth
					elif selection == 6:
						await salt_plot()

					# Exit garden
					elif selection == 0:
						await ctx.send(f"{ctx.author.mention} Thanks for visiting the MOFF Garden! You can use `!mg` to easily return.")
						finished = True
				
				# Invalid selection
				else:
					await ctx.send(f"{ctx.author.mention} {hehe} Invalid Selection. Try again")

				await asyncio.sleep(2)
			
			# Time out
			except asyncio.TimeoutError:
				await ctx.send(f"{ctx.author.mention} Come back when you want to revisit the MOFF Garden")
				ctx.command.reset_cooldown(ctx)
				set_busy(discordID, False)
				return

			# Get db info to update
			document = find_player(discordID)
			document = list(document)

		ctx.command.reset_cooldown(ctx)
		set_busy(discordID, False)
        
def setup(bot: commands.bot):
	bot.add_cog(garden(bot))