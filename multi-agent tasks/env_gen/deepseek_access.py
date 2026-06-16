from openai import OpenAI
import requests
import time

DEEPSEEK_API_KEY = 'sk-c78b19c61bf24a55b9f837c6ae633367'
# 请替换为实际的DeepSeek API端点
# DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'
# DEEPSEEK_API_URL = 'https://api.deepseek.com/v1'
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"


# def get_deepseek_completion(prompt):
#     headers = {
#         'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
#         'Content-Type': 'application/json'
#     }

#     payload = {
#         "model": "deepseek-chat",  # 根据DeepSeek实际模型名称调整
#         "messages": [
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": prompt}
#         ],
#         "temperature": 1,
#         "max_tokens": 2048,
#         "top_p": 0.95,
#         "frequency_penalty": 0,
#         "presence_penalty": 0,
#         "stop": None
#     }

#     try:
#         response = requests.post(
#             DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
#         response.raise_for_status()
#         data = response.json()
#         return data["choices"][0]["message"]["content"]

#     except requests.exceptions.Timeout:
#         print("The DeepSeek API request timed out. Please try again later.")
#         return None
#     except requests.exceptions.RequestException as e:
#         print(f"The DeepSeek API request failed: {e}")
#         return None
#     except (KeyError, IndexError) as e:
#         print(f"Failed to parse DeepSeek API response: {e}")
#         return None


# def call_deepseek(ins):
#     success = False
#     re_try_count = 15
#     ans = ''
#     while not success and re_try_count >= 0:
#         re_try_count -= 1
#         try:
#             ans = get_deepseek_completion(ins)
#             if ans is not None:  # 只有当返回有效结果时才认为成功
#                 success = True
#             else:
#                 time.sleep(5)
#                 print('Retrying for sample:', ins)
#         except Exception as e:
#             time.sleep(5)
#             print(f'Error occurred, retrying for sample {ins}: {str(e)}')
#     return ans


# Please install OpenAI SDK first: `pip3 install openai`

def call_deepseek(ins):
    success = False
    client = OpenAI(api_key="sk-c78b19c61bf24a55b9f837c6ae633367",
                    base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": ins},
        ],
        stream=False
    )

    if response.choices[0].message.content is not None:
        success = True
    else:
        # time.sleep(5)
        # print('Retrying for sample:', ins)
        print("DeepSeek API request failed. Please try again later.")
    return response.choices[0].message.content

    # print(response.choices[0].message.content)
