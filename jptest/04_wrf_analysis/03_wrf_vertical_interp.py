#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
WRF垂直插值分析脚本
================================================================================

脚本名称: 03_wrf_vertical_interp.py
功能描述:
    将WRF模式层的位温、风等变量插值到指定气压层，
    并绘制垂直廓线图。
    
    主要功能:
    1. 等气压层高度的温度/风场平面图
    2. 多层气压平面图对比
    3. 单点垂直廓线图
    
物理背景:
    - 气压坐标: WRF使用eta坐标，需要转换为气压
      P = PB + P (扰动气压 + 基础气压)
    - 位温转换: 模式输出为扰动位温(POTENTIAL TEMP, 相对于参考态的偏差)
      实际位温: θ = T + θ_0
    - 温度递减率: 温度与气压的关系
      T = θ * (P/P0)^R/Cp
      其中 R/Cp ≈ 0.286

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
from scipy.interpolate import interp1d
from matplotlib import rcParams

#================================================================================
# 全局配置参数区
#================================================================================

# -------------------- 数据路径配置 --------------------
WRF_DIR = '/Users/dengmeizhen/cwj'
OUTPUT_DIR = '/Users/dengmeizhen/cwj/jptest/04_wrf_analysis'

# -------------------- 气压层配置 --------------------
# 要插值的气压层 (hPa)
# 常用: 850, 700, 500, 300, 200, 100
PRESSURE_LEVELS = [850, 700, 500, 300]

# -------------------- 绘图区域配置 --------------------
PLOT_EXTENT = None  # [lon_min, lon_max, lat_min, lat_max]
MAP_PROJECTION = ccrs.PlateCarree()

# -------------------- 时间配置 --------------------
TIME_IDX = 0

# -------------------- 图形参数 --------------------
FIGURE_SIZE_SINGLE = (12, 8)
FIGURE_SIZE_MULTI = (16, 10)
FIGURE_SIZE_PROFILE = (16, 8)

DPI = 150

# 字体
rcParams['font.family'] = 'sans-serif'
TITLE_FONT_SIZE = 14
LABEL_FONT_SIZE = 12
COLORBAR_FONT_SIZE = 11

# -------------------- 温度绘图配置 --------------------
TEMP_CMAP = 'RdBu_r'
TEMP_LEVELS = np.linspace(10, 30, 21)  # 850hPa用
TEMP_LABEL = 'Temperature (°C)'

# -------------------- 风速绘图配置 --------------------
WIND_CMAP = 'jet'
WIND_LEVELS = np.linspace(0, 30, 16)
WIND_LABEL = 'Wind Speed (m/s)'

# -------------------- 湿度绘图配置 --------------------
MOISTURE_CMAP = 'GnBu'
MOISTURE_LEVELS = np.linspace(0, 14, 15)
MOISTURE_LABEL = 'Specific Humidity (g/kg)'

# -------------------- 垂直廓线配置 --------------------
PROFILE_VARS = ['temperature', 'u_wind', 'v_wind', 'moisture']
PROFILE_VAR_LABELS = {
    'temperature': 'Temperature (°C)',
    'u_wind': 'U Wind (m/s)',
    'v_wind': 'V Wind (m/s)',
    'moisture': 'Specific Humidity (g/kg)'
}
PROFILE_COLORS = {
    'temperature': '#e41a1c',
    'u_wind': '#377eb8',
    'v_wind': '#4daf4a',
    'moisture': '#984ea3'
}

