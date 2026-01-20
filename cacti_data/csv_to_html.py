import csv
import os
from collections import defaultdict
def csv_to_html(csv_file_path, html_file_path=None, room_column_name="机房"):
    """
    将CSV文件转换为HTML表格页面，支持跨多行合并相同机房名称的单元格
    参数:
        csv_file_path: CSV文件路径
        html_file_path: 输出HTML文件路径，默认为与CSV同目录同名称的.html文件
        room_column_name: 机房列的标题名称，默认为"机房"
    """
    # 如果未指定HTML文件路径，则默认使用CSV文件的路径和名称
    if html_file_path is None:
        file_name = os.path.splitext(os.path.basename(csv_file_path))[0]
        html_file_path = os.path.join(os.path.dirname(csv_file_path), f"{file_name}.html")
    # 读取CSV数据
    data = []
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            data.append(row)
    if not data:
        print("CSV文件为空或无法读取")
        return
    # 查找机房列的索引
    room_column_index = None
    for i, header in enumerate(data[0]):
        if room_column_name in header:
            room_column_index = i
            break
    # 如果找到机房列，则按机房分组；否则按原方式处理
    grouped_data = []
    if room_column_index is not None:
        print(f"找到机房列，将合并所有相同名称的单元格")
        # 按机房名称分组
        room_groups = defaultdict(list)
        for row in data[1:]:  # 跳过表头
            room_name = row[room_column_index]
            room_groups[room_name].append(row)
        # 保持原始顺序的机房列表
        seen_rooms = []
        for row in data[1:]:
            room_name = row[room_column_index]
            if room_name not in seen_rooms:
                seen_rooms.append(room_name)
        # 构建分组数据
        for room in seen_rooms:
            grouped_data.extend(room_groups[room])
    else:
        # 没有找到机房列，使用原始数据
        grouped_data = data[1:]
    # 生成HTML内容
    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSV数据表格</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            line-height: 1.6; 
        }
        h1 { 
            color: #333; 
            border-bottom: 2px solid #4CAF50; 
            padding-bottom: 10px;
            font-size: 1.5em; /* 减小标题字号 */
            margin-bottom: 15px; /* 减小下边距 */
        }
        .table-container { 
            overflow-x: auto; 
            margin-top: 15px; 
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin: 15px 0; 
        }
        th, td { 
            padding: 8px 10px; /* 减小单元格内边距 */
            text-align: left; 
            border-bottom: 1px solid #ddd; 
        }
        th { 
            background-color: #4CAF50; 
            color: white;
            font-size: 0.9em; /* 减小表头字号 */
        }
        tr:hover { 
            background-color: #f5f5f5; 
        }
        tr:nth-child(even) { 
            background-color: #f9f9f9; 
        }
        /* 响应式调整 */
        @media (max-width: 768px) {
            body { margin: 10px; }
            h1 { font-size: 1.2em; }
            th, td { padding: 6px 8px; font-size: 0.85em; }
        }
    </style>
</head>
<body>
    <h1>CSV数据表格展示</h1>
    <div class="table-container">
        <table>
"""
    # 添加表头
    html_content += "            <tr>\n"
    for header in data[0]:
        html_content += f"                <th>{header}</th>\n"
    html_content += "            </tr>\n"
    # 处理表格内容
    if room_column_index is not None:
        # 处理已分组的数据，合并相同机房的单元格
        current_index = 0
        while current_index < len(grouped_data):
            current_room = grouped_data[current_index][room_column_index]
            # 计算当前机房有多少行数据
            span = 1
            while (current_index + span < len(grouped_data) and 
                grouped_data[current_index + span][room_column_index] == current_room):
                span += 1
            # 生成当前行的HTML（包含合并的机房单元格）
            html_content += "            <tr>\n"
            for col_index, cell in enumerate(grouped_data[current_index]):
                if col_index == room_column_index:
                    # 机房列，需要合并
                    html_content += f"                <td rowspan=\"{span}\">{cell}</td>\n"
                else:
                    html_content += f"                <td>{cell}</td>\n"
            html_content += "            </tr>\n"
            # 处理同机房的其他行（不包含机房列，因为已经合并）
            current_index += 1
            for i in range(1, span):
                html_content += "            <tr>\n"
                for col_index, cell in enumerate(grouped_data[current_index]):
                    if col_index != room_column_index:  # 跳过机房列
                        html_content += f"                <td>{cell}</td>\n"
                html_content += "            </tr>\n"
                current_index += 1
    else:
        print(f"未找到'{room_column_name}'列，不进行单元格合并")
        # 添加表格内容（不合并）
        for row in grouped_data:
            html_content += "            <tr>\n"
            for cell in row:
                html_content += f"                <td>{cell}</td>\n"
            html_content += "            </tr>\n"
    # 完成HTML内容
    html_content += """        </table>
    </div>
</body>
</html>"""
    # 写入HTML文件
    with open(html_file_path, 'w', encoding='utf-8') as htmlfile:
        htmlfile.write(html_content)
    print(f"HTML文件已生成: {html_file_path}")
# 使用示例
if __name__ == "__main__":
    # 替换为你的CSV文件路径
    csv_file = "D:\\0Work\\Code\\My-Tools-for-Devops\\output_custom\\daily_cacti_data.csv"
    # 可以指定机房列的名称，如csv_to_html(csv_file, room_column_name="数据中心")
    csv_to_html(csv_file)