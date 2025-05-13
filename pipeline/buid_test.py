# multiplayer judger
# 这个judger需要加载一个设定的地形，将Agent初始化到指定位置
# json文件中包含了任务的地形，以及Agent的初始位置
# we also need to load the stuffing in the chest, and the items in the inventory
# To-Do: 根据Agent的状态，环境的更新，结合json文件，给出累计得分
import shutil
import threading
import time

import numpy as np

from utils import *
import json
import os
import argparse
from javascript import require, On

# python build_test.py --idx 0 --host 10.214.180.148 --port 25565 --task_name test


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--idx', type=int, default=0,
                        help='the index of the task, range from 0 to 99')
    parser.add_argument('--host', type=str,
                        default="127.0.0.1", help='the host of the server')
    parser.add_argument('--port', type=int, default=25565,
                        help='the port of the server')
    parser.add_argument('--agent_num', type=int, default=1,
                        help='how many agents in the test')
    parser.add_argument("--agent_names", type=str, default="",
                        help="the name of the agents in A,B,C format")
    parser.add_argument("--task_name", type=str,
                        default="test", help="the name of the task")
    args = parser.parse_args()

    agent_names = args.agent_names.split(",")
    with open(".cache/load_status.cache", "w") as f:
        json.dump({"status": "loading"}, f, indent=4)

    if not os.path.exists("result"):
        os.makedirs("result")

    # import mineflayer (javascript library)
    mineflayer = require('mineflayer')
    agent_num = args.agent_num
    task_name = args.task_name

    x_b, y_b, z_b = 41, -60, 122
    min_x, min_y, min_z = -11, 0, 0
    max_x, max_y, max_z = 11, 15, 25
    # Create and return an instance of the class bot
    bot = mineflayer.createBot({
        "host": args.host,
        "port": args.port,
        'username': "farm_judge",
        # keep alive interval, if not receiving any message in 10 minutes, the bot will disconnect
        'checkTimeoutInterval': 600000,
        'auth': 'offline',
        'version': "1.19.2"
    })

    with open("data/farm_setting.json", "r") as f:
        settings = json.load(f)
    assert args.idx < len(
        settings), "idx out of range, please make sure idx is in [0, 99]"
    task_data = settings[args.idx]

    start_time = None
    last_time = None

    # max_action_time = complexity * 40
    max_action_time = 10 * 60
    max_time = 10 * 200
    # max_time = complexity * 200
    # max_time = complexity * 200

    @On(bot, 'spawn')  # 当机器人 bot 成功生成到 Minecraft 世界后，自动调用 handleViewer 函数。
    def handleViewer(*args):

        for name in agent_names:
            # 授予玩家管理员权限
            bot.chat(f'/op {name}')  # Sends a publicly broadcast chat message.
            time.sleep(.2)

        bot.chat(f'/op farm_judge')  # Sends a publicly broadcast chat message.
        time.sleep(.2)

        def render_structure(data: dict, x_bias, y_bias, z_bias):
            # return blocks if exist, otherwise return []

            # trial
            bot.chat("/setblock 0 5 0 stone")
            bot.chat("/fill 0 5 1 0 5 4 stone")

            blocks = data.get("blocks", [])
            for b in blocks:
                # if it has a key called "type" and the value is "line":
                if b.get("type") == "line" or b.get("type") == "rectangle":
                    x_0, y_0, z_0 = b["from"][0] + x_bias, b["from"][1] + \
                        y_bias, b["from"][2] + z_bias
                    x_1, y_1, z_1 = b["to"][0] + x_bias, b["to"][1] + \
                        y_bias, b["to"][2] + z_bias
                    # 这里的-1非常奇怪，是程序的bug吗？
                    # fill: 用于填充一个区域。
                    # 例如：/fill 1 2 3 4 5 6 stone
                    bot.chat(
                        f'/fill {x_0} {y_0} {z_0} {x_1} {y_1} {z_1} {b["name"]}')
                    continue
                elif b.get("type") == "tree":
                    # tree: 用于生成树木。
                    # 例如：/tree oak 1 2 3
                    x, y, z = b["position"][0] + x_bias, b["position"][1] + \
                        y_bias, b["position"][2] + z_bias
                    bot.chat(
                        f'/place feature {b["name"]} {x} {y} {z}')
                    continue

                time.sleep(.1)
                x, y, z = b["position"][0] + x_bias, b["position"][1] + \
                    y_bias, b["position"][2] + z_bias

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
                                bot.chat(
                                    f'/item replace block {x} {y} {z} container.{next_slot} with {item_name}')
                                next_slot += 1
                        else:
                            bot.chat(
                                f'/item replace block {x} {y} {z} container.{next_slot} with {item_name} {item_count}')
                            next_slot += 1

            # 生成环境中的实体
            entities = data.get("entities", [])
            for e in entities:
                time.sleep(.1)
                x, y, z = e["position"][0] + x_bias, e["position"][1] + \
                    y_bias, e["position"][2] + z_bias
                # summon: 生成一个实体。
                bot.chat(f'/summon {e["name"]} {x} {y} {z}')

        # render 函数是这段代码中用于动态生成 Minecraft 建筑结构的核心函数，它负责根据任务配置（task_data）在游戏世界中渲染各种建筑、方块和实体。
        def render(data: dict, x_bias, y_bias, z_bias):
            with open("config.json", "r") as f:
                blue_prints = json.load(f)
                blue_prints = blue_prints["blueprint"]
            c = {"position": [
                5,
                0,
                7
            ],
                "name": "test4"
            }
            c = {"position": [
                0,
                0,
                0
            ],
                "name": "test4"
            }
            # render_structure(blue_prints[c["name"]], x_bias + c["position"][0], y_bias + c["position"][1],
            #                  z_bias + c["position"][2])
            render_structure(blue_prints, x_bias + c["position"][0], y_bias + c["position"][1],
                             z_bias + c["position"][2])

        # kill all entities except player to clear the world
        def clear(x_min, y_min, z_min, x_max, y_max, z_max):
            bot.chat(
                f"/fill {x_min} {y_min} {z_min} {x_max} {y_max} {z_max} air")
            bot.chat(f"/kill @e[type=!player]")
            bot.chat(f"/kill @e[type=item]")

        def init():
            global task_data, start_time, last_time
            # clear the specified area of entities
            bot.chat(
                f"test 1")
            clear(x_b + min_x, y_b + min_y, z_b + min_z,
                  x_b + max_x, y_b + max_y, z_b + max_z)
            bot.chat(
                f"test 2")
            print("clear done")
            time.sleep(1)

            bot.chat(
                f"/fill {x_b + min_x} -61 {z_b + min_z} {x_b + max_x} -61 {z_b + max_z} grass_block")
            time.sleep(.1)
            # call the render function to build the structures as specified by the task_data
            print("rendering...")
            render(task_data, x_b, y_b, z_b)

            # build the glass boundary which specifies the experiment area
            bot.chat(
                f"/fill {x_b + min_x} {y_b + min_y} {z_b + min_z} {x_b + max_x} {y_b + max_y} {z_b + min_z} glass")
            time.sleep(.1)
            bot.chat(
                f"/fill {x_b + min_x} {y_b + min_y} {z_b + max_z} {x_b + max_x} {y_b + max_y} {z_b + max_z} glass")
            time.sleep(.1)
            bot.chat(
                f"/fill {x_b + min_x} {y_b + min_y} {z_b + min_z} {x_b + min_x} {y_b + max_y} {z_b + max_z} glass")
            time.sleep(.1)
            bot.chat(
                f"/fill {x_b + max_x} {y_b + min_y} {z_b + min_z} {x_b + max_x} {y_b + max_y} {z_b + max_z} glass")
            time.sleep(.1)

            print("render done")

            # judger bot will be in spectator mode
            bot.chat("/gamemode spectator")
            # set the time and weather to clear
            bot.chat("/gamerule doDaylightCycle false")
            bot.chat("/gamerule doWeatherCycle false")
            bot.chat("/time set day")
            bot.chat("/weather clear")
            bot.chat(f"/tp {bot.username} {x_b} {y_b} {z_b}")
            bot.chat(
                # 将所有处于生存模式的玩家传送到指定坐标位置
                # @e - 选择所有实体
                # [type = minecraft:player] - 只选择玩家实体
                # [gamemode = survival] - 进一步筛选只处于生存模式的玩家
                f"/tp @e[type=minecraft:player, gamemode=survival] {x_b} {y_b} {z_b + 2}")
            # 清除所有处于生存模式的玩家背包中的物品
            bot.chat(f"/clear @e[type=minecraft:player, gamemode=survival]")

            target = []
            # for key in score_dict.keys():
            #     target.append(key)
            # with open("data/recipes.json", "r") as f:
            #     recipes = json.load(f)

            items_in_chest = []
            component = task_data.get("component", [])
            for c in component:
                if c["name"] == "chest":
                    items_in_chest += c.get("items", [])
            # recipe_hint = generate_recipe_hint(recipes, target, items_in_chest)
            # with open("data/recipe_hint.json", "w") as f:
            #     # 存储recipe_hint到文件中
            #     json.dump(recipe_hint, f, indent=4)

            time.sleep(1)

            start_time = time.time()
            last_time = start_time

            with open(".cache/load_status.cache", "w") as f:
                json.dump({"status": "loaded"}, f, indent=4)

        t = threading.Thread(target=init, args=())
        t.start()

    # @On(bot, 'time') 是一个 事件监听装饰器，用于让机器人定时触发某些任务或响应特定时间事件。
    @On(bot, 'time')
    def handleTime(*args):
        def calculate_balance():
            # 计算每个agent的时间
            if not os.path.exists('data/action_log.json'):
                return
            with open('data/action_log.json', 'r') as f:
                data = json.load(f)
            agent_time = []
            for action_name, actions in data.items():
                total_time = 0
                for action in actions:
                    # total_time += action['duration'] (default 0)
                    total_time += action.get('duration', 0)
                agent_time.append(total_time)
            for i in range(agent_num - len(agent_time)):
                agent_time.append(0)
            time_array = np.array(agent_time)

            # 对时间进行归一化处理
            time_array = (time_array) / (np.max(time_array) + 1e-8)

            # 计算并返回 Balanced Agent Utilization Score (BAUS)
            return 1 - np.std(time_array)

        def calculate_action_time():
            if not os.path.exists('data/action_log.json'):
                return 0
            with open('data/action_log.json', 'r') as f:
                data = json.load(f)
            time_list = []
            for name, actions in data.items():
                for action in actions:
                    start = time.mktime(time.strptime(
                        action['start_time'], "%Y-%m-%d %H:%M:%S"))
                    end = time.mktime(time.strptime(
                        action['end_time'], "%Y-%m-%d %H:%M:%S"))
                    time_list.append((start, end))
            if len(time_list) == 0:
                return 0

            # 计算覆盖的总时间
            total_time = 0  # 单位：秒
            time_list.sort(key=lambda x: x[0])  # 按照开始时间排序
            start, end = time_list[0]
            for i in range(1, len(time_list)):
                if time_list[i][0] < end:
                    end = max(end, time_list[i][1])
                else:
                    total_time += end - start
                    start, end = time_list[i]
            total_time += end - start

            return total_time

        def get_player_name():
            global task_data

            name_list = []
            entities = bot.entities
            for key in entities:
                type = entities[key].type
                if type == "player" and entities[key].username != bot.username:
                    x = entities[key].position.x
                    y = entities[key].position.y
                    z = entities[key].position.z
                    if x_b + min_x <= x <= x_b + max_x and y_b + min_y <= y <= y_b + max_y and z_b + min_z <= z <= z_b + max_z:
                        name_list.append(entities[key].username)
            return name_list

        global start_time, last_time
        if start_time is not None:
            global cooperation, efficiency
            now_time = time.time()

            if now_time - last_time > 1:
                with open(".cache/heart_beat.cache", "w") as f:
                    json.dump({"time": now_time}, f, indent=4)
                # if score == 100:
                #     efficiency = max_action_time / calculate_action_time()
                #     # 给出结束信号和写入文件
                #     if not os.path.exists(os.path.join("result", task_name)):
                #         os.mkdir(os.path.join("result", task_name))
                #     else:
                #         shutil.rmtree(os.path.join("result", task_name))
                #         os.mkdir(os.path.join("result", task_name))
                #     # with open(os.path.join(os.path.join("result", task_name), "score.json"), "w") as f:
                #     #     json.dump({
                #     #         "score": score,
                #     #         "cooperation": cooperation,
                #     #         "efficiency": efficiency,
                #     #         "balance": calculate_balance(),
                #     #         "use_time": calculate_action_time(),
                #     #         "end_reason": "complete task",
                #     #         "end_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_time))
                #     #     }, f, indent=4)
                #     with open(".cache/load_status.cache", "w") as f:
                #         json.dump({"status": "end"}, f, indent=4)

                if calculate_action_time() > max_action_time:
                    efficiency = 1
                    if not os.path.exists(os.path.join("result", task_name)):
                        os.mkdir(os.path.join("result", task_name))
                    else:
                        shutil.rmtree(os.path.join("result", task_name))
                        os.mkdir(os.path.join("result", task_name))
                    # with open(os.path.join(os.path.join("result", task_name), "score.json"), "w") as f:
                    #     json.dump({
                    #         "score": score,
                    #         "cooperation": cooperation,
                    #         "efficiency": efficiency,
                    #         "balance": calculate_balance(),
                    #         "use_time": calculate_action_time(),
                    #         "end_reason": "action time out",
                    #         "end_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_time))
                    #     }, f, indent=4)
                    with open(".cache/load_status.cache", "w") as f:
                        json.dump({"status": "end"}, f, indent=4)

                if now_time - start_time > max_time:
                    action_time = calculate_action_time()
                    if action_time == 0:
                        efficiency = 1
                    else:
                        efficiency = max_action_time / action_time
                    if not os.path.exists(os.path.join("result", task_name)):
                        os.mkdir(os.path.join("result", task_name))
                    else:
                        shutil.rmtree(os.path.join("result", task_name))
                        os.mkdir(os.path.join("result", task_name))
                    # with open(os.path.join(os.path.join("result", task_name), "score.json"), "w") as f:
                    #     json.dump({
                    #         "score": score,
                    #         "cooperation": cooperation,
                    #         "efficiency": efficiency,
                    #         "balance": calculate_balance(),
                    #         "use_time": calculate_action_time(),
                    #         "end_reason": "max time out",
                    #         "end_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_time))
                    #     }, f, indent=4)
                    with open(".cache/load_status.cache", "w") as f:
                        json.dump({"status": "end"}, f, indent=4)

            # if now_time - last_time > 5:
            #     name_list = get_player_name()
            #     for name in name_list:
            #         bot.chat(f"/data get entity {name}")
            #         if name not in own_dict.keys():
            #             own_dict[name] = []
            #     last_time = now_time

    # 捕获和处理 Minecraft 服务器发送的系统消息。这是实现玩家物品检测和实时评分的关键机制。
    # 负责处理分数计算和合作度评估
    @On(bot, 'messagestr')
    def handleChat(_, message, messagePosition, jsonMsg, sender, *args):

        global start_time,  cooperation
        if start_time is not None:
            pattern = "(.*) has the following entity data: (.*)"
            match = re.search(pattern, message)
            if match:
                agent_name = match.group(1)
                data_str = match.group(2)
            else:
                agent_name = None
                data_str = None

            if agent_name is not None and data_str is not None:
                # 修复json字符串中的缺失的双引号，有小bug，但是不影响需要的字段
                splits = re.split(r'[\[\]{}]|,\s|:\s', data_str)
                replace_dicts = []
                for split in splits:
                    if split != "":
                        if split.startswith("'") and split.endswith("'"):
                            replace_dicts.append((split, f'{split[1:-1]}'))
                        elif not ((split.startswith('"')) and split.endswith('"')):
                            replace_dicts.append((split, f'"{split}"'))
                start = 0
                for replace_dict in replace_dicts:
                    while True:
                        pos = data_str.find(replace_dict[0], start)
                        if pos == -1:
                            break  # 其实不会发生
                        else:
                            if pos > 0 and data_str[pos - 1] == '"':
                                start = pos + 1
                                continue
                            if pos < len(data_str) - 1 and data_str[pos + 1] == '"':
                                start = pos + 1
                                continue
                            data_str = data_str[:pos] + replace_dict[1] + \
                                data_str[pos + len(replace_dict[0]):]
                            start = pos + len(replace_dict[1])
                            break

                data = json.loads(data_str)

                inventory = data.get("Inventory", [])
                for i, item in enumerate(inventory):
                    count = item.get("Count", 0)
                    # 最后一个不是字母
                    if count[-1].isalpha():
                        count = int(count[:-1])
                    else:
                        count = int(count)

                    name = item.get("id", "")
                    pattern = "minecraft:(.*)"
                    match = re.search(pattern, name)
                    if match:
                        name = match.group(1)
                    else:
                        name = None

                    if name is not None:
                        inventory[i] = {"name": name, "count": count}
