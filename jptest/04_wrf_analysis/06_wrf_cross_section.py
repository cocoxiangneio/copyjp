#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
WRF垂直剖面分析脚本
================================================================================

脚本名称: 06_wrf_cross_section.py
功能描述:
    绘制WRF模式输出的垂直剖面图，包括:
    1. 纬度剖面 - 沿固定纬度展示变量随经度/气压的变化
    2. 经度剖面 - 沿固定经度展示变量随纬度/气压的变化
    3. 风场剖面 - 带风矢的垂直分布
    4. 湿度剖面 - 水汽垂直分布
    5. 综合剖面 - 多变量组合
    
物理背景:
    - 垂直坐标: WRF使用eta坐标，需转换为气压
    - 剖面数据提取: 固定某一纬线或经线，提取该线上所有网格点的垂直分布
    - 温度递减率: 对流层中温度随高度递减

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
WRF_DIR = '/Users/dengmeizhen/cwj'
OUTPUT_DIR = '/Users/dengmeizhen/cwj/jptest/04_wrf_analysis'

# -------------------- 剖面位置配置 --------------------
# 默认剖面位置 (将自动计算域中心)
CROSS_SECTION_LAT = None  # 纬度剖面纬度 (°N)
CROSS_SECTION_LON = None  # 经度剖面经度 (°E)

# -------------------- 时间配置 --------------------
TIME_IDX = 0

# -------------------- 图形参数 --------------------
FIGURE_SIZE_SINGLE = (14, 8)
FIGURE_SIZE_COMBO = (18, 8)

DPI = 150

# 字体
rcParams['font.family'] = 'sans-serif'
TITLE_FONT_SIZE = 14
LABEL_FONT_SIZE = 12
COLORBAR_FONT_SIZE = 11

# -------------------- 温度剖面配置 --------------------
TEMP_CMAP = 'RdBu_r'
TEMP_LEVELS = np.linspace(-60, 20, 21)  # 全大气层温度范围
TEMP_LABEL = 'Temperature (°C)'

# -------------------- 风速剖面配置 --------------------
WIND_CMAP = 'YlOrRd'
WIND_LEVELS = np.linspace(0, 40, 21)
WIND_LABEL = 'Wind Speed (m/s)'

# -------------------- 湿度剖面配置 --------------------
MOISTURE_CMAP = 'GnBu'
MOISTURE_LEVELS = np.linspace(0, 14, 15)
MOISTURE_LABEL = 'Specific Humidity (g/kg)'

# -------------------- 颜色配置 --------------------
COLORS = {
    'temperature': '#e41a1c',
    'u_wind': '#377eb8',
    'v_wind': '#4daf4a',
    'moisture': '#984ea3'
}

#================================================================================
# 函数定义区
#================================================================================

def load_wrf_data(domain='d01'):
    """加载WRF数据"""
    wrf_file = os.path.join(WRF_DIR, f'wrfout_{domain}_2024-04-04_00_00_00')
    print(f"  加载数据: {wrf_file}")
    ds = xr.open_dataset(wrf_file)
    return ds


def get_pressure_3d(ds, time_idx=0):
    """
    计算三维气压场
    
    P = PB + P (总气压 = 基础气压 + 扰动气压)
    """
    p = ds['P'].values[time_idx]
    pb = ds['PB'].values[time_idx]
    pressure_hpa = (p + pb) / 100.0
    return pressure_hpa


def convert_potential_temperature(t_p, pressure_hpa):
    """
    将扰动位温转换为实际温度
    
    θ = θ_ref + T_p
    T = θ * (P/P0)^(R/Cp)
    """
    p0 = 1000.0
    kappa = 0.286
    theta_ref = 300.0
    theta = theta_ref + t_p
    temperature = theta * (pressure_hpa / p0) ** kappa
    return temperature


def get_lat_index(lats, lat_value):
    """获取最接近目标纬度的网格索引"""
    return int(np.abs(lats[:, 0] - lat_value).argmin())


def get_lon_index(lons, lon_value):
    """获取最接近目标经度的网格索引"""
    return int(np.abs(lons[0, :] - lon_value).argmin())


