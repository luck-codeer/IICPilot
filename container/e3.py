import os  
import re  
import subprocess
import re  
import subprocess  
import time  
import os
def run_bash_script_and_measure_time(script_path):  
    # start_time = time.time()  # 获取开始时间  
  
    # 使用subprocess.run运行bash脚本，并确保它在一个shell中执行  
    # 假设rtl2gds.sh是可执行的，并且位于当前工作目录或你的PATH中  
    result = subprocess.run(['bash', script_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
    # for filename in os.listdir("/IICPilot/rtl2gds_2/rtl2gds/test/verilog/10000_gate"):  
    #     if filename.endswith('.v'):  
    #         # 提取文件名（不包括.v扩展名）作为新的值  
    #         base_filename = os.path.splitext(filename)[0]  
    # 检查是否有错误输出  
    if result.stderr:  
        print(f"Error occurred while running the script:\n{result.stderr.decode()}")  
  
    # end_time = time.time()  # 获取结束时间  
    # execution_time = end_time - start_time  # 计算执行时间  
    # with open("/IICPilot/dataset.txt", 'a') as dataset:  
    #     dataset.write(f"{base_filename} runtime:")
    #     dataset.write(str(execution_time))
    #     dataset.write("\n")
    # print(f"The script {script_path} finished in {execution_time:.2f} seconds.")  

def extract_last_values_from_file(file_path, search_strings,filename):    
    last_values = {}    
    count = 0  # 初始化计数器  
    max_prints = 8  # 设置最大打印次数
    # with open("/IICPilot/dataset.txt", 'a') as dataset:  
    #     dataset.write(f"{filename} :")
    with open(file_path, 'r') as file:    
        for line in reversed(file.readlines()):  # 从文件末尾开始读取    
            for search_string in search_strings:    
                # 搜索字符串后面可能紧跟着冒号和空格  
                if search_string.strip(':') in line.strip():    
                    # 假设数字和文本之间有一个或多个空格  
                    with open("/IICPilot/container/dataset/dataset.txt", 'a') as dataset:  
                        dataset.write(str(line))
                    print(line)
                    count += 1  # 每当找到匹配项时增加计数器  
            if count >= max_prints:  
                break  # 当达到最大打印次数时跳出循环 
    with open("/IICPilot/container/dataset/dataset.txt", 'a') as dataset:  
        dataset.write("\n")



# 假设这是你的.v文件所在的目录  
verilog_files_dir = '/IICPilot/rtl2gds_2/rtl2gds/test/verilog/10000_gate'  
  
# 这是你的shell脚本的路径  
shell_script_path = '/IICPilot/rtl2gds_2/rtl2gds/rtl2gds.sh'  
  
# 确保shell脚本存在  
if not os.path.exists(shell_script_path):  
    print(f"Error: Shell script {shell_script_path} does not exist.")  
    exit(1)  
  
# 遍历.v文件目录中的文件  
for filename in os.listdir(verilog_files_dir):  
    if filename.endswith('.v'):  
        # 提取文件名（不包括.v扩展名）作为新的值  
        base_filename = os.path.splitext(filename)[0]  
        new_rtl_file_path = f'$PROJ_PATH/test/verilog/10000_gate/{base_filename}.v'  
        
        # 读取shell脚本内容  
        with open(shell_script_path, 'r', encoding='utf-8') as file:  
            content = file.read()  
          
        # 使用正则表达式替换RTL_FILE的值  
        # 假设RTL_FILE赋值是单独一行，并且没有其他复杂的shell逻辑在那一行  
        new_value_pattern = r'NEW_VALUE="(.*?)"'  
        new_value_replacement = f'NEW_VALUE="{base_filename}"'  
        new_content = re.sub(new_value_pattern, new_value_replacement, content)  
        pattern = r'export RTL_FILE=\$PROJ_PATH/test/verilog/10000_gate/([^ ]+)\.v'    
        replacement = f'export RTL_FILE={new_rtl_file_path}'  
        new_content = re.sub(pattern, replacement, new_content, flags=re.MULTILINE)  

        # 写入更新后的shell脚本内容  
        with open(shell_script_path, 'w', encoding='utf-8') as file:  
            file.write(new_content)  
        # result = subprocess.run(['python3', "/IICPilot/dataset_requirement.py"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
  
        # # 检查是否有输出或错误  
        # if result.stdout:  
        #     print("Script output:")  
        #     print(result.stdout.decode())  
        # if result.stderr:  
        #     print("Script error:")  
        #     print(result.stderr.decode())  
        #更换设计名
        os.chdir("/IICPilot/rtl2gds_2/rtl2gds")
        # 原始bash脚本文件名  
        # 获取当前工作目录  
        current_path = os.getcwd()  
        
        # 打印当前工作目录  
        # print("当前路径是:", current_path)

        bash_script_filename = 'rtl2gds.sh'  # 请替换为你的bash脚本名  
        run_bash_script_and_measure_time("rtl2gds.sh")
        print("1.finish")

        start_time = time.time()  # 获取开始时间  
        # 使用subprocess.run运行bash脚本，并确保它在一个shell中执行  
        # 假设rtl2gds.sh是可执行的，并且位于当前工作目录或你的PATH中  
        run_bash_script_and_measure_time("rtl2gds_test.sh")
        end_time = time.time()  # 获取结束时间  
        print("2.finish")
        execution_time = end_time - start_time  # 计算执行时间  
        with open("/IICPilot/container/dataset/dataset.txt", 'a') as dataset:  
            dataset.write(f"{base_filename} placement runtime:")
            dataset.write(str(execution_time))
            dataset.write("\n")


        # start_time = time.time()  # 获取开始时间  
        # # 使用subprocess.run运行bash脚本，并确保它在一个shell中执行  
        # # 假设rtl2gds.sh是可执行的，并且位于当前工作目录或你的PATH中  
        # run_bash_script_and_measure_time("rtl2gds_test.sh")
        # end_time = time.time()  # 获取结束时间  
        # print("3.finish")
        # execution_time = end_time - start_time  # 计算执行时间  
        # with open("/IICPilot/container/dataset/dataset.txt", 'a') as dataset:  
        #     dataset.write(f"{base_filename} routing runtime:")
        #     dataset.write(str(execution_time))
        #     dataset.write("\n")


        
        print(f"The script finished in {execution_time:.2f} seconds.")  
        # 定义要搜索的字符串  
        search_strings = [  
            "Number of wires:",  
            "Number of wire bits:",  
            "Number of public wires:",  
            "Number of public wire bits:",  
            "Number of memories:",  
            "Number of memory bits:",  
            "Number of processes:",  
            "Number of cells:"  
        ]  
        
        # 调用函数并打印结果  
        file_path = '/IICPilot/rtl2gds_2/rtl2gds/result/verilog/synth_stat.txt'  
        last_values = extract_last_values_from_file(file_path, search_strings,base_filename)  
                # print(new_content)
        # 输出更新信息或执行其他操作...  
        # print(f"Updated {shell_script_path} with RTL_FILE={new_rtl_file_path}")  
          
        # 如果只需要更新一次就退出循环（只处理一个.v文件），可以在这里添加break  
        # break