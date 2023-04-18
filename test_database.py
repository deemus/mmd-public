import pymongo
from pymongo import MongoClient, UpdateOne
import urllib.parse
import datetime
from datetime import timedelta
import os
from dotenv import load_dotenv
import random
from constants import *


cluster = MongoClient(os.getenv("databaseURL"))
db = cluster['mmdragum']

resets_collection = db['resets']

# BETA DB
player = db['test']
templates = db['templates']
mmd = db['player']

def db_week_templates(chosen_templates, game_template):
    time = datetime.datetime.today()
    query = {"title": "weekly templates"}
    templates.update_one(query,
        {"$set": {
            "week":time,
            "chosen":chosen_templates,
            "game":game_template
                }
        })


def get_week_templates():
    return templates.find_one({}, {"chosen": 1})

def get_game_template():
    return templates.find_one({}, {"game":1})



# Return player document
def find_player(id):
    query = {"_id": id}
    return player.find(query)


def get_wax_from_id(id):
    query = {"_id": id}
    return player.find(query, {"wax":1})


def get_all_wax_power():
    return player.find({"all_stats.counts.spire_win":{"$gt":0}}, {"wax":1})

     
def get_reset():
    now = datetime.datetime.today()   
    reset_time = time(16, 20) # 4:20 PM PST
    reset_date = datetime.datetime.combine(datetime.datetime.now().date(), reset_time)
    # time_epoch = int(reset_date.timestamp())

    if now.time() < reset_time:
        # time_epoch = int(reset_date.timestamp())
        reset_date -= timedelta(days=1)

    return reset_date
        


def db_attract(id, roll, time):
    query = {"_id": id}
    player.update_one(query,
    {"$set": {
        "time.attract":time}, 
    "$inc":{
        "inv.moffs":roll,
        "week_stats.totals.moffs":roll, 
        "week_stats.totals.attracted":roll,
        "week_stats.counts.attract":1, 
        "all_stats.totals.moffs":roll, 
        "all_stats.totals.attracted":roll,
        "all_stats.counts.attract":1}})


def db_move(id, pos, move):
    query = {"_id": id}
    player.update_one(query, 
    {"$set": {
        "pos":pos}, 
    "$inc":{
        "info.used_points":move,
        "week_stats.totals.moved":move, 
        "week_stats.counts.move":1,
        "all_stats.totals.moved":move, 
        "all_stats.counts.move":1, 
        }})


def db_roll(id, roll, remaining, time):
    total = roll + remaining
    query = {"_id": id}
    player.update_one(query, 
    {"$set": {
        "info.points":total,
        "info.used_points": 0, 
        "time.move":time}, 
    "$inc":{
        "week_stats.totals.rolled":roll, 
        "week_stats.counts.roll":1,
        "all_stats.totals.rolled":roll, 
        "all_stats.counts.roll":1,
        "all_stats.totals.points":roll, 
        }})


def db_look(id, pos, search):
    query = {"_id": id}
    player.update_one(query, 
    {"$inc":{
        "info.used_points":search,
        "week_stats.totals.looked":search, 
        "week_stats.counts.look":1,
        "all_stats.totals.looked":search, 
        "all_stats.counts.look":1, 
        },
    "$addToSet":{"info.looked":pos}})


def db_heist(id, salt, crystals, time):
    query = {"_id": id}
    if salt > 0:
        player.update_one(query, {"$set":{"time.heist":time}, 
        "$inc":{
            "inv.salt":salt,
            "week_stats.totals.salt":salt,
            "week_stats.totals.heist":salt,
            "week_stats.counts.heist_win":1,
            "week_stats.counts.heist_crystals":crystals,
            "all_stats.totals.salt":salt,
            "all_stats.totals.heist":salt,
            "all_stats.counts.heist_win":1,
            "all_stats.counts.heist_crystals":crystals,}})
    else:
        player.update_one(query, {"$set":{"time.heist":time}, 
        "$inc":{
            "week_stats.counts.heist_lose":1,
            "week_stats.counts.heist_crystals":crystals,
            "all_stats.counts.heist_lose":1,
            "all_stats.counts.heist_crystals":crystals}})


