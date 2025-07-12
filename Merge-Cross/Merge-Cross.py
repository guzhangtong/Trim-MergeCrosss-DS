import pandas as pd
import os
import re  # 导入正则表达式模块，用于提取浓度数值
import numpy as np

# ---------------------------- path -------------------------------
# 获取当前脚本的绝对路径
script_directory = os.path.dirname(os.path.abspath(__file__))

# 定义包含5个Excel文件的文件夹路径
excel_folder_path = os.path.join(script_directory, "一步式-1永定河docx2excel")

# ---------------------------- read and prepare multiple excel files -------------------------------
# 存储所有Excel文件内容的DataFrame列表，附带文件序号
# 需要按文件名排序，以确保df1, df2, ... 的顺序是确定的
dfs_with_index = []

# 定义新的列名，与原始Excel文件一致，用于后续标准化
standard_column_names = ['抗生素名称', '浓度数值及单位', '水体类型', '采样信息', '原文上下文']

# 检查文件夹是否存在
if not os.path.exists(excel_folder_path):
    print(
        f"Error: The folder '{excel_folder_path}' was not found. Please ensure it exists and is located next to the script.")
    exit()

# 获取所有xlsx文件，并按文件名排序
excel_files = sorted([f for f in os.listdir(excel_folder_path) if f.endswith(".xlsx")])

if not excel_files:
    print("No Excel files found in the specified folder.")
    exit()

for i, filename in enumerate(excel_files):
    file_path = os.path.join(excel_folder_path, filename)
    try:
        # 根据您的说明，所有Excel文件的第一行都是列名。
        # 直接使用 header=0 读取，然后强制设置列名。
        df = pd.read_excel(file_path, header=0)

        # 检查DataFrame的列数是否至少包含我们需要的标准列
        if df.shape[1] < len(standard_column_names):
            print(f"Warning: File {filename} has fewer than {len(standard_column_names)} columns. Skipping.")
            continue # 跳过此文件

        # 强制设置前几列的列名，无论原始列名是什么
        # 这里假设Excel文件的列顺序是固定的，前5列就是我们需要的标准列
        df.columns = standard_column_names + list(df.columns[len(standard_column_names):])
        # 确保只保留我们需要的标准列，丢弃多余的列
        df = df[standard_column_names]

        # 添加df名称和源文件信息
        df['df_name'] = f'df{i + 1}'
        df['source_file'] = filename

        # 统一化抗生素名称和浓度值，便于后续匹配和比较
        df['抗生素名称_cleaned'] = df['抗生素名称'].astype(str).str.lower().str.strip()

        # 尝试从 '浓度数值及单位' 中提取数值，并进行清洗
        # 增强 extract_numeric_concentration 函数
        def extract_numeric_concentration(concentration_str):
            if pd.isna(concentration_str):
                return np.nan
            s = str(concentration_str).strip()

            # 匹配各种数值模式：
            # 1. 纯数字（整数、小数）: (\d+(\.\d+)?)
            # 2. 科学计数法: \d+(\.\d+)?[eE][+-]?\d+
            # 3. 以 < 或 > 开头的数字: [<>]\s*(\d+(\.\d+)?)
            # 4. 数字范围 (只取第一个数字作为代表): (\d+(\.\d+)?)\s*[-~—]\s*\d+(\.\d+)?
            # 优先匹配更精确的数字，而不是范围等。
            # 最终的正则表达式会尝试从字符串中提取第一个符合数字模式的数值。
            # 这里是为了捕获尽可能多的数字，如果遇到复杂表示（如范围），会取第一个数字。
            match = re.search(r'[+-]?(\d+(\.\d*)?([eE][+-]?\d+)?|[<>]\s*\d+(\.\d*)?)', s) # 更广义的数字匹配
            if match:
                try:
                    # 移除可能的 < 或 > 符号，然后尝试转换为浮点数
                    numeric_part = match.group(0).replace('<', '').replace('>', '').strip()
                    return float(numeric_part)
                except ValueError:
                    return np.nan  # 转换失败
            return np.nan # 没有匹配到任何数值

        df['浓度数值_extracted'] = df['浓度数值及单位'].apply(extract_numeric_concentration)

        # 在单个df内部处理重复抗生素浓度：对于相同的 '抗生素名称_cleaned' 和 '水体类型' 组合，保留第一条记录
        df_processed = df.drop_duplicates(subset=['抗生素名称_cleaned', '水体类型'], keep='first').copy()

        dfs_with_index.append(df_processed)
    except Exception as e:
        print(f"Error reading or processing {filename}: {e}")

