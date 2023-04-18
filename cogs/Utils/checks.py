import nextcord
from nextcord.ext import commands
import random
import requests
import asyncio
import datetime
import re
from datetime import datetime, timedelta, time

from test_database import *
from constants import *

HOVELS = SETTINGS["hovels"]
BOARD_SIZE = SETTINGS["positions"]
GUESS_ATTEMPTS = SETTINGS["guess_attempts"]
ROLL_EMOJI = EMOJIS["roll"]


ALL_AKU_TEMPLATES = AKUFISHHEADS
FAST_API_LIST = FAST_API
api_index = 0

ignore_template = [403803,339528,176844,175369,406851]

class checks(commands.Cog):
    """ Player uses this command to roll for movement points, and to move to a different position  """

    def __init__(self, bot: commands.bot):
        self.bot = bot

def try_api_request(request:str,endpoints = FAST_API_LIST):
            """Tries to call the request, and handles cases in which we hit a timeout decently well"""
            global api_index
            backoff_factor = 0
            while True: 
                for _ in range(0,len(endpoints)): #Try out all endpoints before we start worrying about backoffs 
                    current_api = endpoints[api_index]
                    api_index = (api_index + 1) % len(endpoints) #Increment in case of failure. 
                    full_req = current_api + request  #get the full request
                    try:
                        r = requests.get(full_req,timeout=3)
                    except (requests.ConnectionError, requests.HTTPError,requests.ReadTimeout,requests.Timeout,requests.ConnectionError):
                        print("Request raised an unknown error. Moving on to next endpoint but that may not be the problem...")
                        # print(full_req)   
                        continue
                    try:
                        data = r.json()
                    except ValueError:
                        print(full_req) 
                        print("Encountered JSON Error, trying again")
                        # print("Encountered JSON Error", r.text)
                        #   
                        continue
                    if data['success'] != True:
                        if data['message'] == 'Rate limit':
                            print("Rate limiting, will try a different API endpoint")
                            # print(full_req)   
                        else: 
                            print("Unknown error in query, continuing but please analyse this closer...")
                            # print(full_req, r)
                        continue 
                    else:
                        api_index = (api_index - 1) % len(endpoints) #The request was succesfull, so let's keep using that API.
                        return data 
                #At this point we hit all of the APIs unsucesfully. Time to sleep for a bit. 
                print("We tried all API endpoints and all are rate limiting us. Time to sleep!")
                if backoff_factor > 10:
                    print("API really doesn't like us today. Giving up...")
                    return -1 
                backoff_factor += 1 
                print(f"Detecting rate limiting, sleeping for {backoff_factor*10} seconds now")
                time.sleep(10*backoff_factor)
    
    
def check_input(input_type, discordID):
    def _check(msg):
        # Check for the correct author
        if msg.author.id != discordID:
            return False

        # Check for a valid integer input
        if input_type == 'int' and msg.content.isdigit():
            return True

        # Check for a valid text input
        if input_type == 'text' and re.match(r'^[a-zA-Z\s]+$', msg.content):
            return True

        return False
    return _check

def check_transfer(wax_address, template, previous_transfer):
    request = f"/atomicassets/v1/transfers?sender={wax_address}&recipient=akutreasures&template_id={template}&after={previous_transfer}&page=1&limit=100&order=desc&sort=created"
    response = try_api_request(request)
    if response == -1:
        print("Encountered an unknown error, exiting")
    data = response["data"]
    return data

def get_mints(template_id, collection = "akufishheads"):
        request = f"/atomicassets/v1/templates/{collection}/{template_id}/stats"
        response = try_api_request(request)
        if response == -1:
            print("Encountered an unknown error, exiting")
            return 
        supply = response["data"]["assets"]
        burnt = response["data"]["burned"]
        return int(supply) - int(burnt)

