# 气象绘图 (03_plotting)

本目录包含海洋气象数据可视化相关的 Python 教程，涵盖热力图、箱型图、风场图、泰勒图等常用气象绘图技能。

## 文件说明

### 热力图与统计图

| 文件名 | 说明 |
|--------|------|
| `Python-heatmap.ipynb` | 使用 seaborn 绘制热力图，展示了数据的时间空间分布 |
| `Python-核密度图.ipynb` | 核密度估计图（KDE），用于分析数据分布 |

### 箱型图

| 文件名 | 说明 |
|--------|------|
| `Python-复现箱型图.py` | 复现气象常用的箱型图 |
| `Python-复现箱型图-多配色方案.py` | 多种配色方案的箱型图实现 |

### 泰勒图

| 文件名 | 说明 |
|--------|------|
| `Python-taylor(泰勒图).ipynb` | 泰勒图绘制，用于评估模型性能 |

### 风场图

| 文件名 | 说明 |
|--------|------|
| `Python-绘制黑底的水平风场分布图.ipynb` | 黑底风格的风场矢量图绘制 |
| `Python-mat.ipynb` | 读取 MATLAB 输出的 .dat 文件并绘图，多 Y 轴绘图 |

### 地形图

| 文件名 | 说明 |
|--------|------|
| `Python-绘制坡度和坡向.ipynb` | 基于高程数据绘制坡度和坡向图，使用 RichDEM 库 |

## 依赖库

```python
numpy
matplotlib
seaborn
pandas
cartopy
RichDEM  # 坡度坡向计算
```

## 典型用法

```python
# 热力图示例
import seaborn as sns
sns.heatmap(data, annot=True, fmt='.2f', cmap='RdBu_r')

# 泰勒图示例
import matplotlib.pyplot as plt
# 需要自行实现或使用 proplot 库
```

## 绘图技巧

1. **黑底图绘制**：设置 axes 的 facecolor 为黑色
2. **多Y轴图**：使用 twinx() 创建多个 Y 轴
3. **投影子图**：使用 cartopy 的投影系统
4. **colorbar**：使用 mpl_toolkits.axes_grid1 精确控制位置
