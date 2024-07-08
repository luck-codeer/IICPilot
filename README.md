# IICPilot: An Intelligent Integrated Circuit Backend Design Framework Using Open EDA



## Description  
  
A multi-agent system based on LLM for the backend of IC can complete script creation, complete EDA tasks, optimize chip performance, optimize machine resource allocation, and other unique tasks in the field of EDA.
  
## Features  
  
- Feature 1  
- Feature 2  
- Feature 3  
<!-- List the main features of your project -->  

## Notice
This project includes k8s architecture and iEDA, so you can first understand these two tasks.
Below are the website addresses of two projects：
1. K8s: https://kubernetes.io/
2. iEDA: https://gitee.com/oscc-project/iEDA
## Installation  

1. source myenv/bin/activate
2. pip3 install -r requirement.txt
pip3 install hypermapper
(hypermapper is an open source tool used in design space exploration, we use it for optimizing chip performance. The relevant website is: https://github.com/luinardi/hypermapper.)

pip3 install optuna
(optuna is an open-source hyperparameter optimization framework written in Python, we use it for optimizing the time prediction model.)

pip3 langchain
pip install -qU langchain-openai
(LangChain is an open-source framework that aims to empower the utilization of Large Language Models (LLMs) and we use GPT-4 as an example.)

## Preparation
1. A secure VPN that can connect to the internet.
2. Create the container for testing.
kubectl apply -f test.yaml
## Usage
We only need to call multi-agent system and make a request to it to complete a series of IC backend work
Step 1. To enter the target path.

```bash
cd ./multi-agent-system
```
Step 2. run the agent.py

```python3
python3 agent.py
```

### 3. Experiment

