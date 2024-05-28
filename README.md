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

pip3 install hypermapper
(hypermapper is an open source tool used in design space exploration, we use it for optimizing chip performance. The relevant website is: https://github.com/luinardi/hypermapper.)
pip3 install optuna
(optuna is an open-source hyperparameter optimization framework written in Python, we use it for optimizing the time prediction model.)
pip3 langchain
pip install -qU langchain-openai
(LangChain is an open-source framework that aims to empower the utilization of Large Language Models (LLMs) and we use GPT-4 as an example.)
  
For example, if your project is a Python library, you can write:  
  


## 2. Run Makefile [^2]
[^2]: We have recently provided an automated Python script (auto_run.py) that you can use as a one-click compilation for all designs after simple modification.

You can run makefile to test the functionality of the code.

Step 1. Replace #DESIGN_NAME# with the design name you need to test.
```
TEST_DESIGN = #DESIGN_NAME#
```
Step 2. Compile the Verilog file.

```bash  
pip install your-package-name
