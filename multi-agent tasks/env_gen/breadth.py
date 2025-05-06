import random
import time

base_instruction = "I want you act as a Prompt Creator.\r\n\
Your goal is to draw inspiration from the #Given Prompt# to create a brand new prompt.\r\n\
This new prompt should belong to the same domain as the #Given Prompt# but be even more rare.\r\n\
The LENGTH and complexity of the #Created Prompt# should be similar to that of the #Given Prompt#.\r\n\
The #Created Prompt# must be reasonable and must be understood and responded by humans.\r\n\
'#Given Prompt#', '#Created Prompt#', 'given prompt' and 'created prompt' are not allowed to appear in #Created Prompt#\r\n"

base_instruction_VA = "I want you act as a Prompt Creator.\r\n\
Your goal is to draw inspiration from the #Given Prompt# to create a brand new prompt.\r\n\
The new prompt shall be coarse-grained task for multi-agent systems, preferably meeting both the simplicity in description and complexity in dependency.\r\n\
This new prompt do not have to belong to the same domain as the #Given Prompt# but shall remain in the minecraft.\r\n\
Do note that the x, y, z coordinates shall be restricted in the range: min_x, min_y, min_z = -11, 0, 0; max_x, max_y, max_z = 11, 15, 25\r\n\
The LENGTH and complexity of the #Created Prompt# should be similar to that of the #Given Prompt#.\r\n\
The #Created Prompt# must be reasonable and must be understood and responded by humans.\r\n\
It would be better if the new task involves intense collaborations and division of labor between agents. Meanwhile the task shall not be too difficult or big.\r\n\
'#Given Prompt#', '#Created Prompt#', 'given prompt' and 'created prompt' are not allowed to appear in #Created Prompt#\r\n"

instruction_actions = "You can use or not to use the following actions to create the multi-agent task. And the actions related to this task can include but not limited to the following actions:\r\n"

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


def createBreadthPrompt(instruction):
    prompt = base_instruction
    prompt += "#Given Prompt#: \r\n {} \r\n".format(instruction)
    prompt += "#Created Prompt#:\r\n"
    return prompt


def createVABreadthPrompt(instruction):
    t = time.time()
    random.seed(int(t) % 1000)
    # randomly select 3 actions from action_list
    random.shuffle(action_list)
    selected_actions = random.sample(action_list, 3)
    # create the action string
    action_string = ""
    for action in selected_actions:
        action_string += "- " + action + "\r\n"
    prompt = base_instruction_VA
    prompt += instruction_actions + action_string
    prompt += "#Given Prompt#: \r\n {}".format(
        instruction)
    # prompt += "No blueprints in your generated task\r\n"
    prompt += "#Created Prompt#:\r\n"
    return prompt
