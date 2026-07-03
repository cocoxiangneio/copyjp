# Xarray 入门 (08_xarray)

本目录包含 Xarray 在海洋气象数据处理中入门教程，是学习 Python 处理 NetCDF 数据的最佳起点。

## 文件说明

### 核心教程

| 文件名 | 说明 |
|--------|------|
| `Python-海洋气象-Xarray-入门.ipynb` | 海洋气象数据 Xarray 入门教程，基于官方文档简化 |

## 教程内容

1. **数据读取**: 从 NetCDF 文件读取数据
2. **数据选择**: 索引和切片操作
3. **数据计算**: 基础数学运算
4. **数据分组**: groupby 和 resample
5. **数据掩膜**: 基于地理范围的数据筛选
6. **数据绘图**: 快速可视化

## 依赖库

```python
numpy
matplotlib
xarray
pandas
netCDF4
cartopy
```

## 典型用法

```python
import xarray as xr

# 读取 NetCDF 数据
ds = xr.open_dataset('data.nc')

# 选择数据
sst = ds['sst'].sel(lat=slice(-20, 20), lon=slice(100, 160))

# 计算月平均
monthly_mean = sst.groupby('time.month').mean()

# 计算气候态
climatology = sst.groupby('time.dayofyear').mean()

# 异常计算
anomaly = sst - climatology
```

## Xarray 优势

- **多维数组**: 原生支持多维数据
- **坐标标签**: 基于维度名称而非位置
- **灵活索引**: 支持多种索引方式
- **整合 pandas**: 继承 pandas 的时间序列功能

## 参考资料

- Xarray 官方文档: https://docs.xarray.dev/
- xarray 气象海洋教程: https://xarray-contrib.github.io/xarray-tutorial/
