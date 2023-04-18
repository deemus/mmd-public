import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import context
import asyncio
from cogs.Utils.checks import *
from test_database import *

class register(commands.Cog):
    """ Use once to get started, then forget about it """

    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command(aliases=["Register", "reg","Reg"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def register(self, ctx: commands.context):
        
        discordID = ctx.author.id   
        discordName = str(ctx.author)
        manualChannel = 881380544917667890
        faqChannel = 888466821060128778
        msg = ctx.message.content.split()
        wax = ''
        
        # Get db info
        document = find_player(discordID)
        document = list(document)

        # Check wax address entered correctly
        try:
            wax = msg[1]
        except IndexError:
            await ctx.send(f"{ctx.author.mention} <a:hehe_aku:867940486395097148> Invalid command use."
            "\nPlease use `!register waxaddress.wam` to register your address to the database.")
            ctx.command.reset_cooldown(ctx)
            return
        
        # Check valid address
        if len(wax) < 5 or len(wax) > 12:
            await ctx.send("I'm fairly certain that is not a valid WAX address."
            "\nPlease try again, or message `Deemaku` if there's an issue.")
            ctx.command.reset_cooldown(ctx)
            return
        
        # Check if already registered
        try:
            if get_player(document, "wax"):
                await ctx.message.delete()
                await ctx.send(f"{ctx.author.mention} <a:hehe_aku:867940486395097148>"
                f"You are already registered with `{wax}`."
                "\nTo prevent cheating, please message <@274656402721472512> if you need to update or correct your registered WAX address."
                "\n(This message will be deleted soon.)", delete_after=20)
                return
        except IndexError:
            # New Player, Register to DB
            await ctx.message.delete() 
            print(f"{ctx.message.created_at} - {ctx.author}: {ctx.message.content}")
            register_player(discordID, discordName, wax)
            
            await ctx.send(f"{ctx.author.mention} WAX Addresss registered!")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention}\nWelcome to AKU WORLDS!"
            "\n\nHave a precious SALT Crystal💎 for free to help you get started!"
            "\nTry using `!attract` and `!roll` now! "
            "\n\nUse `!wtf` for detailed command information."
            f"\nThe pinned hints in <#{manualChannel}> are also going to be useful!"
            f"\nAsk your questions, leave your comments, or report bugs in <#{faqChannel}>")
            return
       

def setup(bot: commands.bot):
    bot.add_cog(register(bot))