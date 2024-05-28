import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np
import optuna
import joblib
# 1. 读取数据
df = pd.read_csv('./csv/designs.csv')

# 2. 数据预处理
# 这里假设所有列都是数值型的，如果有非数值型数据，需要进行编码或处理
# 检查数据中的空值并进行处理（例如删除或填充）
df = df.dropna()

# 3. 特征选择
# 假设目标变量是'runtime'，其余都是特征
X = df.drop(['design', 'runtime'], axis=1)  
y = df['runtime']


# # 增大'cpu_num'特征的权重
# if 'cpu_num' in X.columns:
#     X['cpu_num'] = X['cpu_num'] * 1000  # 这里将'cpu_num'列放大10倍，以增加其权重
# print(X['cpu_num'])
# 4. 数据集划分
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)


# 5. 定义目标函数
def objective(trial):
    n_estimators = trial.suggest_int('n_estimators', 100, 1000)
    max_depth = trial.suggest_int('max_depth', 10, 100)
    min_samples_split = trial.suggest_int('min_samples_split', 2, 10)
    min_samples_leaf = trial.suggest_int('min_samples_leaf', 1, 4)
    max_features = trial.suggest_categorical('max_features', [None, 'sqrt', 'log2'])
    
    rf = RandomForestRegressor(
        n_estimators=n_estimators, 
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        max_features=max_features,
        random_state=42
    )
    
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    return mse

# 6. 使用 Optuna 进行超参数优化
study = optuna.create_study(direction='minimize')
study.optimize(objective, n_trials=1)

# 7. 输出最佳参数
print(f'Best parameters found: {study.best_params}')

# 8. 使用最佳参数训练模型
best_params = study.best_params
best_rf = RandomForestRegressor(
    n_estimators=best_params['n_estimators'],
    max_depth=best_params['max_depth'],
    min_samples_split=best_params['min_samples_split'],
    min_samples_leaf=best_params['min_samples_leaf'],
    max_features=best_params['max_features'],
    random_state=42
)
best_rf.fit(X_train, y_train)


# 9. 模型预测
y_pred = best_rf.predict(X_test)

# 10. 模型评估
mse = mean_squared_error(y_test, y_pred)
# print(f'Mean Squared Error: {mse}')

# 计算MAPE
def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

mape = mean_absolute_percentage_error(y_test, y_pred)
# print(f'Mean Absolute Percentage Error: {mape}%')

# 11. 输出预测结果（可选）
output = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
# print(output.head())

def extract_last_values_from_file(file_path):  
    last_values = {}  
    search_strings_dict = {  
        "Number of wires:": 'wires',  
        "Number of wire bits:": 'wire_bits',  
        "Number of public wires:": 'public_wires',  
        "Number of public wire bits:": 'public_wire_bits',  
        "Number of cells:": 'cells'  
    }  
      
    with open(file_path, 'r') as file:    
        for line in reversed(file.readlines()): 
            for search_string, key in search_strings_dict.items():  
                if search_string in line:  
                    # 提取冒号后的值（假设它后面跟着一个或多个空格和数字）  
                    value = line.split(search_string, 1)[-1].strip().split()[0] 
                    # 尝试将值转换为整数（如果可能）  
                    try:  
                        last_values[key] = int(value)  
                    except ValueError:  
                        last_values[key] = value  
                    break  # 找到匹配项后，跳出内部循环  
            # break  # 因为我们是从文件末尾开始读取的，所以第一个匹配项就是我们要找的  
  
    # 如果需要额外的 'cpu_num' 值（这里假设它是已知的或者可以从其他地方获取）  
    # last_values['cpu_num'] = 2  # 举例值  
  
    return last_values  
  
# 使用函数  
file_path = "/home/dell/jiangzesong/IICPilot/rtl2gds_2/rtl2gds/result/verilog/synth_stat.txt"  # 替换为您的文件路径  
picorv32a_features = extract_last_values_from_file(file_path)  
print(picorv32a_features)
picorv32a_features['cpu_num'] = 1
# # 假设您已经有一个包含单个设计特征的数据字典  
# picorv32a_features = {  
#     'cells': 20005,  
#     'public_wire_bits': 2077,   
#     'public_wires': 1571,
#     'wire_bits': 20241,   
#     'wires': 19375,
#     'cpu_num': 2
# }  
import warnings  
warnings.filterwarnings("ignore", module="sklearn")
import numpy as np  
design_sample = np.array([list(picorv32a_features.values())])
# print(design_sample)
# 使用训练好的随机森林模型进行预测  
predicted_runtime_1 = best_rf.predict(design_sample)[0]  # 索引[0]是因为predict返回一个数组，即使只有一个预测值  
  
# 打印预测的运行时间  
print(f"Predicted runtime for the design and 1vcpu: {predicted_runtime_1}")

picorv32a_features['cpu_num'] = 2 
design_sample = np.array([list(picorv32a_features.values())])  
predicted_runtime_2 = best_rf.predict(design_sample)[0]  # 索引[0]是因为predict返回一个数组，即使只有一个预测值  
print(f"Predicted runtime for the design and 2vcpus: {predicted_runtime_2}")

picorv32a_features['cpu_num'] = 4 
design_sample = np.array([list(picorv32a_features.values())])  
predicted_runtime_4 = best_rf.predict(design_sample)[0]  # 索引[0]是因为predict返回一个数组，即使只有一个预测值  
print(f"Predicted runtime for the design and 4vcpus: {predicted_runtime_4}")

picorv32a_features['cpu_num'] = 8
design_sample = np.array([list(picorv32a_features.values())])  
predicted_runtime_8 = best_rf.predict(design_sample)[0]  # 索引[0]是因为predict返回一个数组，即使只有一个预测值  
print(f"Predicted runtime for the design and 8vcpus: {predicted_runtime_8}")

cost1=predicted_runtime_1*38.790/3600
cost2=predicted_runtime_2*72.650/3600
cost3=predicted_runtime_4*111.920/3600
cost4=predicted_runtime_8*181.750/3600

# 使用sorted()函数对值进行排序（这里以列表形式）  
cost = [cost1, cost2, cost3, cost4]  
sorted_cost = sorted(cost)  
  
if sorted_cost[0]== cost[0]:
    print("1\n")
    print(f"We should choose 1 vCPU, which corresponds to the CPU configuration resource of 1024Mi in test.yaml, with a minimum cost of {cost1}")

if sorted_cost[0]== cost[1]:
    print("2\n")
    print(f"We should choose 2 vCPU, which corresponds to the CPU configuration resource of 2048Mi in test.yaml, with a minimum cost of {cost2}")

if sorted_cost[0]== cost[2]:
    print("4\n")
    print(f"We should choose 4 vCPU, which corresponds to the CPU configuration resource of 4096Mi in test.yaml, with a minimum cost of {cost3}")

if sorted_cost[0]== cost[3]:
    print("8\n")
    print(f"We should choose 8 vCPU, which corresponds to the CPU configuration resource of 8192Mi in test.yaml, with a minimum cost of {cost4}")