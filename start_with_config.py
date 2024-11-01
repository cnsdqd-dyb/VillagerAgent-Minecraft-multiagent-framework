import multiprocessing
import os
import shutil
import random
import psutil

import time
from env.env import VillagerBench, env_type, Agent

start_time = time.time()
from pipeline.controller_tiny import GlobalController
from pipeline.data_manager import DataManager
from pipeline.task_manager import TaskManager
import json

print(f"pipeline Time taken: {time.time() - start_time}")
start_time = time.time()


def run(api_model: str, api_base: str, task_type: str, task_idx: int, agent_num: int, dig_needed: bool, max_task_num: int, task_goal: str, document_file: str, host: str, port: int, task_name: str, role: str = "same"):
    start_time = time.time()

    # 设置agent，都使用gpt-4-0125-preview
    Agent.model = "gpt-4-1106-preview"
    # Agent.model = "gpt-3.5-turbo-1106"
    # Agent.base_url = "https://api.openai.com/v1/"
    Agent.base_url = "https://api.chatanywhere.tech/v1"
    Agent.api_key_list = json.load(open("API_KEY_LIST", "r"))["AGENT_KEY"]

    # 设置env
    if task_type == "construction":
        env = VillagerBench(env_type=env_type.construction, task_id=task_idx, dig_needed=dig_needed, host=host, port=port, max_task_num=max_task_num, task_name=task_name, _virtual_debug=False)
    elif task_type == "farming":
        env = VillagerBench(env_type=env_type.farming, task_id=task_idx, dig_needed=False, host=host, port=port, max_task_num=max_task_num, task_name=task_name, _virtual_debug=False)
    elif task_type == "puzzle":
        env = VillagerBench(env_type=env_type.puzzle, task_id=task_idx, dig_needed=False, host=host, port=port, max_task_num=max_task_num, task_name=task_name, _virtual_debug=False)
    elif task_type == "meta":
        env = VillagerBench(env_type=env_type.meta, task_id=task_idx, dig_needed=False, host=host, port=port, max_task_num=max_task_num, task_name=task_name, _virtual_debug=False)
    else:
        raise NotImplementedError

    # 设置agent_tool
    if task_type == "construction":
        agent_tool = [Agent.placeBlock, Agent.fetchContainerContents, Agent.MineBlock, Agent.scanNearbyEntities, Agent.equipItem,
                      Agent.navigateTo, Agent.withdrawItem, Agent.dismantleDirtLadder, Agent.erectDirtLadder, Agent.handoverBlock]
    elif task_type == "farming":
        agent_tool = [Agent.fetchContainerContents, Agent.MineBlock, Agent.scanNearbyEntities, Agent.equipItem, Agent.SmeltingCooking,
                      Agent.navigateTo, Agent.withdrawItem, Agent.craftBlock, Agent.attackTarget, Agent.UseItemOnEntity,
                      Agent.handoverBlock]
    elif task_type == "puzzle":
        agent_tool = [Agent.placeBlock, Agent.fetchContainerContents, Agent.MineBlock, Agent.scanNearbyEntities, Agent.equipItem,
                      Agent.navigateTo, Agent.withdrawItem, Agent.ToggleAction, Agent.handoverBlock]
    elif task_type == "meta":
        agent_tool = [Agent.scanNearbyEntities, Agent.navigateTo, Agent.attackTarget, Agent.UseItemOnEntity, Agent.sleep, Agent.wake, 
                      Agent.MineBlock, Agent.placeBlock, Agent.equipItem, Agent.handoverBlock, Agent.SmeltingCooking, Agent.withdrawItem, 
                      Agent.storeItem, Agent.craftBlock, Agent.enchantItem, Agent.trade, Agent.repairItem, Agent.eat, Agent.fetchContainerContents, Agent.ToggleAction]
    else:
        raise NotImplementedError

    print(f"VillagerBench Time taken: {time.time() - start_time}")
    start_time = time.time()

    # 设置agent_pool
    name_list = ["Alice", "Bob", "Cindy", "David", "Eve", "Frank", "Grace", "Helen", "Ivy", "Jack", "Kevin", "Lily",
                 "Mary", "Nancy", "Olivia", "Peter", "Queen", "Rose", "Sam", "Tom", "Umbrella", "Vivian", "Wendy",
                 "Xavier", "Yolanda", "Zoe"]
    if agent_num == 3 and task_type == "farming" and role == "different":
        agent_tool = [Agent.fetchContainerContents, Agent.scanNearbyEntities, Agent.equipItem,
                      Agent.navigateTo, Agent.withdrawItem, Agent.craftBlock, Agent.SmeltingCooking,
                      Agent.handoverBlock]
        env.agent_register(agent_tool=agent_tool, agent_number=1, name_list=[name_list[0]])
        agent_tool = [Agent.fetchContainerContents, Agent.scanNearbyEntities, Agent.equipItem,
                      Agent.navigateTo, Agent.withdrawItem, Agent.craftBlock, Agent.MineBlock,
                      Agent.handoverBlock]
        env.agent_register(agent_tool=agent_tool, agent_number=1, name_list=[name_list[1]])
        agent_tool = [Agent.fetchContainerContents, Agent.scanNearbyEntities, Agent.equipItem,
                      Agent.navigateTo, Agent.withdrawItem, Agent.craftBlock, Agent.attackTarget, 
                      Agent.handoverBlock]
        env.agent_register(agent_tool=agent_tool, agent_number=1, name_list=[name_list[2]])
    else:
        env.agent_register(agent_tool=agent_tool, agent_number=agent_num, name_list=name_list[:agent_num])

    with env.run(fast_api=False):  # 新增加了一个参数，用于控制是否使用fastapi server
        # 启动DM
        dm = DataManager(silent=False)
        dm.update_database_init(env.get_init_state())

        print(f"DataManager Time taken: {time.time() - start_time}")
        start_time = time.time()

        # 启动TM
        tm = TaskManager(silent=False)

        print(f"TaskManager Time taken: {time.time() - start_time}")
        start_time = time.time()

        # 设置llm
        if "gpt" in api_model:  # https://api.chatanywhere.tech/v1 default_base_url
            api_key_list = json.load(open("API_KEY_LIST", "r"))["AGENT_KEY"]

            llm_config = {
                "api_model": api_model,
                # "api_base": "https://api.openai.com/v1/",
                "api_base": "https://api.chatanywhere.tech/v1",
                "api_key_list": api_key_list
            }
        elif "gemini" in api_model:
            api_key_list = json.load(open("API_KEY_LIST", "r"))["GEMINI"]
            os.environ["GOOGLE_API_KEY"] = random.choice(api_key_list)

            llm_config = {
                "api_model": api_model,
                "api_key_list": api_key_list
            }
        elif "glm" in api_model:
            api_key_list = json.load(open("API_KEY_LIST", "r"))["GLM"]
            os.environ["ZHIPU_API_KEY"] = random.choice(api_key_list)

            llm_config = {
                "api_model": api_model,
                "api_key_list": api_key_list
            }
        ctrl = GlobalController(llm_config, tm, dm, env)

        document = json.load((open(document_file))) if os.path.exists(document_file) else {}
        tm.init_task(description=task_goal, document=document)

        ctrl.run()

        env.get_score()


