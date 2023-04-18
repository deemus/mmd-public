import nextcord
from nextcord.ext import commands
import random
import asyncio
from datetime import datetime

from cogs.Utils.checks import *
from test_database import *
from constants import *

class dealer(commands.Cog):
    """ TAXICRAB Token Required!  """

    def __init__(self, bot: commands.bot):
        self.bot = bot


    @commands.command(aliases=["kraberto", "pepe", "hamp","Kraberto"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def dealer(self, ctx: commands.context):

        SHOT_PRICE = SETTINGS["kraberto_shot"]
        SUPP_PRICE = SETTINGS["kraberto_supp"]    
        CRAN_PRICE = SETTINGS["kraberto_cran"]                     
        
        # Delete message if not used in a DM
        if not isinstance(ctx.channel, nextcord.channel.DMChannel):
            await ctx.message.delete()
            await ctx.send(f"{ctx.author.mention} *I have no idea who you are talking about. . .*", delete_after=20)
            ctx.command.reset_cooldown(ctx)
            return

        now = datetime.datetime.today()
        discordID = ctx.author.id
        discordUser = ctx.author 

        # Get db info
        document = find_player(discordID)
        document = list(document)
        
        # Check if OK to run command
        pre_checks = ["time", "not_town"]
        if not await all_checks(pre_checks, ctx, document, "kraberto"):
            return
        
        # Only allow dealer visit once per day
        krabertoTime = get_player(document, "time", "kraberto")
        resetTime = get_reset()              
        
        # Check if bought today   
        if krabertoTime > resetTime:             
            await ctx.send(ctx.author.mention + " You're not looking so great. . . I think you should take a break from the boosters for today. . .")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} Use `!bye` to leave town, or maybe hit the `!gym` before you leave.")
            ctx.command.reset_cooldown(ctx)
            return   

        # Get player info
        moffs = get_player(document, "inv", "moffs")
        salt = get_player(document, "inv", "salt")
        taxi_tokens = get_player(document, "inv", "taxicrab")
        
        # See if player has TAXICRAB token and enough SALT	
        if taxi_tokens < 1:
            await ctx.message.delete()
            await ctx.send(f"*I have no idea who you are talking about. . .*", delete_after=20)
            ctx.command.reset_cooldown(ctx)
            return
        else:
            if salt < 5:
                await ctx.send(f"*You'll need more SALT before visiting Kraberto. . .*")
                ctx.command.reset_cooldown(ctx)
                return

        #
        # Player ready to visit dealer    
        #
        await ctx.send(f"*Ahh, excellent choice. Kraberto will take good care of you. . .*")
        
        def check(msg):
            return msg.author.id == discordID and msg.content.isdigit()

        msg = ctx.message.content.split()
                
        try:
            set_busy(discordID, True)
            
            # Request purchase
            await ctx.send("The TAXICRAB carries you toward the edge of town")
            await asyncio.sleep(1)
            await ctx.send("Despite the town being brand new, this area somehow seems to look run-down.")
            await asyncio.sleep(1)
            await ctx.send("As you turn a corner, you notice a funny looking bebe with puppets on both hands who appears deep in conversation.")
            await asyncio.sleep(2)
            await ctx.send("Kraberto notices your arrival and immediately throws open a cloak draped over his head revealing little pockets with signs next to them.")
            await asyncio.sleep(1)
            await ctx.send("It looks like he's selling items that you've never seen before. . .")
            await asyncio.sleep(2)
            await ctx.send("If you want to buy something, enter a number you see below:"
            "\n`5` - Booster shot - 5 SALT"
            "\n`10` - Booster suppository - 10 SALT"
            "\n`15` - Cranial Discombobulator - 15 SALT"
            f"\n\n**Your SALT**: {salt}")
            await asyncio.sleep(1)
            await ctx.send("Enter `0` to change your mind.")
            
            response = await self.bot.wait_for("message", check=check, timeout=60)
            purchase = int(response.content)
            
            # Allow multiple attempts for correct entry
            while purchase not in [0,5,10,15]:
                await response.add_reaction('❌')
                response = await self.bot.wait_for("message", check=check, timeout=10)
                purchase = int(response.content)
        except asyncio.TimeoutError:
            await ctx.send(f"Kraberto has no time to wait for you. . . Come back when you're ready to do business.")
            ctx.command.reset_cooldown(ctx)
            set_busy(discordID, False)
            return
        
        # Broke bebe
        if purchase > salt:
            await ctx.send(" <a:hehe_aku:867940486395097148> Does this look like a charity to you?! Come back when you can afford the wares!")
            ctx.command.reset_cooldown(ctx)
            set_busy(discordID, False)
            return

        movement = 0
        if purchase == 0:
            await ctx.send(f" At the risk of angering Kraberto, you decide to keep your hard-earned SALT and decline to make a purchase.")
            await ctx.send(f" After seeing the look on his face, you decide to tip him 1 SALT for wasting time.")
            purchase = 1
        # Booster shot - medium point boost
        elif purchase == SHOT_PRICE:
            await ctx.send("You choose the Booster shot.")
            await asyncio.sleep(1)
            await ctx.send(f" You feel pumped up!")
            movement = random.randint(3, 6)
            add_stat(discordID, "points", movement)
            await ctx.send(f"You gained {movement} movement points!")
            
            # 50% chance to be able to buy again and not lose health
            chance = random.randint(0,1)
            if chance == 1:
                await asyncio.sleep(1)
                await ctx.send(f" You're feeling energized, but nauseous. . .")
                add_stat(discordID, "health", -movement)
            
            db_kraberto(discordID, "supp", purchase, now)

        # Booster suppository - big point boost
        elif purchase == SUPP_PRICE:
            await ctx.send("You choose the Booster suppository.")
            await asyncio.sleep(1)
            await ctx.send(f" You're feeling energized, but nauseous. . .")
            movement = random.randint(6, 12)
            add_stat(discordID, "points", movement)
            await ctx.send(f" You gained {movement} movement points!")
            add_stat(discordID, "health", -movement)
            db_kraberto(discordID, "supp", purchase, now)
            

        # Cranial Discombobulator - reset looked positions, lose big health, move player to random position
        elif purchase == CRAN_PRICE:
            await ctx.send("For some reason, you choose the Cranial Discombobulator.")
            await asyncio.sleep(1)
            await ctx.send("Even Kraberto looks surprised.")
            await asyncio.sleep(2)
            await ctx.send("He motions for you to kneel as he pulls a strange glowing contraption from his cloak.")
            await asyncio.sleep(1)
            await ctx.send("With a slight tremble, he places the device over your head.")
            await asyncio.sleep(2)
            await ctx.send("You hear a high pitched whine that is increasing in volume.")
            await asyncio.sleep(1)
            await ctx.send("Soon, it becomes unbearable!")
            await asyncio.sleep(1)
            await ctx.send("You reach to pull off the device, but a bright flash of light blinds and disorients you.")
            await asyncio.sleep(2)
            await ctx.send("As your vision returns, you realize you're not in town any more.")
            await asyncio.sleep(1)
            await ctx.send("You don't know where you are. You can't remember where you have been.")
            await asyncio.sleep(1)
            await ctx.send("Your SALT bag feels lighter, and you have a headache.")
            
            # Lose health and salt; move to random position
            db_kraberto(discordID, "cran", purchase, now)
            add_stat(discordID, "health", -15)
            add_item_amt(discordID, "salt", -purchase)            
            remove_looked(discordID)            
            randPos = random.randint(1,20)
            move_player(discordID, randPos)
            
            print(f"{now} - {discordUser} - KRABERTO Discombobulator - Health -15")
            set_busy(discordID, False)
            return

        await ctx.send(f" You pay {purchase} SALT to Kraberto.")
        add_item_amt(discordID, "salt", -purchase)
        print(f"{now} - {discordUser} - Kraberto Visit - Spent {purchase} SALT "
        f"- Gained {movement} move points")
        ctx.command.reset_cooldown(ctx)
        
        set_busy(discordID, False)

def setup(bot: commands.bot):
    bot.add_cog(dealer(bot))