def get_player_templates(wax_address,templates,collection="akufishheads"):
        request = f"/atomicassets/v1/accounts/{wax_address}/{collection}"
        response = try_api_request(request)
        if response == -1:
            print("Encountered an unknown error, exiting")
            return 
        output = [] 
        for template_dict in response['data']['templates']:
            template_id = template_dict['template_id']
            number_owned = template_dict['assets']
            if int(number_owned) > 0 and template_id in templates: #Should work regardless of wether templates is a list of templates or a dict where templates are the key. 
                output.append(template_id)
        return output 
            

def get_schemas(collection="akufishheads"):
    schema_request = f"/atomicassets/v1/schemas?collection_name={collection}"
    response = try_api_request(schema_request)
    if response == -1:
        print("Encountered an unknown error, exiting")
        return -1  
    return response['data']


def get_templates(schema, collection="akufishheads",template_blacklist = ignore_template,):
        request = f"/atomicassets/v1/templates?collection_name={collection}&schema_name={schema}&has_assets=true"
        response = try_api_request(request)
        if response == -1:
            print("Encountered an unknown error, exiting")
            return -1
        output = [] 
        for template in response['data']:
            if template['template_id'] not in template_blacklist:
                output.append(template)
        return output


def get_collection_templates(collection="akufishheads",template_blacklist = ignore_template,):
    schemas = get_schemas(collection)
    if schemas == -1:
        print("Encountered an unknown error, exiting")
        return 
    templates = {}
    for schema in schemas:
        schema_templates = get_templates(schema['schema_name'],collection,template_blacklist)
        if schema_templates == -1: #Really not happy with how I am handling these. 
            print("Encountered an unknown error, exiting")
            return 
        for templ in schema_templates:
            template_id = templ['template_id']
            mints = get_mints(template_id,collection)
            templates[template_id] = mints 
    return templates 


def get_player(player, key='', subkey='', nested=''):
    try:
        if nested:
            return player[0][key][subkey][nested]
        elif subkey:
            return player[0][key][subkey]
        else:
            return player[0][key]
    except KeyError:
        return False


async def all_checks(checks, ctx, player, command=""):
    
    # Waiting for user input
    if "skip_busy" not in checks:
        if player:
            if get_busy(ctx.author.id):
                await ctx.send(f"{ctx.author.mention} Another command is still in progress!")
                return False
    

    # Player not registered
    if not player:
        await ctx.send(f"{ctx.author.mention} <a:hehe_aku:867940486395097148> : Welcome to AKU WORLDS!"
        "\nYou will need a WAX address to play."
        "\nUse `!register waxaddress.wam` to register your address to the database.")
        return False

    # Check command is used in DM
    if "channel" in checks:
        if not check_channel(ctx.channel):
            await ctx.send(" <a:hehe_aku:867940486395097148> Please only use this command in a MMD channel.")
            return False
    
    # Check if command used today
    if "time" in checks:
        now = datetime.datetime.today()        
        last_command = get_player(player, "time", command)

        reset_time = time(16, 20, 00) # 4:20 PM PST
        midnight = time(23, 59, 59) # 12:00 AM PST
        reset_date = datetime.datetime.combine(datetime.datetime.now().date(), reset_time)
        time_epoch = int(reset_date.timestamp())
        
        if now.time() < reset_time:
            time_epoch = int(reset_date.timestamp())
            reset_date -= timedelta(days=1)
            print("now before reset time")

        if reset_time < now.time() < midnight:
            new_reset_date = reset_date + timedelta(days=1)
            time_epoch = int(new_reset_date.timestamp())
            print("now after reset but before midnight")
       
        if last_command and last_command > reset_date:
            # time_until_reset = (reset_date - now).seconds         
            await ctx.send(f" {ctx.author.mention} The next AKU WORLDS day begins <t:{time_epoch}:F>."
            f"\nYou can use this command again <t:{time_epoch}:R>!")
            
            return False
    
    # Check if in town
    if "town" in checks:        
        pos = get_player(player, "pos")
        if pos == 0:
            await ctx.send(" <a:hehe_aku:867940486395097148> You can't use this command in town!"
            "\nTry again after you leave town with `!bye`.")  
            return False

    # Must be in town
    if "not_town" in checks:
        pos = get_player(player, "pos")
        if pos != 0:
            await ctx.send(f"{ctx.author.mention} You have to take the `!taxicrab` to Town (`0`) to use this command!")
            return False
    
    # All checks passed
    return True
    

