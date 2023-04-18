from test_database import *
from nextcord.ext import commands
from nextcord.ext.commands import context
from cogs.Utils.checks import *
import constants
import random
import asyncio
from datetime import datetime

api_index = 0  #Index to keep track of what API we last queried -- having this as a global variable is probably easiest even if not pretty... 

class power(commands.Cog):
    """ How AKU are you? """
    # api_list = constants.API_LIST
    
    def __init__(self, bot: commands.bot):
        self.bot = bot


    @commands.command(aliases=["temps"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def settemplates(self, ctx: commands.context):
        """ ADMIN ONLY """
        MMD_TEMPLATES = constants.MMD_TEMPLATES
        CHOSEN_TEMPLATE_COUNT = 5
        MMD_TEMPLATE_BONUS = 50
        ALL_AKU_TEMPLATES = constants.AKUFISHHEADS
        
        def set_week_templates():
            template_list = list(ALL_AKU_TEMPLATES)
            chosen_templates = random.sample(template_list, CHOSEN_TEMPLATE_COUNT)
            
            game_template = str(random.choice(MMD_TEMPLATES))
            print(f"Chosen templates: ", chosen_templates)
            print(f"Game template: ", game_template)
            db_week_templates(chosen_templates, game_template)
        
        if (ctx.message.author.id == 707092320767705122 or ctx.message.author.id == 274656402721472512):     
            print(f"Setting weekly templates")
            set_week_templates()
            print(f"Templates set")
    
    @commands.command(aliases=["moffcheck"])
    # @commands.cooldown(1, 120, commands.BucketType.user)
    async def check_asset(self, ctx: commands.context):
        discordID = ctx.author.id
        discordUser = ctx.author
        document = find_player(discordID)
        document = list(document) 
        MOFF_TEMPLATE = 263637
        
        # Check if player completed spire
        pre_checks = []
        if not await all_checks(pre_checks, ctx, document):
            return
         
        await ctx.send(f"{ctx.author.mention} Please wait. . . Looking for your latest unrecorded NFT transfers to `akutreasures`.")
        
        
        now = datetime.today()
        player_wax = get_player(document, "wax")
        last_sent_time = get_player(document, "transfers", "last_sent_moff")
        moff_history = get_player(document, "transfers", "history", "moff")
        new_transfers = {}
        shard_amt = 0
        data = check_transfer(player_wax, MOFF_TEMPLATE, last_sent_time)        
        try:
            trans_time = int(data[0]['created_at_time'])
            if last_sent_time > trans_time:
                await ctx.send(f"{ctx.author.mention} No new transfers found!")
                return
        except IndexError:
            await ctx.send(f"{ctx.author.mention} No recent transfers found!")
            return
        except:
            await ctx.send(f"{ctx.author.mention} Something went wrong, Alerting <@274656402721472512>!")
            return
        
        if not moff_history:
            moff_history = []
        for transfer in data:
            tx_id = transfer["transfer_id"]
            if tx_id not in moff_history:
                amt = len(transfer['assets'])
                new_transfers[tx_id] = amt
                shard_amt += amt * 20
                msg_amt = amt * 20
                await ctx.send(f"{ctx.author.mention} Found new transfer of {amt} MOFF Token(s)! Adding {msg_amt} Crystal Shards!")
                await asyncio.sleep(1)
                
        add_item_amt(discordID, "crystal_shard", shard_amt)
        db_transfer_history(discordID, "moff", new_transfers, trans_time)
        print(f"{now} - {discordUser} - TRANSFER {amt} MOFF Token(s). Added {shard_amt} Crystal Shards 🔹")
        await ctx.send(f"{ctx.author.mention} MOFF Token transfer check completed!")
    
    @commands.command(aliases=["aku", "AKU", "Aku", "Fakulty", "fakulty", "FAKULTY"])
    # @commands.cooldown(1, 60, commands.BucketType.user)
    async def power(self, ctx: commands.context):
        

        if ctx.message.author.id == 274656402721472511:     
            wax_doc = get_all_wax_power()
            wax_doc = list(wax_doc)
        
        # Calculate individual fakulty
        else:
            discordID = ctx.author.id
            document = find_player(discordID)
            document = list(document)         
            
            # Check if player completed spire
            pre_checks = []
            if not await all_checks(pre_checks, ctx, document):
                return
            
            requirement = get_player(document, "all_stats", "counts", "spire_win")
            if requirement > 0:
                player_wax = get_player(document, "wax")
                player = {}
                player['id'] = discordID
                player['wax'] = player_wax
                wax_doc = []
                wax_doc.append(player)
                print(wax_doc)
            
            # Player has not completed the Sparkly Spire so cannot get a score
            else:
                await ctx.send(f"{ctx.message.author.mention} Prove yourself worthy by completing the Sparkly Spire in order to set your Fakulty")
                return

        def calc_template_power(issued):
            power = 0
            if issued <= 20:
                power = 25
            if issued <= 40:
                power = 20
            if issued <= 90:
                power = 15
            elif 90 < issued < 200:
                power = 10
            elif issued >= 200:
                power = 5
            
            return power

        await ctx.send("Calculating your Fakulty. . . Please wait.")
        templates = get_week_templates()
        game_template = get_game_template()
        game_chosen = game_template["game"] 
        chosen = templates["chosen"]
        chosen.append(game_chosen)
        # chosen = list(map(int, chosen))
        # print(chosen)        
        # print(wax_doc)
        # print(len(wax_doc))
        index = 0
        
        for player in wax_doc:
            score = 0
            wax = wax_doc[index]["wax"]            
            matching_templates = get_player_templates(wax, chosen)
            index += 1

            # Calculate score based on templates
            for template in matching_templates:
                if template == game_chosen:
                    score += 20
                else:
                    score += calc_template_power(ALL_AKU_TEMPLATES[template])
                # print(score)
            
            # Limit score max
            if score > 75:
                score = 75
            
            # Update db with score
            if score > 0:
                add_fakulty(wax, score)
            print(f"{wax} - {score}")
            await ctx.send(f"Your Fakulty has been set to {score}") 
            # if index == 0:
            #     print(Nothing found))
            #     return

def setup(bot: commands.bot):
    bot.add_cog(power(bot))    

        # def get_matching_templates(wax):
        #     matching_templates = {}
        #     player_templates = get_player_templates(wax)
        #     week_templates = get_week_templates()

        #     for template in week_templates:
        #         if template in player_templates:
        #             matching_templates[template] = ALL_AKU_TEMPLATES[template]

        #     return matching_templates

                # def get_game_template()
        #     template = db.assets.findone("game_template")
        #     return template
                # def get_mints_outdated(template_id, collection = "akufishheads"):
        #     request = f"/atomicassets/v1/templates/{collection}/{template_id}"
        #     response = try_api_request(request)
        #     if response == -1:
        #         print("Encountered an unknown error, exiting")
        #         return 
        #     max_supply = response["data"]["issued_supply"]
        #     return max_supply 

          #Some templates we don't want to use. 


        


        # for _ in range(0,10):
        #     templates = get_collection_templates()
        #     player_addresses = ['4p5cw.wam', '.gfu2.wam','2lhfu2.wam','majicwallet1','majicwallet2','lhfu2.wam']
        #     print(templates)
        #     for i in player_addresses:
        #         print(get_player_assets(i,templates))