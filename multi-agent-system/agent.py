#加入user_proxy agent(与用户交互)，解析用户需求的模块
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
#tool
@tool
def get_human_input(prompt: str) -> str:
        """Get human input and provide this input as message to the agent.
        """
        iostream = IOStream.get_default()
        reply = iostream.input(prompt)
        # print(f"{prompt}+{reply}")
        return f"This is user's new input: {reply}."

_TEMP_DIRECTORY = TemporaryDirectory()
WORKING_DIRECTORY = Path(_TEMP_DIRECTORY.name)
@tool
def read_file(
    file_name: Annotated[str, "File path to read the document."]
                 )->str:
    """Read the specified file and the response does not need to include file content."""
    os.chdir("/home/dell/jiangzesong/IICPilot/rtl2gds_1/rtl2gds/script/iEDA")
    with open(file_name, 'r') as file:
        eda_flow_tcl = file.read()
    return eda_flow_tcl
@tool
def write_file(
    file_name: Annotated[str, "File path to save the content."],
    content: Annotated[str, "Text content to be written into the file."],
    ) -> Annotated[str, "Path of the saved document file."]:
    """Write the new content to a file"""
    os.chdir("/home/dell/jiangzesong/IICPilot/rtl2gds_1/rtl2gds/script/iEDA")
    with open(file_name, 'w') as file:
        file.write(content)
    return f"Document saved to {file_name}"
@tool
def run_eda_flow(
    # command: Annotated[str, "the eda command provided to the control agent."],
    ) -> Annotated[str, "Result of running eda flow"]:
    "provide the command to the container agent to run the eda"
    # Define the path to the Shell command
    target_path = "/IICPilot/rtl2gds_1/rtl2gds"
    command1=f"cd {target_path}"
    command2=f"bash rtl2gds.sh"
    return f"Please provide the information to the container agent: yaml file: ./test.yaml and command:{command1}&&{command2} and tell it to run the container."

@tool
def run_eda_task(
    eda_task: Annotated[str, "the specific task which provided by the other agents."],
    cpu_num=None
    # command: Annotated[str, "the eda command provided to the control agent."],
    ) -> Annotated[str, "Result of running eda task"]:
    "provide the command to the container agent to run the eda task"
    target_path = "/IICPilot/rtl2gds_1/rtl2gds/script/iEDA"
    command1=f"cd {target_path}"
    command2=f"bash run_iEDA_{eda_task}.sh"
    if cpu_num is None:
        return f"Please provide the information to the container agent: yaml file: ./test.yaml and command:{command1}&&{command2} and tell it to run the container."
    elif cpu_num==1:
        return f"Please tell the container agent that it needs to complete two tasks: 1. Update resources(Information required: yaml file: ./test_op.yaml and cpu: 1024, ram: 16384),there is no need to provide the unit of cpu and ram. 2. Run the container(Information required: yaml file: ./test_op.yaml and command:{command1}&&{command2}), note that the first task should be completed before moving on to the second task."
    elif cpu_num==2:
        return f"Please tell the container agent that it needs to complete two tasks: 1. Update resources(Information required: yaml file: ./test_op.yaml and cpu: 2048, ram: 16384),there is no need to provide the unit of cpu and ram. 2. Run the container(Information required: yaml file: ./test_op.yaml and command:{command1}&&{command2}), note that the first task should be completed before moving on to the second task."
    elif cpu_num==4:
        return f"Please tell the container agent that it needs to complete two tasks: 1. Update resources(Information required: yaml file: ./test_op.yaml and cpu: 4096, ram: 16384),there is no need to provide the unit of cpu and ram. 2. Run the container(Information required: yaml file: ./test_op.yaml and command:{command1}&&{command2}), note that the first task should be completed before moving on to the second task."
    elif cpu_num==8:
        return f"Please tell the container agent that it needs to complete two tasks: 1. Update resources(Information required: yaml file: ./test_op.yaml and cpu: 8192, ram: 16384),there is no need to provide the unit of cpu and ram. 2. Run the container(Information required: yaml file: ./test_op.yaml and command:{command1}&&{command2}), note that the first task should be completed before moving on to the second task."
    else:
        return f"please provide more information"