PROFILE_FIGURE_SIZE = (16, 8)

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
    
    WRF模式输出:
    - P: 扰动气压 (Pa)
    - PB: 基础气压 (Pa)
    实际气压: P_total = P + PB
    
    参数:
        ds: WRF数据集
        time_idx: 时间步
        
    返回:
        pressure_3d: (Time, bottom_top, South_North, West_East) 气压 (hPa)
    """
    p = ds['P'].values[time_idx]      # 扰动气压
    pb = ds['PB'].values[time_idx]     # 基础气压
    pressure_pa = p + pb                 # 总气压 (Pa)
    pressure_hpa = pressure_pa / 100.0   # 转换为 hPa
    return pressure_hpa


def convert_potential_temperature(t_p, pressure_hpa):
    """
    将扰动位温转换为实际温度
    
    WRF中T是相对于参考态的位温偏差
    θ = θ_ref + T
    
    温度与气压的关系:
    T = θ * (P/P0)^(R/Cp)
    
    参数:
        t_p: 位温扰动 (K)，来自WRF的T变量
        pressure_hpa: 气压 (hPa)
        
    返回:
        temperature: 实际温度 (K)
    """
    # 转换为摄氏度
    p0 = 1000.0  # 参考气压 (hPa)
    kappa = 0.286  # R/Cp
    
    # 假设参考位温约300K
    theta_ref = 300.0
    theta = theta_ref + t_p
    
    # 转换为温度
    temperature = theta * (pressure_hpa / p0) ** kappa
    return temperature


def interpolate_to_pressure_level(var_3d, pressure_3d, target_pressure):
    """
    将三维变量插值到指定气压层
    
    使用scipy的interp1d进行一维插值
    
    参数:
        var_3d: 三维变量数组 (nz, ny, nx)
        pressure_3d: 三维气压场 (nz, ny, nx) 单位hPa
        target_pressure: 目标气压 (hPa)
        
    返回:
        var_2d: 插值后的二维场
    """
    nz, ny, nx = var_3d.shape
    var_2d = np.zeros((ny, nx))
    
    for j in range(ny):
        for i in range(nx):
            p_profile = pressure_3d[:, j, i]
            var_profile = var_3d[:, j, i]
            
            # 去除无效值
            valid = ~np.isnan(p_profile) & ~np.isnan(var_profile)
            
            if valid.sum() >= 2:
                # 气压需要单调递减才能插值
                if np.all(np.diff(p_profile[valid]) < 0):
                    f = interp1d(p_profile[valid], var_profile[valid],
                                bounds_error=False, fill_value=np.nan)
                    var_2d[j, i] = f(target_pressure)
                else:
                    var_2d[j, i] = np.nan
            else:
                var_2d[j, i] = np.nan
    
    return var_2d


def plot_pressure_level_map(ds, var_name, pressure_level, time_idx=0, save_path=None):
    """
    绘制指定气压层的变量平面图
    
    参数:
        ds: WRF数据集
        var_name: 变量名 ('T', 'U', 'V', 'QVAPOR')
        pressure_level: 目标气压层 (hPa)
        time_idx: 时间步
        save_path: 保存路径
    """
    print(f"  绘制 {pressure_level}hPa {var_name}...")
    
    # 获取气压场
    pressure_3d = get_pressure_3d(ds, time_idx)
    
    # 获取变量场
    if var_name == 'T':
        t_p = ds['T'].values[time_idx]  # 位温扰动
        var_data = convert_potential_temperature(t_p, pressure_3d) - 273.15  # 转摄氏度
        levels = TEMP_LEVELS
        cmap = TEMP_CMAP
        label = TEMP_LABEL
    elif var_name == 'U':
        var_data = ds['U'].values[time_idx]
        levels = WIND_LEVELS
        cmap = WIND_CMAP
        label = 'U Wind (m/s)'
    elif var_name == 'V':
        var_data = ds['V'].values[time_idx]
        levels = WIND_LEVELS
        cmap = WIND_CMAP
        label = 'V Wind (m/s)'
    elif var_name == 'QVAPOR':
        var_data = ds['QVAPOR'].values[time_idx] * 1000  # 转g/kg
        levels = MOISTURE_LEVELS
        cmap = MOISTURE_CMAP
        label = MOISTURE_LABEL
    else:
        raise ValueError(f"Unknown variable: {var_name}")
    
    # 插值到目标气压层
    var_interp = interpolate_to_pressure_level(var_data, pressure_3d, pressure_level)
    
    # 坐标
    lon = ds['XLONG'].values[time_idx]
    lat = ds['XLAT'].values[time_idx]
    
    # 绘图
    fig = plt.figure(figsize=FIGURE_SIZE_SINGLE)
    ax = fig.add_subplot(1, 1, 1, projection=MAP_PROJECTION)
    
    cf = ax.contourf(lon, lat, var_interp,
                     levels=levels,
                     cmap=cmap,
                     transform=ccrs.PlateCarree(),
                     extend='both')
    
    cbar = plt.colorbar(cf, ax=ax)
    cbar.set_label(label, fontsize=COLORBAR_FONT_SIZE)
    
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.set_title(f'{var_name} at {pressure_level} hPa\nTime: {time_idx}',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    ax.set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Latitude (°N)', fontsize=LABEL_FONT_SIZE)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_multiple_pressure_levels(ds, var_name, pressure_levels, time_idx=0, save_path=None):
    """
    绘制多个气压层的对比图
    
    参数:
        ds: WRF数据集
        var_name: 变量名
        pressure_levels: 气压层列表
        time_idx: 时间步
        save_path: 保存路径
    """
    print(f"  绘制多气压层 {var_name}...")
    
    pressure_3d = get_pressure_3d(ds, time_idx)
    
    if var_name == 'T':
        t_p = ds['T'].values[time_idx]
        var_data = convert_potential_temperature(t_p, pressure_3d) - 273.15
        levels = TEMP_LEVELS
        cmap = TEMP_CMAP
        label = '°C'
    else:
        var_data = ds[var_name].values[time_idx]
        levels = WIND_LEVELS
        cmap = WIND_CMAP
        label = 'm/s'
    
    lon = ds['XLONG'].values[time_idx]
    lat = ds['XLAT'].values[time_idx]
    
    n_levels = len(pressure_levels)
    fig, axes = plt.subplots(1, n_levels, figsize=(6*n_levels, 5),
                             subplot_kw={'projection': MAP_PROJECTION})
    
    if n_levels == 1:
        axes = [axes]
    
    for idx, plev in enumerate(pressure_levels):
        var_interp = interpolate_to_pressure_level(var_data, pressure_3d, plev)
        
        cf = axes[idx].contourf(lon, lat, var_interp,
                                levels=levels,
                                cmap=cmap,
                                transform=ccrs.PlateCarree(),
                                extend='both')
        axes[idx].coastlines()
        axes[idx].set_title(f'{plev} hPa', fontsize=TITLE_FONT_SIZE-2)
        plt.colorbar(cf, ax=axes[idx], shrink=0.8, label=label)
    
    fig.suptitle(f'{var_name} at Multiple Pressure Levels\nTime: {time_idx}',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_vertical_profile(ds, lon, lat, time_idx=0, save_path=None):
    """
    绘制单点垂直廓线图
    
    显示温度、风、湿度随高度的变化
    
    参数:
        ds: WRF数据集
        lon: 目标经度
        lat: 目标纬度
        time_idx: 时间步
        save_path: 保存路径
    """
    print("  绘制垂直廓线...")
    
    # 找到最近网格点
    lons = ds['XLONG'].values[time_idx]
    lats = ds['XLAT'].values[time_idx]
    i = int(np.abs(lons[0, :] - lon).argmin())
    j = int(np.abs(lats[:, 0] - lat).argmin())
    
    actual_lon = lons[j, i]
    actual_lat = lats[j, i]
    print(f"    位置: ({actual_lon:.2f}°E, {actual_lat:.2f}°N)")
    
    # 气压
    pressure_3d = get_pressure_3d(ds, time_idx)
    pressure_profile = pressure_3d[:, j, i]  # (nz,)
    
    # 温度
    t_p = ds['T'].values[time_idx, :, j, i]
    temp_k = convert_potential_temperature(t_p, pressure_profile)
    temp_c = temp_k - 273.15
    
    # 风
    u = ds['U'].values[time_idx, :, j, i]
    v = ds['V'].values[time_idx, :, j, i]
    
    # 湿度
    if 'QVAPOR' in ds.data_vars:
        q = ds['QVAPOR'].values[time_idx, :, j, i] * 1000  # g/kg
    else:
        q = np.zeros_like(pressure_profile)
    
    # 绘图
    fig, axes = plt.subplots(1, 4, figsize=PROFILE_FIGURE_SIZE)
    
    # 温度廓线
    axes[0].plot(temp_c, pressure_profile, color=PROFILE_COLORS['temperature'],
                  linewidth=2)
    axes[0].set_xlabel('Temperature (°C)', fontsize=LABEL_FONT_SIZE)
    axes[0].set_ylabel('Pressure (hPa)', fontsize=LABEL_FONT_SIZE)
    axes[0].invert_yaxis()
    axes[0].set_title('Temperature', fontsize=TITLE_FONT_SIZE-2)
    axes[0].grid(True, alpha=0.3)
    
    # U风
    axes[1].plot(u, pressure_profile, color=PROFILE_COLORS['u_wind'],
                  linewidth=2)
    axes[1].set_xlabel('U Wind (m/s)', fontsize=LABEL_FONT_SIZE)
    axes[1].invert_yaxis()
    axes[1].set_title('U Wind', fontsize=TITLE_FONT_SIZE-2)
    axes[1].grid(True, alpha=0.3)
    axes[1].axvline(x=0, color='black', linestyle='--', linewidth=0.5)
    
    # V风
    axes[2].plot(v, pressure_profile, color=PROFILE_COLORS['v_wind'],
                  linewidth=2)
    axes[2].set_xlabel('V Wind (m/s)', fontsize=LABEL_FONT_SIZE)
    axes[2].invert_yaxis()
    axes[2].set_title('V Wind', fontsize=TITLE_FONT_SIZE-2)
    axes[2].grid(True, alpha=0.3)
    axes[2].axvline(x=0, color='black', linestyle='--', linewidth=0.5)
    
    # 湿度
    axes[3].plot(q, pressure_profile, color=PROFILE_COLORS['moisture'],
                  linewidth=2)
    axes[3].set_xlabel('Specific Humidity (g/kg)', fontsize=LABEL_FONT_SIZE)
    axes[3].invert_yaxis()
    axes[3].set_title('Moisture', fontsize=TITLE_FONT_SIZE-2)
    axes[3].grid(True, alpha=0.3)
    
    fig.suptitle(f'Vertical Profile at ({actual_lon:.2f}°E, {actual_lat:.2f}°N)\nTime: {time_idx}',
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
    print("WRF 垂直插值分析")
    print("=" * 60)
    
    print("\n[1/4] 加载WRF数据...")
    ds = load_wrf_data('d01')
    
    print("\n[2/4] 绘制单气压层图...")
    plot_pressure_level_map(ds, 'T', 850, time_idx=TIME_IDX,
                           save_path=os.path.join(OUTPUT_DIR, 'pressure_850hPa.png'))
    
    print("\n[3/4] 绘制多气压层对比...")
    plot_multiple_pressure_levels(ds, 'T', PRESSURE_LEVELS, time_idx=TIME_IDX,
                                  save_path=os.path.join(OUTPUT_DIR, 'pressure_multiple.png'))
    
    print("\n[4/4] 绘制垂直廓线...")
    lons = ds['XLONG'].values[0]
    lats = ds['XLAT'].values[0]
    center_lon = lons[lats.shape[0]//2, lons.shape[1]//2]
    center_lat = lats[lats.shape[0]//2, lons.shape[1]//2]
    plot_vertical_profile(ds, center_lon, center_lat, time_idx=TIME_IDX,
                         save_path=os.path.join(OUTPUT_DIR, 'vertical_profile.png'))
    
    ds.close()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
