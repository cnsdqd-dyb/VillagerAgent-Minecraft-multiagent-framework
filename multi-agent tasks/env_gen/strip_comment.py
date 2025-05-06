import json5

input = '''
{
"blocks": [
// Scattered oak trees in the grassy plain
{"type": "rectangle", "from": [1, 0, 18], "to": [1, 4, 18], "name": "oak_log"},
{"type": "rectangle", "from": [0, 4, 17], "to": [2, 4, 19], "name": "oak_leaves"},
{"type": "rectangle", "from": [5, 0, 19], "to": [5, 4, 19], "name": "oak_log"},
{"type": "rectangle", "from": [4, 4, 18], "to": [6, 4, 20], "name": "oak_leaves"},
// River bordered by sand and gravel
{"type": "rectangle", "from": [4, -1, 21], "to": [6, -1, 23], "name": "sand"},
{"type": "rectangle", "from": [4, -1, 24], "to": [6, -1, 24], "name": "gravel"},
{"type": "rectangle", "from": [5, 0, 22], "to": [5, 0, 22], "name": "water"},
// Small wooden workbench and furnace
{"position": [3, 0, 22], "name": "crafting_table"},
{"position": [3, 0, 23], "name": "furnace", "facing": "north"},
// Chests containing tools and materials
{"position": [3, 0, 18], "name": "chest", "facing": "north", "items": [{"name": "stick", "count": 8}, {"name": "string", "count": 6}]},
{"position": [3, 0, 16], "name": "chest", "facing": "north", "items": []},
{"position": [4, 0, 22], "name": "chest", "facing": "north", "items": [{"name": "coal", "count": 8}, {"name": "bucket", "count": 2}]}
],
"entities": []
}

'''

# strip the comment lines
# input = input.split("\n")
# input = [line for line in input if not line.strip().startswith("//")]
# input = "\n".join(input)
# input = input.replace("\n\n", "\n")

output = json5.loads(input)
print(output)