def check_channel(channel):
    if isinstance(channel, nextcord.channel.DMChannel):
        return False
    else:
        return True


def check_item(player, item):
    has_item = get_player(player, "inv", item)

    if has_item:
        return True
    else:
        return False


def check_count(player, command, max_count):
    player_count = get_player(player, "week_stats", "counts", command)

    if player_count < max_count:
        return True
    else:
        return False


def check_garden_time(plot, action, after_time):
    before_time = plot.get(action)
    if before_time < after_time:
        return True
    else:
        return False


def get_remaining_moves(player):
    points = get_player(player, "info", "points")
    used_points = get_player(player, "info", "used_points")
    return points - used_points


def get_guess_count(player):
    guessWins = get_player(player, "week_stats", "counts", "guess_win")
    guessLosses = get_player(player, "week_stats", "counts", "guess_lose")
    return guessWins + guessLosses


async def check_hovel(ctx, player, id, pos):
	if pos in HOVELS:
		guesses = get_guess_count(player)            
		await asyncio.sleep(1)
		if guesses < GUESS_ATTEMPTS:
			await ctx.send(f"{ctx.author.mention} You are now safe in a HOVEL! You can try to play a `!guess`ing game here.")
		else:
			await ctx.send(f"{ctx.author.mention} You are now safe in a HOVEL! You have used all your `!guess`ing game attempts this week already!")

async def check_cross_border(ctx, id, pos, move):
    if (pos + move) > BOARD_SIZE:
        pos = (pos + move) % BOARD_SIZE
        freeMoffs = random.randint(1,10)
        await ctx.send(f"{ctx.author.mention} You crossed the border! Nothing was stopping you from doing so, and you even happened to find {freeMoffs} MOFFS!")
        add_stat(id, "moffs", freeMoffs)
        return pos
    else:
        return pos + move
		

async def check_health_move(ctx, player, moveRoll):
    # Check for health bonus
    health = get_player(player, "week_stats", "totals", "health")
        
    if health < -20:
        newMove = int(moveRoll / 2)             
        await ctx.send(f"{ctx.author.mention} You feel weak, like a limp noodle. . . You rolled a {moveRoll} but it has been reduced to a {newMove}.  Better take the `!taxicrab` to town so you can visit the `!gym` and get healthy again!")
        moveRoll = newMove
        return moveRoll
    elif health < -5:
        newMove = moveRoll - 1        
        await ctx.send(f"{ctx.author.mention} You're feeling a bit under the weather. . . You rolled a {moveRoll} but it has been reduced to a {newMove}.  It would be a good idea to take the `!taxicrab` to town and visit the `!gym` when you can!")
        moveRoll = newMove
        return moveRoll
    elif health > 0 and health < 20:
        await ctx.send(f"{ctx.author.mention} You rolled a {moveRoll} today and you gained an extra point for staying healthy!")                
        moveRoll += 1                
        return moveRoll
    elif health >= 20 and health < 40:
        bonus = random.randint(1,3)
        await ctx.send(f"{ctx.author.mention} You feel healthy! You rolled a {moveRoll} today and you gained a healthy bonus of {bonus}!")                
        moveRoll += bonus                
        return moveRoll
    elif health >= 40:
        bonus = random.randint(3,5)
        await ctx.send(f"{ctx.author.mention} WOW, you must work out! You're feeling great today! You rolled a {moveRoll} today and you gained a very healthy bonus of {bonus}!")
        moveRoll += bonus
        return moveRoll
    else: 
        return moveRoll


def get_count(player, command):
    return get_player(player, "week_stats", "counts", command)

def setup(bot: commands.bot):
    bot.add_cog(checks(bot))
