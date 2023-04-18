import random
# import requests
import time 
from test_database import *
from nextcord.ext import commands
from nextcord.ext.commands import context
from cogs.Utils.checks import *
import constants
import random
import asyncio

class mom(commands.Cog):
    """ The MOFF-O-MATIC 6900 can produce in-game MOFF Tokens, if you're lucky  """

    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command(aliases=["MOM", "MOFF-O-MATIC", "moff-o-matic", "moffomatic", "machine", "kiosk"])
    @commands.cooldown(1, 15, commands.BucketType.user)

    async def mom(self, ctx: commands.context):

        CRYSTAL_BOOST = SETTINGS["mom_crystal_boost"]
        COST_MULTIPLIER = SETTINGS["mom_moff_cost_multiplier"]

        discordID = ctx.author.id
        discordUser = ctx.author
        now = datetime.datetime.today()
        token = EMOJIS["moff_token"]
        crystal_emojis = "💎<:crystal:936472306224627753><:crystal2:936476907376103475>"
        hehe = EMOJIS["hehe"]

        # Get db info
        document = find_player(discordID)
        document = list(document)

        # Check if OK to use moff o matic
        pre_checks = ["channel", "not_town"]
        if not await all_checks(pre_checks, ctx, document, "mom"):
            return

        # # Valid response checks
        # def check_string(msg):
        #     return msg.author.id == discordID and isinstance(msg.content, str) and (msg.content).upper() in ["YES","NO", "Y","N"]
        # def check_int(msg):
        #     return msg.author.id == discordID and msg.content.isdigit()

        # Get stats
        moffs = get_player(document, "inv", "moffs")
        power = get_player(document, "info", "fakulty")
        successes = get_player(document, "week_stats", "counts", "mom_win")
        success_chance = power

        # MOM Startup messages
        startup_messages = [
            "A noise from inside the machine sounds eerily familiar to what you imagine an army of screaming ants would sound like.",
            "There's a loud **BANG**, followed by a *whirrr*, then a slowing series of clicks.",
            "*The MOFFS in your inventory all shudder in unison*.",
            "*Time feels like it's standing still*.",
            "*In the distance, sirens.*",
            "It appears that nothing happened...  Suddenly, the screen lights up with information:",
            "**OW!** You quickly jerk your hand away after receiving a mild electric shock.",
            "The machine emits a deafening screech, like a thousand nails on a chalkboard, before powering on.",
            "*A cloud of smoke billows out from the machine and slowly dissipates around you.",
            "You hear the sound of gears grinding together, like the inside of a clock, before the screen comes to life.",
            "Suddenly, the air crackles with electricity, and the hair on the back of your neck stands up.",
            "*A bright flash of light blinds you momentarily before the screen flickers on.*",
            "*The ground beneath your feet trembles slightly.*",
            "The machine emits a strange, otherworldly noise that is unlike anything you have ever heard.",
            "The machine emits a low growling sound, like a hungry beast that's just been fed.",
            "The screen flickers to life with a series of glitches and static, before stabilizing.",
            "You hear a faint whistling sound, like a breeze passing through a canyon, before the machine comes to life.",

        ]

        # MOM Info display
        def create_message(moffs, power, moff_cost, success_chance):
            message = ""
            message += f"\n**Your MOFFS**: {moffs}"
            message += f"\n**Your AKU POWER**: {power}"
            message += f"\n**MOFF Cost**: {moff_cost}"
            message += f"\n**Success Chance**: {success_chance}%\n"
            return message
        
        
        # Player can choose to use a crystal, if they have some
        async def get_crystals(document):
            crystal_inv = ''
            salt_crystal = get_player(document, "inv", "salt_crystal")
            time_crystal = get_player(document, "inv", "time_crystal")
            def_crystal = get_player(document, "inv", "def_crystal")
            crystals = {"salt_crystal": salt_crystal, "time_crystal": time_crystal, "def_crystal": def_crystal}
            choices = {"salt_crystal": 1, "time_crystal": 2, "def_crystal": 3}

            # Display available crystals
            for crystal in crystals:
                # if crystals[crystal] > 0:
                crystal_inv += (f"`{choices[crystal]}` - {ITEMS[crystal]['desc']}:  {crystals[crystal] }\n")

            # Ask player which crystal to use, if they have some
            if crystal_inv:
                await ctx.send(f"{ctx.author.mention} **Your Crystals**:\n{crystal_inv}"
                                                            "`0` - None"
                                                            "\nEnter Choice (`0, 1, 2, 3`): ")
            else:
                await ctx.send(f"{ctx.author.mention} You don't have any Crystals available to use!")
                return False
            
            # Get crystal choice
            try:                
                choice = await self.bot.wait_for("message", check=check_input("int", discordID), timeout=60)
                choice = int(choice.content)
                
                if choice in [1, 2, 3]:
                    # Get key from value. Key is the db item name (e.g. 'salt_crystal')
                    key = list(choices.keys())[list(choices.values()).index(choice)]
                    description = ITEMS[key]['desc_s']
                    
                    if crystals[key] > 0:
                        await ctx.send(f"{ctx.author.mention} You added a {description} to the machine.")
                        return key
                    else:
                        await ctx.send(f"{ctx.author.mention} You don't have enough of those Crystals!")
                        return False
                
                elif choice == 0:
                    await ctx.send(f"{ctx.author.mention} You decided not to use any Crystals")
                    return False                    
                else:
                    await ctx.send(f"{ctx.author.mention} Invalid choice")
                    return False

            # Timeout
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention} Crystal addition timed out.")
                set_busy(discordID, False)
                return
        
        
        #
        # MOM
        #
        await ctx.send(f"{ctx.author.mention} You start up the MOFF-O-MATIC 6900.")
        await asyncio.sleep(1)
        
        # Cost to use machine increases each time player succeeds
        moff_cost = 20 + (successes * COST_MULTIPLIER)
        
        # Too broke to use MOM      
        if moffs < moff_cost:
            await ctx.send(f"{ctx.author.mention} {hehe} It currently costs {moff_cost} MOFFS to use this machine, "
                                                    f"but you only have {moffs}!")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} The MOFF-O-MATIC 6900 powers down. ")
            ctx.command.reset_cooldown(ctx)
            return
        
        # OK to Start MOM - Choose startup message
        await ctx.send(f"{ctx.author.mention} {random.choice(startup_messages)}")
        await asyncio.sleep(1)
        
        set_busy(discordID, True)
        message = create_message(moffs, power, moff_cost, success_chance)

        await ctx.send(f"{ctx.author.mention} {message}")
        
        # Chance for player to add crystals to boost chances
        crystal = False
        await ctx.send(f"{ctx.message.author.mention} You can add one Crystal ({crystal_emojis}) to boost your success chance."
        f"\nYou will only lose the Crystal if you are successful.")            
        
        crystal = await get_crystals(document)
        if crystal:
            success_chance += CRYSTAL_BOOST
            message = create_message(moffs, power, moff_cost, success_chance)
            await ctx.send(f"{ctx.message.author.mention} {message}")
        
        # Verify player wants to proceed
        if success_chance != 0:
            await ctx.send(f"{ctx.author.mention} Do you want to spend {moff_cost} MOFFS to attempt to create a {token}?"
                            f"\nEnter `[Y]es` or `[N]o`: ")
        
        # No chance to succeed
        else:
            await ctx.send(f"{ctx.author.mention} Trust me, you don't want to continue using this machine right now. "
            f"You would just be destroying those poor MOFFS for nothing. They have a family! ")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention}"
            f" The MOFF-O-MATIC 6900 powers down with a tone that sounds like disappointment.  Use `!mom` when you're ready to try again.")
            set_busy(discordID, False)
            return
        
        # Proceed with attempt
        try:
            start = await self.bot.wait_for("message", check=check_input("text", discordID), timeout=60)
            start = (start.content).upper()

            if start in  ["YES", "Y"]:                
                # Success if match falls under success chance
                match = random.randint(1, 100)
                if match < success_chance:
                    result = "success"
                    
                    if crystal:
                        await ctx.send(f"{ctx.author.mention} The light from your {ITEMS[crystal]['desc_s']} is absorbed and it disintegrates before your eyes!")

                    await ctx.send(f"{ctx.author.mention} Woohoo! You spent {moff_cost} MOFFS and gained a {token}!")
                
                else:
                    result = "fail"
                    await ctx.send(f"{ctx.author.mention} Sadly, you spent {moff_cost} MOFFS and failed to create a MOFF Token :(")
                    await ctx.send(f"{ctx.author.mention} You were able to recover your Crystal.")
                
                #Finished, update database
                db_mom(discordID, result, moff_cost, crystal)

                print(f"{now} - {discordUser}: MOM - MOFFS: {moff_cost} - Crystals: {crystal} - Result: {result}")
                set_busy(discordID, False)
            
            # Cancel command
            else:
                await ctx.send(f"{ctx.author.mention} You changed your mind and powered down the MOFF-O-MATIC 6900. "
                f"Any inserted Crystals are refunded.  Use `!mom` if you want to try again.")
                set_busy(discordID, False)
                return
        
        # Timeout
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} The machine waited too long for a response and turned itself off to conserve power. "
            f"Any inserted Crystals are refunded.  Use `!mom` when you're ready to try again.")
            set_busy(discordID, False)
            return


def setup(bot: commands.bot):
    bot.add_cog(mom(bot))