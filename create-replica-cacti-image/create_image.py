###################
# 生成cacti图像
# 需要安装pandas和matplotlib
# csv表格需要修改格式，时间列列名为a，入向为b，出向为c，单位为G
###################


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置字体
# 读取CSV文件
file_path = 'My-Tools-for-Devops//create-replica-cacti-image//test.csv' #读取csv文件
data = pd.read_csv(file_path)

# 将b和c列的数据除以10亿
data['b'] = data['b'] / 1e9
data['c'] = data['c'] / 1e9

# 计算统计数据
b_stats = data['b'].agg(['min', 'max', 'mean'])
c_stats = data['c'].agg(['min', 'max', 'mean'])

# 排序b列并找到对应于0.05百分位的值
sorted_b = data['c'].sort_values(ascending=False)
percentile_value = sorted_b.iloc[int(len(sorted_b) * 0.05)]

# 绘制折线图
plt.figure(figsize=(20, 5))
plt.plot(data['a'], data['b'], color='blue', label='InBound流量(G)')  # 蓝色线
plt.fill_between(data['a'], data['c'], color='green', alpha=0.3, label='OutBound流量(G)区域')  # 绿色渐变区域
plt.plot(data['a'], data['c'], color='green', lw=2)  # 绿色线

# 添加横线
#plt.axhline(y=percentile_value, color='red', linestyle='-', label=f'95计费值 b={percentile_value:.2f}G')
plt.axhline(y=percentile_value, color='red', linestyle='-', label=f'95计费值 b=5.83G')

# 添加标题和图例 根据具体需求调整
plt.title('YunJI')
plt.xlabel('时间')
plt.ylabel('流量值 (G)')
plt.legend()

# 控制横坐标上的时间点数量
ax = plt.gca()  # 获取当前的axes实例
ax.xaxis.set_major_locator(MaxNLocator(nbins=10, prune=None))  # 设置最多显示x个时间点
plt.setp(ax.get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")
# 在图表上显示统计数据
# 文本框位置调整到图表最下方
y_min = min(b_stats['min'], c_stats['min'])
y_margin = (b_stats['max'] - y_min) * 0.5  # 保证有足够的空间放置文本
#plt.text(data['a'].iloc[-1], y_margin - y_min,
  #      f'InBound\n最大: {b_stats["max"]:.2f} G\n最小: {b_stats["min"]:.2f} G\n平均: {b_stats["mean"]:.2f} G',
    #    bbox=dict(facecolor='red', alpha=0.5))


#plt.text(data['a'].iloc[-1], y_min - 1 * y_margin,
  #      f'OutBound\n最大: {c_stats["max"]:.2f} G\n最小: {c_stats["min"]:.2f} G\n平均: {c_stats["mean"]:.2f} G',
    #    bbox=dict(facecolor='blue', alpha=0.5))


plt.savefig('test.png')
