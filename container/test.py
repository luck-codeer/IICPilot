# def extract_last_values_from_file(file_path):  
#     last_values = {}  
#     search_strings_dict = {  
#         "Number of wires:": 'wires',  
#         "Number of wire bits:": 'wire_bits',  
#         "Number of public wires:": 'public_wires',  
#         "Number of public wire bits:": 'public_wire_bits',  
#         "Number of memories:": 'memories',  # 注意：如果不需要这个值，可以从字典中删除  
#         "Number of memory bits:": 'memory_bits',  # 注意：如果不需要这个值，可以从字典中删除  
#         "Number of processes:": 'processes',  # 注意：如果不需要这个值，可以从字典中删除  
#         "Number of cells:": 'cells'  
#     }  
      
#     with open(file_path, 'r') as file:    
#         for line in reversed(file.readlines()): 
#             print(line)
#             for search_string, key in search_strings_dict.items():  
#                 print(search_string)
#                 if search_string in line:  
#                     # 提取冒号后的值（假设它后面跟着一个或多个空格和数字）  
#                     value = line.split(search_string, 1)[-1].strip().split()[0] 
#                     # 尝试将值转换为整数（如果可能）  
#                     try:  
#                         last_values[key] = int(value)  
#                     except ValueError:  
#                         last_values[key] = value  
#                     break  # 找到匹配项后，跳出内部循环  
#             # break  # 因为我们是从文件末尾开始读取的，所以第一个匹配项就是我们要找的  
  
#     # 如果需要额外的 'cpu_num' 值（这里假设它是已知的或者可以从其他地方获取）  
#     # last_values['cpu_num'] = 2  # 举例值  
  
#     return last_values  
  
# # 使用函数  
# file_path = "/home/dell/jiangzesong/IICPilot/rtl2gds_2/rtl2gds/result/verilog/synth_stat.txt"  # 替换为您的文件路径  
# picorv32a_features = extract_last_values_from_file(file_path)  

# picorv32a_features['cpu_num'] = 2
# print(picorv32a_features)
import os
os.environ["OPENAI_API_KEY"] = "sk-proj-uvZ8UZfsA7LkDczgL2olT3BlbkFJxVeiSS9xjn8RdE3VC6q2"
# os.environ["OPENAI_API_BASE"] = 'https://api.xty.app/v1'
from langchain_core.tools import tool
from typing import Annotated, List, Tuple, Union
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Optional
import subprocess
from langchain_experimental.utilities import PythonREPL
from typing_extensions import TypedDict
from typing import Any, Callable, List, Optional, TypedDict, Union
import yaml
import sys
from kubernetes import client, config  
from kubernetes.client import ApiClient  
from kubernetes.client.rest import ApiException  
from kubernetes.stream import stream
from io import StringIO  
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, StateGraph
import io
from autogen.io.base import IOStream
import time
def run_container(
    yaml_file: Annotated[str,"the configuration file used for running container"],
    command: Annotated[str,"the command used to run container"],
    )->Annotated[str, "Result of running container"]:
    "Run the container with the configuration file."
    # command='cd /IICPilot/rtl2gds_1/rtl2gds && bash rtl2gds.sh'
    exec_command = ['bash', '-c', command]  
    # create an instance of the API class
    config.load_kube_config()
    api_instance = client.CoreV1Api()
    # 从YAML文件加载Pod定义 
    os.chdir("/home/dell/jiangzesong/IICPilot/container") 
    with open(yaml_file, 'r') as f:  
        pod_yaml = f.read()  
    # 使用ApiClient的sanitize_for_serialization方法处理YAML内容  
    pod_body = yaml.safe_load(pod_yaml)
    pod_body = ApiClient().sanitize_for_serialization(pod_body)
    resp = stream(api_instance.connect_get_namespaced_pod_exec, pod_body['metadata']['name'], 'default',
                command=exec_command,
                stderr=True, stdin=False,
                stdout=True, tty=False)
    # 打印命令执行结果  
    for line in resp:  
        print(line, end='')
    return f"The task is successfully finished."

def update_resources(
    cpu: Annotated[str,"the CPU resources required for a task."], 
    ram: Annotated[str,"the RAM resources required for a task."], 
    yaml_file: Annotated[str,"A configuration file that allows the modification of CPU and RAM resources."],
    )->str:
    "Delete the container with the configuration file."
    result = subprocess.run(["kubectl", "delete", "-f", yaml_file] , check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
    # for filename in os.listdir("/IICPilot/rtl2gds_2/rtl2gds/test/verilog/10000_gate"):  
    #     if filename.endswith('.v'):  
    #         # 提取文件名（不包括.v扩展名）作为新的值  
    #         base_filename = os.path.splitext(filename)[0]  
    # 检查是否有错误输出  
    print("deleted")
    if result.stderr:  
        print(f"Error occurred while deleting the container:\n{result.stderr.decode()}")  

    "update the required resources of container"
    # 读取 YAML 文件
    os.chdir("/home/dell/jiangzesong/IICPilot/container") 
    with open(yaml_file, 'r') as f:
        yaml_data = yaml.safe_load(f)

    # 更新容器的资源请求
    for container in yaml_data['spec']['containers']:
        container['resources']['requests']['cpu'] = str(cpu)+"m"
        container['resources']['requests']['memory'] = str(ram)+"Mi"
        container['resources']['limits']['cpu'] = str(cpu)+"m"
        container['resources']['limits']['memory'] = str(ram)+"Mi"
    # 写入更新后的 YAML 文件
    with open(yaml_file, 'w') as f:
        yaml.dump(yaml_data, f,default_flow_style=False)

    time.sleep(20)
    "Create the container with the configuration file."
    result = subprocess.run(["kubectl", "apply", "-f", yaml_file] , check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
    # for filename in os.listdir("/IICPilot/rtl2gds_2/rtl2gds/test/verilog/10000_gate"):  
    #     if filename.endswith('.v'):  
    #         # 提取文件名（不包括.v扩展名）作为新的值  
    #         base_filename = os.path.splitext(filename)[0]  
    # 检查是否有错误输出  
    print("created")
    if result.stderr:  
        print(f"Error occurred while creating the container:\n{result.stderr.decode()}")  

    return f"The configuration file has been updated.\n"

update_resources(4096,16382,"test_op.yaml")
time.sleep(10)
run_container("test_op.yaml","ls -l")