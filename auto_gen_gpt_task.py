from pipeline.utils import format_string, extract_info
from env.env import VillagerBench, env_type, Agent
from pipeline.controller import GlobalController
from pipeline.data_manager import DataManager
from pipeline.task_manager import TaskManager
import json
from model.init_model import init_language_model
import random
import os
import torch
from datetime import datetime
from rl_env.minecraft_ppo import PPO
from rl_env.minecraft_rl_env import MinecraftRLEnv
import re

def convert_sign_command(command):
    # 匹配两种可能的格式
    pattern = r'/setblock\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(\w+)\[facing=(\w+)\]{Text1:[\'\"]?(.*?)[\'\"]?,\s*Text2:[\'\"]?(.*?)[\'\"]?}'
    
    match = re.match(pattern, command)
    if match:
        x, y, z, block, facing, text1, text2 = match.groups()
        
        # 移除可能存在的引号并清理空格
        text1 = text1.strip('\'"').strip()
        text2 = text2.strip('\'"').strip()
        
        # 构造新的命令格式
        new_command = f'/setblock {x} {y} {z} {block}[facing={facing}]{{Text1:"{{\"text\":\"{text1}\"}}",Text2:"{{\"text\":\"{text2}\"}}"}}'
        return new_command
    else:
        return "Sign Command format not recognized"

def save_task_to_json(task_description, task_milestones, agents, agent_tool_dict, op_command, op_filepath):
    # 创建完整的任务数据结构
    task_data = {
        "task_description": task_description,
        "task_milestones": task_milestones,
        "agents": agents,
        "agent_tool_dict": agent_tool_dict,
        "op_command": op_command,
        "op_filepath": op_filepath,
        "timestamp": datetime.now().strftime("%Y%m%d%H%M%S")
    }
    
    # 创建保存路径
    task_filename = f"{task_data['timestamp']}_task.json"
    task_filepath = os.path.join("rl_env/tasks", task_filename)
    os.makedirs(os.path.dirname(task_filepath), exist_ok=True)
    
    # 保存任务数据
    with open(task_filepath, 'w') as task_file:
        json.dump(task_data, task_file, indent=4)
    
    return task_filepath

def load_random_task():
    # 获取任务文件夹中的所有任务文件
    task_dir = "rl_env/tasks"
    if not os.path.exists(task_dir):
        return None
    
    task_files = [f for f in os.listdir(task_dir) if f.endswith('_task.json')]
    if not task_files:
        return None
    
    # 随机选择一个任务文件
    selected_file = random.choice(task_files)
    task_filepath = os.path.join(task_dir, selected_file)
    
    # 加载任务数据
    with open(task_filepath, 'r') as task_file:
        task_data = json.load(task_file)
    
    return task_data


