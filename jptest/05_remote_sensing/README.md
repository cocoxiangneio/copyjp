# 遥感数据 (05_remote_sensing)

本目录包含卫星遥感数据处理相关的 Python 教程，涵盖 Himawari-8 卫星、GPM 降水数据、可降水量计算等技术。

## 文件说明

### 卫星数据

| 文件名 | 说明 |
|--------|------|
| `Python-ITCZ_GPM.ipynb` | ITCZ（热带辐合带）分析，使用 GPM 降水数据 |
| `Python-计算可降水量.ipynb` | 利用 ERA5 比湿数据计算可降水量，处理中心经度白线 |

### 数据位置

- Himawari-8 卫星数据位于: `../data/Himawari-8/`

## 依赖库

```python
numpy
matplotlib
xarray
pandas
netCDF4
cartopy
gdal  # 遥感数据处理
```

## 典型用法

```python
# GPM 降水数据读取
import xarray as xr
gpm_data = xr.open_dataset('gpm_imerg.nc')

# 可降水量计算
# 需要比湿(q)和气压层数据
precipitable_water = (q * dp / g).sum(dim='level')
```

## 数据来源

- **GPM**: Global Precipitation Measurement
- **ERA5**: European Centre for Medium-Range Weather Forecasts Reanalysis 5
- **Himawari-8**: 日本气象卫星

## 参考资料

- GPM IMERG Final Precipitation L3 Half Hourly 0.1 degree
- Hersbach, H., et al. (2020). The ERA5 global reanalysis.