def db_guess(id, result, moffs, time):
    query = {"_id": id}
    if result == "WIN":
        player.update_one(query, 
        {"$set":{"time.guess":time}, 
        "$inc":{
            "inv.moffs":moffs,
            "week_stats.counts.guess_win": 1,
            "week_stats.totals.moffs": moffs, 
            "all_stats.counts.guess_win": 1,
            "all_stats.totals.moffs": moffs}})
        
    if result == "LOSE":
        player.update_one(query, 
        {"$set":{"time.guess":time}, 
        "$inc":{
            "inv.moffs":moffs,
            "week_stats.counts.guess_lose": 1,
            "week_stats.totals.moffs": moffs, 
            "all_stats.counts.guess_lose": 1,
            "all_stats.totals.moffs": moffs}})


def db_gym(id, health, salt, time):   
    query = {"_id": id}
    player.update_one(query, 
    {"$set": {"time.gym": time},
    "$inc":{
        "week_stats.counts.gym": 1,
        "week_stats.totals.health": health,
        "week_stats.totals.gym": salt,
		"all_stats.totals.gym": salt,
        "all_stats.counts.gym": 1,
        "all_stats.totals.health": health,}})


def db_spire(id, score, crystals, level, time):
    query = {"_id": id}
    
    if level == 6:
        player.update_one(query, 
        {"$set":{
            "time.spire": time, 
            "week_stats.totals.spire_score": score,},
        "$inc":{
            "week_stats.counts.spire_crystals": crystals,
            "all_stats.counts.spire_crystals": crystals, 
            "week_stats.totals.spire_levels": level, 
            "all_stats.totals.spire_levels": level, 
            "week_stats.counts.spire_win": 1,
            "all_stats.counts.spire_win": 1,}})
    else:
        player.update_one(query, 
        {"$set":{
            "time.spire": time, 
            "week_stats.totals.spire_score": score,},
        "$inc":{
            "week_stats.counts.spire_crystals": crystals,
            "all_stats.counts.spire_crystals": crystals, 
            "week_stats.totals.spire_levels": level, 
            "all_stats.totals.spire_levels": level, 
            "week_stats.counts.spire_lose": 1,
            "all_stats.counts.spire_lose": 1,}})


def db_spire_best(id, score, crystals, level, time):
    query = {"_id": id}
    
    if level == 6:
        player.update_one(query, 
        {"$set":{
            "time.spire": time, 
            "week_stats.totals.spire_score": score,
            "all_stats.totals.spire_score": score,},
        "$inc":{
            "week_stats.counts.spire_crystals": crystals,
            "all_stats.counts.spire_crystals": crystals, 
            "week_stats.totals.spire_levels": level, 
            "all_stats.totals.spire_levels": level, 
            "week_stats.counts.spire_win": 1,
            "all_stats.counts.spire_win": 1,}})
    else:
        player.update_one(query, 
        {"$set":{
            "time.spire": time, 
            "week_stats.totals.spire_score": score,
            "all_stats.totals.spire_score": score,},
        "$inc":{
            "week_stats.counts.spire_crystals": crystals,
            "all_stats.counts.spire_crystals": crystals, 
            "week_stats.totals.spire_levels": level, 
            "all_stats.totals.spire_levels": level, 
            "week_stats.counts.spire_lose": 1,
            "all_stats.counts.spire_lose": 1,}})


def db_taxi(id, oldPos, dest, distance, fare):   
    query = {"_id": id}
    player.update_one(query, 
    {"$set": {
        "info.oldPos":oldPos,  
        "pos":dest},
    "$inc":{
        "inv.moffs": -fare,
        "week_stats.counts.rode_taxi": distance,
        "all_stats.counts.rode_taxi": distance,
        "week_stats.totals.taxi_fare": fare,
        "all_stats.totals.taxi_fare": fare,}})
		
		
