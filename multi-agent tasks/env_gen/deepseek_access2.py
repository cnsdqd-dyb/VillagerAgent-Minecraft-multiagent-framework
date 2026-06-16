# deepseek.py

import requests

# 填写你的 API Key
API_KEY = "sk-c78b19c61bf24a55b9f837c6ae633367"

url = "https://api.deepseek.com/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

data = {
    "model": "deepseek-chat",  # 指定使用 R1 模型（deepseek-reasoner）或者 V3 模型（deepseek-chat）
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你是谁？"}
    ],
    "stream": False  # 关闭流式传输
}

data["stream"] = True

response = requests.post(url, headers=headers, json=data, stream=True)

for line in response.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        print(decoded_line)
