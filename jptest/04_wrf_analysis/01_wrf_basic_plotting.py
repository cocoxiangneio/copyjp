#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
WRF表面变量可视化脚本
================================================================================

脚本名称: 01_wrf_basic_plotting.py
功能描述: 
    绘制WRF模式输出的表面气象变量，包括：
    - 10米风场 (U10, V10)
    - 2米温度 (T2)  
    - 累计降水 (RAINC + RAINNC)
    
物理背景:
    - 风速计算: WSP = sqrt(U² + V²)，其中U、V分别为东向和北向风分量
    - 温度转换: WRF输出为开尔文(K)，需转换为摄氏度(°C): T(°C) = T(K) - 273.15
    - 降水累加: 模式输出为累计值，需计算RAINC(对流降水) + RAINNC(大尺度降水)

作者: WRF Analysis Tools
日期: 2024
================================================================================
"""

import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib import rcParams

#================================================================================
# 全局配置参数区
#================================================================================

# -------------------- 数据路径配置 --------------------
WRF_DIR = '/Users/dengmeizhen/cwj'                    # WRF输出文件所在目录
OUTPUT_DIR = '/Users/dengmeizhen/cwj/jptest/04_wrf_analysis'  # 图像输出目录

# -------------------- 绘图区域配置 --------------------
# 地理范围 [lon_min, lon_max, lat_min, lat_max]
# 默认为空表示使用数据原始范围
PLOT_EXTENT = None  # 例如: [105, 125, 15, 35]

# 地图投影方式
MAP_PROJECTION = ccrs.PlateCarree()

# -------------------- 时间索引配置 --------------------
TIME_IDX = 0  # 要绘制的时间步 (从0开始)

# -------------------- 图形参数配置 --------------------
# 图像尺寸 (宽度, 高度) 单位：英寸
FIGURE_SIZE_SINGLE = (12, 8)      # 单图尺寸
FIGURE_SIZE_COMPOSITE = (18, 6)  # 组合图尺寸

# 分辨率 (DPI)
DPI = 150

# 字体配置
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['DejaVu Sans']
TITLE_FONT_SIZE = 14    # 标题字体大小
LABEL_FONT_SIZE = 12   # 坐标轴标签字体大小
TICK_FONT_SIZE = 10    # 刻度字体大小
COLORBAR_FONT_SIZE = 11  # 色标字体大小

# -------------------- 风场绘图配置 --------------------
# 风速色带配置
WIND_CMAP = 'jet'  # 色带名称 (jet, YlOrRd, wind, etc.)
WIND_LEVELS = np.linspace(0, 20, 21)  # 风速等级 (m/s)
WIND_LABEL = 'Wind Speed (m/s)'

# 风矢配置
QUIVER_SCALE = 500      # 风矢缩放因子 (数值越小箭头越长)
QUIVER_INTERVAL = 10    # 风矢抽稀间隔 (每10个网格点绘制一个)
QUIVER_COLOR = 'black'  # 风矢颜色

# -------------------- 温度绘图配置 --------------------
# 温度色带配置
TEMP_CMAP = 'RdBu_r'  # 色带名称 (红-蓝反向)
TEMP_LEVELS = np.linspace(15, 35, 21)  # 温度等级 (°C)
TEMP_LABEL = 'Temperature (°C)'

# -------------------- 降水绘图配置 --------------------
# 降水色带配置
PRECIP_CMAP = 'Blues'  # 色带名称
PRECIP_LEVELS = np.linspace(0, 50, 26)  # 降水等级 (mm)
PRECIP_LABEL = 'Precipitation (mm)'

# -------------------- 地图要素配置 --------------------
SHOW_COASTLINES = True     # 显示海岸线
SHOW_BORDERS = True        # 显示国界
SHOW_PROVINCES = False     # 显示省界 (需要额外数据)
COASTLINE_RESOLUTION = '50m'  # 海岸线分辨率 ( '110m', '50m', '10m' )
BORDER_LINESTYLE = ':'    # 边界线型

#================================================================================
# 函数定义区
#================================================================================

def load_wrf_data(domain='d01'):
    """
    加载WRF模式输出数据
    
    参数:
        domain: 嵌套网格标识符，如 'd01', 'd02', 'd03'
        
    返回:
        ds: xarray Dataset对象，包含所有WRF输出变量
        
    常用变量:
        - XLONG, XLAT: 经纬度坐标
        - U10, V10: 10米风分量
        - T2: 2米温度 (K)
        - RAINC, RAINNC: 累计降水
        - XTIME: 时间
    """
    wrf_file = os.path.join(WRF_DIR, f'wrfout_{domain}_2024-04-04_00_00_00')
    print(f"  加载数据: {wrf_file}")
    ds = xr.open_dataset(wrf_file)
    return ds


def calculate_wind_speed(u, v):
    """
    计算风速标量
    
    物理公式:
        WSP = sqrt(U² + V²)
        
    参数:
        u: 东向风分量 (m/s)，正值为东风
        v: 北向风分量 (m/s)，正值为北风
        
    返回:
        wind_speed: 风速标量 (m/s)
    """
    return np.sqrt(u**2 + v**2)


def convert_kelvin_to_celsius(temp_k):
    """
    将开尔文温度转换为摄氏度
    
    物理公式:
        T(°C) = T(K) - 273.15
        
    参数:
        temp_k: 开尔文温度 (K)
        
    返回:
        temp_c: 摄氏温度 (°C)
    """
    return temp_k - 273.15


def calculate_total_precipitation(rainc, rainnc):
    """
    计算总降水量
    
    WRF模式输出的降水为累计值:
    - RAINC: 对流降水 (convective)
    - RAINNC: 大尺度降水 (non-convective)
    
    总降水 = 对流降水 + 大尺度降水
    
    参数:
        rainc: 对流累计降水 (mm)
        rainnc: 大尺度累计降水 (mm)
        
    返回:
        total_precip: 总累计降水 (mm)
    """
    return rainc + rainnc


def setup_map_axes(fig, projection=None):
    """
    创建带地图投影的坐标轴
    
    参数:
        fig: matplotlib Figure对象
        projection: 地图投影，默认为PlateCarree
        
    返回:
        ax: GeoAxes对象
    """
    if projection is None:
        projection = MAP_PROJECTION
    ax = fig.add_subplot(1, 1, 1, projection=projection)
    return ax


def add_map_features(ax):
    """
    在地图上添加地理要素
    
    参数:
        ax: GeoAxes对象
    """
    if SHOW_COASTLINES:
        ax.coastlines(resolution=COASTLINE_RESOLUTION)
    if SHOW_BORDERS:
        ax.add_feature(cfeature.BORDERS, linestyle=BORDER_LINESTYLE)


def plot_surface_wind(ds, time_idx=0, save_path=None):
    """
    绘制表面风场图
    
    使用 quiver 绘制风矢量底图叠加风速等值线填色
    
    参数:
        ds: WRF数据数据集
        time_idx: 时间步索引
        save_path: 保存路径，若为None则不保存
    """
    print("  绘制表面风场...")
    
    # ---------------- 数据提取 ----------------
    u10 = ds['U10'].values[time_idx]  # 10米东向风 (m/s)
    v10 = ds['V10'].values[time_idx]  # 10米北向风 (m/s)
    wind_speed = calculate_wind_speed(u10, v10)  # 计算风速标量
    
    lon = ds['XLONG'].values[time_idx]  # 经度
    lat = ds['XLAT'].values[time_idx]   # 纬度
    
    # ---------------- 图形创建 ----------------
    fig = plt.figure(figsize=FIGURE_SIZE_SINGLE)
    ax = fig.add_subplot(1, 1, 1, projection=MAP_PROJECTION)
    
    # ---------------- 填色图层 ----------------
    cf = ax.contourf(lon, lat, wind_speed, 
                     levels=WIND_LEVELS, 
                     cmap=WIND_CMAP, 
                     transform=ccrs.PlateCarree(),
                     extend='both')
    
    # 添加色标
    cbar = plt.colorbar(cf, ax=ax)
    cbar.set_label(WIND_LABEL, fontsize=COLORBAR_FONT_SIZE)
    cbar.ax.tick_params(labelsize=TICK_FONT_SIZE)
    
    # ---------------- 风矢叠加 ----------------
    ax.quiver(lon[::QUIVER_INTERVAL, ::QUIVER_INTERVAL], 
              lat[::QUIVER_INTERVAL, ::QUIVER_INTERVAL], 
              u10[::QUIVER_INTERVAL, ::QUIVER_INTERVAL], 
              v10[::QUIVER_INTERVAL, ::QUIVER_INTERVAL],
              transform=ccrs.PlateCarree(), 
              scale=QUIVER_SCALE,
              color=QUIVER_COLOR,
              alpha=0.7)
    
    # ---------------- 地图要素 ----------------
    add_map_features(ax)
    
    # ---------------- 标题与标签 ----------------
    ax.set_title(f'Surface Wind Field\nTime Index: {time_idx}', 
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    ax.set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Latitude (°N)', fontsize=LABEL_FONT_SIZE)
    
    # 设置经纬度刻度
    ax.tick_params(labelsize=TICK_FONT_SIZE)
    
    # ---------------- 保存与关闭 ----------------
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_surface_temperature(ds, time_idx=0, save_path=None):
    """
    绘制2米温度分布图
    
    将WRF输出的开尔文温度转换为摄氏度后填色绘制
    
    参数:
        ds: WRF数据数据集
        time_idx: 时间步索引
        save_path: 保存路径
    """
    print("  绘制2米温度...")
    
    # ---------------- 数据提取 ----------------
    t2_k = ds['T2'].values[time_idx]  # 2米温度 (K)
    t2_c = convert_kelvin_to_celsius(t2_k)  # 转换为摄氏度
    
    lon = ds['XLONG'].values[time_idx]
    lat = ds['XLAT'].values[time_idx]
    
    # ---------------- 图形创建 ----------------
    fig = plt.figure(figsize=FIGURE_SIZE_SINGLE)
    ax = fig.add_subplot(1, 1, 1, projection=MAP_PROJECTION)
    
    # ---------------- 填色图层 ----------------
    cf = ax.contourf(lon, lat, t2_c,
                     levels=TEMP_LEVELS,
                     cmap=TEMP_CMAP,
                     transform=ccrs.PlateCarree(),
                     extend='both')
    
    # 添加等值线
    cs = ax.contour(lon, lat, t2_c,
                    levels=TEMP_LEVELS[::2],
                    colors='black',
                    linewidths=0.3,
                    transform=ccrs.PlateCarree())
    
    # 色标
    cbar = plt.colorbar(cf, ax=ax)
    cbar.set_label(TEMP_LABEL, fontsize=COLORBAR_FONT_SIZE)
    cbar.ax.tick_params(labelsize=TICK_FONT_SIZE)
    
    # ---------------- 地图要素 ----------------
    add_map_features(ax)
    
    # ---------------- 标题 ----------------
    ax.set_title(f'2m Temperature\nTime Index: {time_idx}', 
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    ax.set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Latitude (°N)', fontsize=LABEL_FONT_SIZE)
    ax.tick_params(labelsize=TICK_FONT_SIZE)
    
    # ---------------- 保存 ----------------
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_precipitation(ds, time_idx=0, save_path=None):
    """
    绘制累计降水分布图
    
    显示对流降水(RAINC)与大尺度降水(RAINNC)的总和
    
    参数:
        ds: WRF数据数据集
        time_idx: 时间步索引
        save_path: 保存路径
    """
    print("  绘制降水分布...")
    
    # ---------------- 数据提取 ----------------
    rainc = ds['RAINC'].values[time_idx]    # 对流降水 (mm)
    rainnc = ds['RAINNC'].values[time_idx]  # 大尺度降水 (mm)
    total_precip = calculate_total_precipitation(rainc, rainnc)  # 总降水
    
    lon = ds['XLONG'].values[time_idx]
    lat = ds['XLAT'].values[time_idx]
    
    # ---------------- 图形创建 ----------------
    fig = plt.figure(figsize=FIGURE_SIZE_SINGLE)
    ax = fig.add_subplot(1, 1, 1, projection=MAP_PROJECTION)
    
    # ---------------- 填色图层 ----------------
    cf = ax.contourf(lon, lat, total_precip,
                     levels=PRECIP_LEVELS,
                     cmap=PRECIP_CMAP,
                     transform=ccrs.PlateCarree(),
                     extend='max')
    
    # 色标
    cbar = plt.colorbar(cf, ax=ax)
    cbar.set_label(PRECIP_LABEL, fontsize=COLORBAR_FONT_SIZE)
    cbar.ax.tick_params(labelsize=TICK_FONT_SIZE)
    
    # ---------------- 地图要素 ----------------
    add_map_features(ax)
    
    # ---------------- 标题 ----------------
    ax.set_title(f'Total Precipitation (RAINC + RAINNC)\nTime Index: {time_idx}', 
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    ax.set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Latitude (°N)', fontsize=LABEL_FONT_SIZE)
    ax.tick_params(labelsize=TICK_FONT_SIZE)
    
    # ---------------- 保存 ----------------
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_composite(ds, time_idx=0, save_path=None):
    """
    绘制组合图
    
    在一张图上同时显示风速、温度和降水三个变量，
    便于分析天气系统的三维结构
    
    参数:
        ds: WRF数据数据集
        time_idx: 时间步索引
        save_path: 保存路径
    """
    print("  绘制组合图...")
    
    # ---------------- 数据提取 ----------------
    u10 = ds['U10'].values[time_idx]
    v10 = ds['V10'].values[time_idx]
    wind_speed = calculate_wind_speed(u10, v10)
    
    t2_c = convert_kelvin_to_celsius(ds['T2'].values[time_idx])
    
    total_precip = calculate_total_precipitation(
        ds['RAINC'].values[time_idx],
        ds['RAINNC'].values[time_idx]
    )
    
    lon = ds['XLONG'].values[time_idx]
    lat = ds['XLAT'].values[time_idx]
    
    # ---------------- 图形创建 (1行3列) ----------------
    fig, axes = plt.subplots(1, 3, figsize=FIGURE_SIZE_COMPOSITE,
                             subplot_kw={'projection': MAP_PROJECTION})
    
    # ------ 子图1: 风速 ------
    cf1 = axes[0].contourf(lon, lat, wind_speed,
                            levels=WIND_LEVELS,
                            cmap=WIND_CMAP,
                            transform=ccrs.PlateCarree(),
                            extend='both')
    axes[0].quiver(lon[::QUIVER_INTERVAL, ::QUIVER_INTERVAL], 
                   lat[::QUIVER_INTERVAL, ::QUIVER_INTERVAL], 
                   u10[::QUIVER_INTERVAL, ::QUIVER_INTERVAL], 
                   v10[::QUIVER_INTERVAL, ::QUIVER_INTERVAL],
                   transform=ccrs.PlateCarree(), 
                   scale=QUIVER_SCALE,
                   color=QUIVER_COLOR,
                   alpha=0.7)
    axes[0].coastlines()
    axes[0].set_title('Wind Speed (m/s)', fontsize=TITLE_FONT_SIZE-2)
    plt.colorbar(cf1, ax=axes[0], shrink=0.8)
    
    # ------ 子图2: 温度 ------
    cf2 = axes[1].contourf(lon, lat, t2_c,
                            levels=TEMP_LEVELS,
                            cmap=TEMP_CMAP,
                            transform=ccrs.PlateCarree(),
                            extend='both')
    axes[1].coastlines()
    axes[1].set_title('2m Temperature (°C)', fontsize=TITLE_FONT_SIZE-2)
    plt.colorbar(cf2, ax=axes[1], shrink=0.8)
    
    # ------ 子图3: 降水 ------
    cf3 = axes[2].contourf(lon, lat, total_precip,
                            levels=PRECIP_LEVELS,
                            cmap=PRECIP_CMAP,
                            transform=ccrs.PlateCarree(),
                            extend='max')
    axes[2].coastlines()
    axes[2].set_title('Precipitation (mm)', fontsize=TITLE_FONT_SIZE-2)
    plt.colorbar(cf3, ax=axes[2], shrink=0.8)
    
    # ------ 总标题 ------
    fig.suptitle(f'WRF Surface Variables Composite\nTime Index: {time_idx}', 
                 fontsize=TITLE_FONT_SIZE+2, fontweight='bold')
    
    # ---------------- 保存 ----------------
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


#================================================================================
# 主程序入口
#================================================================================

def main():
    """
    主函数：执行所有绘图任务
    """
    print("=" * 60)
    print("WRF 表面变量可视化")
    print("=" * 60)
    
    # 加载数据
    print("\n[1/5] 加载WRF数据...")
    ds = load_wrf_data('d01')
    print(f"  数据维度: {ds.dims['west_east']} x {ds.dims['south_north']}")
    print(f"  时间步数: {ds.dims['Time']}")
    
    # 绘制各变量
    print("\n[2/5] 绘制表面风场...")
    plot_surface_wind(ds, time_idx=TIME_IDX, 
                      save_path=os.path.join(OUTPUT_DIR, 'surface_wind.png'))
    
    print("\n[3/5] 绘制2米温度...")
    plot_surface_temperature(ds, time_idx=TIME_IDX,
                            save_path=os.path.join(OUTPUT_DIR, 'surface_temperature.png'))
    
    print("\n[4/5] 绘制降水分布...")
    plot_precipitation(ds, time_idx=TIME_IDX,
                       save_path=os.path.join(OUTPUT_DIR, 'precipitation.png'))
    
    print("\n[5/5] 绘制组合图...")
    plot_composite(ds, time_idx=TIME_IDX,
                   save_path=os.path.join(OUTPUT_DIR, 'composite.png'))
    
    # 关闭数据集
    ds.close()
    
    print("\n" + "=" * 60)
    print("完成！所有图像已保存至:")
    print(f"  {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == '__main__':
    main()