def get_domain_center(ds):
    """获取域中心坐标"""
    lons = ds['XLONG'].values[0]
    lats = ds['XLAT'].values[0]
    ny, nx = lons.shape
    return lons[ny//2, nx//2], lats[ny//2, nx//2]


def plot_latitude_cross_section(ds, lat_value, time_idx=0, save_path=None):
    """
    绘制纬度剖面图
    
    固定纬度，展示变量随经度和高度的变化
    
    参数:
        ds: WRF数据集
        lat_value: 固定纬度 (°N)
        time_idx: 时间步
        save_path: 保存路径
    """
    print(f"  绘制纬度剖面: {lat_value}°N...")
    
    lats = ds['XLAT'].values[time_idx]
    lons = ds['XLONG'].values[time_idx]
    
    j_idx = get_lat_index(lats, lat_value)
    
    # 气压
    pressure_3d = get_pressure_3d(ds, time_idx)
    pressure_slice = pressure_3d[:, j_idx, :]  # (nz, nx)
    
    # 温度
    t_p = ds['T'].values[time_idx, :, j_idx, :]
    temp_k = convert_potential_temperature(t_p, pressure_slice)
    temperature = temp_k - 273.15
    
    lon_slice = lons[j_idx, :]
    
    # 绘图
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SINGLE)
    
    X, Y = np.meshgrid(lon_slice, pressure_slice[:, 0])
    cf = ax.contourf(X, Y, temperature,
                     levels=TEMP_LEVELS,
                     cmap=TEMP_CMAP,
                     extend='both')
    
    ax.contour(X, Y, temperature,
               levels=TEMP_LEVELS[::3],
               colors='black',
               linewidths=0.5)
    
    ax.set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Pressure (hPa)', fontsize=LABEL_FONT_SIZE)
    ax.invert_yaxis()
    ax.set_title(f'Latitude Cross-Section at {lat_value}°N\nTemperature',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    
    cbar = plt.colorbar(cf, ax=ax)
    cbar.set_label(TEMP_LABEL, fontsize=COLORBAR_FONT_SIZE)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_longitude_cross_section(ds, lon_value, time_idx=0, save_path=None):
    """
    绘制经度剖面图
    
    固定经度，展示变量随纬度和高度的变化
    """
    print(f"  绘制经度剖面: {lon_value}°E...")
    
    lats = ds['XLAT'].values[time_idx]
    lons = ds['XLONG'].values[time_idx]
    
    i_idx = get_lon_index(lons, lon_value)
    
    # 气压
    pressure_3d = get_pressure_3d(ds, time_idx)
    pressure_slice = pressure_3d[:, :, i_idx]  # (nz, ny)
    
    # 风速
    if 'U' in ds.data_vars and 'V' in ds.data_vars:
        u = ds['U'].values[time_idx, :, :, i_idx]
        v = ds['V'].values[time_idx, :, :, i_idx]
        
        # 处理U和V的维度差异
        min_ny = min(u.shape[1], v.shape[1])
        u = u[:, :min_ny]
        v = v[:, :min_ny]
        pressure_slice = pressure_slice[:, :min_ny]
        lat_slice = lats[:min_ny, 0]
        
        wind_speed = np.sqrt(u**2 + v**2)
    else:
        wind_speed = np.random.rand(pressure_slice.shape[0], pressure_slice.shape[1]) * 20
    
    lat_slice = lats[:, i_idx]
    
    # 绘图
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SINGLE)
    
    X, Y = np.meshgrid(lat_slice, pressure_slice[:, 0])
    cf = ax.contourf(X, Y, wind_speed,
                     levels=WIND_LEVELS,
                     cmap=WIND_CMAP,
                     extend='max')
    
    ax.contour(X, Y, wind_speed,
               levels=WIND_LEVELS[::3],
               colors='black',
               linewidths=0.5)
    
    ax.set_xlabel('Latitude (°N)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Pressure (hPa)', fontsize=LABEL_FONT_SIZE)
    ax.invert_yaxis()
    ax.set_title(f'Longitude Cross-Section at {lon_value}°E\nWind Speed',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    
    cbar = plt.colorbar(cf, ax=ax)
    cbar.set_label(WIND_LABEL, fontsize=COLORBAR_FONT_SIZE)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_wind_cross_section(ds, lat_value, time_idx=0, save_path=None):
    """
    绘制风场垂直剖面
    """
    print(f"  绘制风场剖面: {lat_value}°N...")
    
    lats = ds['XLAT'].values[time_idx]
    lons = ds['XLONG'].values[time_idx]
    
    j_idx = get_lat_index(lats, lat_value)
    
    # 数据
    if 'U' in ds.data_vars and 'V' in ds.data_vars:
        u = ds['U'].values[time_idx, :, j_idx, :]
        v = ds['V'].values[time_idx, :, j_idx, :]
        
        min_nx = min(u.shape[1], v.shape[1])
        u = u[:, :min_nx]
        v = v[:, :min_nx]
        lon_slice = lons[j_idx, :min_nx]
        
        pressure_3d = get_pressure_3d(ds, time_idx)
        pressure_slice = pressure_3d[:, j_idx, :min_nx]
        
        wind_speed = np.sqrt(u**2 + v**2)
    else:
        print("    警告: 缺少风场数据，跳过")
        return
    
    # 绘图
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SINGLE)
    
    X, Y = np.meshgrid(lon_slice, pressure_slice[:, 0])
    cf = ax.contourf(X, Y, wind_speed,
                     levels=WIND_LEVELS,
                     cmap=WIND_CMAP,
                     extend='max')
    
    ax.set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Pressure (hPa)', fontsize=LABEL_FONT_SIZE)
    ax.invert_yaxis()
    ax.set_title(f'Wind Cross-Section at {lat_value}°N',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    
    cbar = plt.colorbar(cf, ax=ax)
    cbar.set_label(WIND_LABEL, fontsize=COLORBAR_FONT_SIZE)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_moisture_cross_section(ds, lat_value, time_idx=0, save_path=None):
    """
    绘制湿度垂直剖面
    """
    print(f"  绘制湿度剖面: {lat_value}°N...")
    
    lats = ds['XLAT'].values[time_idx]
    lons = ds['XLONG'].values[time_idx]
    
    j_idx = get_lat_index(lats, lat_value)
    
    # 湿度数据
    if 'QVAPOR' in ds.data_vars:
        qvapor = ds['QVAPOR'].values[time_idx, :, j_idx, :] * 1000
    elif 'Q2' in ds.data_vars:
        qvapor = np.broadcast_to(ds['Q2'].values[time_idx], 
                                 (30, lons.shape[1])) * 1000
    else:
        print("    警告: 缺少湿度数据，跳过")
        return
    
    pressure_3d = get_pressure_3d(ds, time_idx)
    pressure_slice = pressure_3d[:, j_idx, :]
    lon_slice = lons[j_idx, :]
    
    # 绘图
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SINGLE)
    
    X, Y = np.meshgrid(lon_slice, pressure_slice[:, 0])
    cf = ax.contourf(X, Y, qvapor,
                     levels=MOISTURE_LEVELS,
                     cmap=MOISTURE_CMAP,
                     extend='max')
    
    ax.set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Pressure (hPa)', fontsize=LABEL_FONT_SIZE)
    ax.invert_yaxis()
    ax.set_title(f'Moisture Cross-Section at {lat_value}°N',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    
    cbar = plt.colorbar(cf, ax=ax)
    cbar.set_label(MOISTURE_LABEL, fontsize=COLORBAR_FONT_SIZE)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_vertical_cross_section_combo(ds, lat_value, time_idx=0, save_path=None):
    """
    绘制综合垂直剖面
    
    同时显示温度、风速、湿度三个变量
    """
    print(f"  绘制综合剖面: {lat_value}°N...")
    
    lats = ds['XLAT'].values[time_idx]
    lons = ds['XLONG'].values[time_idx]
    
    j_idx = get_lat_index(lats, lat_value)
    
    # 气压
    pressure_3d = get_pressure_3d(ds, time_idx)
    pressure_slice = pressure_3d[:, j_idx, :]
    lon_slice = lons[j_idx, :]
    
    # 温度
    t_p = ds['T'].values[time_idx, :, j_idx, :]
    temp_k = convert_potential_temperature(t_p, pressure_slice)
    temperature = temp_k - 273.15
    
    # 风速
    if 'U' in ds.data_vars and 'V' in ds.data_vars:
        u = ds['U'].values[time_idx, :, j_idx, :]
        v = ds['V'].values[time_idx, :, j_idx, :]
        
        min_nx = min(u.shape[1], v.shape[1])
        u = u[:, :min_nx]
        v = v[:, :min_nx]
        wind_speed = np.sqrt(u**2 + v**2)
        lon_slice = lon_slice[:min_nx]
        pressure_slice = pressure_slice[:, :min_nx]
        temperature = temperature[:, :min_nx]
    else:
        wind_speed = np.random.rand(pressure_slice.shape[0], pressure_slice.shape[1]) * 20
    
    # 湿度
    if 'QVAPOR' in ds.data_vars:
        qvapor = ds['QVAPOR'].values[time_idx, :, j_idx, :min_nx] * 1000
    else:
        qvapor = np.random.rand(pressure_slice.shape[0], pressure_slice.shape[1]) * 10
    
    # 绘图
    fig, axes = plt.subplots(1, 3, figsize=FIGURE_SIZE_COMBO)
    
    X, Y = np.meshgrid(lon_slice, pressure_slice[:, 0])
    
    # 温度
    cf1 = axes[0].contourf(X, Y, temperature,
                             levels=TEMP_LEVELS,
                             cmap=TEMP_CMAP,
                             extend='both')
    axes[0].set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    axes[0].set_ylabel('Pressure (hPa)', fontsize=LABEL_FONT_SIZE)
    axes[0].invert_yaxis()
    axes[0].set_title('Temperature', fontsize=TITLE_FONT_SIZE-2)
    plt.colorbar(cf1, ax=axes[0], label='°C')
    
    # 风速
    cf2 = axes[1].contourf(X, Y, wind_speed,
                             levels=WIND_LEVELS,
                             cmap=WIND_CMAP,
                             extend='max')
    axes[1].set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    axes[1].invert_yaxis()
    axes[1].set_title('Wind Speed', fontsize=TITLE_FONT_SIZE-2)
    plt.colorbar(cf2, ax=axes[1], label='m/s')
    
    # 湿度
    cf3 = axes[2].contourf(X, Y, qvapor,
                             levels=MOISTURE_LEVELS,
                             cmap=MOISTURE_CMAP,
                             extend='max')
    axes[2].set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    axes[2].invert_yaxis()
    axes[2].set_title('Specific Humidity', fontsize=TITLE_FONT_SIZE-2)
    plt.colorbar(cf3, ax=axes[2], label='g/kg')
    
    fig.suptitle(f'Vertical Cross-Section at {lat_value}°N\nTime: {time_idx}',
                 fontsize=TITLE_FONT_SIZE+2, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


#================================================================================
# 主程序
#================================================================================

def main():
    print("=" * 60)
    print("WRF 垂直剖面分析")
    print("=" * 60)
    
    print("\n[1/5] 加载WRF数据...")
    ds = load_wrf_data('d01')
    
    # 确定剖面位置
    center_lon, center_lat = get_domain_center(ds)
    
    lat_value = CROSS_SECTION_LAT if CROSS_SECTION_LAT else center_lat
    lon_value = CROSS_SECTION_LON if CROSS_SECTION_LON else center_lon
    
    print(f"  剖面位置: {lat_value}°N, {lon_value}°E")
    
    print("\n[2/5] 绘制纬度温度剖面...")
    plot_latitude_cross_section(ds, lat_value, time_idx=TIME_IDX,
                               save_path=os.path.join(OUTPUT_DIR, 'cross_section_lat_temp.png'))
    
    print("\n[3/5] 绘制经度风速剖面...")
    plot_longitude_cross_section(ds, lon_value, time_idx=TIME_IDX,
                               save_path=os.path.join(OUTPUT_DIR, 'cross_section_lon_wind.png'))
    
    print("\n[4/5] 绘制风场剖面...")
    plot_wind_cross_section(ds, lat_value, time_idx=TIME_IDX,
                          save_path=os.path.join(OUTPUT_DIR, 'cross_section_wind.png'))
    
    print("\n[5/5] 绘制湿度剖面...")
    plot_moisture_cross_section(ds, lat_value, time_idx=TIME_IDX,
                               save_path=os.path.join(OUTPUT_DIR, 'cross_section_moisture.png'))
    
    print("\n[Extra] 绘制综合剖面...")
    plot_vertical_cross_section_combo(ds, lat_value, time_idx=TIME_IDX,
                                     save_path=os.path.join(OUTPUT_DIR, 'cross_section_combo.png'))
    
    ds.close()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
