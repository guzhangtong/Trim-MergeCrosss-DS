import json

def split_large_json_by_paper_id(input_filename="抗生素浓度数据.txt"):
    """
    Reads a large JSON file (新4.txt), which contains data for multiple PaperIDs
    and different iteration types. It then splits this data, creating a separate
    JSON file for each PaperID, with specific output filenames:
    "抗生素浓度数据1.json", "抗生素浓度数据2.json", "抗生素浓度数据3.json".
    """
    try:
        # Step 1: Read the content of 新4.txt
        with open(input_filename, 'r', encoding='utf-8') as f:
            full_data = json.load(f)

        # Define the mapping from internal PaperID_X keys to desired output filenames.
        # This explicit mapping ensures correct naming for each PaperID.
        output_filenames_map = {
            "PaperID_0": "抗生素浓度数据1.json",
            "PaperID_1": "抗生素浓度数据2.json",
            "PaperID_2": "抗生素浓度数据3.json",
            # 如果将来有更多的 PaperID (如 PaperID_3, PaperID_4 等)，
            # 您可以在这里继续添加映射关系。
        }

        # Iterate through the top-level keys (e.g., "PaperID_0", "PaperID_1", "PaperID_2")
        # in the full_data.
        for paper_id_key, paper_content in full_data.items():
            # Check if the current paper_id_key is in our predefined mapping.
            if paper_id_key in output_filenames_map:
                # Get the desired output filename from the map.
                output_filename = output_filenames_map[paper_id_key]

                # Create a new dictionary that contains only the data for the current PaperID.
                # This ensures each output JSON file is a standard, valid JSON document
                # with a single top-level key corresponding to its PaperID.
                output_data = {paper_id_key: paper_content}

                # Write the new dictionary to a separate JSON file.
                # indent=2 makes the JSON output more readable with 2-space indentation.
                # ensure_ascii=False ensures non-ASCII characters (like Chinese) are preserved directly,
                # rather than being converted to Unicode escape sequences.
                with open(output_filename, 'w', encoding='utf-8') as outfile:
                    json.dump(output_data, outfile, indent=2, ensure_ascii=False)
                print(f"成功创建文件: {output_filename}")
            else:
                # If an unexpected PaperID key is found, print a warning.
                print(f"警告: 在 {input_filename} 中找到未知 PaperID '{paper_id_key}'，未为其生成文件。")

    except FileNotFoundError:
        print(f"错误: 文件 '{input_filename}' 未找到。请确保它与脚本在同一目录下。")
    except json.JSONDecodeError:
        print(f"错误: 无法解析 '{input_filename}' 中的 JSON。请检查文件格式是否规范。")
    except Exception as e:
        print(f"发生了一个意外错误: {e}")

# 调用函数来执行文件拆分操作
if __name__ == "__main__":
    split_large_json_by_paper_id()