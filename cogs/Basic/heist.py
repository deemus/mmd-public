import nextcord
from nextcord.ext import commands
import random
import asyncio
from datetime import datetime


from cogs.Utils.checks import *
from test_database import *
from constants import *

class heist(commands.Cog):
    """ Attempt to steal SALT from the DRAGUM's lair until your MOFF MAJIC protection runs out """

    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command(aliases=["hiest","H","h","Heist","Hiest"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    
    async def heist(self, ctx: commands.context):
        # Function to Verify response
        def check(msg):
            return msg.author.id == discordID and msg.content.upper() in ["STEAL", "RUN", "S", "R"]

        
        discordUser = ctx.author
        discordID = ctx.author.id
        now = datetime.datetime.today()

        salt_stolen = 0
        salt_total = 0
        crystalsUsed = 0
        round = 1
        
        # Get db info
        document = find_player(discordID)
        document = list(document)

        # Check if OK to heist
        pre_checks = ["channel", "time"]
        if not await all_checks(pre_checks, ctx, document, "heist"):
            return
        
        # Get MOFF MAJIC DEF       
        player_def = get_player(document, "inv", "moffs")
        
        if player_def < 25:
            await ctx.send(ctx.author.mention + " <a:hehe_aku:867940486395097148> It's dangerous to attempt a heist from the DRAGUM's SALT mine."
            "\nYou will need to have attracted at least 25 MOFFS in order to build up your MAJIC MOFF DEF."
            "\nTry again when you have more MOFFS!")
            ctx.command.reset_cooldown(ctx)
            return
        
        # OK To Heist, set busy
        set_busy(discordID, True)

        #Get Majic DEF Crystals
        crystals = get_player(document, "inv", "def_crystal")
        if crystals > 0:
            await ctx.send(f"{ctx.author.mention} MAJIC Defense Crystals<:crystal2:936476907376103475> in your inventory: {crystals}"
            "\nThese Crystals will **automatically** be used when you take a hit from the DARK MOFFS over your remaining DEF, allowing you to escape with your SALT next turn!")
        else:
            await ctx.send(ctx.author.mention + " <a:hehe_aku:867940486395097148> No MAJIC Defense Crystals<:crystal2:936476907376103475> found."
            "\nGo to the `!trader` in town to get some if you want extra protection during your heist.")
        
        # Start Heist
        await ctx.send(f"{ctx.message.author.mention} You started a heist! "
        "It\'s a race against time to get as much SALT as you can from the DRAGUM\'s lair before your armor is drained and you are forced to retreat."
        "\nBe warned. . . The more SALT you try to steal, the angrier the DARK MOFFS will become."
        f"\n\nYour **MOFF MAJIC DEF**: {player_def}\nChoose `[S]TEAL` to start the heist.")

        # Wait for first response
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30) # 30 seconds to reply
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.message.author.mention} You fell asleep on the job. Try again when you're ready to FOCUS!")
            set_busy(discordID, False)
            return    
        
        # Continue Heist
        await ctx.send(f"{ctx.author.mention} You sneak into the SALT mine and look for a good spot to gather some SALT. . .")
        await asyncio.sleep(2)
        await ctx.send(f"{ctx.author.mention} You'll have to withstand attacks from the DARK MOFFS while you attempt this heist.")
        await asyncio.sleep(2)
        await ctx.send(f"{ctx.author.mention} Your MOFF MAJIC DEF will protect you, but not for long. . .")
        await asyncio.sleep(1)
        
        # Continue until player runs away    
        while msg.content.upper() not in  ["RUN", "R"]:
            salt_stolen = random.randint(2, 4+round)
            salt_total += salt_stolen
            dragum_atk = random.randint( (4 * round), (10 * round))
            player_def -= dragum_atk
            
            # Player steals and DRAGUM attacks
            await ctx.send(f"{ctx.message.author.mention} You stole: {salt_stolen} SALT! - Total stolen: {salt_total} SALT\nThe DARK MOFFS drained {dragum_atk} points of your **DEF**!")
            await asyncio.sleep(1)
            
            # Player lost all DEF
            if player_def <= 0:
                if crystals > 0:
                    player_def += dragum_atk
                    crystals -= 1                    
                    add_item_amt(discordID, "def_crystal", -1)
                    print(f"{now} - {discordUser} - Used MAJIC Defense crystal in HEIST")
                    crystalsUsed += 1
                    await ctx.send(f"{ctx.author.mention} Your MAJIC Defense Crystal<:crystal2:936476907376103475> shattered and saved you from the DARK MOFF's attack!"
                    f"\nRemaining MAJIC Defense Crystals<:crystal2:936476907376103475>: {crystals} ")
                else:
                    #Heist Fail
                    salt_total = 0
                    print(f"{now} - {discordUser}: - Heist results: Got BURNED, lost {salt_total}")
                    db_heist(discordID, salt_total, crystalsUsed, now)

                    await ctx.send(f"{ctx.message.author.mention} You ran out of MOFF MAJIC DEF and were forced to retreat, leaving all your SALT behind!"
                    "\nUse `!p` to check your progress.")
                    set_busy(discordID, False)
                    return
            
            # Player still has DEF            
            await ctx.send(f"{ctx.message.author.mention} Your remaining **MOFF MAJIC DEF**: {player_def}\nChoose to `[S]TEAL` or `[R]UN`")
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30) # 30 seconds to reply
            except asyncio.TimeoutError:
                await ctx.send(ctx.message.author.mention + " In your hesitation, the DARK MOFFS attacked!")

            round += 1        
            await asyncio.sleep(1)
        
        # Heist Success
        await ctx.send(f"{ctx.message.author.mention} You managed to complete your heist and escape with {salt_total} SALT!"
        "\nUse `!p` to check your progress.")
        
        print(f"{now} - {discordUser}: - Heist results: {salt_total} SALT stolen")
        db_heist(discordID, salt_total, crystalsUsed, now)
        
        set_busy(discordID, False)


def setup(bot: commands.bot):
    bot.add_cog(heist(bot))