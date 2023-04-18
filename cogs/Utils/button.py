import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from nextcord.ext.commands import Bot, Cog


# class Ping(Cog):
#     def __init__(self, bot: Bot) -> None:
#         self.bot = bot

#     @commands.command(name="ping", description="A simple ping command.")
#     async def ping(self, inter: Interaction) -> None:
#         await inter.send(f"Pong! {self.bot.latency * 1000:.2f}ms")




class Button(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        

    @nextcord.ui.button(label= 'Test', style=nextcord.ButtonStyle.green)
    async def test(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("Button tested", ephemeral=True)
        self.value = True
        self.stop()

    @nextcord.ui.button(label= 'Toast', style=nextcord.ButtonStyle.red)
    async def toast(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("Button tested", ephemeral=True)
        self.value = False
        self.stop()

class button(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def butt(self, ctx):
        view = Button()
        await ctx.send("Let's test", view=view, hidden = True )
        await view.wait()
        if view.value is None:
            return
        elif view.value:
            await ctx.send("Thanks for testing")
        else:
            await ctx.send("Thanks for nothing")

def setup(bot: Bot):
    bot.add_cog(button(bot))