@tool
def create_container(
    yaml_file: Annotated[str,"the configuration file used for creating container"],
    )->Annotated[str, "Result of container creating"]:
    "Create the container with the configuration file."
    # 加载Kubernetes配置  
    config.load_kube_config()  
    # 创建API对象  
    v1 = client.CoreV1Api()  
    # 从YAML文件加载Pod定义  
    with open(yaml_file, 'r') as f:  
        pod_yaml = f.read()  
    # 使用ApiClient的sanitize_for_serialization方法处理YAML内容  
    pod_body = yaml.safe_load(pod_yaml)  
    pod_body = ApiClient().sanitize_for_serialization(pod_body)  
    # 创建Pod  
    try:  
        api_response = v1.create_namespaced_pod(body=pod_body, namespace="default")  
        print("Pod created. status='%s'" % str(api_response.status))  
    except ApiException as e:  
        print("Exception when calling CoreV1Api->create_namespaced_pod: %s\n" % e)  

@tool
def delete_container(
    yaml_file: Annotated[str,"the configuration file used for deleting container"],
    )->Annotated[str, "Result of container deleting"]:
    "Delete the container with the configuration file."
    # 加载Kubernetes配置  
    config.load_kube_config()  
    # 创建API对象  
    v1 = client.CoreV1Api()  
    # 从YAML文件加载Pod定义  
    with open(yaml_file, 'r') as f:  
        pod_yaml = f.read()  
    # 使用ApiClient的sanitize_for_serialization方法处理YAML内容  
    pod_body = yaml.safe_load(pod_yaml)  
    pod_body = ApiClient().sanitize_for_serialization(pod_body)  
    # 删除Pod
    try:  
        body = client.V1DeleteOptions()
        api_response = v1.delete_namespaced_pod(name=pod_body['metadata']['name'], namespace="default", body=body) 
        # print("Pod deleted. status='%s'" % str(api_response.status))   
        print("Pod deleted. ")
    except ApiException as e:  
        print(f"Exception when calling CoreV1Api->delete_namespaced_pod: {e}")

@tool
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

@tool
def update_resources(
    cpu: Annotated[str,"the CPU resources required for a task."], 
    ram: Annotated[str,"the RAM resources required for a task."], 
    yaml_file: Annotated[str,"A configuration file that allows the modification of CPU and RAM resources."],
    )->str:
    "Delete the container with the configuration file."
    result = subprocess.run(["kubectl", "delete", "-f", yaml_file] , check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)   
    print("container deleted")
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
    print("container created")
    if result.stderr:  
        print(f"Error occurred while creating the container:\n{result.stderr.decode()}")  
    time.sleep(10)
    return f"The configuration file has been updated.\n"

@tool
def prediction_resource(
    rtl_design: Annotated[str, "the specific rtl design used for the eda flow"],
    task: Annotated[str, "the specific eda part of the execution."],
    run_task: Annotated[bool, "whether to run the task."]=False,
    )->Annotated[str,"the CPU and RAM required for the specific rtl_desgin and eda_part"]:
    "Predict the CPU resources required for container execution through RTL design and the EDA process utilized."
    os.chdir("/home/dell/jiangzesong/IICPilot/container") 
    print(rtl_design)
    print(task)
    if rtl_design=="picorv32.v" and task=="placement":
        try:  
            result = subprocess.run(['python3', 'rf_test.py']  , check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
            # 检查是否有标准输出  
            if result.stdout:  
                # 分割输出为多行，并取最后一行  
                lines = result.stdout.decode('utf-8').strip().split('\n')   
                if lines:  
                    cpu_num = lines[-2]
                    last_line = lines[-1]
            if result.stderr:  
                print(result.stderr.decode(), file=sys.stderr)  
        except subprocess.CalledProcessError as e:  
            # 如果命令返回非零退出码，这里会捕获到异常  
            print(f'命令执行出错，退出码：{e.returncode}')  
            print(e.stderr.decode(), file=sys.stderr)  
        if run_task==False:
            return f"{last_line}\n "
        else:
            return f"{last_line}\n Please provide the information to the EDA_process_implementation_agent: eda_task:{task} and cpu_num: {cpu_num}"
    
@tool
def run_dse(
    )->Annotated[str,"the dse command provided to the container agent "]:
    "provide the command to the container agent to run the dse"
    target_path = "/IICPilot/dse/hypermapper"
    file1_path="/IICPilot/dse/hypermapper/example_scenarios/synthetic/eda_design_space_exploration/eda_dse.py"
    file2_path="/IICPilot/dse/hypermapper/example_scenarios/synthetic/eda_design_space_exploration/eda_dse.json"
    command1=f"cd {target_path}"
    command2=f"python3 {file1_path}"
    command3=f"hm-compute-pareto {file2_path}"
    return f"Please provide the information to the container agent: yaml file: ./test.yaml and command:{command1}&&{command2} and tell it to run the container."


#agent
def create_agent(
    llm: ChatOpenAI,
    tools: list,
    system_prompt: str,
) -> str:
    """Create a function-calling agent and add it to the graph."""
    system_prompt += "\nWork autonomously according to your specialty, using the tools available to you."
    " Do not ask for clarification."
    " Your other team members (and other teams) will collaborate with you with their own specialties."
    " You are chosen for a reason! You are one of the following team members: {team_members}."
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_functions_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor

def create_user_agent(
    llm: ChatOpenAI,
    tools: list,
    system_prompt: str,
) -> str:
    """Create a function-calling agent and add it to the graph."""
    system_prompt += "Make the arguments in your response a valid JSON"
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_functions_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor

def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result["output"], name=name)]}