def auto_gen_one_task(use_existing_task=False):
    # Set Environment
    # env = VillagerBench(env_type.auto, task_id=0, _virtual_debug=False, dig_needed=False, host="10.214.180.148", task_name="auto_gen")
    env = VillagerBench(env_type.auto, task_id=0, _virtual_debug=False, dig_needed=False, host="10.192.24.163", task_name="auto_gen")

    # Set Agent
    # api_key_list = ["sk-villageragent"]
    # base_url = "http://10.130.130.13:8000/v1"
    # llm_config = {
    #     "api_base": base_url,
    #     "api_model": "llama_gptq4",
    #     "api_key": "sk-villageragent",

    # }
    # Agent.model = f'{llm_config["api_model"]}/'
    # Agent.base_url = base_url
    # Agent.api_key_list = api_key_list

    api_key_list = json.load(open("API_KEY_LIST", "r"))["AGENT_KEY"]
    base_url = "https://api.chatanywhere.tech/v1"
    llm_config = {
        "api_base": base_url,
        "api_model": "gpt-4-1106-preview",
        "api_key_list": api_key_list,

    }
    Agent.model = "gpt-4-1106-preview"
    Agent.base_url = base_url
    Agent.api_key_list = api_key_list
    
    rl_env = MinecraftRLEnv(
        max_instruction_length = 128,
        max_state_length = 256,
        max_history_length = 512,
    )
    
    rl_model = PPO(
        hidden_dim = 256,
        action_dim = rl_env.action_dim,
        actor_lr = 1e-4,
        critic_lr = 1e-4,
        gamma = 0.99,
        lmbda = 0.95,
        eps = 0.2,
        device = "cuda" if torch.cuda.is_available() else "cpu",
        buffer_size = 10000
    )
    
    if use_existing_task:
        # 尝试加载现有任务
        task_data = load_random_task()
        if task_data:
            task_description = task_data["task_description"]
            task_milestones = task_data["task_milestones"]
            op_command = task_data["op_command"]
            op_filepath = task_data["op_filepath"]
            task_description_str = str(task_description)
            task_description = {"milestones": task_milestones, "agents": task_data["agents"]}
            agent_tool_dict = task_data["agent_tool_dict"]

            agent_tool = [Agent.MineBlock, Agent.placeBlock, Agent.scanNearbyEntities, Agent.get_entity_info, Agent.read,
                        Agent.navigateTo, Agent.withdrawItem, Agent.craftBlock, Agent.fetchContainerContents]
            
            basic_tools = [
                Agent.scanNearbyEntities, Agent.navigateTo, Agent.attackTarget,
                Agent.useItemOnEntity,
                Agent.MineBlock, Agent.placeBlock, Agent.equipItem,
                Agent.handoverBlock, Agent.SmeltingCooking, Agent.talkTo, Agent.waitForFeedback,
                Agent.withdrawItem, Agent.storeItem, Agent.craftBlock,Agent.ToggleAction, 
                Agent.sleep, Agent.wake, Agent.tossItem, Agent.read,
                Agent.get_entity_info, Agent.get_environment_info, Agent.performMovement,
                Agent.lookAt, Agent.startFishing, Agent.stopFishing, Agent.mountEntity, Agent.dismountEntity
            ]
            if type(agent_tool_dict) == list:
                agent_tool_dict = {"agent_tool": agent_tool_dict}
            for tool_name in agent_tool_dict["agent_tool"]:
                for t in basic_tools:
                    if t.name == tool_name:
                        agent_tool.append(t)

            env.op_path = op_filepath

            print("Using existing task from:", task_data["timestamp"])
        else:
            print("No existing tasks found, generating new task...")
            use_existing_task = False
    
    if not use_existing_task:

        # more agent tools can be added here you can refer to the agent_tool in doc/api_library.md
        basic_tools = [
            Agent.scanNearbyEntities, Agent.navigateTo, Agent.attackTarget,
            Agent.useItemOnEntity,
            Agent.MineBlock, Agent.placeBlock, Agent.equipItem,
            Agent.handoverBlock, Agent.SmeltingCooking, Agent.talkTo, Agent.waitForFeedback,
            Agent.withdrawItem, Agent.storeItem, Agent.craftBlock,Agent.ToggleAction, 
            Agent.sleep, Agent.wake, Agent.tossItem, Agent.read,
            Agent.get_entity_info, Agent.get_environment_info, Agent.performMovement,
            Agent.lookAt, Agent.startFishing, Agent.stopFishing, Agent.mountEntity, Agent.dismountEntity
        ]
    
        llm = init_language_model(llm_config)

        # Define lists of actions, materials, entities, etc.
        actions = [
            "Agent can talk with other agents, you need to specify the agent name and the topic.",
            "Agent can move to a specific location, you need to specify the location near 0, -60, 0.",
            "Agent can equip items, you need to specify the item name and the agent name, or put the item in the chest and remind the agent to equip it.",
            "Agent can craft items, you need to specify the item name and give materials to the agent or put the item in the chest or set the item in the environment.",
            "Agent can interact with doors, buttons, levers, pressure plates, and trapdoors. You need to set them and let the agent interact with them.",
            "Agent can attack entities, haunt entities, or kill entities. You need to summon entities in the environment.",
            "Agent can dig the ground, you need to set the block and give the agent a tool.",
            "Agent can read the signs, you need to write the text on the sign.",
            "Agent can feed animals, mount the horse.",
            "Agent can use chest, furnace, you can ask the agent to store items, withdraw items, or smelting items, cooking food, but you need to set the chest, furnace, and required items.",
            "Agent can sleep and wake up, please set the bed and the time.",
            "Agent can fish, you need to set the water and the fish and the fishing rod.",
            "Agent can get the information of the entities or agents, you can ask the agent to get the information of the entities or agents.",
            "Agent can perform movement, you can ask the agent to jump forward back left right for Seconds.",
        ]

        materials = ["wooden", "stone", "iron", "golden", "diamond", "netherite"]
        agents = ["Alice", "Bob"]
        entities = ["zombie", "skeleton", "sheep", "cow", "rabbit", "pig", "chicken", "creeper", "spider", "enderman"]
        equipments = ["helmet", "chestplate", "leggings", "boots"]
        food = ["mutton", "beef", "rabbit", "porkchop", "chicken", "potato", "cod", "salmon", "wheat_seeds", "melon_seeds", "pumpkin_seeds", "beetroot_seeds"]
        other_food = ["apple", "golden_apple", "carrot", "beetroot", "bread", "cookie", "baked_potato", "pumpkin_pie", "beetroot_soup", "rabbit_stew", "mushroom_stew"]
        tools = ["axe", "pickaxe", "shovel", "hoe", "sword", "flint_and_steel", "compass", "shears", "fishing_rod", "clock"]

        # Randomly select a subset of actions
        selected_actions = random.sample(actions, k=2)

        # Generate prompt with random actions
        prompt_task_description = format_string("""
        Generate a task description for the agent to complete in the Minecraft environment.
        [TASK Action]:
        {{selected_actions}}
        Agent can not trade or talk with villagers.
        Agent can be given materials, foods, tools, for finish the task.
        The task should only focus on 1~2 [TASK Action], the task should be simple and clear.                              
        The common materials, entities, equipments, food, and tools names:
        materials: {{materials}}
        agents: {{agents}}
        entities: {{entities}}
        equipments: {{equipments}}
        food: {{food}}
        other_food: {{other_food}}
        tools: {{tools}}
        You need to design a task description that includes 1~2 of the above actions for agents to complete.
        return in json format.
        {
            "main_actions": [...], a list of main actions designed for agents to complete in the Minecraft environment (no more than 5).
            "agents": [...], a list of agents in the environment.
            "task_description": str, "The task description designed for each agent to complete in the Minecraft environment."
            "entities": [...], a list of entities in the environment.
            "materials": [...], a list of materials in the environment.
            "equipments": [...], a list of equipments in the environment.
            "tools": [...], a list of tools in the environment.
            "environment": str, "rainy, sunny, snowy, desert, etc."
            "milestones": [...], a list of milestones designed for agents to complete in the Minecraft environment.
        }
        """, {
            "selected_actions": ', '.join(selected_actions),
            "materials": materials,
            "agents": agents,
            "entities": entities,
            "equipments": equipments,
            "food": food,
            "other_food": other_food,
            "tools": tools
        })

        # Use LLM to generate task description
        task_description = llm.few_shot_generate_thoughts("", prompt_task_description, cache_enabled=True, json_check=True, temperature=0.3)
        task_description = extract_info(task_description)[0]
        task_description["environment"] = random.choice(["rainy", "sunny", "snowy", "desert", "savanna", "taiga", "plains", "stormy"])
        task_description_str = str(task_description["task_description"])
        print(task_description)
        # input()

        # Use LLM to select the agent tool
        prompt_agent_tool = """
        Select the agent tool for the agent to complete the task in the Minecraft environment. The agent basic tools are:
        attackTarget, useItemOnEntity, equipItem, handoverBlock, SmeltingCooking, 
        talkTo, waitForFeedback, storeItem, ToggleAction,
        sleep, wake, tossItem, read, get_entity_info, get_environment_info, performMovement,
        startFishing, stopFishing, mountEntity, dismountEntity.

        Current Task Description is:
        {{TASK_JSON}}
        Only select the agent tools that are necessary for the agent to complete the task.
        return in json format.
        {
            "agent_tool": [...], a list of agent tools selected for the agent to complete the task in the Minecraft environment.
        }
        """
        prompt_agent_tool = format_string(prompt_agent_tool, {"TASK_JSON": task_description})
        response = llm.few_shot_generate_thoughts("", prompt_agent_tool, cache_enabled=True, json_check=True, check_tags=["agent_tool"])
        agent_tool_dict = extract_info(response)[0]
        print(agent_tool_dict)
        agent_tool = [Agent.MineBlock, Agent.placeBlock, Agent.scanNearbyEntities, Agent.get_entity_info, Agent.read,
                    Agent.navigateTo, Agent.withdrawItem, Agent.craftBlock, Agent.fetchContainerContents]
        if type(agent_tool_dict) == list:
            agent_tool_dict = {"agent_tool": agent_tool_dict}
        for tool_name in agent_tool_dict["agent_tool"]:
            for t in basic_tools:
                if t.name == tool_name:
                    agent_tool.append(t)

        # Use LLM to generate OP command
        prompt_op_command = """
        Generate a OP command for the agent to complete in the Minecraft environment. The OP command should be designed in various styles.

        1. set the environ_op:
        /time set day/night
        /weather clear/rain/thunder

        2. set the place_op:
        "prefix": ["desert_","plains_","savanna_","snowy_","taiga_"],
        "houses": ["animal_pen", "butcher_shop", "cartographer_house", "butcher_shop", "farm", "fletcher_house", "library", "shepherd_house", "small_house", "weaponsmith", "medium_house"],
        /place template prefix+houses

        3. summon entities_op:
        /summon name int int int

        4. set the blocks_op:
        /setblock int int int chest{Items:[{Slot:int, id:"minecraft:name", Count:int}, {Slot:int, id:"minecraft:name", Count:int}]}
        write text on the sign in the environment:
        /setblock int int int jungle_wall_sign[facing=north]{Text1:str, Text2:str}
        
        5. set the inventory_op:
        /give agent_name minecraft:name{Count:int}

        6. set optional materials_op:
        give logs, planks, cobblestone, iron_ore etc. to the environment:
        remember some names are combined with type_name format like: oak_log, oak_planks, cobblestone.
        At least 10 materials, furnaces, chests, crafting tables, beds, doors, buttons, levers, pressure plates, trapdoors, etc.
        /setblock int -60 int minecraft:name
        
        make the environment more interesting:
        flowers, grass, remember some names are combined with type_name format like: dandelion, poppy, grass_block, water.
        /setblock int -60 int minecraft:name
        At least 6 fishes need to be in the water:
        cod, salmon, pufferfish, tropical_fish.
        water should be placed in the environment for at least 6 blocks y=-61.
        /setblock int -61 int minecraft:water
        the animals need to be in the grass:
        sheep, cow, rabbit, pig, chicken.

        Remember: equippent should named in material_toolname format like: iron_sword.

        You need to generate OP according to the task json generated by the LLM.
        The task json:
        {{TASK_JSON}}
        remember the center of the environment is (0, -60, 0). 
        The environment size is 15*10*15.
        houses are placed in the center 5*10*5 area.
        materials, chest and agents should be placed in x,z in -15~-5 or 5~15.
        return in json format.
        {
            "environ_op":["/..."], a list of OP for set the environment.
            "place_op": str, place template house OP.
            "entities_op":["/..."], a list of OP to summon the entites.
            "blocks_op":["/..."], a list of OP to set the useful blocks and signs.
            "inventory_op":["/..."], a list of OP to add useful materials to agents or chests.
            "materials_op":["/..."], At least 10 materials, At least 6 water blocks, At least 6 fishes, At least 5 animals.
        }
        """
        op_prompt = format_string(prompt_op_command, {"TASK_JSON": task_description})
        # /setblock x y z jungle_wall_sign[facing=north]{{Text1:\"{{\\\"text\\\":\\\"{Text you want to write 1.}\\\"}}\",Text2:\"{{\\\"text\\\":\\\"{Text you want to write 2.}\\\"}}\"}}
        response = llm.few_shot_generate_thoughts("", op_prompt, cache_enabled=True, json_check=True)
        op_command = extract_info(response)[0]
        # input()

        for i, op in enumerate(op_command["blocks_op"]):
            if "Text1" in op:
                op_command["blocks_op"][i] = convert_sign_command(op)
        print(op_command)
        # Save OP to JSON
        op_filename = datetime.now().strftime("%Y%m%d%H%M%S_op.json")
        op_filepath = os.path.join("auto_task/op_commands", op_filename)
        os.makedirs(os.path.dirname(op_filepath), exist_ok=True)
        with open(op_filepath, 'w') as op_file:
            json.dump(op_command, op_file, indent=4)
        
        env.op_path = op_filepath
        print(f"OP commands saved to {op_filepath}")
        # input()

        task_filepath = save_task_to_json(task_description_str, task_description["milestones"], task_description["agents"], agent_tool_dict, op_command, op_filepath)
        print(f"New task saved to {task_filepath}")


    # Register Agent
    env.agent_register(agent_tool=agent_tool, agent_number=len(task_description["agents"]), name_list=task_description["agents"]) # Attention that the agent number should be consistent with the agent_tool

    # Run Environment
    with env.run():
        
        # Set Data Manager
        dm = DataManager(silent=False)
        dm.update_database_init(env.get_init_state())

        # Set Task Manager
        tm = TaskManager(silent=False)

        # Set Controller
        ctrl = GlobalController(llm_config, tm, dm, env
                                , RL_mode="PPO"
                                , rl_env=rl_env
                                , rl_model=rl_model)

        ctrl.set_stop_condition(max_execution_time=2400, stop_after_fail_times=2, stop_after_success_times=3)

        # Set Task
        tm.init_task(task_description_str, {"milestones": task_description["milestones"]})

        # Run Controller
        ctrl.run()
    
    rl_model.save_ckpt(actor_path="rl_env/ckpt/actor.pth", critic_path="rl_env/ckpt/critic.pth")

if __name__ == "__main__":
    # 随机决定是否使用现有任务
    use_existing = random.choice([True, True, True, False])
    auto_gen_one_task(use_existing_task=use_existing)