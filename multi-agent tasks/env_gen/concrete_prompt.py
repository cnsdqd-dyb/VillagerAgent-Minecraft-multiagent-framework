import random
base_instruction = "I want you act as a Task Designer.\r\n\
Your goal is to learn the format from the pairs of #Given Simple Task# and #Given Augmented Task#, and use it to augment the given #Simple Task Input# into #Augmented Task Output#.\r\n\
This new augmented task should augment or enrich the content of the given simple task by adding: environment infomation and auxilliary information.\r\n\
The #Augmented Task Output# must be reasonable and must be understood and responded by humans.\r\n\
'#Given Simple Task#', '#Given Augmented Task#' and '#Simple Task Input#' are not allowed to appear in #Augmented Task Output#\r\n"


# input shall be of the format: {'examples': [{'simple': '...', 'augmentation': '...'}, ...], 'input': '...'}
def createVAVolumePrompt(input):
    prompt = base_instruction
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
