# 工具类 (07_tools)

本目录包含海洋气象数据处理中常用的工具脚本，涵盖坐标转换、数据读取、文件格式转换等实用技能。

## 文件说明

### 坐标转换

| 文件名 | 说明 |
|--------|------|
| `Python-坐标转换-WGS84.ipynb` | CGCS2000 坐标系转 WGS84 坐标系 |
| `Python-gdal_trans.ipynb` | 使用 GDAL 将 TIF 格式转换为 NC 格式，坐标转换 |

### 数据读取

| 文件名 | 说明 |
|--------|------|
| `Python-读取各省份数据.ipynb` | 使用 cnmaps 库读取省份边界，进行区域裁剪 |
| `Python-mat.ipynb` | 读取 MATLAB 输出的 .dat/.mat 文件 |

### 数据采集

| 文件名 | 说明 |
|--------|------|
| `Python-爬取微信公众号.ipynb` | 爬取微信公众号文章（仅供学习交流） |

## 依赖库

```python
numpy
matplotlib
xarray
pandas
gdal  # 遥感数据处理
cnmaps  # 省份边界
scipy  # 读取mat文件
```

## 典型用法

```python
# GDAL 坐标转换
from osgeo import gdal
gdal.Translate('output.nc', 'input.tif', format='NetCDF')

# 省份数据读取
import cnmaps
cnmaps.get_map_by_name('广东省')

# MATLAB 数据读取
from scipy.io import loadmat
data = loadmat('file.mat')
```

## 注意事项

- GDAL 安装可能需要额外配置
- 微信公众号爬取仅供学习交流，请遵守相关法律法规

## 参考资料

- GDAL Documentation
- cnmaps: https://github.com/huangyonghome/cnmaps
