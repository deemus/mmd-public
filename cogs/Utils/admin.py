from nextcord.ext import commands
import math
import sys
import random
import asyncio
import time
from cogs.Utils.checks import *
from constants import *
from test_database import *
# from database import add_item, get_wax_from_id

class admin(commands.Cog):
    """ Admin Only Commands! """
    def __init__(self, bot: commands.bot):
        self.bot = bot           
           
    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def reset(self, ctx):
        discordID = ctx.author.id
        if discordID not in TESTERS:
            await ctx.send(ctx.author.mention + " Bad bebe.")
            return
        daily_reset(discordID)
        await ctx.send(ctx.author.mention + " Daily commands reset.")


    @commands.command()
    async def busy(self, ctx):
        discordID = ctx.author.id
        if discordID not in TESTERS:
            await ctx.send(ctx.author.mention + " Bad bebe.")
            return
        set_busy(discordID, False)
        await ctx.send(ctx.author.mention + " Set Busy to False")

    
    @commands.command()
    async def add(self, ctx):
        discordID = ctx.author.id
        discordUser = ctx.author
        now = datetime.datetime.today()

        if discordID not in TESTERS:
            await ctx.send(ctx.author.mention + " Bad bebe.")
            return
        
        msg = ctx.message.content.split()
        item = msg[2]
        amount = int(msg[1])
        if item in ITEMS:
            add_item_amt(discordID, item, amount)
            
        elif item == "points":
            add_stat(discordID, "points", amount)

        else:
            await ctx.send(f" {ctx.author.mention} Invalid usage")
        
        await ctx.send(f" {ctx.author.mention} Added {amount} {item}")
        print(f"{now} - {discordUser} added {amount} {item}")
    

    @commands.command()
    async def resetweek(self, ctx):
        if ctx.message.author.id not in TESTERS:
            await ctx.send(ctx.author.mention + " Use `!p` or `!inv` to view your stats.")
            return
        reset_week()
        print("week reset")
    

    # @commands.command()
    # async def rode(self, ctx):
    #     if ctx.message.author.id != 274656402721472512:
    #         await ctx.send(ctx.author.mention + " Use `!p` or `!inv` to view your stats.")
    #         return

    #     message = ''
    #     totals = sum_one("rode")
    #     record = totals.next()
    #     rodeTotal = record["rode"]
    #     print(rodeTotal)


    # @commands.command()
    # async def user(self, ctx):
    #     if ctx.message.author.id != 274656402721472512:
    #         await ctx.send(ctx.author.mention + " Use `!p` or `!inv` to view your stats.")
    #         return
    #     msg = ctx.message.content.split()
    #     wax = msg[1]
    #     user = get_user_from_wax(wax)
    #     user = user.next()
    #     name = user['name']
    #     await ctx.send(f"{ctx.author.mention} User: {name}")


    # @commands.command()
    async def spear(self, ctx, draghp=''):
        DRAGUM_NAME = "SANDSTONE DRAGUM"

        players = get_all_moffs()
        players = list(players)

        index = 0
        max_moffs = 0
        # for player in players:
        #     if max_moffs < players[index]["moffs"]:
                
        #     index += 1
        
        dragum = int(draghp)
        draghp = dragum

        # dragum = 1000
        # draghp = 1000

        attacked = {}
        attack_count = 0
        last_player = False
        dragum_alive = True

        player_count = len(players)
        await ctx.send(f"There are {player_count} players with enough MOFFS to form a MOFF SPEAR that can attack the {DRAGUM_NAME}!")
        await asyncio.sleep(2)

        def get_spears():

            spears = {}
            index = 0
            for player in players:
                player_id = players[index]["_id"]
                max_moffs = players[index]["moffs"]
                spear_power = random.randint(1, max_moffs)
                spears[player_id] = spear_power
                index += 1
            # print(spears)
            return spears


        while dragum_alive:
            spear_players = get_spears()
            spear_list = list(spear_players.items())
            random.shuffle(spear_list)
            spear_players = dict(spear_list)

            for player in spear_players:

                if spear_players[player]:
                    damage = spear_players[player]
                    print(f"{player} hits for {damage}")
                    await asyncio.sleep(1)
                    await ctx.send(f"<@{player}> hits for {damage}")
                    draghp -= damage
                    attack_count += 1

                    try:
                        attacked[player] += damage
                    except:
                        attacked[player] = damage

                if draghp <= 0:
                    await asyncio.sleep(2)
                    print(f"{DRAGUM_NAME} was killed by player: {player}")
                    await ctx.send(f"{DRAGUM_NAME} was killed by: <@{player}>!!")
                    await asyncio.sleep(2)
                    last_player = player
                    dragum_alive = False
                    break

            if draghp > 0:
                await asyncio.sleep(2)
                print(f"{DRAGUM_NAME} was not defeated, remaining hp: {draghp} attacking again!")
                await ctx.send(f"{DRAGUM_NAME} was not defeated, remaining HP: {draghp} attacking again!")
                await asyncio.sleep(2)


        min_attack = (dragum / player_count) + 20


        def calc_badges(attacked, last_player):
            badges = []
            wax_adds = []
            
            for player in attacked:
                id = player
                damage = attacked[player]

                if damage >= min_attack:
                    mention = "<@" + str(id) + ">"
                    badges.append(mention)
                    wax_doc = get_wax_from_id(id)
                    wax_doc = list(wax_doc)
                    wax_adds.append(wax_doc[0]["WAX"])

            mention_last = "<@" + str(last_player) + ">"
            if mention_last not in badges:                
                badges.append(mention_last)

            print(wax_adds)
            return badges


        badges = calc_badges(attacked, last_player)
        badge_count = len(badges)
        # print(badges)
        

        print(f"{badge_count } out of {player_count} players dealt enough damage to the {DRAGUM_NAME} and earned a badge!")
        await ctx.send(f"{badge_count } out of {player_count} players dealt enough damage to the {DRAGUM_NAME} and earned a badge!")
        await ctx.send(f"Badge earners:\n{badges}")


    @commands.command()
    async def allstats(self, ctx):
        if ctx.message.author.id not in TESTERS:
            await ctx.send(ctx.author.mention + " Use `!p` or `!inv` to view your stats.")
            return

        message = ''
        totals = sum_totals()
        players = count_players()
        message += "There were " + str(players) + " active players this week!" +"\n\n"
        message += "Here's what was found: \n"

        record = totals.next()
        for item in record:
            if record[item] == None:
                pass
            else:
                message += str(item) + " - " + str(record[item]) +"\n"
                print(f"{item} - {record[item]}" )
        
        await ctx.send(message)

    
    @commands.command()
    async def dist(self, ctx):
        discordID = ctx.author.id
        if ctx.message.author.id not in TESTERS:
            await ctx.send(ctx.author.mention + " You're welcome to distribute your own funds to everyone!")
            return

        id = ''
        inv = ''
        total_vitc = 0
        total_ban = 0
        today = datetime.today().date()
        
        all_players_db = get_treasure()
        all_players = list(all_players_db)
        
        filename = 'dist-'
        filename += str(today)
        filename += ".txt"
        
        original_stdout = sys.stdout

        def check(msg):
            return msg.author.id == discordID and msg.content.isdigit()

        try:
            await ctx.send(ctx.author.mention + " How much VITC is getting distributed this week?")
            vitc_response = await self.bot.wait_for("message", check=check, timeout=20)
            vitc_dist = int(vitc_response.content)
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.message.author.mention} Command timed out.")
            return
        try:
            await ctx.send(ctx.author.mention + " How much BAN is getting distributed this week?")
            ban_response = await self.bot.wait_for("message", check=check, timeout=20)        
            ban_dist = int(ban_response.content)
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.message.author.mention} Command timed out.")
            return
        
        vit_bronze_total = int(vitc_dist * .20)
        vit_silver_total = int(vitc_dist * .30)
        vit_gold_total = int(vitc_dist * .50)

        ban_bronze_total = int(ban_dist * .20)
        ban_silver_total = int(ban_dist * .30)
        ban_gold_total = int(ban_dist * .50)

        totals = sum_totals()

        record = totals.next()
        for item in record:
            if record[item] == None:
                pass
            else:
                if item == "VITC Bronze":
                    vit_bronze_count = record[item]
                elif item == "VITC Silver":
                    vit_silver_count = record[item]
                elif item == "VITC Gold":
                    vit_gold_count = record[item]
                elif item == "BAN Bronze":
                    ban_bronze_count = record[item]
                elif item == "BAN Silver":
                    ban_silver_count = record[item]
                elif item == "BAN Gold":
                    ban_gold_count = record[item]
                else:
                    continue

        vit_bronze_amt = int(vit_bronze_total / vit_bronze_count)
        vit_silver_amt = int(vit_silver_total / vit_silver_count)
        vit_gold_amt = int(vit_gold_total / vit_gold_count)

        ban_bronze_amt = int(ban_bronze_total / ban_bronze_count)
        ban_silver_amt = int(ban_silver_total / ban_silver_count)
        ban_gold_amt = int(ban_gold_total / ban_gold_count)

        vitc_items = {"vit_bronze":vit_bronze_amt, "vit_silver":vit_silver_amt, "vit_gold":vit_gold_amt}
        ban_items = {"ban_bronze":ban_bronze_amt, "ban_silver":ban_silver_amt, "ban_gold":ban_gold_amt}
        vitc_tips = []
        ban_tips = []
        print("Treasure prices:")
        print(vitc_items)
        print(ban_items)

        original_stdout = sys.stdout

        def sortpayouts(payout_data,currency,tuple_entry):
            payout_data.sort(key = lambda t : t[tuple_entry]) 
            cur_val = 0
            cur_msg = ""
            for entry in payout_data: 
                id = entry[0]
                amount = entry[tuple_entry]
                if  amount > 0:	
                    if amount != cur_val: 
                        #New amount, print current one and reset message
                        print(cur_msg)
                        cur_val = amount 
                        cur_msg = "." + str(currency) + " " + str(amount)
                    cur_msg += " <@%d>" % id 
            print(cur_msg)
        
        with open(filename, 'w') as f:
            sys.stdout = f
            payout_data = [] 
            for player in all_players:
                vitc = 0
                ban = 0
                id = player['_id']
                
                try:
                    inv = player['inv']                    
                    for item in inv:
                        for x in vitc_items:
                            if x == item:
                                vitc += (vitc_items[x] * inv[item])
                                
                        for x in ban_items:
                            if x == item:
                                ban += (ban_items[x] * inv[item])
                    if vitc > 0:
                        vitc_tips.append(vitc)
                        total_vitc += vitc
                    if ban > 0:
                        ban_tips.append(ban)
                        total_ban += ban	
                    payout_data.append((id,vitc,ban))
                except KeyError:	
                    continue
            #Sort by vitc payouts 
            sortpayouts(payout_data,"v",1)
            sortpayouts(payout_data,"b",2)	
            sys.stdout = original_stdout
            print(f"{filename} created")
            
        vitc_mean = int(mean(vitc_tips))
        ban_mean = int(mean(ban_tips))
        # vitc_median = median(vitc_tips)
        # ban_median = median(ban_tips)
        # vitc_mode = mode(vitc_tips)
        # ban_mode = mode(ban_tips)
        vitc_max = max(vitc_tips)
        ban_max = max(ban_tips)
        ban_tip_count = len(ban_tips)
        vitc_tip_count = len(vitc_tips)

        await ctx.send(ctx.author.mention + " Distribution file created!")
        await ctx.send(f"{ctx.author.mention} VITC Treasure values (Bronze / Silver / Gold): {vit_bronze_amt} / {vit_silver_amt} / {vit_gold_amt} ")
        await ctx.send(f"{ctx.author.mention} BAN Treasure values (Bronze / Silver / Gold): {ban_bronze_amt} / {ban_silver_amt} / {ban_gold_amt} ")
        await ctx.send(f"{ctx.author.mention} Total VITC to be distributed: {total_vitc}")
        await ctx.send(f"{ctx.author.mention} Total BAN to be distributed: {total_ban}")
        await ctx.send(f"**VITC**\nBiggest Tip: {vitc_max}"
        f"\nAverage Tip: {vitc_mean}"
        f"\nUnique Tips: {vitc_tip_count}"
        f"\n\n**BAN**\nBiggest Tip: {ban_max}"
        f"\nAverage Tip: {ban_mean}"
        f"\nUnique Tips: {ban_tip_count}")
    

    @commands.command()
    async def dragum(self, ctx: commands.context):
        if ctx.message.author.id not in TESTERS:
            await ctx.send(ctx.author.mention + " The DRAGUM will not listen to you!")
            return
        
        # {DRAGUM_NAME} ROLLS
        #akuburn - 891423245608304651
        DELAY = 5
        DRAGUM_NAME = "SANDSTONE DRAGUM"
        HOVELS = [6, 20]

        if (ctx.message.author.id == 707092320767705122 or ctx.message.author.id == 274656402721472512):     
            print(f"{ctx.message.created_at}: - {ctx.message.author}: {DRAGUM_NAME} TIME")
            
            dragumHP = 0
            originalHP = 0
            moff = "<:moff:899796605044146197>"

            totalMoffs = sum_one("moffs")
            totalMoffs = totalMoffs.next()
            totalMoffs = totalMoffs["moffs"]

            # totals = sum_one("rode")
            # record = totals.next()
            # rodeTotal = record["rode"]
            # taxiMoffs = int(rodeTotal)


            dragumHP = totalMoffs

            # defenseRoll = random.randint(1, totalMoffs) 
            # defense = defenseRoll + taxiMoffs
            dragumTotalHP = int(dragumHP)

            # add_salt_crystals(19)
            # await asyncio.sleep(1)
            # add_salt_crystals(49)
            # await asyncio.sleep(1)
            # add_salt_crystals(99)
            
            await ctx.send("Calculating weekly statistics. . .")
            await asyncio.sleep(DELAY)
            await ctx.send("**Total MOFFS attracted this week**: " + str(totalMoffs))            
            await asyncio.sleep(DELAY)
            await ctx.send(f"*For every MOFF gathered, the {DRAGUM_NAME} grows stronger*. . .")
            await asyncio.sleep(DELAY)
            await ctx.send(f"**{DRAGUM_NAME} HP**: {dragumHP}")
            await asyncio.sleep(DELAY)
            # await ctx.send(f"*{DRAGUM_NAME} rolls a {totalMoffs} sided die for DEF this week*")
            # await asyncio.sleep(DELAY)
            # await ctx.send(f"**Result:** {defenseRoll}")
            # await asyncio.sleep(DELAY)
            # await ctx.send(f"*The {DRAGUM_NAME} raided the TAXICRAB station on the way in, and it absorbed the power of {taxiMoffs} additional MOFFS!*")
            # await asyncio.sleep(DELAY)
            # await ctx.send(f"**Bonus DEF to {DRAGUM_NAME} HP**: {defense}")
            # await asyncio.sleep(DELAY)
            # await ctx.send(f"** {DRAGUM_NAME}'s HP+DEF**: {dragumTotalHP}")
            # await asyncio.sleep(DELAY)
            await ctx.send("*The MOFFS shudder in unison as a ripple of MAJIC emanates from the lair.*")
            await asyncio.sleep(DELAY)
            await ctx.send(f"*The {DRAGUM_NAME} has been disturbed from it's slumber. . .*")
            await asyncio.sleep(DELAY)
            await ctx.send("*It has been building power over the last week. . .*")
            await asyncio.sleep(DELAY)
            await ctx.send("*Now, it wakes. . .*")
            await asyncio.sleep(DELAY)
            await ctx.send("*And it is angry.*")
            await asyncio.sleep(DELAY)
            await asyncio.sleep(DELAY)
            # await ctx.send(":fire:    :fire:    :fire:    :fire:    :fire:    :fire:  \n:fire:   * {DRAGUM_NAME} ROLL:**   " + rollString.zfill(2) + "   :fire:\n:fire:    :fire:    :fire:    :fire:    :fire:    :fire:")
            await ctx.send("*It is time. . .*")
            await asyncio.sleep(DELAY)
            await ctx.send("*Some may perish. . .*")
            await asyncio.sleep(DELAY)
            await ctx.send("*But* ***WE ARE AKU!***")
            await asyncio.sleep(DELAY)
            await ctx.send("*By now, the MOFFS have learned that they must form MOFF SPEARS to strike the DRAGUM!*")
            await asyncio.sleep(DELAY)
            await ctx.send(f"*Players who have collected at least 20 MOFFS let them loose to begin the attack!*")
            await asyncio.sleep(DELAY)
            await ctx.send(f"*As the MOFF SPEARS form, the players take cover inside the nearest CRAB hole for protection from the DRAGUM's fire.*")
            await asyncio.sleep(DELAY)
            await ctx.send("*With the turn of it's massive head and the wind gusts from it's flapping wings. . .*")
            await asyncio.sleep(DELAY)
            await ctx.send(f"*The {DRAGUM_NAME} attacks!*")
            await asyncio.sleep(DELAY)
            await asyncio.sleep(DELAY)
            await ctx.send("<a:akuburn:890838686885892136> <a:akuburn:890838686885892136> <a:akuburn:890838686885892136> <a:akuburn:890838686885892136>")
            await asyncio.sleep(DELAY)        
            await ctx.send(f"*The SALT players have gathered begins to melt. . .*")
            await asyncio.sleep(DELAY)
            await ctx.send(f"*Though, for those who managed to gather a large enough amount. . .*")
            await asyncio.sleep(DELAY)
            await ctx.send(f"*A crystalized lump remains.*")    
            await asyncio.sleep(DELAY)
            await ctx.send(f"Before the {DRAGUM_NAME} can fly away, the MOFF SPEARS have formed a barrier around it!*")
            await asyncio.sleep(DELAY)
            await ctx.send(f"It's time to strike back!*")
            await asyncio.sleep(DELAY)
            await spear.spear(self, ctx, dragumTotalHP)
            await asyncio.sleep(DELAY)
            # await ctx.send("*HOVELS that have leveled up their ATTACK POWER will get to attack more than once. . .*")
            # await asyncio.sleep(DELAY)
            # for land in HOVELS:
            #     await asyncio.sleep(DELAY)
            #     await ctx.send(f"*HOVEL {land} attacks!*")
            #     await asyncio.sleep(DELAY)
            #     hovelLevel = 0
            #     moffs=0
            #     totalDamage = 0
            #     attacks = 1
            #     damage = 0

            #     try:
            #         hovel = get_hovel(land)
            #         hovel = list(hovel)
            #         hovelLevel = [ sub['level'] for sub in hovel]
            #         hovelLevel = hovelLevel[0]

            #         # Get moffs per position from db
            #         moffs = get_moffs_per_position(land)
            #         moffs = moffs.next()
            #         moffs = moffs['moffs']
            #     except:
            #         await ctx.send(f"*Oh no! There are no MOFFS gathered in this HOVEL, so it is unable to launch an attack at the {DRAGUM_NAME}!*")
            #         continue

            #     await ctx.send(f"*HOVEL {land} is level {hovelLevel}, so it will get {hovelLevel} attacks!*")
            #     await asyncio.sleep(DELAY)
            #     if moffs == 0:
            #         await ctx.send("*No MOFFS in this HOVEL*")

            #     else:
            #         await ctx.send(f"**MOFFS in this HOVEL**: {moffs}")
            #         await asyncio.sleep(DELAY)
            #         if (moffs > 1):
            #             while attacks < (hovelLevel + 1):
            #                 damage = int(random.randint(1,moffs))
            #                 await ctx.send(f"**Damage dealt by MOFF SPEAR {attacks}**: {damage}")
            #                 await asyncio.sleep(DELAY)
            #                 totalDamage += damage
            #                 attacks += 1

            #             dragumTotalHP -= totalDamage
                        
            #         await ctx.send(f"**Damage dealt by HOVEL {land}**:  {totalDamage}")
            #         await ctx.send(f"**Remaining {DRAGUM_NAME} HP**: {dragumTotalHP}")
            #         await asyncio.sleep(DELAY)
            #         if dragumTotalHP <= 0:
            #             await ctx.send(f"**THE {DRAGUM_NAME} HAS BEEN DEFEATED BY HOVEL {land}!!!**")
            #             await asyncio.sleep(DELAY)
            #         else:        
            #             await asyncio.sleep(DELAY)

            # if dragumTotalHP > 0:
            #     await ctx.send(f"*The MOFF SPEAR attacks were not strong enough to defeat the mighty {DRAGUM_NAME} this week. . .*") 
            #     await asyncio.sleep(DELAY)
            #     await ctx.send(f"*The {DRAGUM_NAME}--having spent all it's energy--returns to it's lair to fall asleep once again.*")
            #     await asyncio.sleep(DELAY)
            #     await ctx.send(f"*As the {DRAGUM_NAME} flies away, the wind from its wings scatter the players to random positions across the map.*")
            #     await asyncio.sleep(DELAY)
            #     await ctx.send("*Thank you, brave MOFFS, for your sacrifice. RIP*")  
                
            # if dragumTotalHP < dragumHP:
            #     update_dragum(DRAGUM_NAME, dragumTotalHP)
            # elif originalHP == -1:
            #     update_dragum(DRAGUM_NAME, dragumTotalHP)

            await asyncio.sleep(DELAY)

            try:
                print(f"{ctx.message.created_at}: - {ctx.message.author}: RESET MOFFS AND POSITIONS RANDOMIZED")
                # reset_week()        
                await ctx.send("*A new week begins, and the players must begin to rebuild and regroup. . .*")
                await asyncio.sleep(DELAY)
                await ctx.send("*May the next MOFF SPEARS strike true, and AKU be with you. . .*")
            except ValueError:
                await ctx.send(ctx.message.author.mention + ' <a:hehe_aku:867940486395097148> Something went wrong')
        else:
            await ctx.send(f"{ctx.author.mention} <a:hehe_aku:867940486395097148> The {DRAGUM_NAME} does not listen to the likes of you!")
            return   

def setup(bot: commands.bot):
    bot.add_cog(admin(bot))

    
    # @commands.command()
    # async def stats(self, ctx):
    #     if ctx.message.author.id != 274656402721472512:
    #         await ctx.send(ctx.author.mention + " Bad bebe.")
    #         return

    #     message = ''
    #     totals = sum_totals()
        
    #     record = totals.next()
    #     for item in record:
    #         if record[item] == None:
    #             pass
    #         else:
    #             message += str(item) + " - " + str(record[item]) +"\n"
    #             print(f"{item} - {record[item]}" )
        
    #     await ctx.send(message)
