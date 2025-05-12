import json
import random
import re

from model.init_model import init_language_model

breadth_base_instruction = '''
I want you act as a Prompt Creator.
Your goal is to draw inspiration from the #Given Prompt# to create a brand new prompt.
This new prompt should belong to the same domain as the #Given Prompt# but be even more rare.
The LENGTH and complexity of the #Created Prompt# should be similar to that of the #Given Prompt#.
The #Created Prompt# must be reasonable and must be understood and responded by humans.
'#Given Prompt#', '#Created Prompt#', 'given prompt' and 'created prompt' are not allowed to appear in #Created Prompt#
'''

VA_base_instruction = '''
I want you act as a Prompt Creator.
Your goal is to draw inspiration from the #Given Prompt# to create a brand new prompt.
The new prompt shall be coarse-grained task for multi-agent systems, preferably meeting both the simplicity in description and complexity in dependency.
This new prompt do not have to belong to the same domain as the #Given Prompt# but shall remain in the minecraft.
Do note that the x, y, z coordinates shall be restricted in the range: min_x, min_y, min_z = -11, 0, 0; max_x, max_y, max_z = 11, 15, 25
The LENGTH and complexity of the #Created Prompt# should be similar to that of the #Given Prompt#.
The #Created Prompt# must be reasonable and must be understood and responded by humans.
It would be better if the new task involves intense collaborations and division of labor between agents. Meanwhile the task shall not be too difficult or big.
'#Given Prompt#', '#Created Prompt#', 'given prompt' and 'created prompt' are not allowed to appear in #Created Prompt#
'''

VA_Volume_base_instruction = '''
I want you act as a Task Designer.
Your goal is to learn the format from the pairs of #Given Simple Task# and #Given Augmented Task#, and use it to augment the given #Simple Task Input# into #Augmented Task Output#.
This new augmented task should augment or enrich the content of the given simple task by adding: environment infomation and auxilliary information.
The #Augmented Task Output# must be reasonable and must be understood and responded by humans.
'#Given Simple Task#', '#Given Augmented Task#' and '#Simple Task Input#' are not allowed to appear in #Augmented Task Output#
'''

blueprint_base_instruction = '''
I want you to act as an **environment designer in Minecraft**. Your goal is to **create the environment necessary for a given task**, serving as the foundation for agents to complete the task. You will receive a **#Background#**, which provides context for the task. Please do the following: 1. **Identify** which parts of the background describe the **environment** that needs to be built now, and which parts describe the **building(s)** required later by the task (those buildings do **not** need to be built at this stage).
 2. **Design the initial environment** accordingly, making sure it satisfies the specified constraints.
**Constraints**:
 * Coordinate boundaries: `min_x, min_y, min_z = -11, 0, 0` `max_x, max_y, max_z = 11, 15, 25`
 * **Flat ground is at y = -1 (already filled by grass_block)**.
 * Don't forget to surround the water with other blocks if you need to place water blocks (e.g. if there is a river in the setting).
 * Be careful **not** to overwrite already placed blocks.
 * The tools and materials needed for the task shall all be included in the box.
 * Blocks can be placed **individually** or as a **line** or a **rectangle**.
 * The output for the designed environment must follow the **JSON format shown in the #Example#** section.
Please refer to the **#Example#** section for how to format the output as a JSON structure.
'''

