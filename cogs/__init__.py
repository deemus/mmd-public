from cogs import Basic, Town, Status, Special, Utils
def unload(bot) -> None:
    """
    Reinstates the original help command.
    This is run if the cog raises an exception on load, or if the extension is unloaded.
    """
    bot._old_help = bot.get_command("help")
    bot.remove_command("help")
    bot.add_command(bot._old_help)

def teardown(bot) -> None:
    """
    The teardown for the help extension.
    This is called automatically on `bot.unload_extension` being run.
    Calls `unload` in order to reinstate the original help command.
    """
    unload(bot)

def setup(bot):
    #load cogs at the start of the bot
    #Basic
    bot.load_extension('cogs.Basic.attract')
    bot.load_extension('cogs.Basic.move')
    bot.load_extension('cogs.Basic.heist')
    bot.load_extension('cogs.Basic.guess')
    bot.load_extension('cogs.Basic.look')
    bot.load_extension('cogs.Basic.taxi')
    
    #Town    
    bot.load_extension('cogs.Town.gym')
    bot.load_extension('cogs.Town.spire')
    bot.load_extension('cogs.Town.trader')
    bot.load_extension('cogs.Town.mom')
    bot.load_extension('cogs.Town.garden')
    
    #Special
    bot.load_extension('cogs.Special.movelook')
    bot.load_extension('cogs.Special.dealer')
    bot.load_extension('cogs.Special.pump')
    # bot.load_extension('cogs.Special.mine')

    #Status
    bot.load_extension('cogs.Status.register')
    bot.load_extension('cogs.Status.progress')
    bot.load_extension('cogs.Status.inventory')
    
    #Utils    
    # bot.load_extension('cogs.Utils.dragum')    
    bot.load_extension('cogs.Utils.stats')
    bot.load_extension('cogs.Utils.admin')
    bot.load_extension('cogs.Utils.power')
    bot.load_extension('cogs.Utils.events')
    bot.load_extension('cogs.Utils.checks')
    # bot.load_extension('cogs.Utils.reset')

        