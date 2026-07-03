# 气象统计 (06_statistics)

本目录包含气象统计方法相关的 Python 教程，涵盖功率谱估计、自相关分析、有效稳定性分析、核密度估计等核心技术。

## 文件说明

### 功率谱分析

| 文件名 | 说明 |
|--------|------|
| `Python-基于自相关函数的功率谱估计.ipynb` | 使用自相关函数进行标准化功率谱估计 |
| `Python-计算自相关系数.ipynb` | 自相关系数（ACF）计算方法 |

### 稳定性分析

| 文件名 | 说明 |
|--------|------|
| `Python_effective_stability.ipynb` | 有效静力稳定性分析，大气海洋稳定性判据 |

### 概率分布

| 文件名 | 说明 |
|--------|------|
| `Python-核密度图.ipynb` | 核密度估计（KDE）用于分析数据分布特征 |

## 依赖库

```python
numpy
matplotlib
xarray
pandas
scipy
seaborn
```

## 典型用法

```python
# 功率谱估计
from scipy import signal
f, Pxx = signal.welch(data, fs=1.0, nperseg=256)

# 自相关函数
acf = np.correlate(data - data.mean(), data - data.mean(), mode='full')
acf = acf[len(acf)//2:] / acf[len(acf)//2]

# 核密度估计
from scipy import stats
kde = stats.gaussian_kde(data)
```

## 统计概念

- **功率谱**: 将时间序列分解为不同频率成分
- **自相关**: 衡量时间序列与其滞后版本的相关性
- **有效稳定性**: 考虑相位变化的大气稳定性判据

## 参考资料

- Priestley, M. B. (1981). Spectral Analysis and Time Series.
- Emanuel, K. A. (1994). Atmospheric Convection.