all_objs = [
  "**Task: **\r\n - Collaborate to place blocks according to the blueprint `minecraft/templates/nether_fossils_fossil_3`.\r\n - Use the materials from the chest at[-4, 0, 5]. The other chest in the factory with tools is not needed for this task.\r\n",
  "**Task:**  \r\n- Work together to catch at least 10 fish (a mix of cod and salmon) using the fishing rods and bait from the chest.  \r\n- Ensure the caught fish are stored in a second chest placed at [10, 0, 20].",
  "**Task:**  \n- Cooperate to smelt 20 iron ingots using the furnace located at [5, 0, 12].  \n- Retrieve the necessary iron ore from the chest at [5, 0, 10] and fuel (coal) from the chest at [5, 0, 8].  \n- Store the smelted iron ingots in the chest at [5, 0, 14].",
  "**Task:**  \n- Collaborate to construct a small village well using the materials from the chest at [10, 0, 15]. The well should be 3 blocks deep and 5 blocks wide, with a bucket placed inside for decoration.  \n- One agent must gather water from the nearby lake at [8, 0, 20] using empty buckets, while another agent assembles the well structure using the cobblestone and wooden planks provided.  \n- Ensure all unused materials are returned to the chest upon completion.",
  "**Task:**  \n\n- Cooperate to defend the village from a zombie raid by building barricades and equipping weapons.  \n- Use the wood and stone materials from the chest at [5, 0, 15] to construct barriers around the village perimeter.  \n- Equip swords and bows from the armory chest at [7, 0, 18] and distribute them among the agents.  \n- Ensure all villagers are safely inside their houses by interacting with doors to close them.  \n- Eliminate at least 15 zombies before they breach the village defenses.",
  "**Task:**  \n- Collaborate to build a small animal pen near the village at [8, 0, 15].  \n- Gather materials (wooden planks and fences) from the chest at [7, 0, 14] and construct the pen.  \n- Lead at least 3 sheep and 2 cows into the pen using wheat from the chest.  \n- Ensure the animals are safely enclosed and fed before sunset.",
  "**Task:**  \n- Collaborate to bake 30 loaves of bread using the furnace located at [8, 0, 10].  \n- Harvest wheat from the nearby farm at [8, 0, 15] and collect the necessary fuel (charcoal) from the chest at [8, 0, 8].  \n- Store the baked bread in the chest at [8, 0, 12].  \n- Ensure all agents sleep in the beds at [7, 0, 10] and [9, 0, 10] by nighttime to avoid phantoms.  \n\nThis task requires division of labor (farming, fuel collection, baking, and storage) and coordination to meet the time constraint.",
  "**Task:**  \n- Work together to prepare a sustainable food source by creating a small fishing pond and cooking the caught fish.  \n- One agent must dig a 4x4 pond at [3, 0, 20] and fill it with water from the nearby river at [5, 0, 22] using buckets.  \n- Another agent should craft fishing rods using sticks and string from the chest at [3, 0, 18] and start fishing in the pond.  \n- A third agent must collect the caught fish, cook them in the furnace at [3, 0, 22] using coal from the chest, and store the cooked fish in the chest at [3, 0, 16].  \n- Ensure all tools and unused materials are returned to their respective chests after completion.",
  "**Task:**  \n\n- Work together to organize a nighttime fishing competition by the lake at [5, 0, 20].  \n- One agent must craft fishing rods using sticks from the nearby forest and string from spiders (summon 3 spiders if needed).  \n- Another agent should gather food supplies (bread or fish) from the village storage at [10, 0, 10] and set up a campfire near the lake.  \n- A third agent must ensure safety by lighting up the area with torches and keeping hostile mobs away (eliminate any creepers or skeletons that spawn).  \n- The competition begins at nightfall (set time to 18000) and ends after catching at least 10 fish collectively.  \n- All agents must sleep in beds placed near the campfire once the competition is over (set time to sunrise afterward).",
  "**Task:**  \n- Collaborate to build a small bridge across the river located near [0, 0, 5].  \n- Gather the required materials (wooden planks and sticks) from the chest at [5, 0, 2].  \n- Construct the bridge with a width of at least 3 blocks and a length sufficient to span the river.  \n- Place a sign at each end of the bridge with the text \"Safe Crossing\" to mark the path.",
  "**Task:**  \n- Work together to brew 10 potions of healing using the brewing stand located at [3, 0, 20].  \n- Retrieve the necessary nether wart from the chest at [3, 0, 18] and glowstone dust from the chest at [3, 0, 22].  \n- Fill glass bottles with water from the nearby cauldron at [6, 0, 20] before brewing.  \n- Store the finished potions in the chest at [3, 0, 24].  \n\n**Roles:**  \n- One agent must collect water using glass bottles.  \n- Another agent must handle the brewing process by adding nether wart and glowstone dust.  \n- A third agent should organize and store the potions once brewed.  \n- Ensure all unused materials are returned to their respective chests upon completion."
]