def db_kraberto(id, item, spent, time):   
    query = {"_id": id}
    player.update_one(query, {
	"$set": {
		"time.kraberto":time},
	"$inc": {
		"week_stats.totals.kraberto": spent,
		"all_stats.totals.kraberto": spent,
		"week_stats.counts.kraberto_"+item: 1,		
		"all_stats.counts.kraberto_"+item: 1,}})


def db_trade(id, item, amount):
    query = {"_id": id}
    player.update_one(query, 
    {"$inc":{
        "week_stats.counts.traded_"+item:amount,
        "all_stats.counts.traded_"+item:amount,}})


def db_pump(id, points, time):
    query = {"_id": id}
    player.update_one(query, 
    {"$set": {
        "time.pump":time}, 
    "$inc":{
        "info.points": points,
        "week_stats.totals.pump_gain":points, 
        "week_stats.counts.pump":1,
        "all_stats.totals.pump_gain":points, 
        "all_stats.counts.pump":1, 
        }})


def db_mom(id, result, moffs, crystal):
    query = {"_id": id}
    if result == "success":
        player.update_one(query, {
            "$inc": {
                "week_stats.counts.mom_win":1,
                "week_stats.counts.mom_crystals":1,
                "week_stats.counts.mom_moffs":moffs,
                "all_stats.counts.mom_win":1,
                "all_stats.counts.mom_crystals":1,
                "all_stats.counts.mom_moffs":moffs,
                "inv."+crystal: -1,
                "inv."+"moffs": -moffs,
                "inv."+"moff_token": 1,
                }})
    else:
        player.update_one(query, {
            "$inc": {
                "week_stats.counts.mom_lose": 1,
                "week_stats.counts.mom_moffs":moffs,
                "all_stats.counts.mom_lose": 1,
                "all_stats.counts.mom_moffs":moffs,
                "inv."+"moffs": -moffs,
                }})        


def add_item_amt(id, item, amount):    
    query = {"_id": id}

    if amount > 0:
        # add item
        player.update_one(query, 
        {"$inc":{
            "inv."+item: amount,
            "week_stats.totals."+item: amount,
            "all_stats.totals."+item: amount
            }}, upsert=True)
    else:        
        # remove item
        player.update_one(query, 
        {"$inc":{
            "inv."+item: amount,
            }}, upsert=True)


def add_stat(id, stat, amount):
    query = {"_id": id}
    if stat in ["moffs", "salt", "health"]:
        player.update_one(query,
        {"$inc":{
            "week_stats.totals."+stat: amount,
            "all_stats.totals."+stat: amount
            }})
    if stat in ["points", "used_points", "fakulty"]:
        player.update_one(query,
        {"$inc":{
            "info."+stat: amount,
            "all_stats.totals."+stat: amount
        }})


def db_buy_plot(id, plot, cost):
    new_plot = str(plot + 1)
    query = {"_id": id}
    player.update_one(query, 
        {"$set": {
            "garden.plot_"+new_plot:{
                "seed":'',
        }},
        "$inc":{
            "inv.moff_token": -cost,
            "garden.unlocked_plots": 1,
        },
        "$addToSet":{
            "garden.free_plots":new_plot
        }})


def db_clear_plot(id, plot, num, cost):
    query = {"_id": id}
    player.update_one(query, 
        {"$set": {
            "garden."+plot:{
                "seed":'',
        }},
        "$inc":{
            "inv.salt": -cost,
        },
        "$addToSet":{
            "garden.free_plots":str(num)
        }})


def db_plant(id, plot, seed, time):
    harvest_time = time + timedelta(days=PLANTS[seed]["days_to_grow"])
    plot = str(plot)
    query = {"_id": id}
    player.update_one(query, 
        {"$set": {
            "garden.plot_"+plot:{
                "seed":seed,
                "harvests_remaining":PLANTS[seed]["harvests"],
                "plant_time":time,
                "harvest_time":harvest_time,
                "daily_harvest":datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
                "fert_time":datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
        }},
        "$inc":{
            "inv.seeds":-1
        },
        "$pull":{
            "garden.free_plots":plot
        }})


