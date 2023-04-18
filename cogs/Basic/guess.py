# import nextcord
from nextcord.ext import commands
import random
import asyncio
from datetime import datetime

from cogs.Utils.checks import *
from test_database import *
from constants import *

HOVELS = SETTINGS["hovels"]
WIN_AMT = SETTINGS["guess_win_amt"]
LOSE_AMT = SETTINGS["guess_lose_amt"]
GUESS_ATTEMPTS = SETTINGS["guess_attempts"]

MOFF_EMOJI = EMOJIS["moff"]
CRAB_EMOJI = EMOJIS["crab"]
DRAGUM_EMOJI = EMOJIS["dragum"]

error_message = "<a:hehe_aku:867940486395097148> Not a valid choice."
error_message +=f"\nValid choices are:" 
error_message +=f"\n{MOFF_EMOJI} `:moff:`"
error_message +=f"\n{CRAB_EMOJI} `:akucrab:`"
error_message +=f"\n{DRAGUM_EMOJI} `:dragum:`"

class guess(commands.Cog):
    """ Play a guessing game while at a Hovel  """

    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command(aliases=["gamble", "gambol", "g", "G","Guess"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def guess(self, ctx: commands.context):
        now = datetime.datetime.today()
        discordID = ctx.author.id
        discordUser = ctx.author

        valid = ["moff", "crab", "dragum"]
        choice = 0        
        
        # Get db info
        document = find_player(discordID)
        document = list(document)

        # Check if OK to guess
        pre_checks = ["channel"]
        if not await all_checks(pre_checks, ctx, document, "move"):
            return        
    
        # Split message
        parts = ctx.message.content.split(' ')
        
        # Must be in an established hovel to guess
        position = get_player(document, "pos")        
        if position not in HOVELS:
            await ctx.send(ctx.author.mention + ' <a:hehe_aku:867940486395097148> There\'s no one around to play the guessing game at this location. Get to an established hovel first!\nEstablished hovels are located at positions: ' + str(HOVELS))
            ctx.command.reset_cooldown(ctx)
            return        
                
        # Check guess count
        guesses = get_guess_count(document)
        if guesses == GUESS_ATTEMPTS:
            await ctx.send(ctx.author.mention + ' <a:hehe_aku:867940486395097148> You have reached your guess limit for this week!')
            return
            
        # Guess Explanation message
        if len(parts) < 2:
            await ctx.send(f"{ctx.author.mention} <a:hehe_aku:867940486395097148> So you want to test your luck?"
            "\nUse `!guess <choice>` to play."
            f"\nValid choices are:  {MOFF_EMOJI} / {CRAB_EMOJI} / {DRAGUM_EMOJI}  (`:moff: / :akucrab: / :dragum:`)"
            f"\nYou may guess up to {GUESS_ATTEMPTS} times each week. Correct matches will win {WIN_AMT} MOFFS."
            f"\nWrong guesses lose {LOSE_AMT}. You have a 1 in 3 chance of winning."
            f"\n\n**NOTE**: You must be on an established HOVEL to play this game."
            f"\nHOVELS are located at positions: {HOVELS}")
            ctx.command.reset_cooldown(ctx)
            return
        
        # Check Player's guess    
        guess = parts[1].lower()
        if any(x in guess for x in valid): 
            if "moff" in guess:
                choice = 1
                emoChoice = MOFF_EMOJI
            elif "crab" in guess:
                choice = 2
                emoChoice = CRAB_EMOJI
            elif "dragum" in guess:
                choice = 3
                emoChoice = DRAGUM_EMOJI
        else:
            # Invalid guess
            await ctx.send(f"{ctx.author.mention} {error_message}")
            ctx.command.reset_cooldown(ctx)
            return

        # Out of guesses
        if guesses >= GUESS_ATTEMPTS:
            await ctx.send(ctx.author.mention + ' <a:hehe_aku:867940486395097148> You have reached your guess limit for this week!')
            return
        
        # Able to guess here                   
        spin = random.randint(1, 3)
        if spin == 1:
            emoSpin = MOFF_EMOJI
        elif spin == 2:
            emoSpin = CRAB_EMOJI
        elif spin == 3:
            emoSpin = DRAGUM_EMOJI
        
        await ctx.send('You guessed: ' + emoChoice)                        
        await ctx.send('Hovel pick: ')
        await asyncio.sleep(3)
        await ctx.send(emoSpin)
        await asyncio.sleep(1)
        
        # Correct guess
        if choice == spin:
            print(f"{now} - {discordUser} - Picked {choice}: WIN")                     
            await ctx.send(f"{ctx.author.mention} Correct! You win {WIN_AMT} MOFFS!")
            db_guess(discordID, "WIN", WIN_AMT, now)
        
        # Wrong guess
        else:
            print(f"{now} - {discordUser} - Picked {choice}: LOSE")                     
            await ctx.send(ctx.author.mention + ' <a:hehe_aku:867940486395097148> You lost!')
            db_guess(discordID, "LOSE", LOSE_AMT, now)
        
        guessesRemaining = (GUESS_ATTEMPTS - 1) - guesses
        await asyncio.sleep(1)
        await ctx.send(f"{ctx.author.mention} Guess attempts remaining: {guessesRemaining}")
        ctx.command.reset_cooldown(ctx)
        
    
    # @guess.error
    # async def guess_error(self, ctx: commands.Context, error: commands.CommandError):
    #     """Handle errors for the example command."""
    #     print(error)
    #     message = error_message
    #     await ctx.send(message, delete_after=6)
    #     await ctx.message.delete(delay=6)

        
def setup(bot: commands.bot):
    bot.add_cog(guess(bot))