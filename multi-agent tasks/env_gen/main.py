import json
import random
import time

from openai_access import call_chatgpt
from deepseek_access import call_deepseek
# from depth import createConstraintsPrompt, createDeepenPrompt, createConcretizingPrompt, createReasoningPrompt
from breadth import createBreadthPrompt, createVABreadthPrompt


# fr = open('alpaca_data_cleaned.json', 'r')
# fr = open('alpaca_data_simple.json', 'r')
fr = open('example_simple_tasks.json', 'r')

all_objs = json.load(fr)


times = 5
evol_objs = []


for i in range(times):
    evol_prompts = []

    t = time.time()
    random.seed((int(t) + i) % 1000)
    random.shuffle(all_objs)
    # choose 2 samples from the data
    samples = random.sample(all_objs, 2)
    format_str = "Example 1: {}\n Example 2: {}\n"
    cur_obj = format_str.format(
        samples[0], samples[1])
    instruction = cur_obj

    evol_prompts.append(createVABreadthPrompt(instruction))

    print("evol_prompts:", evol_prompts)

    selected_evol_prompt = random.choice(evol_prompts)

    evol_instruction = call_deepseek(selected_evol_prompt)
    # we don't need answer at the moment
    # answer = call_deepseek(evol_instruction)

    # evol_objs.append({"instruction": evol_instruction, "output": answer})
    evol_objs.append({"instruction": evol_instruction})


# with open('alpaca_data_evol.json', 'w') as f:
#     json.dump(evol_objs, f, indent=4)

with open('alpaca_data_evol.json', 'r') as f:
    try:
        existing_data = json.load(f)
    except json.JSONDecodeError:
        existing_data = []

# merge the new data with the existing data
for obj in evol_objs:
    if obj not in existing_data:
        existing_data.append(obj)

# append the evol_objs to the alpaca_data_cleaned.json file
with open('alpaca_data_evol.json', 'w') as f:
    json.dump(existing_data, f, indent=4)
