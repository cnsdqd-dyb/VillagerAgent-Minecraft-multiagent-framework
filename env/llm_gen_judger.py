import json
import platform
import os
from utils import *
import argparse

# python env/buid_test.py --host 127.0.0.1 --port 25565 
system_type = platform.system().lower()

parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str, default="10.21.31.18", help='the host of the server')
parser.add_argument("--port", type=int, default=25565, help="the port of the server")
parser.add_argument('--agent_num', type=int, default=1, help='how many agents in the test')
parser.add_argument("--agent_names", type=str, default="", help="the name of the agents in A,B,C format")
parser.add_argument("--task_name", type=str, default="test", help="the name of the task")
args = parser.parse_args()

agent_num = args.agent_num
agent_names = args.agent_names.split(",")
task_name = args.task_name

mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')
collectBlock = require('mineflayer-collectblock')
pvp = require("mineflayer-pvp").plugin
if system_type == 'linux':
    minecraftHawkEye = require("minecrafthawkeye").default
else:
    minecraftHawkEye = require("minecrafthawkeye")
Vec3 = require("vec3")
Socks = require("socks5-client")
minecraftData = require('minecraft-data')


bot = mineflayer.createBot({
    "host": args.host,
    "port": args.port,
    'username': "gen_judger",
    'checkTimeoutInterval': 600000,
    'auth': 'offline',
    'version': "1.19.2",
})

bot.loadPlugin(pathfinder.pathfinder)
bot.loadPlugin(collectBlock.plugin)
bot.loadPlugin(pvp)
bot.loadPlugin(minecraftHawkEye)

#TODO: cache
with open(".cache/meta_setting.json", "r") as f:
    blueprint = json.load(f)["blueprint"]

### reset the environments
with open("data/score.json", "w") as f:
    json.dump({}, f, indent=4) 

with open(".cache/env.cache", "w") as f:
    json.dump([], f, indent=4)

with open(".cache/load_status.cache", "w") as f:
    json.dump({"status": "loading"}, f, indent=4)

if not os.path.exists("result"):
    os.makedirs("result")

x_b, y_b, z_b = 41, -60, 122
min_x, min_y, min_z = -11, 0, 0
max_x, max_y, max_z = 11, 15, 25

start_time = None
last_time = None
max_time = 300

