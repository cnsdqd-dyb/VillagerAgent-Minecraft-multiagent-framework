# import os
# import json
# import shutil
# distribution = {}
# def check_and_delete_folders():
#     # Get current directory
#     current_dir = os.getcwd()
    
#     # Track deleted folders
#     deleted_folders = []
    
#     # Iterate through all folders in current directory
#     for folder in os.listdir(current_dir):
#         folder_path = os.path.join(current_dir, folder)
        
#         # Check if it's a directory
#         if os.path.isdir(folder_path):
#             score_file = os.path.join(folder_path, 'score.json')
#             DM_file = os.path.join(folder_path, 'DM_query.json')
#             # Check if score file exists
#             if os.path.exists(score_file):
#                 try:
#                     with open(score_file, 'r') as f:
#                         data = json.load(f)
#                     # Check score value
#                     if data.get('score') != 100:
#                     #     # Delete the folder
#                     #     shutil.rmtree(folder_path)
#                         deleted_folders.append(folder)
#                     else:
#                         config_info = folder_path.split('_')
#                         if config_info[0] not in distribution:
#                             distribution[config_info[0]] = 1
#                         else:
#                             distribution[config_info[0]] += 1
#                         if config_info[0] == "interact":
#                             if config_info[1] not in distribution:
#                                 distribution[config_info[1]] = 1
#                             else:
#                                 distribution[config_info[1]] += 1

#                 except (json.JSONDecodeError, FileNotFoundError) as e:
#                     print(f"Error reading {score_file}: {e}")
#             # elif os.path.exists(DM_file):
#             #     shutil.rmtree(folder_path)
#             #     deleted_folders.append(folder)

#     # Print results
#     if deleted_folders:
#         print("Deleted folders:")
#         for folder in deleted_folders:
#             print(f"- {folder}")
#     else:
#         print("No folders needed to be deleted.")
#     print(len(deleted_folders))

# # Run the function
# if __name__ == "__main__":
#     check_and_delete_folders()
#     # for key in distribution.keys():
#     #     print(key, distribution[key])

import os
import json
from collections import defaultdict
import openpyxl

# 定义路径
base_dir = '.'  # 当前路径
output_excel_path = 'SFT base agent.xlsx'

# 初始化统计数据
score_100_distribution = defaultdict(int)  # score 为 100 的文件夹数量

# 遍历当前路径下的所有文件夹
for folder_name in os.listdir(base_dir):
    if os.path.isdir(os.path.join(base_dir, folder_name)):
        # 解析文件夹名称
        parts = folder_name.split('_')
        category = parts[0]

        # 如果是 interact 类别，进一步解析子类别
        if category == 'interact' and len(parts) > 1:
            subcategory = parts[1]
            category = f"interact_{subcategory}"  # 使用 interact_子类别 作为类别名

        # 检查 score.json 文件
        score_json_path = os.path.join(base_dir, folder_name, 'score.json')
        if os.path.exists(score_json_path):
            with open(score_json_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    # 检查是否有 score 字段且值为 100
                    if data.get('score') == 100:
                        score_100_distribution[category] += 1
                except json.JSONDecodeError:
                    print(f"Error decoding JSON in {score_json_path}")
                    continue

# 创建 Excel 文件
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "QWEN"

# 写入表头
ws.append(["类别", "score 为 100 的文件夹数量"])

# 写入 score 为 100 的分布情况
for category, count in score_100_distribution.items():
    ws.append([category, count])

# 保存 Excel 文件
wb.save(output_excel_path)

print(f"统计结果已保存到 {output_excel_path}")