def create_team_supervisor(llm: ChatOpenAI, system_prompt, members) -> str:
    """An LLM-based router."""
    options = ["FINISH"] + members
    function_def = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {
                "next": {
                    "title": "Next",
                    "anyOf": [
                        {"enum": options},
                    ],
                },
            },
            "required": ["next"],
        },
    }
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, which function should be called next?"
                "Or should we FINISH? Select one of: {options}.",
            ),
        ]
    ).partial(options=str(options), team_members=", ".join(members))
    return (
        prompt
        | llm.bind_functions(functions=[function_def], function_call="route")
        | JsonOutputFunctionsParser()
    )
    

#graph
import functools
import operator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai.chat_models import ChatOpenAI
import functools


# IC team graph state
class ICTeamState(TypedDict):
    # A message is added after each team member finishes
    messages: Annotated[List[BaseMessage], operator.add]
    # The team members are tracked so they are aware of
    # the others' skill-sets
    team_members: List[str]
    # Used to route work. The supervisor calls a function
    # that will update this every time it makes a decision
    next: str


llm = ChatOpenAI(model="gpt-4-1106-preview")

EDA_process_implementation_agent = create_agent(
    llm,
    [read_file, write_file, run_eda_flow, run_eda_task],
    '''You are an EDA_process_implementation agent who can generate scripts for the IC backend and pass information to the container agent and your response is the information that can be passed on.
     Of course, you need to reply to the result of the generated script in the first part of the response if we need you to modify or generate the script.
     Concretely, your response should consist of two parts. One part should be the reply regarding the generation or modification of the script and the response does not need to include file content,
     and the other part should be the information to be passed to the container agent. and when it is necessary to run eda flow, you only need to 
     use the tool run_eda_flow to pass the return value of the tool to the the container agent. and when it is necessary to run eda task, you only need to 
     use the tool run_eda_task to pass the return value of the tool to the the container agent.
     If the information is insufficient and there is no specific detail information about hwo to finish reqiurements, you should response for more information.''',
)
EDA_process_implementation_node = functools.partial(agent_node, agent=EDA_process_implementation_agent, name="EDA_process_implementation")

container_agent = create_agent(
    llm,
    [create_container, delete_container, run_container, update_resources, prediction_resource],
    '''You are an container agent who can allocate resources and run an container,
    and be able to execute tasks based on the information passed by other agents.
    If the information is insufficient, you can pass it to the user_proxy through control agent.''',
)
container_node = functools.partial(agent_node, agent=container_agent, name="Container")

dse_agent = create_agent(
    llm,
    [read_file, write_file, run_dse],
    '''You are a Dse agent who can generate scripts for design space exploration and pass information to the container agent and your response is the information that can be passed on.
     Of course, you need to reply to the result of the generated script in the first part of the response if we need you to modify or generate the script.
     Concretely, your response should consist of two parts. One part should be the reply regarding the generation or modification of the script and the response does not need to include file content,
     and the other part should be the information to be passed to the container agent. and when it is necessary to run dse for optimizing performance metrics, you only need to 
     use the tool run_dse to pass the return value of the tool to the the container agent. When you need to modify or generate scripts, first, you should read the files in that specific path using a file reading tool. 
     Then, you can refer to that file and use a file writing tool to modify and generate the scripts accordingly.
     If the information is insufficient, you can pass it to the user_proxy through control agent.
''',
)
dse_node = functools.partial(agent_node, agent=dse_agent, name="Dse")

control_agent = create_team_supervisor(
    llm,
    "You are a control agent tasked with managing a conversation between the"
    " following workers:  EDA_process_implementation, Container, Dse, user_proxy. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH. Please note:"
    "When more information is needed, please select user_proxy;"
    "When the task involves EDA flow, please consider EDA_process_implementation; when it involves containers and the information has been passed to the container agent, please consider selecting Container;" 
    "and when it involves design space exploration, please consider selecting Dse. Finally, make sure to choose one of them if respond without FINISH.",
    ["EDA_process_implementation", "Container", "Dse", "user_proxy"],
)

