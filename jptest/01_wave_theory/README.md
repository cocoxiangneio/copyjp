# 波动理论 (01_wave_theory)

本目录包含海洋气象波动理论相关的 Python 教程，主要涉及 Kelvin 波、Matsuno 波动方程、赤道波动等的数值模拟和可视化。

## 文件说明

### Kelvin 波相关

| 文件名 | 说明 |
|--------|------|
| `kelvin_wave_propagation.ipynb` | Kelvin 波传播的数值模拟，展示波在赤道地区的传播特征 |
| `Python_kelvin_wave_propagation_with_geo_div.ipynb` | 带地理散度的 Kelvin 波传播模拟，更真实地模拟大气运动 |
| `Python-kelvin波-空间分布.ipynb` | Kelvin 波的水平空间分布特征分析 |
| `Python-kelvin波-超前滞后合成.ipynb` | Kelvin 波的超前滞后合成分析，用于研究波的时间演变 |
| `Python-kelvin波-追踪信号.ipynb` | Kelvin 波信号追踪，识别波传播路径 |
| `Python-kelvin波位相合成.ipynb` | Kelvin 波位相合成分析 |
| `Python-Kelvin波理论解水平空间.py` | Kelvin 波理论解的水平空间分布 Python 实现 |
| `Python-kelvin波的频散曲线.py` | Kelvin 波频散曲线计算，描述波速与波数的关系 |

### Matsuno 波动理论

| 文件名 | 说明 |
|--------|------|
| `Python-matsuno-赤道波动频散关系图.py` | Matsuno 赤道波动频散关系图，展示不同波动模式的频散特性 |

### Gill 模型

| 文件名 | 说明 |
|--------|------|
| `Python-Gill-模型.ipynb` | Gill 大气响应模型，模拟赤道对热源的响应 |
| `Python-Gill响应-动画版.ipynb` | Gill 模型响应的动画展示，动态展示响应过程 |

### 垂直模态

| 文件名 | 说明 |
|--------|------|
| `Python-垂直模态分解.py` | 大气垂直模态分解，分析不同垂直模态的特征 |
| `Python_kelvin_wave_vertical_mode_structure.ipynb` | Kelvin 波垂直模态结构分析 |

### 时空分析

| 文件名 | 说明 |
|--------|------|
| `Python_wk_spacetime.ipynb` | Wheeler-Kiladis 时空谱分析，用于分析热带波动 |
| `Python_time_scale_fig.ipynb` | 时间尺度分析图 |
| `Python_wave_speed_Explain.ipynb` | 波动速度理论解释 |

## 依赖库

```python
numpy
matplotlib
xarray
scipy
cartopy
```

## 典型用法

```python
# 导入必要的库
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
```

## 参考资料

- Gill, A. E. (1980). Some simple solutions for heat-induced tropical circulation. 
- Matsuno, T. (1966). Quasi-geostrophic motions in the equatorial area.
- Wheeler, M., & Kiladis, G. N. (1999). Convectively coupled equatorial waves.