def db_fert(id, plots, cost, now):
    query = {"_id": id}
    garden = player.find(query, {"garden"})
    garden = garden.next()
    garden = garden.get('garden')    
    operations = []
    
    for plot in plots:
        plot_num = f"plot_{plot}"
        this_plot = garden.get(plot_num)
        harvest_time = this_plot.get('harvest_time')
        new_harvest_time = harvest_time - timedelta(days=1)

        operations.append(UpdateOne({"_id": id}, 
        {"$set": {
            "garden."+plot_num+".harvest_time":new_harvest_time,
            "garden."+plot_num+".fert_time":now,
        }}))

    operations.append(UpdateOne({"_id": id}, 
        {"$inc": {
            "inv.crystal_shard":-cost
        }}))
    
    player.bulk_write(operations)
    

def db_harvest(id, plot, bonus, bonus_amt, akumen, now):
    query = {"_id": id}  
    if bonus in ITEMS:
        player.update_one(query, 
        {"$set": {
            "garden."+plot+".daily_harvest":now,
        },
        "$inc":{
            "garden."+plot+".harvests_remaining":-1,
            "garden.akumen": akumen,
            "inv."+bonus: bonus_amt
        }})
    elif bonus == "points":
        player.update_one(query, 
        {"$set": {
            "garden."+plot+".daily_harvest":now,
        },
        "$inc":{
            "garden."+plot+".harvests_remaining":-1,
            "garden.akumen": akumen,
            "info.points": bonus_amt,
        }})


def db_transfer_time(id, time):
    query = {"_id": id}
    player.update_one(query,
        {"$set":{
            "transfers.last_sent_moff": time
            }})


def db_transfer_history(id, asset, transactions, time):
    query = {"_id": id}
    operations = []

    for trans in transactions:
        amt = transactions[trans]
        operations.append(UpdateOne({"_id": id}, 
        {"$set": {
            "transfers.history."+asset+"."+trans:amt
        }}))

    operations.append(UpdateOne(query, 
        {"$set":{
            "transfers.last_sent_"+asset: time,
            }}))
    
    player.bulk_write(operations)

def db_add_prizes(id, prizes):
    query = {"_id": id}
    operations = []

    for item in prizes:
        amount = prizes[item]
        operations.append(UpdateOne(query, 
        {"$inc":{
            "inv."+item: amount,
            "week_stats.totals."+item: amount,
            "all_stats.totals."+item: amount
            }}, upsert=True))

    
    player.bulk_write(operations)

def add_fakulty(wax, score):
    query = {"wax": wax}
    player.update_one(query,
        {"$set":{"info.fakulty": score}})


def move_player(id, pos):
    query = {"_id": id}
    player.update_one(query, {"$set": {"pos":pos}})


def remove_looked(id):
    query = {"_id": id}
    player.update(query, {"$set": {"info.looked":[]}})


def set_busy(id, status):
    query = {"_id": id}
    player.update(query, {"$set": {"info.busy": status}})


def get_busy(id):
    query = {"_id": id}
    info = {"info": 1}
    result = player.find_one(query, info)
    
    return result["info"]["busy"]

def daily_reset(id):
    query = {"_id": id}
    player.update(query, {"$set":{
        'time':{
                'attract': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
                'move': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
                'gym': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
                'kraberto': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
                'pump': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
                'heist': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
                'spire': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
                'mom': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
            }}})


