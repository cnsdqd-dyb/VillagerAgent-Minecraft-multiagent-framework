import json
import random
import re

from model.init_model import init_language_model
import argparse
from llm_gen_prompt import *

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
        return str2dict(evol_instruction, 'blueprints.json')


def filter_des(task_str):
    cleaned_text = re.sub(r'^\*\*Task:\*\*\s*\n*\s*', '', task_str)  # 匹配前缀并替换
    print(cleaned_text)
    return cleaned_text

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

if __name__ == "__main__":
    task = gen_task(1)
    task_description = filter_des(task[0]["instruction"])
    concreted_task = concreting_task(task)
    blueprint = create_blueprint(concreted_task, 1)
    create_config(task_description, blueprint, args.api_model, args.host, args.port, args.agent_num)