action_list = [
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

instruction_actions = "You can use or not to use the following actions to create the multi-agent task. And the actions related to this task can include but not limited to the following actions:\r\n"

concreting_examples = [
    {'simple': "**Task:**\n- Collaborate to place blocks according to the blueprint `minecraft/templates/nether_fossils_fossil_3`.\n- Use the materials from the chest at [-4, 1, 10]. The other chest in the factory with tools is not needed for this task.",
                'augmentation': "**Interactive-Items:**\n- **Oak Sign**: [-3, 3, 10] (facing west)\n\n**Environment:**\n- The area around [-4, 2, 11] includes a structure made of stone bricks, spruce planks, and sandstone. There is a chest and a furnace facing west, and a spruce fence to the east. The ground is primarily dirt and grass blocks.\n- The blueprint provided is for `minecraft/templates/nether_fossils_fossil_3`.\n\n**Task:**\n- Collaborate to place blocks according to the blueprint `minecraft/templates/nether_fossils_fossil_3`.\n- Use the materials from the chest at [-4, 1, 10]. The other chest in the factory with tools is not needed for this task.\nSign info: \nminecraft/templates/nether_fossils_fossil_3"},
    {'simple': "**Task:** \n- Work together to catch at least 10 fish (a mix of cod and salmon) using the fishing rods and bait from the chest. \n- Ensure the caught fish are stored in a second chest placed at [6, 0, 20]. \n- Avoid disturbing a nearby school of tropical fish swimming around [7, 0, 18].",
     'augmentation': "**Environment:** \n- A coastal area at [5, 0, 20] features a small wooden dock made of oak planks and fences, extending into the ocean. A chest containing fishing rods and bait is placed at [5, 0, 21]. The water is populated with cod and salmon. \n\n**Task:** \n- Work together to catch at least 10 fish (a mix of cod and salmon) using the fishing rods and bait from the chest. \n- Ensure the caught fish are stored in a second chest placed at [6, 0, 20]. \n- Avoid disturbing a nearby school of tropical fish swimming around [7, 0, 18]. \n\n**Actions available:** \n- Agents can use fishing rods to catch fish. \n- Agents can move along the dock or swim in designated areas. \n- Agents can transfer caught fish to the storage chest. \n- Agents must avoid scaring away the tropical fish."}
]

example_string = """{
"blocks": [
// Oak plank floor (workspace base)
{"type": "rectangle", "from ": [-1, 0, 11], "to": [1, 0, 13], "name": "oak_planks"},
// Left oak log pillar
{"type": "line", "from ": [-1, 1, 11], "to": [-1, 2, 11], "name": "oak_log"},
// Right oak log pillar
{"type": "line", "from ": [1, 1, 11], "to": [1, 2, 11], "name": "oak_log"},
// Roof over the structure
{"type": "rectangle", "from ": [-1, 3, 11], "to": [1, 3, 13], "name": "oak_planks"},
// Crafting table at center
{"position": [0, 0, 12], "name": "crafting_table"},
// Log pile simulating wood storage
{"type": "rectangle", "from ": [5, 0, 10], "to": [7, 0, 12], "name": "oak_log"},
// Cobweb for making fishing rods
{"position": [7, 0, 8], "name": "cobweb"},
// Path to pond area
{"type": "line", "from ": [0, 0, 15], "to": [0, 0, 20], "name": "oak_planks"},
// Chest with fishing rods
{"position": [-1, 0, 20], "name": "chest", "facing": "north", "items": [{"name": "fishing_rod", "count": 2}]},
// Chest with caught fish
{"position": [1, 0, 20], "name": "chest", "facing": "north", "items": [{"name": "cod", "count": 6}, {"name": "salmon", "count": 4}]}
]
"entities": [
// Fish in the water
{"position": [0, 1, 16], "name": "cod"},
{"position": [1, 1, 17], "name": "salmon"},
{"position": [-1, 1, 18], "name": "cod"}
]
}"""

api_key_list = json.load(open("API_KEY_LIST", "r"))["AGENT_KEY"]
llm_config = {
    "api_key": api_key_list[0],
    "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_model": "qwen-max",
    "api_key_list": api_key_list
}
llm = init_language_model(llm_config)

def createBreadthPrompt(instruction):
    prompt = breadth_base_instruction
    prompt += "#Given Prompt#: \r\n {} \r\n".format(instruction)
    prompt += "#Created Prompt#:\r\n"
    return prompt

def createVABreadthPrompt(instruction):
    # randomly select 3 actions from action_list
    selected_actions = random.sample(action_list, 3)
    # create the action string
    action_string = ""
    for action in selected_actions:
        action_string += "- " + action + "\r\n"
    prompt = VA_base_instruction
    prompt += instruction_actions + action_string
    prompt += "#Given Prompt#: \r\n {}".format(
        instruction)
    # prompt += "No blueprints in your generated task\r\n"
    prompt += "#Created Prompt#:\r\n"
    return prompt

def createVAVolumePrompt(input):
    prompt = VA_Volume_base_instruction
    for example in input['examples']:
        simple = example['simple']
        augmentation = example['augmentation']
        prompt += "#Given Simple Task#: \r\n {} \r\n".format(simple)
        prompt += "#Given Augmented Task#: \r\n {} \r\n".format(augmentation)
    # prompt += "#Given Simple Task#: \r\n {}".format(
    #     instruction)
    # prompt += "#Given Augmented Task#: \r\n{}".format(
    #     instruction)
    prompt += "#Simple Task Input#: \r\n{}\r\n".format(
        input['input'])
    # prompt += "No blueprints in your generated task\r\n"
    prompt += "#Augmented Task Output#: \r\n"
    return prompt

def createBlueprintPrompt(background, example=example_string):
    prompt = blueprint_base_instruction
    # prompt = large_scale_instruction
    prompt += "#Example#: \r\n {}".format(
        example)
    prompt += "#Background#: \r\n {}".format(
        background)
    # prompt += "#To-Build#: \r\n {}".format(
    #     to_build)
    # prompt += "No blueprints in your generated task\r\n"
    prompt += "Do NOT include anything other than a json object in your output. And do not format the json object, we just need a string representing a json object. You can insert comments.\r\n"
    prompt += "#Designed Building#:\r\n"
    return prompt

def extract_outermost_braces_content(text):
    """
    提取第一个最外层的完整 {...} 内容，确保括号正确匹配
    返回提取到的内容字符串，或 None（如果未找到）
    """
    start_index = text.find('{')
    if start_index == -1:
        return None
    
    brace_depth = 1
    current_index = start_index + 1
    
    while current_index < len(text) and brace_depth > 0:
        char = text[current_index]
        if char == '{':
            brace_depth += 1
        elif char == '}':
            brace_depth -= 1
        current_index += 1
    
    if brace_depth == 0:
        return text[start_index:current_index]
    else:
        return None  # 括号不匹配

def remove_json_comments(json_str):
    """移除JSON字符串中的注释（//开头或行内）"""
    lines = []
    for line in json_str.split('\n'):
        # 移除整行注释
        stripped = line.strip()
        if stripped.startswith('//'):
            continue
        # 移除行内注释
        line = re.sub(r'//.*', '', line)
        lines.append(line)
    return '\n'.join(lines)

def save_dict_from_string(raw_str, filename):
    # 1. 提取最外层 {...} 内容
    json_block = extract_outermost_braces_content(raw_str)
    if not json_block:
        print("错误：未找到完整的花括号内容块")
        return False
    
    # 2. 移除注释
    clean_json_str = remove_json_comments(json_block)
    
    # 3. 解析为字典
    try:
        data_dict = json.loads(clean_json_str)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print("有问题的JSON内容:")
        print(clean_json_str)
        return False
    
    # 4. 保存到文件
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=4, ensure_ascii=False)
        print(f"成功保存到 {filename}")
        return True
    except Exception as e:
        print(f"文件保存失败: {e}")
        return False