def register_player(id, name, wax):
    randPos = random.randint(1, 20)

    player.insert_one(    
    {
        "_id":id,
        "name":name,
        "wax":wax,            
        "pos":randPos,
            
        'info':{
            'oldPos': randPos,
            'points': 0,
            'used_points': 0,
            'looked': [],
            'fakulty': 0,
            'busy': False,
        },
        'transfers':{
            'last_sent_moff': 1675276465500,
            'history':{},
        },
        'week_stats':{
            'totals':{
                'moffs': 0,
                'salt': 0,
                'health': 0,
                'points': 0,
                'attracted': 0,
                'rolled': 0,
                'moved': 0,
                'looked': 0,
                'heist': 0,
                'gym': 0,
                'spire_score': 0,
                'spire_levels': 0,
				'taxi_fare': 0,
				'kraberto': 0,

                'vit_bronze': 0,
                'vit_silver': 0,
                'vit_gold': 0,
                'ban_bronze': 0,
                'ban_silver': 0,
                'ban_gold': 0,                
                'salt_crystal': 1,
                'time_crystal': 0,
                'def_crystal': 0,
                'crystal_shard': 0,
                'moff_token':0,
            },            
            'counts':{
                'attract': 0,
                'roll': 0,
                'move': 0,
                'look': 0,
                'heist_win': 0,
                'heist_lose': 0,
                'heist_crystals': 0,
                'gym': 0,
                'guess_win': 0,
                'guess_lose': 0,
                'spire_win': 0,
                'spire_lose': 0,
                'spire_crystals': 0,
				'rode_taxi': 0,
				'kraberto_shot': 0,
				'kraberto_supp': 0,
				'kraberto_cran': 0,
                'traded_crystal_shard': 0,
                'traded_salt_crystal': 0,
                'mom_win': 0,
                'mom_lose': 0,
                'mom_crystals': 0,
                'mom_moffs': 0,
            },
        },
        'all_stats':{
            'totals':{
                'moffs': 0,
                'salt': 0,
                'health': 0,
                'points':0,
                'attracted': 0,
                'rolled': 0,
                'moved': 0,
                'looked': 0,
                'heist': 0,
                'gym': 0,
                'spire_score': 0,
                'spire_levels': 0,
				'taxi_fare': 0,
				'kraberto': 0,

                'vit_bronze': 0,
                'vit_silver': 0,
                'vit_gold': 0,
                'ban_bronze': 0,
                'ban_silver': 0,
                'ban_gold': 0,                
                'salt_crystal': 1,
                'time_crystal': 0,
                'def_crystal': 0,
                'crystal_shard': 0,
                'moff_token':0,
            },            
            'counts':{
                'attract': 0,
                'roll': 0,
                'move': 0,
                'look': 0,
                'heist_win': 0,
                'heist_lose': 0,
                'heist_crystals': 0,
                'gym': 0,
                'guess_win': 0,
                'guess_lose': 0,
                'spire_win': 0,
                'spire_lose': 0,
                'spire_crystals': 0,
				'rode_taxi': 0,
				'kraberto_shot': 0,
				'kraberto_supp': 0,
				'kraberto_cran': 0,
                'traded_crystal_shard': 0,
                'traded_salt_crystal': 0,
                'mom_win': 0,
                'mom_lose': 0,
                'mom_crystals': 0,
                'mom_moffs': 0,
            },
        },      
        'time':{
            'attract': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
            'move': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
            'gym': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
            'kraberto': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
            'pump': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
            'heist': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
            'spire': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
            'mom': datetime.datetime(2021, 4, 20, 16, 20, 0, 000000),
        },

        'garden': {
            'unlocked_plots': 0,
            'free_plots':[],
            'akumen': 0,
        },

        'inv':{
            'moffs': 0,
            'salt': 0,

            'vit_bronze': 0,
            'vit_silver': 0,
            'vit_gold': 0,
            'ban_bronze': 0,
            'ban_silver': 0,
            'ban_gold': 0,

            'moff_token': 0,
            'seeds': 0,
            
            'salt_crystal': 1,
            'time_crystal': 0,
            'def_crystal': 0,
            'crystal_shard': 0,

            'taxicrab': 0,          
            'hacker': 0,
            'pumps': 0,
            'fire_pumps': 0
        },
    })
