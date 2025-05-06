import json
import random
import time
import json5
base_instruction = "I want you act as a building designer in Minecraft.\r\n\
Your goal is to design buildings required by the tasks.\r\n\
You will be given a #Background# which specifies the background information, and a #To-Build# which specifies the building you are required to design.\r\n\
This new building should meet constraints of the standands and should not be too large.\r\n\
Do note that the x, y, z coordinates shall be restricted in the range: min_x, min_y, min_z = -11, 0, 0; max_x, max_y, max_z = 11, 15, 25\r\n\
The #Designed Building# must follow the json format as the example given in #Example#.\r\n\
'#Example#', '#To-Build#', '#Background#' and '#Designed Building#' are not allowed to appear in #Designed Building#\r\n"

large_scale_instruction = "I want you act as a building designer in Minecraft.\r\n\
Your goal is to design buildings required by the tasks.\r\n\
You will be given a #Background# which specifies the background information, and a #To-Build# which specifies the buildings you are required to design.\r\n\
This new buildings should meet constraints of the standands.\r\n\
Do note that the x, y, z coordinates shall be restricted in the range: min_x, min_y, min_z = -11, 0, 0; max_x, max_y, max_z = 11, 15, 25\r\n\
The #Designed Building# must follow the json format as the example given in #Example#.\r\n\
'#Example#', '#To-Build#', '#Background#' and '#Designed Building#' are not allowed to appear in #Designed Building#\r\n"

base_prompt_v2 = "I want you to act as an **environment designer in Minecraft**. Your goal is to **create the environment necessary for a given task**, serving as the foundation for agents to complete the task. You will receive a **#Background#**, which provides context for the task. Please do the following:\n 1. **Identify** which parts of the background describe the **environment** that needs to be built now, and which parts describe the **building(s)** required later by the task (those buildings do **not** need to be built at this stage).\n 2. **Design the initial environment** accordingly, making sure it satisfies the specified constraints.\n **Constraints**:\n * Coordinate boundaries: `min_x, min_y, min_z = -11, 0, 0` `max_x, max_y, max_z = 11, 15, 25`\n * **Flat ground is at y = -1 (already filled by grass_block)**.\n * Don't forget to surround the water with other blocks if you need to place water blocks (e.g. if there is a river in the setting).\n * Be careful **not** to overwrite already placed blocks.\n * The tools and materials needed for the task shall all be included in the box.\n * Blocks can be placed **individually** or as a **line** or a **rectangle**.\n * The output for the designed environment must follow the **JSON format shown in the #Example#** section.\nPlease refer to the **#Example#** section for how to format the output as a JSON structure.\n"

example_json = {"blocks": [{"type": "rectangle", "from ": [6, 0, 10], "to": [10, 0, 20], "name": "oak_log"}, {"type": "line", "from ": [4, 0, 4], "to": [4, 0, 10], "name": "oak_fence"}, {"position": [2, 0, 4], "name": "oak_log"}, {"position": [
    2, 0, 11], "name": "oak_log"}, {"position": [-1, 0, 10], "name": "chest", "facing": "north", "items": [{"name": "egg", "count": 1}, {"name": "milk_bucket", "count": 3}, {"name": "sugar", "count": 2}]}], "entities": [{"position": [0, 1, 20], "name": "cod"}]}
example_json = {"blocks": [{"type": "rectangle", "from ": [-1, 0, 11], "to": [1, 0, 13], "name": "oak_planks"}, {"type": "line", "from ": [-1, 1, 11], "to": [-1, 2, 11], "name": "oak_log"}, {"type": "line", "from ": [1, 1, 11], "to": [1, 2, 11], "name": "oak_log"}, {"type": "rectangle", "from ": [-1, 3, 11], "to": [1, 3, 13], "name": "oak_planks"}, {"position": [0, 0, 12], "name": "crafting_table"}, {"type": "rectangle", "from ": [5, 0, 10], "to": [7, 0, 12], "name": "oak_log"}, {"position": [
    7, 0, 8], "name": "cobweb"}, {"type": "line", "from ": [0, 0, 15], "to": [0, 0, 20], "name": "oak_planks"}, {"position": [-1, 0, 20], "name": "chest", "facing": "north", "items": [{"name": "fishing_rod", "count": 2}]}, {"position": [1, 0, 20], "name": "chest", "facing": "north", "items": [{"name": "cod", "count": 6}, {"name": "salmon", "count": 4}]}], "entities": [{"position": [0, 1, 16], "name": "cod"}, {"position": [1, 1, 17], "name": "salmon"}, {"position": [-1, 1, 18], "name": "cod"}]}

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


# example_default = json.dumps(example_json)
example_default = json5.dumps(example_json)
example_default = example_string
# example_default = json.dumps(example_json, indent=4)


def createBlueprintPrompt(to_build, background, example=example_default):
    # t = time.time()
    # random.seed(int(t) % 1000)
    # # randomly select 3 actions from action_list
    # random.shuffle(action_list)
    # selected_actions = random.sample(action_list, 3)
    # # create the action string
    # action_string = ""
    # for action in selected_actions:
    #     action_string += "- " + action + "\r\n"

    prompt = base_prompt_v2
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
