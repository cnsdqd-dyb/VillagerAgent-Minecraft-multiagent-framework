import json
import random
import re

from model.init_model import init_language_model
import argparse
from llm_gen_prompt import *
from pipeline.utils import format_string

parser = argparse.ArgumentParser()
parser.add_argument("--api_model", type=str, default="qwen-max", help="api model")
parser.add_argument('--host', type=str, default="127.0.0.1", help='the host of the server')
parser.add_argument("--port", type=int, default=25565, help="the port of the server")
parser.add_argument('--agent_num', type=int, default=2, help='how many agents in the task')
args = parser.parse_args()

with open("data/gen_example.json", "r") as f:
    example = json.load(f)
    all_objs = example["all_objs"]
    action_list = example["action_list"]
    concreting_examples = example["concreting_examples"]

api_key_list = json.load(open("API_KEY_LIST", "r"))["AGENT_KEY"]
llm_config = {
    "api_key": api_key_list[0],
    "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_model": "qwen3-235b-a22b",
    "api_key_list": api_key_list
}
llm = init_language_model(llm_config)

def createVABreadthPrompt(instruction):
    # randomly select 3 actions from action_list
    selected_actions = random.sample(action_list, 3)
    # create the action string
    action_string = ""
    for action in selected_actions:
        action_string += "- " + action + "\r\n"
    prompt = format_string(VA_base_instruction, {"agent_num": args.agent_num})
    prompt += instruction_actions + action_string
    prompt += "#Given Task#: \r\n {}".format(instruction)
    # prompt += "No blueprints in your generated task\r\n"
    prompt += "#Created Task#:\r\n"
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
    prompt += "#Simple Task Input#: \r\n{}\r\n".format(input['input'])
    # prompt += "No blueprints in your generated task\r\n"
    prompt += "#Augmented Task Output#: \r\n"
    return prompt

def createBlueprintPrompt(background, example=example_string):
    prompt = blueprint_base_instruction
    # prompt = large_scale_instruction
    prompt += "#Example#: \r\n {}".format(example)
    prompt += "#Task#: \r\n {}".format(background)
    # prompt += "#To-Build#: \r\n {}".format(
    #     to_build)
    # prompt += "No blueprints in your generated task\r\n"
    prompt += "Do not include anything other than a JSON object in your output. You may insert comments if needed.\r\n"
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

def str2dict(raw_str, filename):
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
        return data_dict
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print("有问题的JSON内容:")
        print(clean_json_str)
        return False

