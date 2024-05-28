# 假设您的文本数据存储在名为 'dataset1.txt' 的文件中  
  
# 读取文件内容  
with open('./dataset/dataset1.txt', 'r') as file:  
    lines = file.readlines()  
  
# 初始化CSV文件的列名，不包含被过滤的属性  
header = ['design', 'runtime', 'cells', 'public_wire_bits', 'public_wires', 'wire_bits', 'wires']  
  
# 初始化一个列表来存储CSV数据行  
csv_data = [','.join(header) + '\n']  # 添加表头到CSV数据  
  
# 当前是否在处理一个设计的数据块  
processing_design = False  
current_design = {}  
  
# 遍历文件的每一行  
for line in lines:  
    # 跳过空行  
    if not line.strip():  
        continue  
      
    # 检查是否开始一个新的设计数据块  
    if ' runtime:' in line:  
        # 如果之前已经处理了一个设计，则将其添加到CSV数据中  
        if processing_design:  
            # 过滤掉不想要的属性  
            csv_row = [str(current_design['design']), str(current_design['runtime'])]  
            for key in ['cells', 'public_wire_bits', 'public_wires', 'wire_bits', 'wires']:  
                csv_row.append(str(current_design[key]))  
            csv_data.append(','.join(csv_row) + '\n')  
          
        # 重置当前设计的数据  
        processing_design = True  
        current_design = {'design': line.split(' runtime:')[0].strip()}  
        current_design['runtime'] = float(line.split(' runtime:')[1].strip())  
    else:  
        # 提取属性和值，但跳过不想要的属性  
        key, value_str = line.split(':')  
        key = key.strip().replace('Number of ', '').replace(' ', '_')  
        if key not in ['processes', 'memory_bits', 'memories']:  # 过滤掉不想要的属性  
            value = int(value_str.strip())  
            current_design[key] = value  
  
# 添加最后一个设计的数据（如果有的话）  
if processing_design:  
    csv_row = [str(current_design['design']), str(current_design['runtime'])]  
    for key in ['cells', 'public_wire_bits', 'public_wires', 'wire_bits', 'wires']:  
        csv_row.append(str(current_design[key]))  
    csv_data.append(','.join(csv_row) + '\n')  
  
# 写入CSV文件  
with open('./csv/designs.csv', 'w', newline='') as csvfile:  
    csvfile.writelines(csv_data)  
  
print("CSV文件已成功创建！")



