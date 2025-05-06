import json
# import random

# from openai_access import call_chatgpt
from deepseek_access import call_deepseek
# from depth import createConstraintsPrompt, createDeepenPrompt, createConcretizingPrompt, createReasoningPrompt
# from breadth import createBreadthPrompt, createVABreadthPrompt
from concrete_prompt import createVAVolumePrompt

# fr = open('alpaca_data_cleaned.json', 'r')
# fr = open('alpaca_data_evol.json', 'r')
fr = open('example_simple_tasks.json', 'r')

all_objs = json.load(fr)

evol_objs = []

examples = []

examples.append({'simple': "**Task:**\n- Collaborate to place blocks according to the blueprint `minecraft/templates/nether_fossils_fossil_3`.\n- Use the materials from the chest at [-4, 1, 10]. The other chest in the factory with tools is not needed for this task.",
                'augmentation': "**Interactive-Items:**\n- **Oak Sign**: [-3, 3, 10] (facing west)\n\n**Environment:**\n- The area around [-4, 2, 11] includes a structure made of stone bricks, spruce planks, and sandstone. There is a chest and a furnace facing west, and a spruce fence to the east. The ground is primarily dirt and grass blocks.\n- The blueprint provided is for `minecraft/templates/nether_fossils_fossil_3`.\n\n**Task:**\n- Collaborate to place blocks according to the blueprint `minecraft/templates/nether_fossils_fossil_3`.\n- Use the materials from the chest at [-4, 1, 10]. The other chest in the factory with tools is not needed for this task.\nSign info: \nminecraft/templates/nether_fossils_fossil_3"})

examples.append(
    {'simple': "**Task:** \n- Work together to catch at least 10 fish (a mix of cod and salmon) using the fishing rods and bait from the chest. \n- Ensure the caught fish are stored in a second chest placed at [6, 0, 20]. \n- Avoid disturbing a nearby school of tropical fish swimming around [7, 0, 18].",
     'augmentation': "**Environment:** \n- A coastal area at [5, 0, 20] features a small wooden dock made of oak planks and fences, extending into the ocean. A chest containing fishing rods and bait is placed at [5, 0, 21]. The water is populated with cod and salmon. \n\n**Task:** \n- Work together to catch at least 10 fish (a mix of cod and salmon) using the fishing rods and bait from the chest. \n- Ensure the caught fish are stored in a second chest placed at [6, 0, 20]. \n- Avoid disturbing a nearby school of tropical fish swimming around [7, 0, 18]. \n\n**Actions available:** \n- Agents can use fishing rods to catch fish. \n- Agents can move along the dock or swim in designated areas. \n- Agents can transfer caught fish to the storage chest. \n- Agents must avoid scaring away the tropical fish."})

prompt = {'examples': examples, 'input': ""}

for cur_obj in all_objs:

    # instruction = cur_obj['instruction'].strip(
    # )
    instruction = cur_obj.strip()

    prompt['input'] = instruction

    evol_prompts = createVAVolumePrompt(prompt)

    print("evol_prompts:", evol_prompts)

    # selected_evol_prompt = random.choice(evol_prompts)
    selected_evol_prompt = evol_prompts

    # evol_instruction = call_chatgpt(selected_evol_prompt)
    evol_instruction = call_deepseek(selected_evol_prompt)

    # evol_objs.append({"instruction": evol_instruction, "output": answer})
    evol_objs.append({"instruction": evol_instruction})

# append the evol_objs to the alpaca_data_cleaned.json file
with open('concreted_tasks.json', 'a') as f:
    json.dump(evol_objs, f, indent=4)