if not dfs_with_index:
    print("No valid Excel files processed.")
    exit()

# ---------------------------- Core Merge and Aggregation Logic --------------------------
# 创建一个用于最终合并的基准DataFrame，包含所有不重复的 '抗生素名称_cleaned' 和 '水体类型' 组合
all_unique_antibiotics = pd.concat([df[['抗生素名称_cleaned', '水体类型']].drop_duplicates() for df in dfs_with_index])
all_unique_antibiotics = all_unique_antibiotics.drop_duplicates().reset_index(drop=True)

final_merged_df = all_unique_antibiotics.copy()

# 动态合并每个df的数据
for i, df in enumerate(dfs_with_index):
    df_name = f'df{i + 1}'
    # 选择需要合并的列：抗生素名称、水体类型、浓度数值及单位和提取的数值
    temp_df = df[['抗生素名称_cleaned', '水体类型', '浓度数值及单位', '浓度数值_extracted']].copy()
    temp_df.rename(columns={
        '浓度数值及单位': f'浓度数值及单位_{df_name}',
        '浓度数值_extracted': f'浓度数值_extracted_{df_name}'
    }, inplace=True)

    # 执行左连接，将每个df的数据添加到 final_merged_df 中
    final_merged_df = pd.merge(final_merged_df, temp_df,
                               on=['抗生素名称_cleaned', '水体类型'],
                               how='left')

# ---------------------------- Generate _merge column ----------------------------
# 根据图片示意，_merge 列应记录出现该抗生素的df名称
final_merged_df['_merge_list'] = ''
for i in range(len(dfs_with_index)):
    df_name = f'df{i + 1}'
    col_name = f'浓度数值及单位_{df_name}'
    # 对于每个浓度列，如果不是NaN，则表示该df包含此条目
    final_merged_df['_merge_list'] = final_merged_df.apply(
        lambda row: row['_merge_list'] + (f',{df_name}' if pd.notna(row.get(col_name)) else ''),
        axis=1
    )
# 清理_merge_list，移除开头的逗号
final_merged_df['_merge'] = final_merged_df['_merge_list'].str.lstrip(',')


# ---------------------------- Generate ALL MATCH column ----------------------------
# 判断某种抗生素在各个含有它的excel中浓度是否一致
def check_all_match_final(row, num_dfs):
    concentrations = []
    for i in range(num_dfs):
        col_name = f'浓度数值_extracted_df{i + 1}'
        if pd.notna(row.get(col_name)):
            concentrations.append(row[col_name])

    # 根据您的要求："抗生素浓度种类小于等于1的ALL MATCH不填"
    # 并且您明确了“目的是比较 不同来源（df1, df2等）提供的浓度值 是否一致”
    # 这里的concentrations列表包含了来自不同df的有效浓度值
    if len(concentrations) <= 1: # 只有0或1个有效浓度值，不进行ALL MATCH判断
        return np.nan
    else:  # 浓度记录超过一条（来自不同来源的有效数值），进行比较
        first_concentration = concentrations[0]
        # 使用np.isclose进行浮点数比较，atoll 容差用于处理浮点数精度问题
        return 'T' if all(np.isclose(c, first_concentration, atol=1e-9) for c in concentrations) else 'F'


final_merged_df['ALL MATCH'] = final_merged_df.apply(lambda row: check_all_match_final(row, len(dfs_with_index)),
                                                     axis=1)

# ---------------------------- Final Cleanup and Renaming ----------------------------
# 最终抗生素名称只保留一个
final_merged_df.rename(columns={'抗生素名称_cleaned': '抗生素名称'}, inplace=True)

# 重新排序和选择最终输出的列，以符合示意图的顺序和要求
output_columns = ['_merge', '抗生素名称']

# 动态添加浓度列
for i in range(len(dfs_with_index)):
    output_columns.append(f'浓度数值及单位_df{i + 1}')

output_columns.append('ALL MATCH')

# 筛选并重新排序列
# 确保所有要输出的列都存在于 final_merged_df 中，否则会报错
actual_output_columns = [col for col in output_columns if col in final_merged_df.columns]
final_output_df = final_merged_df[actual_output_columns].copy()

# ---------------------------- Save Final Excel File --------------------------
output_excel_filename = '1永定河merged_cross_validation_result7.xlsx'  # 更改文件名，表示第七版
output_excel_path = os.path.join(script_directory, output_excel_filename)

# 将最终的 DataFrame 保存到 Excel 文件
final_output_df.to_excel(output_excel_path, index=False)
print(f"\nFinal merged results saved to: {output_excel_path}")