import json
import pandas as pd
import os

# 定义基础目录，假设脚本与“一步式-1永定河Json”和“一步式-1永定河json2excel”文件夹处于同一级别
# 获取当前脚本的执行目录
base_directory = os.getcwd()

# 定义输入和输出文件夹的名称
input_folder_name = "一步式-1永定河json"
output_folder_name = "一步式-1永定河json2excel"

# 构造输入和输出文件夹的完整路径
input_json_dir = os.path.join(base_directory, input_folder_name)
output_excel_dir = os.path.join(base_directory, output_folder_name)

# 确保输出目录存在，如果不存在则创建它
os.makedirs(output_excel_dir, exist_ok=True)

print(f"输入文件目录: {input_json_dir}")
print(f"输出文件目录: {output_excel_dir}")

# 获取输入目录中的所有 json 文件
# 使用 os.listdir 遍历并筛选出 .json 文件
json_files_in_dir = [f for f in os.listdir(input_json_dir) if f.endswith('.json')]

# 遍历每个 JSON 文件
for json_file_name in json_files_in_dir:
    print(f"\n正在处理文件: {json_file_name}")

    # 构造完整输入文件路径
    input_file_path = os.path.join(input_json_dir, json_file_name)

    try:
        # 读取 JSON 文件内容
        # 确保使用正确的编码，通常 UTF-8 是安全的
        with open(input_file_path, 'r', encoding='utf-8') as f:
            json_content = f.read()

        # 解析 JSON 内容
        data = json.loads(json_content)

        # 将 JSON 数据转换为 DataFrame
        # 假设 JSON 文件的顶级结构是列表（多个记录）或可以转换为 DataFrame 的字典
        df = pd.DataFrame(data)

        # 构造输出 Excel 文件的名称和完整路径
        excel_filename = json_file_name.replace('.json', '.xlsx')
        excel_output_path = os.path.join(output_excel_dir, excel_filename)

        # 将 DataFrame 保存为 Excel 文件
        # index=False 表示不在 Excel 中写入 DataFrame 的索引
        df.to_excel(excel_output_path, index=False)
        print(f"已成功将 '{json_file_name}' 转换为 '{excel_output_path}'")

    except FileNotFoundError:
        print(f"错误: 文件 '{input_file_path}' 未找到。请检查文件路径是否正确。")
    except json.JSONDecodeError as e:
        print(f"错误: 文件 '{json_file_name}' 的内容不是有效的 JSON 格式。详细信息: {e}")
        # 打印出提取到的可能导致错误的文本内容片段，有助于调试
        print(f"尝试解析的文本内容片段（前500字符）: {json_content[:500]}")
    except Exception as e:
        print(f"处理文件 '{json_file_name}' 时发生未知错误: {e}")

print("\n所有文件处理完毕。")