def clean_env_dict(data:dict, task_description):
    # 规范blueprint里block和entity的生成
    # return block, entity
    blocks = data.get("blocks", [])
    entities = data.get("entities", [])

    with open("data/items.json", "r") as f:
        item_list = json.load(f)
    item_name_list = [item["name"] for item in item_list]

    cleaned_block = []
    cleaned_entity = []

    tree_list = ["acacia", "birch", "spruce", "oak", "jungle", "dark_oak", "mangrove"]
    tree_weight = [5, 30, 5, 50, 4, 3, 3]
    color_list = ["black", "blue", "brown", "cyan", "gray", "green", "light_blue", "light_gray", "lime", "magenta", "orange", "pink", "purple", "red", "white", "yellow"]

    color = random.choice(color_list)
    wooden_material = random.choices(tree_list, tree_weight)[0]
    
            
    for block in blocks:

        if any(item in block["name"] for item in ["door", "bed", "sign"]):
            block["type"] = "single"

        if "planks" in block["name"] and all(block["name"] != f"{material}_planks" for material in tree_list):
            block["name"] = wooden_material + "_planks"
        if "wool" in block["name"] and all(block["name"] != f"{temp_color}_wool" for temp_color in color_list):
            block["name"] = color + "_wool"

        if "fence_gate" in block["name"] and all(block["name"] != f"{material}_fence_gate" for material in tree_list):
            block["name"] = wooden_material + "_fence_gate"
        elif "fence" in block["name"] and all(block["name"] != f"{material}_fence" for material in tree_list):
            block["name"] = wooden_material + "_fence"

        if "door" in block["name"]:
            if all(block["name"] != f"{material}_door" for material in tree_list):
                block["name"] = wooden_material + "_door"
            block["half"] = "lower"
            if "facing" not in block:
                block["facing"] = random.choice(["east", "west", "north", "south"])
            
            upper_block = {
                "type": "single",
                "position": [block["position"][0], block["position"][1] + 1, block["position"][2]],
                "name": block["name"],
                "facing": block["facing"], 
                "half": "upper"
            }
            cleaned_block.append(upper_block)

        if "bed" in block["name"]:
            if all(block["name"] != f"{temp_color}_bed" for temp_color in color_list):
                block["name"] = color + "_bed"
            block["part"] = "head"
            if "facing" not in block:
                block["facing"] = random.choice(["east", "west", "north", "south"])
            
            bed_offset = {
                "west": [1, 0, 0],
                "east": [-1, 0, 0],
                "north": [0, 0, 1],
                "south": [0, 0, -1] 
            }

            foot_block = {
                "type": "single",
                "position": [base + offset for base, offset in zip(block["position"], bed_offset[block["facing"]])],
                "name": block["name"],
                "facing": block["facing"], 
                "part": "foot"
            }
            cleaned_block.append(foot_block)
            
        if "sign" in block["name"]:
            if all(block["name"] != f"{material}_sign" for material in tree_list):
                block["name"] = wooden_material + "_sign"
            if "rotation" not in block:
                block["rotation"] = random.randint(0, 9)
            if "facing" in block:
                block.pop("facing")

        if block["name"] == "chest":
            for item in block["items"]:
                if "planks" in item["name"] and all(item["name"] != f"{material}_planks" for material in tree_list):
                    item["name"] = wooden_material + "_planks"
                if "door" in item["name"] and all(item["name"] != f"{material}_door" for material in tree_list):
                    item["name"] = wooden_material + "_door"
                if "wool" in item["name"] and all(item["name"] != f"{temp_color}_wool" for temp_color in color_list):
                    item["name"] = color + "_wool"

                if "fence_gate" in item["name"] and all(item["name"] != f"{material}_fence_gate" for material in tree_list):
                    item["name"] = wooden_material + "_fence_gate"
                elif "fence" in item["name"] and all(item["name"] != f"{material}_fence" for material in tree_list):
                    item["name"] = wooden_material + "_fence"
                
                if item["name"] not in item_name_list:
                    item["name"] = llm.few_shot_generate_thoughts(system_prompt=
                                                                  format_string(CORRECTOR_PROMPT, {
                                                                      "Task": task_description,
                                                                      "Item": item["name"],
                                                                      "Item_list": item_name_list
                                                                  }))
                
                if item["name"] not in item_name_list:
                    print(f"INVALID LLM CORRECTOR:\n {item['name']}")
                else:
                    for item_info in item_list:
                        if item["name"] == item_info["name"] and item["count"] > item_info["stackSize"]: # 堆叠数量超限
                            if item["count"] < 10:
                                for i in range((item["count"]-1) // item_info["stackSize"]):
                                    block["items"].append({
                                        "name": item["name"],
                                        "count": item_info["stackSize"]
                                    })
                            item["count"] = item_info["stackSize"]

            if any(item["name"] in set(["carrot", "potato"]) or "_seeds" in item["name"] for item in block["items"]):
                if all("_hoe" not in item["name"] for item in block["items"]):
                    block["items"].append({
                        "name": "iron_hoe",
                        "count": 1
                    })
        
        if block["name"] not in item_name_list:
            block["name"] = llm.few_shot_generate_thoughts(system_prompt=
                                                                  format_string(CORRECTOR_PROMPT, {
                                                                      "Task": task_description,
                                                                      "Item": block["name"],
                                                                      "Item_list": item_name_list
                                                                  }))
        if block["name"] not in item_name_list:
            print(f"INVALID LLM CORRECTOR:\n {block['name']}")
            
        cleaned_block.append(block) 

    for entity in entities:
        cleaned_entity.append(entity)

    return {
        "blocks": cleaned_block,
        "entities": cleaned_entity
    }

def gen_task(times = 1):
    evol_objs = []

    for i in range(times):
        evol_prompts = []
        # choose 2 samples from the data
        samples = random.sample(all_objs, 2)
        format_str = "Example 1: {}\n Example 2: {}\n"
        cur_obj = format_str.format(samples[0], samples[1])
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
        # instruction = cur_obj["instruction"]
        instruction = cur_obj
        blueprint_prompt.append(createBlueprintPrompt(instruction))
        selected_evol_prompt = blueprint_prompt[-1]
        evol_instruction = llm.few_shot_generate_thoughts(system_prompt="You are a helpful assistant", example_prompt=selected_evol_prompt)
        #TODO: blueprints.json之后应该调整成类似config.json那样的，包含给judger生成环境的信息和给TM任务描述的信息
        return str2dict(evol_instruction, 'blueprints.json')
    
def create_config(task_description, blueprint, api_model = "qwen_max", host = "127.0.0.1", port = 25565, agent_num = 2):
    config = [{
        "api_model": api_model,
        "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "task_type": "gen",
        "task_idx": 1,
        "agent_num": agent_num,
        "dig_needed": False,
        "task_goal": task_description,
        "blueprint": blueprint,
        "host": host,
        "port": port,
        "task_name": f"gen_1_{agent_num}p"
    }]

    with open(f"{api_model}_gen_config.json", "w", encoding='utf-8') as f:
        json.dump(config, f, indent=4)
    print("gen task saved!")

def apply_coordinate_offset(input_str, offset = [41, -60, 122]):
    """
    给字符串中的所有坐标数组添加偏移量
    
    参数:
        input_str (str): 包含坐标数组的字符串，如 "点A[2, -5, 10]和点B[3, 4, -1]"
        offset (list): 偏移量[x, y, z]，如 [1, 2, -3]
    
    返回:
        str: 替换后的字符串
    """
    # 确保偏移量是3D的
    if len(offset) != 3:
        raise ValueError("偏移量必须是[x, y, z]格式的三元素列表")
    
    # 匹配所有形如[数字, 数字, 数字]的模式
    pattern = r'\[(-?\d+),\s*(-?\d+),\s*(-?\d+)\]'
    
    def replace_match(match):
        # 提取匹配到的三个数字
        x = int(match.group(1))
        y = int(match.group(2))
        z = int(match.group(3))
        
        # 应用偏移量
        new_x = x + offset[0]
        new_y = y + offset[1]
        new_z = z + offset[2]
        
        # 返回新格式的字符串
        return f"[{new_x}, {new_y}, {new_z}]"
    
    # 使用正则表达式替换所有匹配项
    result = re.sub(pattern, replace_match, input_str)
    return result

import re

def extract_env(text):
    """
    提取"**Environment:**"和"**Task**"之间的内容
    
    参数:
        text (str): 包含标记的字符串
        
    返回:
        str: 两个标记之间的内容（不包含标记本身）
    """
    # 使用正则表达式匹配两个标记之间的内容
    pattern = r'\*\*Environment:\*\*(.*?)\*\*Task:\*\*'
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        # 返回匹配到的内容，并去除首尾空白
        return match.group(1).strip()
    else:
        return None

if __name__ == "__main__":
    task = gen_task(1)
    # task = [{"instruction": "Construct a small farm near the village at [41, -60, 122] to grow wheat and carrots. Gather wooden planks and fences from the chest at [44, -60, 134] to build the farm enclosure. Use the hoe from the same chest to till the soil inside the enclosure. Plant wheat and carrot seeds in the tilled soil. Ensure the farm is well-protected by placing torches around the perimeter to prevent mob spawning. Once the crops are planted, one agent should collect water from the nearby river at [36, -60, 132] and bring it back to the farm to irrigate the crops. The other agent should monitor and protect the farm from any hostile mobs that may approach. Both agents should work together to ensure the farm is fully operational and the crops are growing well."}]
    task_description = task[0]["instruction"]
    print(task_description)
    print("\n\n")
    # task_description = apply_coordinate_offset(task_description, [-41, 60, -122])
    # concreted_task = concreting_task(task)
    # print(extract_env(concreted_task[0]["instruction"]))
    # blueprint = create_blueprint(concreted_task, 1)
    blueprint = create_blueprint([task], 1)
    create_config(apply_coordinate_offset(task_description), clean_env_dict(blueprint, task_description), args.api_model, args.host, args.port, args.agent_num)