@On(bot, 'spawn')
def handleViewer(*args):   
    def render_structure(data: dict, x_bias, y_bias, z_bias):

        blocks = data.get("blocks", [])
        for b in blocks:
            # if it has a key called "type" and the value is "line":
            if b.get("type") == "line" or b.get("type") == "rectangle":
                x_0, y_0, z_0 = b["from"][0] + x_bias, b["from"][1] + y_bias, b["from"][2] + z_bias
                x_1, y_1, z_1 = b["to"][0] + x_bias, b["to"][1] + y_bias, b["to"][2] + z_bias
                # fill: 用于填充一个区域。
                # 例如：/fill 1 2 3 4 5 6 stone
                bot.chat(f'/fill {x_0} {y_0} {z_0} {x_1} {y_1} {z_1} {b["name"]}')
                time.sleep(.1)
            
            elif b.get("type") == "tree":
                # tree: 用于生成树木。
                # 例如：/tree oak 1 2 3
                x, y, z = b["position"][0] + x_bias, b["position"][1] + \
                    y_bias, b["position"][2] + z_bias
                bot.chat(f'/place feature {b["name"]} {x} {y} {z}')
                time.sleep(.1)
                
            else:
                x, y, z = b["position"][0] + x_bias, b["position"][1] + y_bias, b["position"][2] + z_bias

                parameter = {}
                for key in b.keys():
                    # this is for other parameters, like facing, etc. they are not compulsory so we need to check if they exist
                    if key != "position" and key != "name" and key != "items":
                        parameter[key] = b[key]
                if len(parameter) == 0:
                    bot.chat(f'/setblock {x} {y} {z} {b["name"]}')
                else:
                    # if there are other parameters like facing, text, etc.
                    # example: /setblock 1 2 3 stone[facing=west]
                    parameter_str = ""
                    for i, key in enumerate(parameter.keys()):
                        if i != 0:
                            parameter_str += ","
                        parameter_str += f"{key}={parameter[key]}"
                    bot.chat(
                        f'/setblock {x} {y} {z} {b["name"]}[{parameter_str}]')

                # if the block is a chest, we need to set the items in it
                if b["name"] == "chest":
                    items = b.get("items", [])
                    next_slot = 0
                    for i, item in enumerate(items):
                        item_name = item["name"]
                        item_count = item["count"]
                        if item_name == "milk_bucket" or item_name == "bucket":
                            for j in range(item_count):
                                # item	用于修改方块或实体的物品栏。
                                # 替换方块（箱子、熔炉等）或实体（玩家或生物）物品栏内的物品。
                                bot.chat(f'/item replace block {x} {y} {z} container.{next_slot} with {item_name}')
                                next_slot += 1
                        else:
                            bot.chat(f'/item replace block {x} {y} {z} container.{next_slot} with {item_name} {item_count}')
                            next_slot += 1

            # 生成环境中的实体
        entities = data.get("entities", [])
        for e in entities:
            time.sleep(.1)
            x, y, z = e["position"][0] + x_bias, e["position"][1] + y_bias, e["position"][2] + z_bias
            # summon: 生成一个实体。
            bot.chat(f'/summon {e["name"]} {x} {y} {z}')

    # render 函数是这段代码中用于动态生成 Minecraft 建筑结构的核心函数，它负责根据任务配置（task_data）在游戏世界中渲染各种建筑、方块和实体。
    def reset():
        bot.chat("/gamemode spectator")
        time.sleep(.2)
        bot.chat("/gamerule doDaylightCycle false")
        time.sleep(.2)
        bot.chat("/gamerule doWeatherCycle false")
        time.sleep(.2)
        bot.chat("/time set day")
        time.sleep(.2)
        bot.chat("/weather clear")
        time.sleep(.2)
        bot.chat(f"/fill {x_b+min_x} {y_b+min_y} {z_b+min_z} {x_b+max_x} {y_b+max_y} {z_b+max_z} air")
        time.sleep(.2)
        for agent_name in agent_names:
            bot.chat(f"/gamemode survival {agent_name}")
        bot.chat("/clear @a[gamemode=survival]")
        time.sleep(.2)
        bot.chat("/kill @e[type=!minecraft:player]")
        time.sleep(.2)
        bot.chat("/kill @e[type=!minecraft:player]")
        time.sleep(.2)

        bot.chat(f"/fill {x_b + min_x} {y_b + min_y} {z_b + min_z} {x_b + max_x} {y_b + max_y} {z_b + min_z} glass")
        time.sleep(.1)
        bot.chat(f"/fill {x_b + min_x} {y_b + min_y} {z_b + max_z} {x_b + max_x} {y_b + max_y} {z_b + max_z} glass")
        time.sleep(.1)
        bot.chat(f"/fill {x_b + min_x} {y_b + min_y} {z_b + min_z} {x_b + min_x} {y_b + max_y} {z_b + max_z} glass")
        time.sleep(.1)
        bot.chat(f"/fill {x_b + max_x} {y_b + min_y} {z_b + min_z} {x_b + max_x} {y_b + max_y} {z_b + max_z} glass")
        time.sleep(.1)
        bot.chat(f"/fill {x_b + min_x} -61 {z_b + min_z} {x_b + max_x} -61 {z_b + max_z} grass_block")
        time.sleep(.1)

        render_structure(blueprint, x_b, y_b, z_b)

        for agent_name in agent_names:
            bot.chat(f"/tp {agent_name} {x_b} {y_b} {z_b + 2}")
            time.sleep(.1)
            bot.chat(f"/give {agent_name} dirt 15")
            time.sleep(.1)
            bot.chat(f"/give {agent_name} ladder 15")

    for name in agent_names:
        bot.chat(f'/op {name}')  # Sends a publicly broadcast chat message.
        time.sleep(.2)
    
    reset()

    with open(".cache/load_status.cache", "w") as f:
       json.dump({"status": "loaded"}, f, indent=4)

    global start_time, last_time
    start_time = time.time()
    last_time = start_time


@On(bot, "time")
def handleTime(*args):
    global start_time, max_time, last_time
    if start_time is not None:
        now_time = time.time()

        if now_time - last_time > 20:
            bot.chat(f"time: {now_time - start_time}")
            last_time = now_time

        if now_time - start_time > max_time:
            with open(".cache/load_status.cache", "w") as f:
                json.dump({"status": "end"}, f, indent=4)