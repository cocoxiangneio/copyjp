#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
WRF诊断计算脚本
================================================================================

脚本名称: 04_wrf_diagnostics.py
功能描述:
    基于WRF模式输出计算诊断变量，包括:
    - 风速散度 (Divergence)
    - 相对涡度 (Vorticity)
    - 行星边界层高度 (PBLH)
    - 表面热通量 (HFX, LH)
    
物理背景:
    - 散度: D = ∂u/∂x + ∂v/∂y
      正值表示质量流出(辐散)，负值表示流入(辐合)
    - 涡度: ζ = ∂v/∂x - ∂u/∂y
      正值表示气旋性旋转，负值表示反气旋性旋转
    - PBLH: 行星边界层厚度，混合层高度
    - HFX: 感热通量，地表与大气间的显热交换
    - LH: 潜热通量，地表与大气间的潜热交换(蒸发/凝结)

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

# -------------------- 图形参数 --------------------
FIGURE_SIZE_SINGLE = (12, 8)
FIGURE_SIZE_MULTI = (16, 12)

DPI = 150

# 字体
rcParams['font.family'] = 'sans-serif'
TITLE_FONT_SIZE = 14
LABEL_FONT_SIZE = 12
COLORBAR_FONT_SIZE = 11

# -------------------- 散度/涡度配置 --------------------
# 网格距 (米) - WRF默认10km分辨率
DX = 10000.0  # 东-西方向
DY = 10000.0  # 南-北方向

# 散度色带
DIVERGENCE_CMAP = 'RdBu'
DIVERGENCE_LEVELS = np.linspace(-5, 5, 21)  # 单位: 10^-5 s^-1
DIVERGENCE_LABEL = 'Divergence (10⁻⁵ s⁻¹)'

# 涡度色带
VORTICITY_CMAP = 'RdBu_r'
VORTICITY_LEVELS = np.linspace(-10, 10, 21)
VORTICITY_LABEL = 'Vorticity (10⁻⁵ s⁻¹)'

# -------------------- 风速配置 --------------------
WIND_SPEED_CMAP = 'YlOrRd'
WIND_SPEED_LEVELS = np.linspace(0, 20, 21)
WIND_SPEED_LABEL = 'Wind Speed (m/s)'

# -------------------- PBL高度配置 --------------------
PBLH_CMAP = 'viridis'
PBLH_LEVELS = np.linspace(0, 2000, 21)
PBLH_LABEL = 'PBL Height (m)'

# -------------------- 热通量配置 --------------------
HFX_CMAP = 'YlOrRd'
HFX_LEVELS = np.linspace(-200, 400, 31)
HFX_LABEL = 'Sensible Heat Flux (W/m²)'

LH_CMAP = 'Blues'
LH_LEVELS = np.linspace(0, 300, 31)
LH_LABEL = 'Latent Heat Flux (W/m²)'

#================================================================================
# 函数定义区
#================================================================================

def load_wrf_data(domain='d01'):
    """加载WRF数据"""
    wrf_file = os.path.join(WRF_DIR, f'wrfout_{domain}_2024-04-04_00_00_00')
    print(f"  加载数据: {wrf_file}")
    ds = xr.open_dataset(wrf_file)
    return ds


def calculate_divergence(u, v, dx, dy):
    """
    计算风速散度
    
    物理公式:
        D = ∂u/∂x + ∂v/∂y
        
    使用有限差分近似:
        ∂u/∂x ≈ (u[i+1,j] - u[i-1,j]) / (2*dx)
        ∂v/∂y ≈ (v[i,j+1] - v[i,j-1]) / (2*dy)
        
    参数:
        u: 东向风 (m/s)
        v: 北向风 (m/s)
        dx: 东-西方向网格距 (m)
        dy: 南-北方向网格距 (m)
        
    返回:
        divergence: 散度 (s^-1)
    """
    # 使用numpy的gradient计算一阶导数
    du_dx = np.gradient(u, dx, axis=1)
    dv_dy = np.gradient(v, dy, axis=0)
    divergence = du_dx + dv_dy
    return divergence


