# 海温分析 (04_sst_analysis)

本目录包含海表温度（SST）分析相关的 Python 教程，涵盖 SST 数据读取、趋势分析、超前滞后相关、海温锋面识别等技术。

## 文件说明

### 海温基础

| 文件名 | 说明 |
|--------|------|
| `Python-basemap-sst.ipynb` | 使用 basemap/cartopy 绘制 SST 空间分布图 |

### 趋势分析

| 文件名 | 说明 |
|--------|------|
| `Python-GPCP-趋势分析.ipynb` | GPCP 降水数据的趋势分析方法，同样适用于 SST |
| `Python-GPCP-趋势分析.ipynb` | 包含空间纬向加权计算和空间平均 |

### 超前滞后分析

| 文件名 | 说明 |
|--------|------|
| `Python-sst-超前滞后.ipynb` | SST 数据的超前滞后相关分析，计算 Niño 3.4 指数 |

### 海温锋面

| 文件名 | 说明 |
|--------|------|
| `python-海温锋面及指数.ipynb` | 海温锋面识别算法及锋面指数计算 |

## 依赖库

```python
numpy
matplotlib
xarray
pandas
netCDF4
cartopy
seaborn
```

## 典型用法

```python
# Niño 3.4 指数计算
sst_anom = sst - sst_clim
nino34 = sst_anom.sel(lon=slice(190, 240), lat=slice(-5, 5)).mean()

# 超前滞后相关
lead_lag_corr = xr.corr(sst_anom.isel(time=i), index_anom, dim='time')
```

## Niño 指数说明

- **Niño 3.4**: 5°N-5°S, 170°W-120°W
- 用于监测中东太平洋海温异常

## 参考资料

- NOAA Climate Prediction Center - Niño 3.4 Index
- Trenberth, K. E. (1997). The definition of El Niño.
