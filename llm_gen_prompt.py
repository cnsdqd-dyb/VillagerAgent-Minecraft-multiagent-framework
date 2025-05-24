VA_base_instruction = '''
I want you to act as a Task Designer.
Your objective is to take inspiration from the #Given Task# and design a brand-new coarse-grained task.
This coarse-grained task suitable for multi-agent systems with {{agent_num}} agent, ideally balancing descriptive simplicity with dependency complexity.
While it does not need to belong to the same domain as the #Given Task#, it must still be situated within the Minecraft environment.
#Created Task# should meet the following requirements:
- The x, y, z coordinates must strictly fall within the following bounds: min_x = -10, min_y = -1, min_z = 1; max_x = 10, max_y = 5, max_z = 24. Coordinates outside this range are not allowed.
- Make sure the new task is reasonable and interpretable by humans.
- Tasks that encourage intensive collaboration are preferred.
- Provide only a general task specification and avoid explicitly assigning specific tasks to any individual agent.
- The length of #Created Task# should be within 800 characters.
- The terms '#Given Task#', '#Created Task#', 'given task', and 'created task' must not appear in the #Created Task#.
'''

VA_Volume_base_instruction = '''
I want you to act as a Environment Designer.
Your objective is to learn the formatting style from the pairs of #Given Simple Task# and #Given Augmented Task#, and apply this format to transform the provided #Simple Task Input# into an #Augmented Task Output#.
The purpose of the augmented task is to enrich or expand upon the original simple task by incorporating environment details and auxiliary information.
The #Augmented Task Output# must be reasonable and interpretable by humans.
Note: the terms '#Given Simple Task#', '#Given Augmented Task#', and '#Simple Task Input#' must not appear in the #Augmented Task Output#.
'''

blueprint_base_instruction = '''
You are an **environment designer in Minecraft**, responsible for creating the **initial environment** needed for a given task. This environment will serve as the foundation for agents to complete the task.

You will receive a **#Task#** that specifies a goal to be completed collaboratively by multiple agents.

### Your tasks:

1. Analyze the task description
- Identify all entities mentioned in the task, including blocks, creatures, and items.
- Distinguish which entities are part of the task objectives that agents need to accomplish, and which are part of the environment that agents need to interact with or utilize during task execution.

2. Design the initial environment
- Based on the analysis, generate the initial environment, ensuring that all necessary interactive or usable entities are properly included.
- Only generate elements that agents need to interact with; do not include any content that represents the actual task objectives agents are expected to complete.
    * For example, if the task says "- Place a sign at [0, 0, 10] with the text 'test sign'", provide an oak_sign in a chest, but do not place a sign with the specified text in the environment beforehand.
- Blocks can be placed individually by setting the 'type' to 'single', or placed in a cube-shaped structure by setting the 'type' to 'cube'.
- To place trees, use the following format:

```json
{"type": "tree", "position": [x, y, z], "name": "oak"}
```

    * Optional tree names: `oak`, `birch`, `spruce`, `jungle`, `acacia`, `dark_oak` 
    * Since trees occupy more space, they should maintain a minimum distance of 3 blocks from any other tree or block.

### Constraints:

- The x, y, z coordinates must strictly fall within the following bounds: min_x = -10, min_y = -1, min_z = 1; max_x = 10, max_y = 5, max_z = 24. Coordinates outside this range are not allowed.
- **Flat ground** is at `y = -1` and is pre-filled with `grass_block`.
- Water blocks must be **surrounded by solid blocks** or placed at `y = -1`.
- Do not overwrite any existing blocks.
- Include all **tools and materials** needed in a **chest**.

### Output:

* Format your design as a **JSON object**, following the structure in the **#Example#** section.
'''

instruction_actions = "You may use, but are not limited to, the following actions to create the multi-agent task:"

example_string = """
{
    "blocks": [
        {
            // Place an oak tree at position (3, 0, 5)
            "type": "tree",
            "position": [3, 0, 5],
            "name": "oak"
        },
        {
            // Place a oak_log at position (5, 0, 10)
            "type": "single",
            "position": [5, 0, 10],
            "name": "oak_log"
        },
        {
            // Create a vertical water channel at y = -1 (underground level), so water doesn't spill
            "type": "cube",
            "from": [2, -1, 3],
            "to": [4, -1, 9],
            "name": "water"
        },
        {
            // Create a horizontal line of oak planks from (1, -1, 15) to (1, -1, 20)
            "type": "cube",
            "from": [1, -1, 15],
            "to": [1, -1, 20],
            "name": "oak_planks"
        },
        {
            // Create a horizontal line of oak planks from (-5, -1, 15) to (-5, -1, 20)
            "type": "cube",
            "from": [-5, -1, 15],
            "to": [-5, -1, 20],
            "name": "oak_planks"
        },
        {
            // Create a vertical line of oak planks from (-4, -1, 20) to (0, -1, 20)
            "type": "cube",
            "from": [-4, -1, 20],
            "to": [0, -1, 20],
            "name": "oak_planks"
        },
        {
            // Place a chest at (1, 0, 15) facing north, containing seeds and hoes
            "type": "single",
            "position": [1, 0, 15],
            "name": "chest",
            "facing": "north",
            "items": [
                {
                    "name": "wheat_seeds",
                    "count": 16
                },
                {
                    "name": "iron_hoe",
                    "count": 1
                },
                {
                    "name": "iron_hoe",
                    "count": 1
                }
            ]
        },
        {
            // Place an empty chest at (1, 0, 20) facing north, possibly for future use
            "type": "single",
            "position": [1, 0, 20],
            "name": "chest",
            "facing": "north",
            "items": []
        },
        {
            // Place a crafting table at position (-5, 0, 20)
            "type": "single",
            "position": [-5, 0, 20],
            "name": "crafting_table"
        }
    ],
    "entities": [
        // Fish in the water
        {"position": [4, -1, 8], "name": "cod"},
        {"position": [4, -1, 9], "name": "salmon"},
        {"position": [-4, 0, 10], "name": "cow"}
    ]
}
"""

CORRECTOR_PROMPT = '''
You are a Corrector. Your task is to identify and correct an invalid item name based on a Minecraft task description.
You are given the following multi-agent task:
{{Task}}

The task is meant to be supported by an automatically generated environment. However, the environment includes an invalid item — {{Item}}, which does not exist in Minecraft.
Use the task description to infer which valid Minecraft item was most likely intended in place of the invalid one.
You are also provided with the complete list of valid Minecraft item names:
{{Item_list}}

*** Important Notice:***
- Focus only on items that should exist in the environment agents interact with during task execution.
- Do not return items that are part of the goal agents are expected to achieve.
- Select and return only one valid item name from the provided list.
- Do not include any reasoning, explanation, or additional output — just return the corrected item name.
'''