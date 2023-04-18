import nextcord
from nextcord.ext import commands
import random
import asyncio
import constants
import datetime

from cogs.Utils.checks import *

from test_database import *

class events(commands.Cog):
    """ Events utility """

    def __init__(self, bot: commands.bot):
        self.bot = bot

async def get_event(self, ctx, event, look):
    playerDEF = 100
    stoleSALT = 0
    totalSALT = 0
    position = 0
    foundMoffs = 0
    round = 1
    discordUser = ctx.author
    discordID = ctx.author.id
    now = datetime.datetime.today()

    
    #
    # VITC EVENT (1)  
    #
    if event == 1:
        item = ''
        await asyncio.sleep(1)
        
        # Better odds for thorough look
        if look == 1:
            prizeRoll = random.randint(1, 10)
        elif look == 3:
            prizeRoll = random.randint(3, 12)
        
        # Determine prize
        if prizeRoll < 8:
            # BRONZE VITAMIN
            await ctx.send(f"{ctx.author.mention} You found a Bronze Vitamin!")
            item += "vit_bronze"
            await asyncio.sleep(2)
        elif prizeRoll < 12:
            # SILVER VITAMIN
            await ctx.send(f"{ctx.author.mention} You found a Silver Vitamin!")
            item += "vit_silver"
            await asyncio.sleep(2)
        elif prizeRoll == 12:
            await ctx.send(f"{ctx.author.mention} You found a Golden Vitamin!")
            item += "vit_gold"
            await asyncio.sleep(2)

        add_item_amt(discordID, item, 1)
        print(f"{now} - {ctx.author}: Found VITC")
        # Chance for extra
        chance = random.randint(1,2)
        if chance == 1:
            foundMoffs = random.randint(2,5)
            add_item_amt(discordID, "moffs", foundMoffs)
            await ctx.send(f"{ctx.message.author.mention} You found {foundMoffs} MOFFS!")
            print(f"{now} - {ctx.author}: Found {foundMoffs} MOFFS")
            await asyncio.sleep(1)
            chance = random.randint(1,3)
            if chance == 1:
                foundSalt = random.randint(1,5)
                add_item_amt(discordID, "salt", foundSalt)
                await ctx.send(f"{ctx.message.author.mention} You found {foundSalt} SALT!")
                print(f"{now} - {ctx.author}: Found {foundSalt} SALT")
                await asyncio.sleep(1)
        return
    
    #
    # CRAB EVENT (2)
    #
    if event == 2:

        def check(msg):
            return msg.author.id == discordID and msg.content.upper() in ["HELP", "IGNORE", "H", "I"]
        
        await ctx.send(f"{ctx.message.author.mention} You see something strange happening. . .")    
        await ctx.send(f"{ctx.author.mention} You spotted a MOFF family being attacked by a CRAB!\nDo you want to `[H]ELP` or `[I]GNORE` the poor MOFFS?")
        
        # Wait for first response
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=90) # 30 seconds to reply
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} You took too long to decide, and the CRAB ran away with all the MOFFS.")            
            return
        
        # IGNORE
        if msg.content.upper() not in ["HELP", "H"]:
            await ctx.send(f"{ctx.author.mention} You didn't want to disturb the CRAB during it's mealtime, so you decided to look away.")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} The CRAB notices you waiting patiently and decides to share it's meal with you.")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You found 2 MOFFS!")
            print(f"{now} - {discordUser}: Ignored CRAB - 4 MOFFS")
            add_item_amt(discordID, "moffs", 4)            
            return
        
        # HELP
        await ctx.send(f"{ctx.author.mention} You attempt to convince the CRAB to let go of the MOFFS. . .")
        await asyncio.sleep(2)
        success = random.randint(0, 1)
        
        # HELP FAIL
        if success == 0:
            await ctx.send(f"{ctx.author.mention} The CRAB did not find you very convincing. It must have been hungry because it popped the MOFFS in it's mouth before you could finish your argument.")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} Better luck next time.")
            print(f"{now} - {discordUser}: - CRAB event: fail")
            return

        # HELP SUCCESS
        if success == 1:
            foundShards = random.randint(2,5)
            await ctx.send(f"{ctx.author.mention} The CRAB seems to seriously consider your argument. . .")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You were able to convince the CRAB that the MOFFS would be more useful in your care so that they could contribute to taking down the mighty DRAGUM."
            "\nThe MOFF family is thankful for your help, and begin to fly around in a way that looks like they want you to follow them. . ."
            "\nThey guide you to a normal looking rock in the ground and fly around it in circles."
            "\nYou lift the rock. . .")
            await asyncio.sleep(1)
            print(f"{now} - {discordUser}: - CRAB event: success - {foundShards} Shards")
            await ctx.send(f"{ctx.author.mention} You found {foundShards} Crystal Shards🔹!")
            # Found shards
            add_item_amt(discordID, "crystal_shard", foundShards)            
            await asyncio.sleep(1)
            return
           
    #
    # MOFF SWARM EVENT (3)
    #
    if event == 3:

        def check(msg):
            return msg.author.id == discordID and msg.content.upper() in ["FOLLOW", "CATCH", "F", "C"]

        await ctx.send(f"{ctx.author.mention} A group of MOFFS suddenly fly into your face!\nThey look like they want to show you something."
        "\nDo you want to `[F]OLLOW` or try to `[C]ATCH` the MOFFS?")
        
        # Wait for first response
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=90) # 30 seconds to reply
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} You took too long to decide, and the MOFFS flew away into the sky.")
            return
        
        # CATCH
        if msg.content.upper() not in ["FOLLOW", "F"]:
            await ctx.send(f"{ctx.author.mention} You decide the MOFFS are not to be trusted and try to catch instead."
            "\nYou start grabbing at the air desparately trying to capture the MOFFS.")
            success = random.randint(0, 1)
            
            # Fail to gain moffs, gain health
            if success == 0: 
                await asyncio.sleep(2)
                await ctx.send(f"{ctx.author.mention} The MOFFS were too fast for you and managed to escape before you could grab a single one."             
                "\nHowever, after all that running around, you feel much healthier!")
                
                if look == 1:
                    health = random.randint(2,5)
                elif look == 3:
                    health = random.randint(4,8)

                add_health(discordID, health)
                print(f"{now} - {discordUser} - Health +{health}")
                await asyncio.sleep(1)
                print(f"{now} - {discordUser}: - Moff in face event: fail")
            
            # Caught some moffs
            if success == 1:    
                if look == 1:
                    capturedMoffs = random.randint(2,6)
                elif look == 3:
                    capturedMoffs = random.randint(5,10)                
                await asyncio.sleep(2)
                await ctx.send(f"{ctx.author.mention} With your quick hands, you managed to capture {capturedMoffs} MOFFS!")
                await asyncio.sleep(1)
                print(f"{now} - {discordUser}: Captured Moffs - {capturedMoffs} MOFFS")
                add_item_amt(discordID, "moffs", capturedMoffs)
            return 
        
        # FOLLOW
        await ctx.send(f"{ctx.author.mention} You decided to follow the MOFFS. . .")
        await asyncio.sleep(2)
        if look == 1:
            event = random.randint(0, 2)
        elif look == 3:
            event = random.randint(1, 3)
        
        if event == 0: # Failure 
            await ctx.send(f"{ctx.author.mention} You weren't able to keep up with the MOFFS and you lost track of them!")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} Better luck next time.")
            await asyncio.sleep(1)
            print(f"{now} - {discordUser}: - Moff Follow event: fail")
            return
        
        if event == 1: # Injured Moff 
            if look == 1:
                gainedMoffs = random.randint(2,5)
            elif look == 3:
                gainedMoffs = random.randint(4,10)
            await ctx.send(f"{ctx.author.mention} The MOFFS lead you to a clearing where you find an injured MOFF lying on the ground. . .")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You try to help the injured MOFF to the best of your abilities. . ."
            "\n The MOFF manages to get up and starts flying around"
            "\n The MOFF family is thankful for your help, and decide to join you on your adventure of slaying the dragum. . .")
            await asyncio.sleep(1)
            print(f"{now} - {discordUser}: - Moff Follow event: Injured - {gainedMoffs} Moffs")
            await ctx.send(f"{ctx.author.mention} You gained {gainedMoffs} MOFFS!")
            add_item_amt(discordID, "moffs", gainedMoffs)
            return
        
        if event == 2: # Crystal shards
            if look == 1:
                foundShards = random.randint(2,4)
            elif look == 3:
                foundShards = random.randint(3,6)
            await ctx.send(f"{ctx.author.mention} The MOFFS guide you to a normal looking rock in the ground and fly around it in circles."
            "\nYou lift the rock. . .")
            await asyncio.sleep(1)
            print(f"{now} - {discordUser}: - Moff Follow event: rock - {foundShards} Shards")
            await ctx.send(f"{ctx.author.mention} You found {foundShards} Crystal Shards🔹!")
            # add shards
            add_item_amt(discordID, "crystal_shard", foundShards)
            await asyncio.sleep(1)
            return

        if event == 3: # Majic DEF crystal
            await ctx.send(f"{ctx.author.mention} The MOFFS guide you along a long contrived path, you are struggling to keep up . . .")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You finally arrive at a secret field where you witness what looks like a MAJIC MOFF ritual dance.")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} The MOFFS seem excited that you are there, and guide you towards a glowing purple crystal on the ground.")
            await asyncio.sleep(1)
            print(f"{now} - {discordUser}: - Moff Follow event: defense crystal")
            await ctx.send(f"{ctx.author.mention} You gained a MAJIC DEFENSE Crystal<:crystal2:936476907376103475>!")
            # add def crystal
            add_item_amt(discordID, "def_crystal", 1)
            await asyncio.sleep(1)
            return

    #
    # VITAMIN EVENT (4)
    #
    if event == 4:
        vitamin = random.randint(1, 20)
        
        # Limit what vits you can find for quick search
        if look == 1:
            while vitamin in [1, 16,17,18,19, 20]:
                vitamin = random.randint(2,19)
        # Increase good odds for thorough search        
        if look == 3:
            while vitamin in [2,3, 8,9,10,11,12,14]:
                vitamin = random.randint(1,20)

        await ctx.send(f"{ctx.author.mention} You discover a mysterious looking vitamin lying on the ground."
        "\nThis must be one of those healthy new vitamins you keep hearing about!"
        "\nExcitedly, you pop the vitamin in your mouth. . . and swallow."
        "\nA short time passes. . ."
        "\nYou start to feel. . .")
        await asyncio.sleep(1)
        
        # 5% chance (1)
        # Thorough look only
        # Reset all looked locations
        if vitamin < 2:
            await ctx.send(f"{ctx.author.mention} FORGETFUL!"
            "\nYou can't remember where you have used `!look` already this week."
            "\nGuess you'll just have to look around some more!")
            await asyncio.sleep(1)
            
            #Reset looked array
            remove_looked(discordID)
            add_stat(discordID, "health", -5)
            add_stat(discordID, "points", look)          
            print(f"{now} - {discordUser}: FORGETFUL VITAMIN: Looked positions reset")
            print(f"{now} - {discordUser} - Health -4")
            return

        # 10% chance (2,3)
        # Quick look only
        # Random location
        elif vitamin < 4:
            await ctx.send(f"{ctx.author.mention} CONFUSED!"
            "\nYou have no idea where you are."
            "\nYou start to feel dizzy. . . and you black out.")
            await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.mention} When you wake up, you feel like you may be somewhere else."
            "\nBetter use `!p` to check your position.")
            # Move player to random position
            position = random.randint(1, 20)
            move_player(discordID, position)
            add_stat(discordID, "health", -5)
            await asyncio.sleep(1)
            print(f"{now} - {discordUser}: CONFUSING VITAMIN: Moved to position {position}")
            print(f"{now} - {discordUser} - Health -4")

        
        # 20% chance (4,5,6,7)
        # Attract again
        elif vitamin < 8:
            await ctx.send(f"{ctx.author.mention} ATTRACTIVE!")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You perform an attractive dance for the MOFFS. . .")
            await asyncio.sleep(1)
            if look == 1:
                attract = random.randint(2, 10)
            elif look == 3:
                attract = random.randint(2, 20)
            await asyncio.sleep(1)
            print(f"{now} - {discordUser}: ATTRACTIVE VITAMIN: Gained {attract} MOFFS")
            await ctx.send(f"{ctx.author.mention} You found {attract} MOFFS!")
            add_item_amt(discordID, "moffs", attract)
            await asyncio.sleep(1)

        
        # 40% chance (8,9,10,11,12,13,14,15,16,17)
        # Small energy
        elif vitamin < 18:
            await ctx.send(f"{ctx.author.mention} HEALTHY!")
            await asyncio.sleep(1)
            movement = random.randint(2, 4)
            add_stat(discordID, "points", movement)
            add_stat(discordID, "health", movement)
            print(f"{now} - {discordUser} - Health +5")
            await ctx.send(f"{ctx.author.mention} You feel healthier and ready to take on the day. . ."
            f"\nYou gained {movement} movement points!")
            await asyncio.sleep(1)
            print(f"{now} - {discordUser}: HEALTHY VITAMIN: Gained {movement} points and health")
        
        
        # 10% chance (18,19)
        # Big energy
        elif vitamin < 20:
            await ctx.send(f"{ctx.author.mention} PUMPED UP!")
            await asyncio.sleep(1)
            movement = random.randint(4, 8)
            add_stat(discordID, "points", movement)
            await ctx.send(f"{ctx.author.mention} You are shaking with energy and feel ready to take on AKU WORLDS! Your stomach doesn't feel great, though. . ."
            f"\nYou gained {movement} movement points!")
            await asyncio.sleep(1)
            print(f"{now} - {discordUser}: PUMPED VITAMIN: Gained {movement} move points")
            # lose health based on movement points gained
            add_stat(discordID, "health", -movement)
            print(f"{now} - {discordUser} - Health -{movement}")
        
            
        # 5% chance (20)
        # Thorough look only
        # Start MATRIX heist with 100hp
        else:
            # Function to Verify response
            def check(msg):
                return msg.author.id == discordID and msg.content.upper() in ["RED", "BLUE"]
            
            await ctx.send(f"{ctx.author.mention} . . .like you know AKU FU!")
            await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} You are suddenly transported to an expanse of purple color that surrounds you in all directions as far as you can see."
            "\nIn your hands, you see a `RED` vitamin, and a `BLUE` vitamin."
            "\nYou take the `BLUE` vitamin, the story ends. You wake up in your HOVEL and believe whatever you want to."
            "\nYou take the `RED` vitamin, you stay in Wizardland, and I show you how deep the CRAB hole goes."
            "\n\nWhich do you choose? Enter `RED` or `BLUE`")

            # Wait for first response
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=90) # 90 seconds to reply
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention} You took too long to decide, and the effect fades away."
                "\nThe purple expanse dissolves around you and you find yourself back in AKU WORLDS with everything as you left it.")
                return

            # Don't play aku fu
            if msg.content.upper() == "BLUE":
                await ctx.send(f"{ctx.author.mention} The purple expanse dissolves around you and you find yourself back in AKU WORLDS with everything as you left it.")
                return
                
            # Took red pill
            await ctx.send(f"{ctx.author.mention} You are transported into the DRAGUM's SALT mine! Everything feels familiar yet different at the same time."
            "\nYour MOFF MAJIC DEF will protect you, but not for long. . .")
            await asyncio.sleep(1)
            
            # Continue until player runs away    
            while msg.content.upper() != "BLUE":
                stoleSALT = random.randint(2, 6+round)
                totalSALT += stoleSALT
                dragumATK = random.randint((3 * round), (10 * round))
                playerDEF -= dragumATK
                # Player steals and DRAGUM attacks
                await ctx.send(f"{ctx.author.mention} You stole: {stoleSALT} SALT! - Total stolen: {totalSALT} SALT\nThe DARK MOFFS drained {dragumATK} points of your **DEF**!")
                await asyncio.sleep(1)
                # Player lost all DEF
                if playerDEF <= 0:
                    totalSALT = 0
                    await ctx.send(f"{ctx.author.mention} You ran out of MOFF MAJIC DEF and suddenly felt yourself jolted back to AKU WORLDS, dazed and confused."
                    "\nWas it just a dream? You don't feel any different. . .")
                    await asyncio.sleep(1)
                    print(f"{now} - {discordUser}: MATRIX VITAMIN results: Got BURNED, lost {totalSALT}")
                    return
                # Player still has DEF
                else:
                    await ctx.send(f"{ctx.author.mention} Your remaining **MOFF MAJIC DEF**: {playerDEF}\nChoose the `RED` or `BLUE` vitamin.")
                    try:
                        msg = await self.bot.wait_for("message", check=check, timeout=30) # 30 seconds to reply
                    except asyncio.TimeoutError:
                        await ctx.send(ctx.message.author.mention + " In your hesitation, the DARK MOFFS attacked!")

                round += 1        
                await asyncio.sleep(1)        
            
            # Player ran away
            add_item_amt(discordID, "salt", totalSALT)
            add_stat(discordID, "health", -round)
            print(f"{now} - {discordUser}: MATRIX VITAMIN results: {totalSALT} SALT stolen")
            print(f"{now} - {discordUser} - Health -{round}")
            
            await ctx.send(f"{ctx.author.mention} You decide to escape the simulation and head back to reality. . .")
            await asyncio.sleep(1) 
            await ctx.send(f"{ctx.author.mention} . . . or is it the other way around?")          
            await asyncio.sleep(1) 
            await ctx.send(f"{ctx.author.mention} You take a moment to ponder the true nature of existence.")
            await asyncio.sleep(2)
            await ctx.send(f"{ctx.author.mention} Sometimes you feel like you are just a cog stuck in an endless repeating cycle performing actions beyond your control to fulfill the desires of a. . . ")
            await asyncio.sleep(1) 
            await ctx.send(f"{ctx.author.mention} Oh look! You now have {totalSALT} more SALT!")
            await asyncio.sleep(1) 
            await ctx.send(f"{ctx.author.mention} You start to think about all the cool stuff you can buy with your new SALT.")
            await asyncio.sleep(1)
        
        return
    
    #
    # CHEST EVENT (5)
    #
    if event == 5:
        desc = ''
        count = 0

        await ctx.send(f"{ctx.author.mention} You found a chest! Wonder what's inside?")
        await asyncio.sleep(1)
        await ctx.send(f"{ctx.author.mention} Attempting to open with MOFF MAJIC. . .")
        await asyncio.sleep(5)
        
        # Quick look may not win an NFT from a chest
        if look == 1:
            prizeType = 1
        # Thorough look has 1 in 10 chance to win NFT from chest
        elif look == 3:
            prizeType = random.randint(1,9)

        if prizeType < 9:
            wonItems = {}
            prizes = ["vit", "ban", "salt", "moffs", "seeds", "crystal_shard", "salt_crystal"]            
            levels = ["bronze", "silver"]            
            items = ["vit", "ban"]            
            descriptions = {"vit_bronze":"Bronze Vitamin", "vit_silver":"Silver Vitamin", "vit_gold":"Golden Vitamin",
                            "ban_bronze":"Bronze Banana", "ban_silver":"Silver Banana", "ban_gold":"Golden Banana"}
            
            # Quick look may only win up to 2 prizes from a chest
            if look == 1:
                count = random.randint(1,2)
                prizeWeight = [7,1,30,51,5,5,1]
                levelWeight = [90,10]
            # Thorough look may win up to 4 prizes from a chest
            elif look == 3:
                count = random.randint(2,3)
                prizeWeight = [15,2,30,38,5,9,1]
                levelWeight = [75,25]

            wonPrizes = random.choices(prizes, prizeWeight, k=count)
            print(wonPrizes)

            if "salt_crystal" in wonPrizes:
                chance = random.randint(1,3)
                if chance < 3:
                    wonPrizes.remove("salt_crystal")
                    wonPrizes.append("crystal_shard")

            total_prizes = {}
            amount = 1
            for prize in wonPrizes:
                 
                if prize in items:
                    item = ''
                    level = random.choices(levels, levelWeight, k=1)
                    wonItems[prize] = level
                    wonLevel = wonItems[prize][0]
                    item = str(prize)+'_'+str(wonLevel)
                    prize = item
                    amount = 1     

                
                if prize == "salt":
                    amount = random.randint(1,5)                               
                if prize == "moffs":
                    amount = random.randint(2,7)
                if prize == "salt_crystal":
                    amount = 1
                if prize == "crystal_shard":
                    amount = random.randint(2,5)
                
                if amount == 1:
                    desc = ITEMS[prize]["desc_s"]
                else:
                    desc = ITEMS[prize]["desc"] 

                await asyncio.sleep(1)  
                await ctx.send(f"{ctx.author.mention} You found {amount} {desc}!")
                print(f"{now} - {discordUser}: Found {amount} {desc}")
                if prize in total_prizes:
                    total_prizes[prize] += amount
                else:
                    total_prizes[prize] = amount

            db_add_prizes(discordID, total_prizes)

        # Moff Jackpot
        elif prizeType == 9:
            foundMoffs = 19
            await ctx.send(f"{ctx.author.mention} JACKPOT! You found {foundMoffs} MOFFS!")
            add_item_amt(discordID, "moffs", foundMoffs)
            print(f"{now} - {discordUser}: Jackpot! {foundMoffs} MOFFS")
            await asyncio.sleep(1)
        return
    
    #
    # CRAB RAVE
    #
    if event == 6:
        await ctx.send(f"{ctx.message.author.mention} You stumble upon a clearing in the woods and are immediately drawn to the pulsing beat of music. "
        "As you approach, you see a group of CRABs dancing wildly, their eyes shining with energy. "
        "One of the CRABs notices you and scurries over, shouting to be heard above the music. ")
        await asyncio.sleep(1)
        await ctx.send(f"{ctx.message.author.mention} \"Greetings, AKU! Welcome to our rave!\" says the CRAB."
        "\"We just consumed a large quantity of vitamins and are feeling particularly lively. Would you care to join us?\"")
        # Wait for first response
        
        
        # RAVE
        confirmations = ["YES", "Y", "[Y]ES", "[Y]"]
        rejections =  ["NO", "N", "[N]O", "[N]"]

        while msg.content.upper() not in confirmations + rejections:
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=90) # 30 seconds to reply
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention} You took too long to decide, and the CRAB disappeared into the vibrating crowd.")
                return

            await ctx.send(f"{ctx.message.author.mention} Enter `[Y]es` or `[N]o`: ")
            if msg.content.upper() in confirmations:
                await ctx.send(f"{ctx.author.mention} Who could turn down an opportunity to join in the legendary CRAB rave?"
                "\nAs soon as you make your way to the edge of the crowd, a claw reaches your way and offers you a Vitamin.")
                await asyncio.sleep(1)
                break
            #LEAVE
            elif msg.content.upper() in rejections:
                ending = random.randint(0, 1)
                await ctx.send(f"{ctx.author.mention} You don't have time for this! You decide to leave the CRAB rave and continue on your way.")
                if ending == 0:
                    await ctx.send(f"{ctx.author.mention} As you're leaving, you spot a Vitamin that was dropped on the ground and quickly stash it in your inventory.")
                    await asyncio.sleep(1)
                
                break
    
    #
    # NOTHING (7)
    #
    if event == 7:
        # Nothing gained
        if look == 1:
            await ctx.send(f"{ctx.message.author.mention} Sadly, you couldn't find a thing!")
        # Gain health
        if look == 3:
            await ctx.send(f"{ctx.message.author.mention} You weren't able to find anything. . ."
            f"\nHowever, after all that walking around and searching, you feel much healthier!")
            await asyncio.sleep(1)

            health = random.randint(4,8)
            add_stat(discordID, "health", health)
            print(f"{now} - {ctx.author} - Health +{health}")

def setup(bot: commands.bot):
    bot.add_cog(events(bot))