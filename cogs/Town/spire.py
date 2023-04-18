import nextcord
from nextcord.ext import commands
import random
import asyncio
from datetime import datetime

from cogs.Utils.checks import *
# from cogs.roles import *
from test_database import *
from constants import *


class spire(commands.Cog):
    """ (TOWN) Climb the Sparkly Spire for fame, glory, and Crystals """

    def __init__(self, bot: commands.bot):
        self.bot = bot
        
    
    @commands.command(aliases=["sparkle", "sparkly","s","S","Spire"])
    @commands.cooldown(1, 45, commands.BucketType.user)
    
    async def spire(self, ctx: commands.context):

        DANCE_EMOJI = EMOJIS["dance"]
        

        def check_string(msg):
            return msg.author.id == discordID and isinstance(msg.content, str) and (msg.content).upper() in ["YES","NO", "Y","N","START","S"]


        def check_int(msg):
            return msg.author.id == discordID and msg.content.isdigit()


        def submit_score(id, score, crystals, level):
            # Save score to db
            if score >= bestScore or score >= oldScore:
                db_spire_best(id, score, crystals, level, now)
            else:
                db_spire(id, oldScore, crystals, level, now)
                
        
        now = datetime.datetime.today()
        discordID = ctx.author.id
        discordUser = ctx.author

        score = distance = choice = guess = totalScore = usedCrystals = 0
        hasFinished = False
        redo = True
        level = 1   

        # Get db info
        document = find_player(discordID)
        document = list(document)

        # Check if OK to Spire
        pre_checks = ["channel", "time", "not_town"]
        if not await all_checks(pre_checks, ctx, document, "spire"):
            return

        # Show scores
        bestScore = get_player(document, "all_stats", "totals", "spire_score")
        oldScore = get_player(document, "week_stats", "totals", "spire_score")
        if not bestScore:
            bestScore = 0
        if not oldScore:
            oldScore = 0
        await ctx.send(f"{ctx.author.mention}"
        f"\nBest Score (All Time): {bestScore}"
        f"\nBest Score (This Week): {oldScore}"
        "\nTop Scores: https://tinyurl.com/sparklyspire")
        await asyncio.sleep(1)

        # Require 20 SALT to enter Spire
        salt = get_player(document, "inv", "salt")
        if salt < 20:
            await ctx.send(f"{ctx.author.mention} <a:hehe_aku:867940486395097148> "
            "You must collect at least 20 SALT before you attempt to climb the Sparkly Spire!")
            ctx.command.reset_cooldown(ctx)
            return

        # No Time Crystals message
        crystals = get_player(document, "inv", "time_crystal")
        if crystals > 0:
            await ctx.send(f"{ctx.author.mention} TIME Crystals<:crystal:936472306224627753> in your inventory: {crystals}")
        else:
            await ctx.send(ctx.author.mention + " <a:hehe_aku:867940486395097148> No Time Crystals<:crystal:936472306224627753> found."
            "\nGo to the `!trader` first to get some! Without them, it's unlikely you will reach the top. Good luck!")
        
        # Initial Spire message, wait for player to start
        await ctx.send(f"{ctx.message.author.mention} You entered the 💎**Crystal Crab's Sparkly Spire**💎!"
        "\nTo progress, you must guess a number in the top 45% or bottom 45% of the max value for each level."
        "\nThe Crystal Crab will also choose a number in either the top or bottom 45%."
        "\nThe closer you are to the Crystal Crab's guess, the more points you will get!"
        "\nGuess exactly correct and get bonus points!"
        "\nThe range of valid guesses will be provided, and the middle 10% (that the Crystal Crab will never choose) is displayed as the **DEAD ZONE**"
        "\n\nAdditionally, your Time Crystals<:crystal:936472306224627753> (if you have them) will signal whenever you guess incorrectly."
        "\nWhen that happens, you can sacrifice 1 Time Crystal<:crystal:936472306224627753> to change your guess."
        "\nThe CRAB's guess will not change."
        "\n\nThere are **6 levels** total."
        "\nWhen you're ready, type `[S]TART` to begin!"
        "\n\n**NOTE: Visit the `!trader` to swap SALT Crystals💎 for Time Crystals<:crystal:936472306224627753>!**")
        try:
            begin = await self.bot.wait_for("message", check=check_string, timeout=40)
            begin = (begin.content).upper()

            if begin in  ["START", "S"]:
                set_busy(discordID, True)
                await ctx.send(f"{ctx.author.mention} You begin your climb. . .")
            else:
                await ctx.send(f"{ctx.author.mention} You decide you're not ready to climb yet.")
                return
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} You decide you're not ready to climb yet.")
            return

        def calculate_ranges(salt, level):
            MAX = salt * level
            MID = MAX / 2
            loRange = int(MID - (MAX * 0.05))
            hiRange = int(MID + (MAX * 0.05))
            totalPoints = 1000 + MAX
            return MAX, MID, loRange, hiRange, totalPoints

        def calculate_score(distance, totalPoints, level, loRange, hiRange, guess, rangeMAX):
            odds = distance / rangeMAX
            oddsBonus = rangeMAX * level
            bonus_scale = 10 / (10 - level)
            bonus = oddsBonus - (oddsBonus * odds)
            bonus = max(0, bonus) * bonus_scale

            score = int((totalPoints - (distance * (11 - level))) + bonus)

            if loRange <= guess <= hiRange:
                score /= 2

            bonus_percentages = [(0.01, 2), (0.03, 1.5), (0.06, 1.25)]
            for percentage, multiplier in bonus_percentages:
                if distance <= (rangeMAX * percentage):
                    score *= multiplier
                    break

            return int(score)
        
        # Start spire
        while not hasFinished:
            MAX, MID, loRange, hiRange, totalPoints = calculate_ranges(salt, level)
            rangeMAX = int(MAX / 2)
            # #MAX = totals[level]
            # MAX = salt * level
            # MID = MAX / 2
            # loRange = int(MID - (MAX * .05))
            # hiRange = int(MID + (MAX * .05))
            # totalPoints = 1000 + MAX

            # Choose random number outside of middle 10% of range
            choice = random.randint(1, MAX)
            print(choice)
            while choice not in range(1, loRange) and choice not in range(hiRange+1, MAX+1):
                choice = random.randint(1, MAX)
                print(choice)

            # New Level message
            await ctx.send(f"{ctx.author.mention} \n##################\n**Level {level}**"
            f"\nTime Crystals<:crystal:936472306224627753>: {crystals} \nDEAD ZONE: `{loRange}` to `{hiRange}`"
            "\n##################")

            # Let user guess again if they use a crystal
            while redo:
                redo = False

                # Get user's guess
                try:
                    await ctx.send(f"{ctx.author.mention} Guess a number from `1` to `{MAX}`: ")
                    guess = await self.bot.wait_for("message", check=check_int, timeout=90)
                    guess = int(guess.content)

                    # Invalid guess
                    while guess not in range(1,MAX+1):
                        await ctx.send(f"{ctx.author.mention} Invalid Guess! Guess a number from `1` to `{MAX}`: ")
                        guess = await self.bot.wait_for("message", check=check_int, timeout=90)
                        guess = int(guess.content)
                    
                    # Let player use time crystal for wrong guess
                    if crystals > 0:
                        if (choice < MID and guess >= MID) or (choice > MID and guess < MID):
                            await ctx.send(f"{ctx.author.mention} Your Time Crystal<:crystal:936472306224627753> "
                            "is glowing red, do you want to sacrifice the Crystal to guess again?"
                            "\nEnter: `[Y]ES` or `[N]O`")
                            
                            # Validate confirmation
                            confirm = await self.bot.wait_for("message", check=check_string, timeout=90)
                            confirm = (confirm.content).upper()
                            
                            # Subtract crystal
                            if confirm in  ["YES", "Y"]:
                                await ctx.send(f"{ctx.author.mention} You smash your Time Crystal<:crystal:936472306224627753> "
                                "and feel time rewinding back to the point where you made your last guess!")
                                
                                add_item_amt(discordID, "time_crystal", -1)
                                print(f"{now} - {discordUser} - Used Time Crystal in SPIRE")
                                
                                crystals -= 1
                                usedCrystals += 1
                                redo = True
                            else:
                                continue
                        else:
                            continue
                    else:
                        continue
                
                # Time out
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.message.author.mention} You took too long to guess, try again tomorrow.")
                    await ctx.send(f"{ctx.author.mention} Total Score: {totalScore}")
                    submit_score(discordID, totalScore, usedCrystals, level)
                    set_busy(discordID, False)
                    return                
                
            # Calculate score
            # rangeMAX = int(MAX / 2)
            # distance = abs(choice - guess)
            # odds = distance / rangeMAX
            # oddsBonus = rangeMAX * level
            # bonus = oddsBonus - (oddsBonus * odds)
            # if bonus < 0:
            #     bonus = 0
            # score = int((totalPoints - (distance * (11 - level))) + bonus)
            
            # # Penalty for guessing in mid range
            # if guess in range(loRange, hiRange+1):
            #     score /= 2

            # # Bonus for exact or close guesses
            # if distance == 0:
            #     score *= 2
            # elif distance <= (rangeMAX * .01):
            #     score *= 1.5
            # elif distance <= (rangeMAX * .03):
            #     score *= 1.25
            # elif distance <= (rangeMAX * .06):
            #     score *= 1.1
            
            score = calculate_score(distance, totalPoints, level, loRange, hiRange, guess, rangeMAX)

            # Display stats
            await ctx.send(f"{ctx.author.mention} \nYou guessed: `{guess}`\nCRAB chose: `{choice}`")
            await asyncio.sleep(1)

            # Advance to next level if guess is close enough
            if (choice > MID and guess >= MID) or (choice < MID and guess < MID):
                await asyncio.sleep(1)
                await ctx.send(f"{ctx.author.mention} <:akucool:890838685308825610> Level Completed! <:akucoolright:920795863918460948>"
                f"\nLevel Score: {score}")
                totalScore += score
                level += 1
                redo = True

                # Chance to gain crystal shards
                if level > 1:
                    randomShard = random.randint(0,2)
                    if randomShard > 0:
                        await ctx.send(f"{ctx.author.mention} Crystal Shards🔹 collected: {randomShard}")
                        add_item_amt(discordID, "crystal_shard", randomShard)
                        print(f"{now} - {discordUser} - Found {randomShard} Crystal Shard(s)")

            else:
                await asyncio.sleep(1)
                await ctx.send(f"{ctx.author.mention} <a:hehe_aku:867940486395097148> Bummer, your guess was wrong. Better luck next time!")
                await ctx.send(f"{ctx.author.mention} Level score: 0")
                hasFinished = True
            
            # Completed spire
            if level == 7:
                await asyncio.sleep(1)
                await ctx.send(f"{ctx.author.mention} Congratulations!, you bested the CRYSTAL CRAB and reached the top of the Sparkly Spire!")
                add_item_amt(discordID, "salt_crystal", 1)
                await ctx.send(f"{ctx.author.mention} You gain a SALT Crystal💎 for reaching the top!")
                # await give_role(self, ctx, "SPARKLY")
                hasFinished = True

        # Add score to db        
        finishedLevel = level - 1
        submit_score(discordID, totalScore, usedCrystals, finishedLevel)
        await asyncio.sleep(1)
        await ctx.send(f"{ctx.author.mention} You completed {finishedLevel} out of 6 levels.\nFinal score = {totalScore}")
        await asyncio.sleep(1)
        await ctx.send(f"{ctx.author.mention} If you are done in town, use `!bye` to return back to where you were, "
        "or `!look` to see what else is around.")

        # Save score to DB
        print(f"{now} - {discordUser} - SPIRE - LEVEL {finishedLevel} - CRYSTALS: {usedCrystals} - SALT: {salt} - SCORE: {totalScore}")
        set_busy(discordID, False)


def setup(bot: commands.bot):
    bot.add_cog(spire(bot))