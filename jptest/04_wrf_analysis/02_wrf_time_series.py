#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
WRF时间序列分析脚本
================================================================================

脚本名称: 02_wrf_time_series.py
功能描述:
    提取并可视化WRF模式输出在指定位置的时间演变，包括：
    - 2米温度 (T2) 时间序列
    - 10米风速 (U10, V10) 时间序列
    - 累计降水 (RAINC + RAINNC) 时间序列
    - 表面热通量 (HFX, LH) 时间序列
    
    支持单点时间序列和多站点对比

物理背景:
    - 热通量:
      - HFX (感热通量): 湍流交换导致的显热传递, 单位 W/m²
      - LH (潜热通量): 相变导致的能量传递, 单位 W/m²
    - 降水: WRF输出为累计值，需计算差值获得时段降水量

作者: WRF Analysis Tools
日期: 2024
================================================================================
"""

import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib import rcParams

#================================================================================
# 全局配置参数区
#================================================================================

# -------------------- 数据路径配置 --------------------
WRF_DIR = '/Users/dengmeizhen/cwj'                    # WRF输出文件目录
OUTPUT_DIR = '/Users/dengmeizhen/cwj/jptest/04_wrf_analysis'  # 输出目录

# -------------------- 时间索引配置 --------------------
TIME_START = 0    # 起始时间步
TIME_END = None   # 结束时间步 (None表示到最后)

# -------------------- 站点配置 --------------------
# 站点列表，每个站点为 (经度, 纬度)
# 注意: 应选择位于WRF模拟域内的位置
STATION_LOCATIONS = [
    (119.2, 26.0),   # 站点1: (lon, lat) 格式
    (108.0, 18.0),   # 站点2
]

# 站点标签
STATION_LABELS = ['Station A', 'Station B']

# -------------------- 图形参数配置 --------------------
FIGURE_SIZE_SINGLE = (14, 10)    # 单站点图尺寸
FIGURE_SIZE_MULTI = (14, 14)      # 多站点对比图尺寸

DPI = 150

# 字体配置
rcParams['font.family'] = 'sans-serif'
TITLE_FONT_SIZE = 14
AXIS_LABEL_FONT_SIZE = 12
LEGEND_FONT_SIZE = 11
TICK_FONT_SIZE = 10

# 线条配置
LINE_WIDTH = 2.0
ALPHA = 0.9

# 颜色配置
COLORS = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']

# -------------------- 变量绘图配置 --------------------
# 温度配置
TEMP_COLOR = '#e41a1c'
TEMP_ylabel = 'Temperature (°C)'

# 风速配置
WIND_COLOR = '#377eb8'
WIND_ylabel = 'Wind Speed (m/s)'

# 降水配置
PRECIP_COLOR = '#4daf4a'
PRECIP_ylabel = 'Precipitation (mm)'

# 热通量配置
SENSIBLE_HEAT_COLOR = '#e41a1c'
LATENT_HEAT_COLOR = '#377eb8'
FLUX_ylabel = 'Heat Flux (W/m²)'

# 网格配置
GRID_ALPHA = 0.3
GRID_LINESTYLE = '--'

#================================================================================
# 函数定义区
#================================================================================

def load_wrf_data(domain='d01'):
    """
    加载WRF模式输出数据
    
    参数:
        domain: 嵌套网格标识符
        
    返回:
        ds: xarray Dataset
    """
    wrf_file = os.path.join(WRF_DIR, f'wrfout_{domain}_2024-04-04_00_00_00')
    print(f"  加载数据: {wrf_file}")
    ds = xr.open_dataset(wrf_file)
    return ds


def find_nearest_index(arr, value):
    """
    查找数组中最接近给定值的索引
    
    用于: 在WRF网格上找到最接近目标经纬度的网格点
    
    参数:
        arr: 一维数组 (如经度或纬度数组)
        value: 目标值
        
    返回:
        idx: 最接近值对应的索引
    """
    return int(np.abs(arr - value).argmin())


def extract_time_series_at_location(ds, lon, lat):
    """
    在指定位置提取时间序列数据
    
    参数:
        ds: WRF数据集
        lon: 目标经度 (°E)
        lat: 目标纬度 (°N)
        
    返回:
        dict: 包含以下键的时间序列字典:
            - time: 时间数组
            - t2: 2米温度 (°C)
            - u10: 10米东向风 (m/s)
            - v10: 10米北向风 (m/s)
            - wind_speed: 风速 (m/s)
            - precip: 总降水 (mm)
            - hfx: 感热通量 (W/m²)
            - lh: 潜热通量 (W/m²)
            - location: (lon, lat) 元组
    """
    # 获取网格坐标
    lons = ds['XLONG'].values[0]  # (south_north, west_east)
    lats = ds['XLAT'].values[0]
    
    # 找到最近的网格点
    i = find_nearest_index(lons[0, :], lon)  # 经度方向
    j = find_nearest_index(lats[:, 0], lat)   # 纬度方向
    
    # 获取实际坐标
    actual_lon = lons[j, i]
    actual_lat = lats[j, i]
    print(f"  站点位置: ({actual_lon:.2f}°E, {actual_lat:.2f}°N), 网格点: ({j}, {i})")
    
    # 时间轴
    time = ds['XTIME'].values
    
    # 提取变量数据 [时间, 纬度, 经度]
    t2_k = ds['T2'].values[:, j, i] - 273.15  # 转换为摄氏度
    u10 = ds['U10'].values[:, j, i]
    v10 = ds['V10'].values[:, j, i]
    wind_speed = np.sqrt(u10**2 + v10**2)
    
    rainc = ds['RAINC'].values[:, j, i]
    rainnc = ds['RAINNC'].values[:, j, i]
    total_precip = rainc + rainnc
    
    # 热通量 (W/m²)
    hfx = ds['HFX'].values[:, j, i]
    lh = ds['LH'].values[:, j, i]
    
    return {
        'time': time,
        't2': t2_k,
        'u10': u10,
        'v10': v10,
        'wind_speed': wind_speed,
        'precip': total_precip,
        'hfx': hfx,
        'lh': lh,
        'location': (actual_lon, actual_lat)
    }


def plot_time_series_single(data, save_path=None):
    """
    绘制单站点时间序列
    
    创建包含4个子图的复合图:
    1. 2米温度
    2. 10米风速
    3. 累计降水
    4. 表面热通量
    
    参数:
        data: extract_time_series_at_location返回的字典
        save_path: 保存路径
    """
    print("  绘制单站点时间序列...")
    
    time = data['time']
    location = data['location']
    
    # 创建4行1列的子图
    fig, axes = plt.subplots(4, 1, figsize=FIGURE_SIZE_SINGLE)
    fig.suptitle(f'Time Series at ({location[0]:.2f}°E, {location[1]:.2f}°N)',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    
    # ------ 子图1: 温度 ------
    axes[0].plot(time, data['t2'], color=TEMP_COLOR, 
                  linewidth=LINE_WIDTH, alpha=ALPHA)
    axes[0].set_ylabel(TEMP_ylabel, fontsize=AXIS_LABEL_FONT_SIZE)
    axes[0].set_title('2m Temperature', fontsize=TITLE_FONT_SIZE-2)
    axes[0].grid(True, alpha=GRID_ALPHA, linestyle=GRID_LINESTYLE)
    axes[0].tick_params(labelsize=TICK_FONT_SIZE)
    
    # ------ 子图2: 风速 ------
    axes[1].plot(time, data['wind_speed'], color=WIND_COLOR,
                  linewidth=LINE_WIDTH, alpha=ALPHA)
    axes[1].set_ylabel(WIND_ylabel, fontsize=AXIS_LABEL_FONT_SIZE)
    axes[1].set_title('10m Wind Speed', fontsize=TITLE_FONT_SIZE-2)
    axes[1].grid(True, alpha=GRID_ALPHA, linestyle=GRID_LINESTYLE)
    axes[1].tick_params(labelsize=TICK_FONT_SIZE)
    
    # ------ 子图3: 降水 ------
    axes[2].plot(time, data['precip'], color=PRECIP_COLOR,
                  linewidth=LINE_WIDTH, alpha=ALPHA)
    axes[2].fill_between(time, 0, data['precip'], color=PRECIP_COLOR, alpha=0.3)
    axes[2].set_ylabel(PRECIP_ylabel, fontsize=AXIS_LABEL_FONT_SIZE)
    axes[2].set_title('Total Precipitation (RAINC + RAINNC)', fontsize=TITLE_FONT_SIZE-2)
    axes[2].grid(True, alpha=GRID_ALPHA, linestyle=GRID_LINESTYLE)
    axes[2].tick_params(labelsize=TICK_FONT_SIZE)
    
    # ------ 子图4: 热通量 ------
    axes[3].plot(time, data['hfx'], color=SENSIBLE_HEAT_COLOR,
                  linewidth=LINE_WIDTH, alpha=ALPHA, label='Sensible Heat (HFX)')
    axes[3].plot(time, data['lh'], color=LATENT_HEAT_COLOR,
                  linewidth=LINE_WIDTH, alpha=ALPHA, label='Latent Heat (LH)')
    axes[3].set_ylabel(FLUX_ylabel, fontsize=AXIS_LABEL_FONT_SIZE)
    axes[3].set_xlabel('Time', fontsize=AXIS_LABEL_FONT_SIZE)
    axes[3].set_title('Surface Heat Fluxes', fontsize=TITLE_FONT_SIZE-2)
    axes[3].legend(loc='best', fontsize=LEGEND_FONT_SIZE)
    axes[3].grid(True, alpha=GRID_ALPHA, linestyle=GRID_LINESTYLE)
    axes[3].tick_params(labelsize=TICK_FONT_SIZE)
    axes[3].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_multi_location_comparison(ds, locations, labels=None, save_path=None):
    """
    绘制多站点时间序列对比图
    
    参数:
        ds: WRF数据集
        locations: 位置列表 [(lon1, lat1), (lon2, lat2), ...]
        labels: 站点标签列表
        save_path: 保存路径
    """
    print("  绘制多站点对比...")
    
    if labels is None:
        labels = [f'Station {i+1}' for i in range(len(locations))]
    
    # 创建3行1列的子图
    fig, axes = plt.subplots(3, 1, figsize=FIGURE_SIZE_MULTI)
    fig.suptitle('Multi-Location Time Series Comparison',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    
    # 颜色循环
    n_stations = len(locations)
    
    for idx, (lon, lat) in enumerate(locations):
        data = extract_time_series_at_location(ds, lon, lat)
        color = COLORS[idx % len(COLORS)]
        label = labels[idx]
        
        # 温度
        axes[0].plot(data['time'], data['t2'], color=color,
                      linewidth=LINE_WIDTH, alpha=ALPHA, label=label)
        
        # 风速
        axes[1].plot(data['time'], data['wind_speed'], color=color,
                      linewidth=LINE_WIDTH, alpha=ALPHA, label=label)
        
        # 降水
        axes[2].plot(data['time'], data['precip'], color=color,
                      linewidth=LINE_WIDTH, alpha=ALPHA, label=label)
    
    # 设置子图属性
    axes[0].set_ylabel(TEMP_ylabel, fontsize=AXIS_LABEL_FONT_SIZE)
    axes[0].set_title('2m Temperature', fontsize=TITLE_FONT_SIZE-2)
    axes[0].legend(loc='best', fontsize=LEGEND_FONT_SIZE)
    axes[0].grid(True, alpha=GRID_ALPHA, linestyle=GRID_LINESTYLE)
    axes[0].tick_params(labelsize=TICK_FONT_SIZE)
    
    axes[1].set_ylabel(WIND_ylabel, fontsize=AXIS_LABEL_FONT_SIZE)
    axes[1].set_title('10m Wind Speed', fontsize=TITLE_FONT_SIZE-2)
    axes[1].legend(loc='best', fontsize=LEGEND_FONT_SIZE)
    axes[1].grid(True, alpha=GRID_ALPHA, linestyle=GRID_LINESTYLE)
    axes[1].tick_params(labelsize=TICK_FONT_SIZE)
    
    axes[2].set_ylabel(PRECIP_ylabel, fontsize=AXIS_LABEL_FONT_SIZE)
    axes[2].set_xlabel('Time', fontsize=AXIS_LABEL_FONT_SIZE)
    axes[2].set_title('Total Precipitation', fontsize=TITLE_FONT_SIZE-2)
    axes[2].legend(loc='best', fontsize=LEGEND_FONT_SIZE)
    axes[2].grid(True, alpha=GRID_ALPHA, linestyle=GRID_LINESTYLE)
    axes[2].tick_params(labelsize=TICK_FONT_SIZE)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def get_domain_center(ds):
    """
    获取WRF模拟域中心坐标
    
    参数:
        ds: WRF数据集
        
    返回:
        (center_lon, center_lat): 中心经纬度
    """
    lons = ds['XLONG'].values[0]
    lats = ds['XLAT'].values[0]
    
    ny, nx = lons.shape
    center_lon = lons[ny//2, nx//2]
    center_lat = lats[ny//2, nx//2]
    
    return center_lon, center_lat


#================================================================================
# 主程序入口
#================================================================================

def main():
    """
    主函数
    """
    print("=" * 60)
    print("WRF 时间序列分析")
    print("=" * 60)
    
    # 加载数据
    print("\n[1/4] 加载WRF数据...")
    ds = load_wrf_data('d01')
    
    # 获取域中心
    center_lon, center_lat = get_domain_center(ds)
    print(f"  域中心: ({center_lon:.2f}°E, {center_lat:.2f}°N)")
    
    # 单站点分析
    print("\n[2/4] 单站点时间序列分析...")
    data = extract_time_series_at_location(ds, center_lon, center_lat)
    plot_time_series_single(
        data, 
        save_path=os.path.join(OUTPUT_DIR, 'time_series_single.png')
    )
    
    # 多站点对比
    print("\n[3/4] 多站点时间序列对比...")
    # 使用配置中的站点
    if len(STATION_LOCATIONS) >= 2:
        plot_multi_location_comparison(
            ds, 
            STATION_LOCATIONS,
            STATION_LABELS,
            save_path=os.path.join(OUTPUT_DIR, 'time_series_multi.png')
        )
    else:
        print("  站点数量不足，跳过多站点对比")
    
    ds.close()
    
    print("\n[4/4] 完成!")
    print("\n" + "=" * 60)
    print("输出文件:")
    print(f"  {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == '__main__':
    main()
