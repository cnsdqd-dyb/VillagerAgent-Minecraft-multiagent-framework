import json
import random
import time
import json5

from openai_access import call_chatgpt
from deepseek_access import call_deepseek
from depth import createConstraintsPrompt, createDeepenPrompt, createConcretizingPrompt, createReasoningPrompt
from breadth import createBreadthPrompt, createVABreadthPrompt
from blueprintGen import createBlueprintPrompt

# fr = open('alpaca_data_cleaned.json', 'r')
# fr = open('alpaca_data_simple.json', 'r')
# fr = open('simple_tasks.json', 'r')
fr = open("D:\VillagerAgent\VillagerAgent_git3\VillagerAgent_git3\VillagerAgent\multi-agent tasks\env_gen\concreted_tasks.json", 'r')

all_objs = json.load(fr)


times = 1
evol_objs = []

to_build = "Please build the building needed in the task given in the background infomation."
to_build = ""

instruction_default = "We want to build a village house. It shall be a large house."

for i in range(times):
    blueprint_prompt = []

    t = time.time()
    random.seed((int(t) + i) % 1000)
    rdn_idx = random.randint(0, 100)
    rdn_idx = str(rdn_idx) + "_"
    # random.shuffle(all_objs)
    # # choose 2 samples from the data
    # samples = random.sample(all_objs, 2)
    # format_str = "Example 1: {}\n Example 2: {}\n"
    # cur_obj = format_str.format(
    #     samples[0], samples[1])
    # cur_obj = all_objs[0]
    # cur_obj = all_objs[-1]
    # cur_obj = all_objs[2]
    # cur_obj = all_objs[1]
    cur_obj = random.choice(all_objs)
    instruction = cur_obj["instruction"]
    # instruction = instruction_default

    blueprint_prompt.append(createBlueprintPrompt(to_build, instruction))

    print("blueprint_prompt:", blueprint_prompt)

    # selected_evol_prompt = random.choice(blueprint_prompt)
    selected_evol_prompt = blueprint_prompt[-1]

    # evol_instruction = call_chatgpt(selected_evol_prompt)
    # answer = call_chatgpt(evol_instruction)
    evol_instruction = call_deepseek(selected_evol_prompt)
    # we don't need answer at the moment
    # answer = call_deepseek(evol_instruction)

    try:
        evol_instruction = json.loads(evol_instruction)
    except json.JSONDecodeError:
        print("Error decoding JSON:", evol_instruction)

    # evol_objs.append({"instruction": evol_instruction, "output": answer})
    evol_objs.append({rdn_idx+"blueprint": evol_instruction})

existing_data = []

with open('D:\\VillagerAgent\\VillagerAgent_git3\\VillagerAgent_git3\\VillagerAgent\\multi-agent tasks\\env_gen\\blueprints.json', 'r') as f:
    try:
        # existing_data = json.load(f)
        existing_data = json5.loads(f)
    except json.JSONDecodeError:
        print("File is empty or not a valid JSON. Starting with an empty list.")
        existing_data = []

# merge the new data with the existing data
for obj in evol_objs:
    # if obj not in existing_data:
    #     existing_data.append(obj)
    existing_data.append(obj)

# append the evol_objs to the alpaca_data_cleaned.json file
with open('D:\\VillagerAgent\\VillagerAgent_git3\\VillagerAgent_git3\\VillagerAgent\\multi-agent tasks\\env_gen\\blueprints.json', 'w') as f:
    # json.dump(existing_data, f, indent=4)
    json5.dump(existing_data, f, indent=4)