if __name__ == "__main__":

    with open("meta_test_config.json", "r") as f:
        launch_config = json.load(f)
    for i, config in enumerate(launch_config):

        if os.path.exists(f"result/{config['task_name']}"):
            print(f"task {config['task_name']} exists")
            continue
        print(f"task {i} start")
        print("config:", config)

        with open(".cache/load_status.cache", "w") as f:
            json.dump({"status": "start"}, f, indent=4)
        if os.path.exists(".cache/heart_beat.cache"):
            os.remove(".cache/heart_beat.cache")

        process = multiprocessing.Process(target=run,
                                            args=(config["api_model"],
                                                config["api_base"],
                                                config["task_type"],
                                                config["task_idx"],
                                                config["agent_num"],
                                                config.get("dig_needed", False),
                                                config.get("max_task_num", 0),
                                                config["task_goal"],
                                                config.get("document_file", ""),
                                                config["host"],
                                                config["port"],
                                                config["task_name"],
                                                config.get("role", "same")
                                            )
                                          )
        process.start()

        parent = psutil.Process(process.pid)

        while True:
            time.sleep(1)
            try:
                with open(".cache/load_status.cache", "r") as f:
                    status = json.load(f)["status"]
                if status == "end":
                    for child in parent.children(recursive=True):
                        child.kill()
                    parent.kill()
                    shutil.move("data/action_log.json",
                                os.path.join(os.path.join("result", config["task_name"]), "action_log.json"))
                    shutil.move("data/tokens.json",
                                os.path.join(os.path.join("result", config["task_name"]), "tokens.json"))
                    break
                if os.path.exists(".cache/heart_beat.cache"):
                    with open(".cache/heart_beat.cache", "r") as f:
                        env_time = json.load(f)["time"]
                        if time.time() - env_time > 60:
                            print("env error")
                            # pipeline test log save
                            if os.path.exists(".cache"):
                                if os.path.exists(f".cache/pipeline_test_logs.json"):
                                    with open(f".cache/pipeline_test_logs.json", "r") as f:
                                        logs = json.load(f)
                                else:
                                    logs = []
                                logs.append({
                                    "task_name": config["task_name"],
                                    "time": time.time(),
                                    "exception": "env error"
                                })
                                with open(f".cache/pipeline_test_logs.json", "w") as f:
                                    json.dump(logs, f, indent=4)
                            for child in parent.children(recursive=True):
                                child.kill()
                            parent.kill()
                            break
            except:
                pass

        print(f"task {i} end")