# import autogen
# from autogen import AssistantAgent, UserProxyAgent
# import os
# llm_config = {"model": "gpt-4-1106-preview", "api_key": os.environ["OPENAI_API_KEY"]}
# assistant = AssistantAgent("assistant", llm_config=llm_config)

user_proxy_agent = create_user_agent(
    llm,
    [get_human_input],
    '''You are a user proxy agent. You just need to call the tool human_input based on the user's prompt every time
    and tell other agents user's requirement and information, if user need to run eda_flow or modify the content of script, please tell EDA process implementation agent.
''',
)
#input
user_proxy_node = functools.partial(agent_node, agent=user_proxy_agent, name="user_proxy")
# floorplan_node = functools.partial(agent_node, agent=floorplan_agent, name="Floorplan")
# user_proxy = UserProxyAgent(
#     "user_proxy", code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")}
# )

icbackend_graph = StateGraph(ICTeamState)
icbackend_graph.add_node("EDA_process_implementation", EDA_process_implementation_node)
icbackend_graph.add_node("Container", container_node)
icbackend_graph.add_node("Dse", dse_node)
icbackend_graph.add_node("Control", control_agent)
icbackend_graph.add_node("user_proxy", user_proxy_node)

# Define the control flow
icbackend_graph.add_edge("EDA_process_implementation", "Control")
icbackend_graph.add_edge("Container", "Control")
icbackend_graph.add_edge("Dse", "Control")
icbackend_graph.add_edge("user_proxy", "Control")
icbackend_graph.add_conditional_edges(
    "Control",
    lambda x: x["next"],
    {"EDA_process_implementation": "EDA_process_implementation", "Container": "Container", "Dse": "Dse", "user_proxy": "user_proxy", "FINISH": END},
)


icbackend_graph.set_entry_point("Control")
chain = icbackend_graph.compile()


#test
# The following functions interoperate between the top level graph state
# and the state of the IC sub-graph
# this makes it so that the states of each graph don't get intermixed
def enter_chain(message: str):
    results = {
        "messages": [HumanMessage(content=message)],
    }
    # print(results)
    return results

user_input = input("user: ") 
IC_chain = enter_chain | chain

# example1
# Please invoke the dse_agent to provide command to the container_agent by using the tool run_dse.
# and then invoke the container_agent to run container based on the ./test.yaml and command. When finished, respond with FINISH.

# example2
# Please Firstly, Floorplan agent need to reduce the value of DIE AREA slightly 
# in the /home/dell/jiangzesong/IICPilot/rtl2gds_1/rtl2gds/script/iEDA/iFP_script/run_iFP.tcl. 
# Secondly, Dse agent need to narrow down the range of target_density and unchange the ranges of other parameters in the
# /home/dell/jiangzesong/IICPilot/dse/hypermapper/example_scenarios/synthetic/eda_design_space_exploration/eda_dse.json.
# Thirdly, Dse agent will provide command to the Container agent by using the tool run_dse, and then Container agent need 
# to update the resources of the container and the allocation of CPU and RAM resources is 2048. then run container 
# based on the ./test.yaml and provided command. Finally, these tasks are finished.

# example3
# Please invoke EDA_process_implementation agent to reduce the value of DIE AREA slightly 
# in the iFP_script/run_iFP.tcl, and then run eda flow.
# Secondly, Floorplan agent need to provide command to the Container agent by invoking the tool run_eda_flow.
# Thirdly, Container agent need to update the resources of the container(the allocation of CPU and RAM resources is 2048). Then run container 
# based on the ./test.yaml and command provided in the second step. Finally, when the container has completed the task, these tasks are finished.

#example4
# Please invoke EDA_process_implementation agent to reduce the value of DIE AREA to "0.0    0.0   148   148"
#  in the iFP_script/run_iFP.tcl, and then run eda flow.

# example5
# Please invoke the dse_agent to run dse.

# example6
# Please invoke the container agent to predict the CPU resources required for the placement of the rtl design picorv32.v

# example7
# Please invoke the container agent to predict the CPU resources required for the placement of the rtl design picorv32.v, and run eda task: placement


#example5
# Please invoke EDA_process_implementation agent to relax the constraint in the ../../gcd/gcd.sdc, and then run the EDA flow.

#example5
# Please invoke EDA_process_implementation agent to relax the constraint, and then run the EDA flow.

for s in IC_chain.stream(
    user_input
    , {"recursion_limit": 100}
):
    if "__end__" not in s:
        print(s)
        print("---")
