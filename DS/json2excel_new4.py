import json
import pandas as pd


def json_to_excel(json_filename, excel_filename):
    """
    Reads a JSON file (e.g., 抗生素浓度数据X.json), extracts relevant data from
    deepseek_chat, deepseek_coder, ChatGPT_4o_mini, and ChatGPT_41_mini iteration types,
    and saves it to an Excel file (e.g., 抗生素浓度数据X.xlsx).

    The Excel format will be aligned with the expected structure for antibiotic concentration data.

    Args:
        json_filename (str): The path to the input JSON file.
        excel_filename (str): The path to the output Excel file.
    """
    try:
        # Open and load the JSON data from the specified file.
        with open(json_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract the top-level PaperID key (e.g., "PaperID_0", "PaperID_1", "PaperID_2").
        # Assuming there is only one top-level PaperID key per JSON file.
        paper_id_key = list(data.keys())[0]
        paper_data = data[paper_id_key]

        # Initialize a list to store all extracted records, which will later be converted to a DataFrame.
        all_records = []

        # Define all iteration types to process.
        iteration_types = ["deepseek_chat", "deepseek_coder", "ChatGPT_4o_mini", "ChatGPT_41_mini"]

        for iteration_type in iteration_types:
            if iteration_type in paper_data:
                iteration_data = paper_data[iteration_type]

                # Process '话术一' for the current iteration type.
                if "话术一" in iteration_data:
                    ws1_content = iteration_data["话术一"]
                    # Check if '话术一' contains an 'antibiotics' list (common for deepseek_chat, ChatGPT_4o_mini)
                    # or a direct dictionary (common for deepseek_coder).
                    if isinstance(ws1_content, dict) and (
                    ws1_content_list := ws1_content.get("antibiotics")) is not None:
                        # If it's a list under 'antibiotics'
                        for record in ws1_content_list:
                            current_record = record.copy()  # Create a copy to avoid modifying original dict

                            # Handle "Value and Unit" and "Location & Date" for deepseek_chat specifically.
                            # Other models (ChatGPT_4o_mini, ChatGPT_41_mini) seem to have these parsed already.
                            if "Value and Unit" in current_record:
                                value_unit = current_record.pop("Value and Unit", "").replace("–", "-")
                                if " " in value_unit and any(unit in value_unit for unit in
                                                             ["ng/L", "ng/g", "ng L−1", "mg L−1", "μg L−1", "μg/L"]):
                                    parts = value_unit.rsplit(' ', 1)
                                    current_record['Value'] = parts[0].strip()
                                    current_record['Unit'] = parts[1].strip()
                                else:
                                    current_record['Value'] = value_unit.strip()
                                    current_record['Unit'] = ''  # Assign empty if unit cannot be parsed

                            if "Location & Date" in current_record:
                                loc_date = current_record.pop("Location & Date", "")
                                if "," in loc_date:
                                    parts = loc_date.split(', ', 1)
                                    current_record['Location'] = parts[0].strip()
                                    current_record['Date'] = parts[1].strip()
                                else:
                                    current_record['Location'] = loc_date.strip()
                                    current_record['Date'] = ''

                            current_record['Iteration_Type'] = iteration_type
                            current_record['Speech_Act'] = '话术一'
                            all_records.append(current_record)
                    elif isinstance(ws1_content, dict) and (ws1_content_list := ws1_content.get("data")) is not None:
                        # If it's a list under 'data' (common for ChatGPT_4o_mini, ChatGPT_41_mini)
                        for record in ws1_content_list:
                            current_record = record.copy()
                            current_record['Iteration_Type'] = iteration_type
                            current_record['Speech_Act'] = '话术一'
                            all_records.append(current_record)
                    elif isinstance(ws1_content, dict):
                        # If '话术一' is a direct dictionary (common for deepseek_coder)
                        current_record = ws1_content.copy()
                        current_record['Iteration_Type'] = iteration_type
                        current_record['Speech_Act'] = '话术一'
                        all_records.append(current_record)

                # Process '话术二' for the current iteration type.
                if "话术二" in iteration_data:
                    ws2_content = iteration_data["话术二"]
                    # Check if '话术二' contains an 'antibiotics' list or 'data' list
                    ws2_data_keys = ["antibiotic_data", "monitoring_data", "antibiotics", "data"]
                    ws2_content_list = []
                    for key in ws2_data_keys:
                        if isinstance(ws2_content, dict) and (temp_list := ws2_content.get(key)) is not None:
                            ws2_content_list = temp_list
                            break

                    if ws2_content_list:  # If a list was found
                        for record in ws2_content_list:
                            current_record = record.copy()

                            # Handle "Value and Unit" and "Location & Date" for deepseek_chat specifically.
                            if "Value and Unit" in current_record:
                                value_unit = current_record.pop("Value and Unit", "").replace("–", "-")
                                if " " in value_unit and any(unit in value_unit for unit in
                                                             ["ng/L", "ng/g", "ng L−1", "mg L−1", "μg L−1", "μg/L"]):
                                    parts = value_unit.rsplit(' ', 1)
                                    current_record['Value'] = parts[0].strip()
                                    current_record['Unit'] = parts[1].strip()
                                else:
                                    current_record['Value'] = value_unit.strip()
                                    current_record['Unit'] = ''

                            if "Location & Date" in current_record:
                                loc_date = current_record.pop("Location & Date", "")
                                if "," in loc_date:
                                    parts = loc_date.split(', ', 1)
                                    current_record['Location'] = parts[0].strip()
                                    current_record['Date'] = parts[1].strip()
                                else:
                                    current_record['Location'] = loc_date.strip()
                                    current_record['Date'] = ''

                            current_record['Iteration_Type'] = iteration_type
                            current_record['Speech_Act'] = '话术二'
                            all_records.append(current_record)
                    elif isinstance(ws2_content, dict):
                        # If '话术二' is a direct dictionary (common for deepseek_coder)
                        current_record = ws2_content.copy()
                        current_record['Iteration_Type'] = iteration_type
                        current_record['Speech_Act'] = '话术二'
                        all_records.append(current_record)

        # Create a DataFrame from all collected records.
        df = pd.DataFrame(all_records)

        # Define a consistent column order to match your "ds实例表格" (assuming these are the desired columns).
        # Please adjust these column names if your actual "ds实例表格" has different headers.
        standard_columns = [
            "PaperID", "Iteration_Type", "Speech_Act", "Name", "Water",
            "Value", "Unit", "Location", "Date", "Context"
        ]

        # Reorder columns. Any columns in standard_columns not present in df will be added as NaN (empty in Excel).
        # Any columns in df not in standard_columns will be dropped.
        df_reordered = df.reindex(columns=standard_columns)

        # Save the DataFrame to an Excel file.
        # index=False prevents pandas from writing the DataFrame index as a column in Excel.
        df_reordered.to_excel(excel_filename, index=False)
        print(f"成功将 {json_filename} 转换为 {excel_filename}")

    except FileNotFoundError:
        print(f"错误: 文件 '{json_filename}' 未找到。请确保它与脚本在同一目录下。")
    except json.JSONDecodeError:
        print(f"错误: 无法解析 '{json_filename}' 中的 JSON。请检查文件格式是否规范。")
    except Exception as e:
        print(f"发生了一个意外错误在处理 {json_filename}: {e}")


# --- Main execution part ---
if __name__ == "__main__":
    # List of input JSON files generated in the previous step.
    json_files = [
        "抗生素浓度数据1.json",
        "抗生素浓度数据2.json",
        "抗生素浓度数据3.json"
    ]

    # Iterate through the JSON files and convert each to an Excel file.
    for i, json_file in enumerate(json_files):
        # Construct the output Excel filename based on the JSON filename.
        # Replace ".json" with ".xlsx" and ensure the base name matches.
        excel_file = json_file.replace(".json", ".xlsx")
        json_to_excel(json_file, excel_file)