def gen_task(times = 1):
    evol_objs = []

    for i in range(times):
        evol_prompts = []
        # choose 2 samples from the data
        samples = random.sample(all_objs, 2)
        format_str = "Example 1: {}\n Example 2: {}\n"
        cur_obj = format_str.format(
            samples[0], samples[1])
        instruction = cur_obj

        evol_prompts.append(createVABreadthPrompt(instruction))

        # print("evol_prompts:", evol_prompts)

        selected_evol_prompt = random.choice(evol_prompts)

        evol_instruction = llm.few_shot_generate_thoughts(system_prompt="You are a helpful assistant", example_prompt=selected_evol_prompt)
        evol_objs.append({"instruction": evol_instruction})

    return evol_objs

def concreting_task(task_list):
    evol_objs = []

    prompt = {"examples": concreting_examples, "input": ""}

    for cur_obj in task_list:
        instruction = cur_obj['instruction'].strip()
        prompt["input"] = instruction
        evol_prompts = createVAVolumePrompt(prompt)
        selected_evol_prompt = evol_prompts
        evol_instruction = llm.few_shot_generate_thoughts(system_prompt="You are a helpful assistant", example_prompt=selected_evol_prompt)
        evol_objs.append({"instruction": evol_instruction})
    
    return evol_objs

def create_blueprint(concreted_task, times = 1):
    blueprint_prompt = []
    for i in range(times):
        cur_obj = random.choice(concreted_task)
        instruction = cur_obj["instruction"]
        blueprint_prompt.append(createBlueprintPrompt(instruction))
        selected_evol_prompt = blueprint_prompt[-1]
        evol_instruction = llm.few_shot_generate_thoughts(system_prompt="You are a helpful assistant", example_prompt=selected_evol_prompt)
        #TODO: blueprints.json之后应该调整成类似config.json那样的，包含给judger生成环境的信息和给TM任务描述的信息
        save_dict_from_string(evol_instruction, 'blueprints.json')


if __name__ == "__main__":
    task = gen_task(1)
    concreted_task = concreting_task(task)
    create_blueprint(concreted_task, 1)