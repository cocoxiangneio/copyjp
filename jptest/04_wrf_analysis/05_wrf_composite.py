#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
WRF组合分析脚本
================================================================================

脚本名称: 05_wrf_composite.py
功能描述:
    综合可视化WRF输出的多个变量，包括:
    1. 全要素综合图 (风、温度、降水、湿度)
    2. 能量平衡分量 (辐射通量、热通量)
    3. 土壤湿度分布
    4. 时间演变动画帧
    
物理背景:
    - 能量平衡: R_n = H + LE + G
      R_n: 净辐射, H: 感热, LE: 潜热, G: 地热通量
    - 辐射分量:
      - SWDOWN: 向下短波辐射 (太阳辐射)
      - GLW: 向下长波辐射 (大气辐射)
    - 热通量:
      - HFX: 感热通量
      - LH: 潜热通量
      - QFX: 水汽通量

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
WRF_DIR = '/Users/dengmeizhen/cwj'
OUTPUT_DIR = '/Users/dengmeizhen/cwj/jptest/04_wrf_analysis'

# -------------------- 时间配置 --------------------
TIME_IDX = 0
N_FRAMES = 6  # 动画帧数

# -------------------- 图形参数 --------------------
FIGURE_SIZE_FULL = (20, 16)
FIGURE_SIZE_ENERGY = (18, 12)
FIGURE_SIZE_EVOLUTION = (18, 12)
FIGURE_SIZE_SINGLE = (12, 8)

DPI = 150

# 字体
rcParams['font.family'] = 'sans-serif'
TITLE_FONT_SIZE = 16
SUBTITLE_FONT_SIZE = 14
LABEL_FONT_SIZE = 12
COLORBAR_FONT_SIZE = 11

# -------------------- 变量配置 --------------------
# 风速
WIND_CMAP = 'YlOrRd'
WIND_LEVELS = np.linspace(0, 20, 21)

# 温度
TEMP_CMAP = 'RdBu_r'
TEMP_LEVELS = np.linspace(15, 35, 21)

# 降水
PRECIP_CMAP = 'Blues'
PRECIP_LEVELS = np.linspace(0, 50, 26)

# 湿度
MOISTURE_CMAP = 'GnBu'
MOISTURE_LEVELS = np.linspace(0, 18, 19)

# 辐射通量
SWDOWN_CMAP = 'YlOrBr'
SWDOWN_LEVELS = np.linspace(0, 800, 21)

# 热通量
HFX_CMAP = 'RdYlBu_r'
HFX_LEVELS = np.linspace(-200, 400, 31)

LH_CMAP = 'Blues'
LH_LEVELS = np.linspace(0, 300, 31)

# 土壤湿度
SOIL_MOISTURE_CMAP = 'BrBG'
SOIL_MOISTURE_LEVELS = np.linspace(0, 50, 26)

# PBL高度
PBLH_CMAP = 'viridis'
PBLH_LEVELS = np.linspace(0, 2000, 21)

#================================================================================
# 函数定义区
#================================================================================

def load_wrf_data(domain='d01'):
    """加载WRF数据"""
    wrf_file = os.path.join(WRF_DIR, f'wrfout_{domain}_2024-04-04_00_00_00')
    print(f"  加载数据: {wrf_file}")
    ds = xr.open_dataset(wrf_file)
    return ds


def calculate_wind_speed(u, v):
    """计算风速标量"""
    return np.sqrt(u**2 + v**2)


def calculate_total_precipitation(rainc, rainnc):
    """计算总降水"""
    return rainc + rainnc


