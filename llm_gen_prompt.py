breadth_base_instruction = '''
I want you act as a Prompt Creator.
#Given Prompt# to create a brand new prompt.
Your goal is to draw inspiration from the
#Given Prompt# but be even more rare.
This new prompt should belong to the same domain as the
#Created Prompt# should be similar to that of the #Given Prompt#.
The LENGTH and complexity of the
#Created Prompt# must be reasonable and must be understood and responded by humans.
The
'#Given Prompt#', '#Created Prompt#', 'given prompt' and 'created prompt' are not allowed to appear in #Created Prompt#
'''

VA_base_instruction = '''
I want you act as a Prompt Creator.
#Given Prompt# to create a brand new prompt.
Your goal is to draw inspiration from the
The new prompt shall be coarse-grained task for multi-agent systems, preferably meeting both the simplicity in description and complexity in dependency.
#Given Prompt# but shall remain in the minecraft.
This new prompt do not have to belong to the same domain as the
Do note that the x, y, z coordinates shall be restricted in the range: min_x, min_y, min_z = -10, 0, 1; max_x, max_y, max_z = 10, 15, 24
#Created Prompt# should be similar to that of the #Given Prompt#.
The LENGTH and complexity of the
#Created Prompt# must be reasonable and must be understood and responded by humans.
The
It would be better if the new task involves intense collaborations and division of labor between agents. Meanwhile the task shall not be too difficult or big.
'#Given Prompt#', '#Created Prompt#', 'given prompt' and 'created prompt' are not allowed to appear in #Created Prompt#
'''

VA_Volume_base_instruction = '''
I want you act as a Task Designer.
#Given Simple Task# and #Given Augmented Task#, and use it to augment the given #Simple Task Input# into #Augmented Task Output#.
Your goal is to learn the format from the pairs of
This new augmented task should augment or enrich the content of the given simple task by adding: environment infomation and auxilliary information.
#Augmented Task Output# must be reasonable and must be understood and responded by humans.
The
#Augmented Task Output#
'#Given Simple Task#', '#Given Augmented Task#' and '#Simple Task Input#' are not allowed to appear in
'''

blueprint_base_instruction = '''
You are an **environment designer in Minecraft**, responsible for creating the **initial environment** needed for a given task. This environment will serve as the foundation for agents to complete the task.

#Background#**, which contains both environmental context and potential future building requirements.
You will receive a **

### Your tasks:

1. **Analyze the background**:

   * Identify which parts describe the **environment to be built now**.
   * Distinguish elements that refer to **future structures** (these buildings do **not** need to be built yet).

2. **Design the initial environment**:

   * Ensure it satisfies all constraints and matches the described setting.

3. To place trees, use the following format:

   ```json
   {"type": "tree", "position": [x, y, z], "name": "oak"}
   ```

   * Tree types: `oak`, `birch`, `spruce`, `jungle`, `acacia`, `dark_oak`

### Constraints:

* Coordinate boundaries:
  `min_x, min_y, min_z = -10, 0, 1`
  `max_x, max_y, max_z = 10, 15, 24`
* **Flat ground** is at `y = -1` and is pre-filled with `grass_block`.
* Water blocks must be **surrounded by solid blocks** or placed at `y = -1`.
* **Do not overwrite** existing blocks.
* Include all **tools and materials** needed in a **chest**.

  * **Do not place any block on top of the chest**, or it won't open.
* Blocks can be placed **individually**, as a **line**, or as a **rectangle**.

### Output:

#Example#** section.
* Format your design as a **JSON object**, following the structure in the **
'''

instruction_actions = "You can use or not to use the following actions to create the multi-agent task. And the actions related to this task can include but not limited to the following actions:\r\n"

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
      // Place a oak_log at position (6, 0, 15)
      "position": [6, 0, 15],
      "name": "oak_log"
    },
    {
      // Create a vertical water channel at y = -1 (underground level), so water doesn't spill
      "type": "rectangle",
      "from": [4, -1, 7],
      "to": [4, -1, 9],
      "name": "water"
    },
    {
      // Create a horizontal line of oak planks from (1, 0, 15) to (1, 0, 20)
      "type": "line",
      "from": [1, 0, 15],
      "to": [1, 0, 20],
      "name": "oak_planks"
    },
    {
      // Create a rectangular patch of grass blocks for planting or decoration
      "type": "rectangle",
      "from": [0, 0, 10],
      "to": [4, 0, 14],
      "name": "grass_block"
    },
    {
      // Place a chest at (2, 0, 12) facing north, containing seeds and hoes
      "position": [2, 0, 12],
      "name": "chest",
      "facing": "north",
      "items": [
        {
          // 16 wheat seeds for planting
          "name": "wheat_seeds",
          "count": 16
        },
        {
          // 2 iron hoes for tilling soil
          "name": "iron_hoe",
          "count": 2
        }
      ]
    },
    {
      // Place an empty chest at (0, 0, 14) facing north, possibly for future use
      "position": [1, 0, 14],
      "name": "chest",
      "facing": "north",
      "items": []
    },
    {
      // Place a crafting table at position (-2, 1, 20)
      "position": [-2, 1, 20],
      "name": "crafting_table"
    },
    {
      // Place a sign at (1, 0, 12) facing north with task instructions
      "position": [1, 0, 12],
      "name": "oak_sign",
      "facing": "north",
      "text": "Wheat Farm Setup: Till soil, plant seeds, build water channel from river."
    }
  ],
  // No entities (e.g., animals, villagers) are included in the environment
  "entities": [
    // Fish in the water
    {"position": [4, -1, 8], "name": "cod"},
    {"position": [4, -1, 9], "name": "salmon"},
  ]
}
"""