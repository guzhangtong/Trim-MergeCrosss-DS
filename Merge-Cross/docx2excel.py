import json
import pandas as pd
import os
from docx import Document # 导入 Document 类
# 定义基础目录，假设脚本与“一步式-1永定河Json”和“一步式-1永定河excel”文件夹处于同一级别
# 获取当前脚本的执行目录
base_directory = os.getcwd() 

# 定义输入和输出文件夹的名称
input_folder_name = "一步式-1永定河docx"
output_folder_name = "一步式-1永定河docx2excel"

# 构造输入和输出文件夹的完整路径
input_docx_dir = os.path.join(base_directory, input_folder_name)
output_excel_dir = os.path.join(base_directory, output_folder_name)

# 确保输出目录存在，如果不存在则创建它
os.makedirs(output_excel_dir, exist_ok=True)

print(f"输入文件目录: {input_docx_dir}")
print(f"输出文件目录: {output_excel_dir}")

# 获取输入目录中的所有 docx 文件
# 考虑到中文文件名，使用 os.listdir 遍历
docx_files_in_dir = [f for f in os.listdir(input_docx_dir) if f.endswith('.docx')]

# 遍历每个 DOCX 文件
for docx_file_name in docx_files_in_dir:
    print(f"\n正在处理文件: {docx_file_name}")
    
    # 构造完整输入文件路径
    input_file_path = os.path.join(input_docx_dir, docx_file_name)
    try:
        # 使用 python-docx 库读取 docx 文件并提取所有段落的文本
        # 注意：如果 JSON 字符串可能分布在多个段落或表格中，需要更复杂的逻辑来拼接
        # 但根据你之前提供的JSON片段，它看起来是作为连续文本存在于文档中
        document = Document(input_file_path)
        full_text = []
        for para in document.paragraphs:
            full_text.append(para.text)

        # 将所有段落文本拼接成一个字符串
        json_content = "\n".join(full_text)

        # 检查是否提取到了有效的JSON内容
        if not json_content.strip():
            print(f"警告: 文件 '{docx_file_name}' 中未提取到任何文本内容，跳过。")
            continue

        # 解析 JSON 内容
        data = json.loads(json_content)

        # 将 JSON 数据转换为 DataFrame
        df = pd.DataFrame(data)

        # 构造输出 Excel 文件的名称和完整路径
        excel_filename = docx_file_name.replace('.docx', '.xlsx')
        excel_output_path = os.path.join(output_excel_dir, excel_filename)

        # 将 DataFrame 保存为 Excel 文件
        df.to_excel(excel_output_path, index=False)
        print(f"已成功将 '{docx_file_name}' 转换为 '{excel_output_path}'")

    except FileNotFoundError:
        print(f"错误: 文件 '{input_file_path}' 未找到。请检查文件路径是否正确。")
    except json.JSONDecodeError as e:
        print(f"错误: 文件 '{docx_file_name}' 的内容不是有效的 JSON 格式。详细信息: {e}")
        # 打印出提取到的可能导致错误的文本内容，有助于调试
        print(f"尝试解析的文本内容片段（前500字符）: {json_content[:500]}")
    except Exception as e:
        print(f"处理文件 '{docx_file_name}' 时发生未知错误: {e}")
        # 如果是其他关于docx库的错误，这里也会捕获
        print(f"请检查 '{docx_file_name}' 是否是有效的或未损坏的DOCX文件。")

    print("\n所有文件处理完毕。")