def plot_full_composite(ds, time_idx=0, save_path=None):
    """
    绘制全要素综合图
    
    2x2布局:
    - 风场 + 风矢
    - 温度 + 等值线
    - 降水
    - 湿度
    """
    print("  绘制全要素综合图...")
    
    lon = ds['XLONG'].values[time_idx]
    lat = ds['XLAT'].values[time_idx]
    
    # 提取变量
    u10 = ds['U10'].values[time_idx]
    v10 = ds['V10'].values[time_idx]
    wind_speed = calculate_wind_speed(u10, v10)
    
    t2_c = ds['T2'].values[time_idx] - 273.15
    
    total_precip = calculate_total_precipitation(
        ds['RAINC'].values[time_idx],
        ds['RAINNC'].values[time_idx]
    )
    
    # 湿度
    if 'QVAPOR' in ds.data_vars:
        moisture = ds['QVAPOR'].values[time_idx, -1] * 1000
    elif 'Q2' in ds.data_vars:
        moisture = ds['Q2'].values[time_idx] * 1000
    else:
        moisture = np.zeros_like(wind_speed)
    
    # 创建2x2子图
    fig = plt.figure(figsize=FIGURE_SIZE_FULL)
    
    # 子图1: 风场
    ax1 = plt.subplot(2, 2, 1, projection=ccrs.PlateCarree())
    cf1 = ax1.contourf(lon, lat, wind_speed,
                        levels=WIND_LEVELS,
                        cmap=WIND_CMAP,
                        transform=ccrs.PlateCarree(),
                        extend='max')
    ax1.quiver(lon[::8, ::8], lat[::8, ::8],
                u10[::8, ::8], v10[::8, ::8],
                transform=ccrs.PlateCarree(), scale=400, alpha=0.7)
    ax1.coastlines()
    ax1.set_title('Wind Field', fontsize=SUBTITLE_FONT_SIZE)
    plt.colorbar(cf1, ax=ax1, label='Wind Speed (m/s)', shrink=0.8)
    
    # 子图2: 温度
    ax2 = plt.subplot(2, 2, 2, projection=ccrs.PlateCarree())
    cf2 = ax2.contourf(lon, lat, t2_c,
                        levels=TEMP_LEVELS,
                        cmap=TEMP_CMAP,
                        transform=ccrs.PlateCarree(),
                        extend='both')
    ax2.contour(lon, lat, t2_c, levels=TEMP_LEVELS[::2],
                colors='black', linewidths=0.3,
                transform=ccrs.PlateCarree())
    ax2.coastlines()
    ax2.set_title('2m Temperature', fontsize=SUBTITLE_FONT_SIZE)
    plt.colorbar(cf2, ax=ax2, label='Temperature (°C)', shrink=0.8)
    
    # 子图3: 降水
    ax3 = plt.subplot(2, 2, 3, projection=ccrs.PlateCarree())
    cf3 = ax3.contourf(lon, lat, total_precip,
                        levels=PRECIP_LEVELS,
                        cmap=PRECIP_CMAP,
                        transform=ccrs.PlateCarree(),
                        extend='max')
    ax3.coastlines()
    ax3.set_title('Precipitation', fontsize=SUBTITLE_FONT_SIZE)
    plt.colorbar(cf3, ax=ax3, label='Precipitation (mm)', shrink=0.8)
    
    # 子图4: 湿度
    ax4 = plt.subplot(2, 2, 4, projection=ccrs.PlateCarree())
    cf4 = ax4.contourf(lon, lat, moisture,
                        levels=MOISTURE_LEVELS,
                        cmap=MOISTURE_CMAP,
                        transform=ccrs.PlateCarree(),
                        extend='max')
    ax4.coastlines()
    ax4.set_title('Moisture', fontsize=SUBTITLE_FONT_SIZE)
    plt.colorbar(cf4, ax=ax4, label='Specific Humidity (g/kg)', shrink=0.8)
    
    fig.suptitle(f'WRF Comprehensive Analysis\nTime Index: {time_idx}',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_energy_balance(ds, time_idx=0, save_path=None):
    """
    绘制能量平衡分量
    
    包括: SWDOWN, GLW, HFX, LH, QFX, PBLH
    """
    print("  绘制能量平衡...")
    
    lon = ds['XLONG'].values[time_idx]
    lat = ds['XLAT'].values[time_idx]
    
    fig, axes = plt.subplots(2, 3, figsize=FIGURE_SIZE_ENERGY,
                             subplot_kw={'projection': ccrs.PlateCarree()})
    axes = axes.flatten()
    
    # SWDOWN
    if 'SWDOWN' in ds.data_vars:
        swdown = ds['SWDOWN'].values[time_idx]
        cf0 = axes[0].contourf(lon, lat, swdown,
                                levels=SWDOWN_LEVELS,
                                cmap=SWDOWN_CMAP,
                                transform=ccrs.PlateCarree(),
                                extend='max')
        axes[0].coastlines()
        axes[0].set_title('Shortwave Radiation', fontsize=SUBTITLE_FONT_SIZE-2)
        plt.colorbar(cf0, ax=axes[0], label='W/m²', shrink=0.8)
    
    # GLW
    if 'GLW' in ds.data_vars:
        glw = ds['GLW'].values[time_idx]
        cf1 = axes[1].contourf(lon, lat, glw,
                                levels=SWDOWN_LEVELS,
                                cmap=SWDOWN_CMAP,
                                transform=ccrs.PlateCarree(),
                                extend='max')
        axes[1].coastlines()
        axes[1].set_title('Longwave Radiation', fontsize=SUBTITLE_FONT_SIZE-2)
        plt.colorbar(cf1, ax=axes[1], label='W/m²', shrink=0.8)
    
    # HFX
    if 'HFX' in ds.data_vars:
        hfx = ds['HFX'].values[time_idx]
        cf2 = axes[2].contourf(lon, lat, hfx,
                                levels=HFX_LEVELS,
                                cmap=HFX_CMAP,
                                transform=ccrs.PlateCarree(),
                                extend='both')
        axes[2].coastlines()
        axes[2].set_title('Sensible Heat Flux', fontsize=SUBTITLE_FONT_SIZE-2)
        plt.colorbar(cf2, ax=axes[2], label='W/m²', shrink=0.8)
    
    # LH
    if 'LH' in ds.data_vars:
        lh = ds['LH'].values[time_idx]
        cf3 = axes[3].contourf(lon, lat, lh,
                                levels=LH_LEVELS,
                                cmap=LH_CMAP,
                                transform=ccrs.PlateCarree(),
                                extend='max')
        axes[3].coastlines()
        axes[3].set_title('Latent Heat Flux', fontsize=SUBTITLE_FONT_SIZE-2)
        plt.colorbar(cf3, ax=axes[3], label='W/m²', shrink=0.8)
    
    # QFX
    if 'QFX' in ds.data_vars:
        qfx = ds['QFX'].values[time_idx]
        cf4 = axes[4].contourf(lon, lat, qfx,
                                levels=LH_LEVELS,
                                cmap=LH_CMAP,
                                transform=ccrs.PlateCarree(),
                                extend='max')
        axes[4].coastlines()
        axes[4].set_title('Moisture Flux', fontsize=SUBTITLE_FONT_SIZE-2)
        plt.colorbar(cf4, ax=axes[4], label='kg/m²/s', shrink=0.8)
    
    # PBLH
    if 'PBLH' in ds.data_vars:
        pblh = ds['PBLH'].values[time_idx]
        cf5 = axes[5].contourf(lon, lat, pblh,
                                levels=PBLH_LEVELS,
                                cmap=PBLH_CMAP,
                                transform=ccrs.PlateCarree(),
                                extend='max')
        axes[5].coastlines()
        axes[5].set_title('PBL Height', fontsize=SUBTITLE_FONT_SIZE-2)
        plt.colorbar(cf5, ax=axes[5], label='m', shrink=0.8)
    
    fig.suptitle(f'WRF Energy Balance Components\nTime Index: {time_idx}',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_soil_moisture(ds, time_idx=0, save_path=None):
    """
    绘制土壤湿度分布
    
    土壤湿度单位为kg/m²或m³/m³，这里假设为体积含水量百分比
    """
    print("  绘制土壤湿度...")
    
    if 'SMOIS' not in ds.data_vars:
        print("    警告: SMOIS变量不存在，跳过")
        return
    
    lon = ds['XLONG'].values[time_idx]
    lat = ds['XLAT'].values[time_idx]
    
    # 第一层土壤 (0-10cm)
    smois = ds['SMOIS'].values[time_idx, 0] * 100  # 转换为百分比
    
    fig = plt.figure(figsize=FIGURE_SIZE_SINGLE)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    
    cf = ax.contourf(lon, lat, smois,
                     levels=SOIL_MOISTURE_LEVELS,
                     cmap=SOIL_MOISTURE_CMAP,
                     transform=ccrs.PlateCarree(),
                     extend='max')
    
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.set_title(f'Soil Moisture (0-10cm)\nTime Index: {time_idx}',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    ax.set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Latitude (°N)', fontsize=LABEL_FONT_SIZE)
    
    plt.colorbar(cf, ax=ax, label='Soil Moisture (%)')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_time_evolution_frames(ds, n_frames=6, save_path=None):
    """
    绘制时间演变帧
    
    用于展示风场等变量的时间演变
    """
    print("  绘制时间演变...")
    
    nt = ds['XTIME'].values.shape[0]
    step = max(1, nt // n_frames)
    
    fig, axes = plt.subplots(2, 3, figsize=FIGURE_SIZE_EVOLUTION,
                             subplot_kw={'projection': ccrs.PlateCarree()})
    axes = axes.flatten()
    
    for idx, t in enumerate(range(0, nt, step)):
        if idx >= 6:
            break
        
        u10 = ds['U10'].values[t]
        v10 = ds['V10'].values[t]
        wind_speed = calculate_wind_speed(u10, v10)
        
        lon = ds['XLONG'].values[t]
        lat = ds['XLAT'].values[t]
        
        cf = axes[idx].contourf(lon, lat, wind_speed,
                                levels=15,
                                cmap=WIND_CMAP,
                                transform=ccrs.PlateCarree(),
                                extend='max')
        axes[idx].quiver(lon[::10, ::10], lat[::10, ::10],
                        u10[::10, ::10], v10[::10, ::10],
                        transform=ccrs.PlateCarree(), scale=400, alpha=0.7)
        axes[idx].coastlines()
        axes[idx].set_title(f'Time Step {t}', fontsize=SUBTITLE_FONT_SIZE-2)
    
    fig.suptitle('Wind Evolution Over Time',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    
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
    print("WRF 组合分析")
    print("=" * 60)
    
    print("\n[1/4] 加载WRF数据...")
    ds = load_wrf_data('d01')
    
    print("\n[2/4] 绘制全要素综合图...")
    plot_full_composite(ds, time_idx=TIME_IDX,
                       save_path=os.path.join(OUTPUT_DIR, 'composite_full.png'))
    
    print("\n[3/4] 绘制能量平衡...")
    plot_energy_balance(ds, time_idx=TIME_IDX,
                       save_path=os.path.join(OUTPUT_DIR, 'composite_energy.png'))
    
    print("\n[4/4] 绘制土壤湿度...")
    plot_soil_moisture(ds, time_idx=TIME_IDX,
                       save_path=os.path.join(OUTPUT_DIR, 'composite_soil.png'))
    
    print("\n[Extra] 绘制时间演变...")
    plot_time_evolution_frames(ds, n_frames=N_FRAMES,
                               save_path=os.path.join(OUTPUT_DIR, 'composite_evolution.png'))
    
    ds.close()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
