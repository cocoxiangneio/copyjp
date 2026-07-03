# 数据处理 (02_data_processing)

本目录包含海洋气象数据处理相关的 Python 教程，涵盖滤波、EOF/PCA 分析、数据同化等核心技术。

## 文件说明

### 滤波分析

| 文件名 | 说明 |
|--------|------|
| `00_bandpass_compare.ipynb` | 带通滤波方法比较，对比不同滤波器的效果 |
| `Python-空间滤波.ipynb` | 空间滤波（带通、低通、高通）实现与应用 |
| `Python-kf-filter-like-ncl.ipynb` | Kalman 滤波实现，类似 NCL 的滤波方法 |
| `Python-保留谐波.ipynb` | 谐波保留方法，复现 NCL 的 smthClmDayTLL 函数 |

### EOF/PCA 分析

| 文件名 | 说明 |
|--------|------|
| `00_bsiso_EOF.ipynb` | BSISO（南海夏季风指数）EOF 分析 |
| `Python-EOF-PCA对比.ipynb` | EOF 与 PCA 方法对比验证 |

### 数据同化

| 文件名 | 说明 |
|--------|------|
| `Python-数据同化示例.ipynb` | 集合滤波数据同化方法示例 |

### 网格处理

| 文件名 | 说明 |
|--------|------|
| `Python-非常规经纬度网格.ipynb` | 处理非标准经纬度网格数据 |
| `Python-空间投影法-ccew.ipynb` | 基于投影法的赤道波动识别 |
| `Python-经向投影-ccew.ipynb` | 数据的经向投影处理 |

## 辅助脚本

| 文件名 | 说明 |
|--------|------|
| `Python_wave_filter.py` | 波动滤波 Python 实现 |
| `kf_filter_like_ncl_calculate_freq_kelvin.py` | Kalman 滤波计算 Kelvin 波频率 |

## 依赖库

```python
numpy
matplotlib
xarray
pandas
scipy
eofs  # EOF分析
```

## 典型用法

```python
# EOF分析示例
from eofs.xarray import Eof
solver = Eof(data)
eofs = solver.eofs(neofs=3)
pcs = solver.pcs(npcs=3)
```

## 参考资料

- Lorenz, E. N. (1956). Empirical orthogonal functions and statistical weather prediction.
- Evensen, G. (1994). Sequential data assimilation with a nonlinear quasi-geostrophic model.