def calculate_vorticity(u, v, dx, dy):
    """
    计算相对涡度
    
    物理公式:
        ζ = ∂v/∂x - ∂u/∂y
        
    参数:
        u: 东向风 (m/s)
        v: 北向风 (m/s)
        dx: 东-西方向网格距 (m)
        dy: 南-北方向网格距 (m)
        
    返回:
        vorticity: 相对涡度 (s^-1)
    """
    dv_dx = np.gradient(v, dx, axis=1)
    du_dy = np.gradient(u, dy, axis=0)
    vorticity = dv_dx - du_dy
    return vorticity


def calculate_wind_speed(u, v):
    """
    计算风速标量
    
    公式: WSP = sqrt(U² + V²)
    """
    return np.sqrt(u**2 + v**2)


def plot_divergence(ds, time_idx=0, save_path=None):
    """
    绘制风速散度图
    
    参数:
        ds: WRF数据集
        time_idx: 时间步
        save_path: 保存路径
    """
    print("  绘制散度...")
    
    # 提取数据
    u = ds['U10'].values[time_idx]
    v = ds['V10'].values[time_idx]
    
    # 计算散度
    div = calculate_divergence(u, v, DX, DY)
    
    # 坐标
    lon = ds['XLONG'].values[time_idx]
    lat = ds['XLAT'].values[time_idx]
    
    # 绘图
    fig = plt.figure(figsize=FIGURE_SIZE_SINGLE)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    
    # 转换为常用单位
    div_scaled = div * 1e5
    
    cf = ax.contourf(lon, lat, div_scaled,
                     levels=DIVERGENCE_LEVELS,
                     cmap=DIVERGENCE_CMAP,
                     transform=ccrs.PlateCarree(),
                     extend='both')
    
    cbar = plt.colorbar(cf, ax=ax)
    cbar.set_label(DIVERGENCE_LABEL, fontsize=COLORBAR_FONT_SIZE)
    
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.set_title(f'Wind Divergence\nTime: {time_idx}',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    ax.set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Latitude (°N)', fontsize=LABEL_FONT_SIZE)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_vorticity(ds, time_idx=0, save_path=None):
    """
    绘制相对涡度图
    
    参数:
        ds: WRF数据集
        time_idx: 时间步
        save_path: 保存路径
    """
    print("  绘制涡度...")
    
    u = ds['U10'].values[time_idx]
    v = ds['V10'].values[time_idx]
    
    vor = calculate_vorticity(u, v, DX, DY)
    
    lon = ds['XLONG'].values[time_idx]
    lat = ds['XLAT'].values[time_idx]
    
    fig = plt.figure(figsize=FIGURE_SIZE_SINGLE)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    
    vor_scaled = vor * 1e5
    
    cf = ax.contourf(lon, lat, vor_scaled,
                     levels=VORTICITY_LEVELS,
                     cmap=VORTICITY_CMAP,
                     transform=ccrs.PlateCarree(),
                     extend='both')
    
    cbar = plt.colorbar(cf, ax=ax)
    cbar.set_label(VORTICITY_LABEL, fontsize=COLORBAR_FONT_SIZE)
    
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.set_title(f'Relative Vorticity\nTime: {time_idx}',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    ax.set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Latitude (°N)', fontsize=LABEL_FONT_SIZE)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_wind_speed_with_contours(ds, time_idx=0, save_path=None):
    """
    绘制风速等值线填色图
    
    参数:
        ds: WRF数据集
        time_idx: 时间步
        save_path: 保存路径
    """
    print("  绘制风速等值线...")
    
    u10 = ds['U10'].values[time_idx]
    v10 = ds['V10'].values[time_idx]
    wind_speed = calculate_wind_speed(u10, v10)
    
    lon = ds['XLONG'].values[time_idx]
    lat = ds['XLAT'].values[time_idx]
    
    fig = plt.figure(figsize=FIGURE_SIZE_SINGLE)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    
    # 填色层
    cf = ax.contourf(lon, lat, wind_speed,
                     levels=WIND_SPEED_LEVELS,
                     cmap=WIND_SPEED_CMAP,
                     transform=ccrs.PlateCarree(),
                     extend='max')
    
    # 等值线
    cs = ax.contour(lon, lat, wind_speed,
                    levels=10,
                    colors='black',
                    linewidths=0.5,
                    transform=ccrs.PlateCarree())
    ax.clabel(cs, inline=True, fontsize=8, fmt='%.0f')
    
    cbar = plt.colorbar(cf, ax=ax)
    cbar.set_label(WIND_SPEED_LABEL, fontsize=COLORBAR_FONT_SIZE)
    
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.set_title(f'Wind Speed with Contours\nTime: {time_idx}',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    ax.set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Latitude (°N)', fontsize=LABEL_FONT_SIZE)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_pbl_height(ds, time_idx=0, save_path=None):
    """
    绘制行星边界层高度图
    
    PBLH: 行星边界层厚度，表示湍流混合能达到的高度
    
    参数:
        ds: WRF数据集
        time_idx: 时间步
        save_path: 保存路径
    """
    print("  绘制PBL高度...")
    
    if 'PBLH' not in ds.data_vars:
        print("    警告: PBLH变量不存在，跳过")
        return
    
    pblh = ds['PBLH'].values[time_idx]
    
    lon = ds['XLONG'].values[time_idx]
    lat = ds['XLAT'].values[time_idx]
    
    fig = plt.figure(figsize=FIGURE_SIZE_SINGLE)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    
    cf = ax.contourf(lon, lat, pblh,
                     levels=PBLH_LEVELS,
                     cmap=PBLH_CMAP,
                     transform=ccrs.PlateCarree(),
                     extend='max')
    
    cbar = plt.colorbar(cf, ax=ax)
    cbar.set_label(PBLH_LABEL, fontsize=COLORBAR_FONT_SIZE)
    
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.set_title(f'Planetary Boundary Layer Height\nTime: {time_idx}',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    ax.set_xlabel('Longitude (°E)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Latitude (°N)', fontsize=LABEL_FONT_SIZE)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_heat_fluxes(ds, time_idx=0, save_path=None):
    """
    绘制表面热通量图
    
    - HFX: 感热通量 (W/m²)，地面与大气间的显热交换
    - LH: 潜热通量 (W/m²)，地面与大气间的潜热交换(蒸发/凝结)
    
    参数:
        ds: WRF数据集
        time_idx: 时间步
        save_path: 保存路径
    """
    print("  绘制热通量...")
    
    if 'HFX' not in ds.data_vars or 'LH' not in ds.data_vars:
        print("    警告: 热通量变量不存在，跳过")
        return
    
    hfx = ds['HFX'].values[time_idx]
    lh = ds['LH'].values[time_idx]
    
    lon = ds['XLONG'].values[time_idx]
    lat = ds['XLAT'].values[time_idx]
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6),
                             subplot_kw={'projection': ccrs.PlateCarree()})
    
    # 感热通量
    cf1 = axes[0].contourf(lon, lat, hfx,
                           levels=HFX_LEVELS,
                           cmap=HFX_CMAP,
                           transform=ccrs.PlateCarree(),
                           extend='both')
    axes[0].coastlines()
    axes[0].set_title('Sensible Heat Flux (HFX)', fontsize=TITLE_FONT_SIZE-2)
    plt.colorbar(cf1, ax=axes[0], label=HFX_LABEL)
    
    # 潜热通量
    cf2 = axes[1].contourf(lon, lat, lh,
                           levels=LH_LEVELS,
                           cmap=LH_CMAP,
                           transform=ccrs.PlateCarree(),
                           extend='max')
    axes[1].coastlines()
    axes[1].set_title('Latent Heat Flux (LH)', fontsize=TITLE_FONT_SIZE-2)
    plt.colorbar(cf2, ax=axes[1], label=LH_LABEL)
    
    fig.suptitle(f'Surface Heat Fluxes\nTime: {time_idx}',
                 fontsize=TITLE_FONT_SIZE, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
        print(f"    保存至: {save_path}")
    plt.close()


def plot_composite_diagnostics(ds, time_idx=0, save_path=None):
    """
    绘制诊断变量综合图
    
    参数:
        ds: WRF数据集
        time_idx: 时间步
        save_path: 保存路径
    """
    print("  绘制综合诊断图...")
    
    lon = ds['XLONG'].values[time_idx]
    lat = ds['XLAT'].values[time_idx]
    
    # 准备数据
    u10 = ds['U10'].values[time_idx]
    v10 = ds['V10'].values[time_idx]
    wind_speed = calculate_wind_speed(u10, v10)
    vor = calculate_vorticity(u10, v10, DX, DY) * 1e5
    
    # 创建2x2子图
    fig, axes = plt.subplots(2, 2, figsize=FIGURE_SIZE_MULTI,
                             subplot_kw={'projection': ccrs.PlateCarree()})
    
    # 风速
    cf1 = axes[0, 0].contourf(lon, lat, wind_speed,
                               levels=WIND_SPEED_LEVELS,
                               cmap=WIND_SPEED_CMAP,
                               transform=ccrs.PlateCarree(),
                               extend='max')
    axes[0, 0].coastlines()
    axes[0, 0].set_title('Wind Speed', fontsize=TITLE_FONT_SIZE-2)
    plt.colorbar(cf1, ax=axes[0, 0], label='m/s')
    
    # 涡度
    cf2 = axes[0, 1].contourf(lon, lat, vor,
                               levels=VORTICITY_LEVELS,
                               cmap=VORTICITY_CMAP,
                               transform=ccrs.PlateCarree(),
                               extend='both')
    axes[0, 1].coastlines()
    axes[0, 1].set_title('Vorticity', fontsize=TITLE_FONT_SIZE-2)
    plt.colorbar(cf2, ax=axes[0, 1], label='10⁻⁵ s⁻¹')
    
    # PBL高度
    if 'PBLH' in ds.data_vars:
        pblh = ds['PBLH'].values[time_idx]
        cf3 = axes[1, 0].contourf(lon, lat, pblh,
                                  levels=PBLH_LEVELS,
                                  cmap=PBLH_CMAP,
                                  transform=ccrs.PlateCarree(),
                                  extend='max')
        axes[1, 0].coastlines()
        axes[1, 0].set_title('PBL Height', fontsize=TITLE_FONT_SIZE-2)
        plt.colorbar(cf3, ax=axes[1, 0], label='m')
    
    # 热通量
    if 'HFX' in ds.data_vars:
        hfx = ds['HFX'].values[time_idx]
        cf4 = axes[1, 1].contourf(lon, lat, hfx,
                                  levels=HFX_LEVELS,
                                  cmap=HFX_CMAP,
                                  transform=ccrs.PlateCarree(),
                                  extend='both')
        axes[1, 1].coastlines()
        axes[1, 1].set_title('Sensible Heat Flux', fontsize=TITLE_FONT_SIZE-2)
        plt.colorbar(cf4, ax=axes[1, 1], label='W/m²')
    
    fig.suptitle(f'WRF Diagnostic Variables\nTime: {time_idx}',
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
    print("WRF 诊断计算")
    print("=" * 60)
    
    print("\n[1/6] 加载WRF数据...")
    ds = load_wrf_data('d01')
    
    print("\n[2/6] 绘制散度...")
    plot_divergence(ds, time_idx=TIME_IDX,
                   save_path=os.path.join(OUTPUT_DIR, 'diagnostics_divergence.png'))
    
    print("\n[3/6] 绘制涡度...")
    plot_vorticity(ds, time_idx=TIME_IDX,
                  save_path=os.path.join(OUTPUT_DIR, 'diagnostics_vorticity.png'))
    
    print("\n[4/6] 绘制风速等值线...")
    plot_wind_speed_with_contours(ds, time_idx=TIME_IDX,
                                 save_path=os.path.join(OUTPUT_DIR, 'diagnostics_wind_speed.png'))
    
    print("\n[5/6] 绘制PBL高度...")
    plot_pbl_height(ds, time_idx=TIME_IDX,
                   save_path=os.path.join(OUTPUT_DIR, 'diagnostics_pblh.png'))
    
    print("\n[6/6] 绘制热通量...")
    plot_heat_fluxes(ds, time_idx=TIME_IDX,
                     save_path=os.path.join(OUTPUT_DIR, 'diagnostics_heat_fluxes.png'))
    
    print("\n[Extra] 绘制综合诊断图...")
    plot_composite_diagnostics(ds, time_idx=TIME_IDX,
                              save_path=os.path.join(OUTPUT_DIR, 'diagnostics_composite.png'))
    
    ds.close()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
