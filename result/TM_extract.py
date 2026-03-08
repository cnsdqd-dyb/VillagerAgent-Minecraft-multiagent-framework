import os
import json
from pathlib import Path

def process_gen_folders(result_path="result"):
    result_dir = Path(result_path)
    if not result_dir.exists():
        raise FileNotFoundError(f"路径不存在: {result_path}")
    
    dataset = []
    
    for folder in result_dir.iterdir():
        if not folder.is_dir():
            continue
        
        parts = folder.name.split('_')
        if len(parts) > 0 and parts[0] == "gen":
            history_file = folder / "TM_history.json"
            if history_file.exists():
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                    
                    # 检查是否是列表形式
                    prompts = history_data.get("prompt", [])
                    responses = history_data.get("response", [])
                    
                    if isinstance(prompts, list) and isinstance(responses, list):
                        if len(prompts) != len(responses):
                            print(f"警告: {history_file} 中prompt和response长度不一致")
                            continue
                        
                        # 按索引配对
                        for prompt, response in zip(prompts, responses):
                            dataset.append({
                                "input": prompt,
                                "output": response
                            })
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    print(f"处理文件 {history_file} 时出错: {e}")
                    continue
    
    output_file = result_dir / "TM_dataset.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"处理完成，共提取 {len(dataset)} 条数据，已保存到 {output_file}")

if __name__ == "__main__":
    process_gen_folders()