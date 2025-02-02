# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 17:02:59 2021

@author: Administrator
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import jenkspy

from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['FangSong']
mpl.rcParams['axes.unicode_minus'] = False

def network_analysis(df_migra_data, target_city, CN_city_shp, n = 5):
    if target_city == '全国':
        city_network = df_migra_data
    else:
        city_network = df_migra_data[(df_migra_data['城市1'].isin(target_city))|(df_migra_data['城市2'].isin(target_city))]
    breaks = jenkspy.jenks_breaks(city_network['总流量'], nb_class = n)
    
    fig, ax0 = plt.subplots(figsize = (12,12))
    ax1 = CN_city_shp.plot(ax = ax0, color='#D9D9D9', linewidth=0.5, edgecolor='w')
    
    width = [0.5,1,1.5,3,6]
    alphas = [0.8,0.7,0.6,0.5,0.45]
    colors = ['#FFEBD6','#F2B599','#E08465','#D64F33','#C40A0A']
    for i in range(1,n+1):
        line_list_name = 'line_list' + str(i)
        df_name = 'df_bar' + str(i) 
        gdp_line_name = 'gdp_line'+ str(i)
        locals()[df_name] = city_network[(city_network['总流量']<= breaks[i])&(city_network['总流量']>= breaks[i-1])]
        locals()[line_list_name] = fill_line_list(locals()  [df_name])
        locals()[gdp_line_name] = gpd.GeoDataFrame(locals()[df_name], geometry = locals()[line_list_name], crs='EPSG:4326')
        locals()[gdp_line_name].sort_values('总流量',ascending=True,inplace=True)
        # locals()[gdp_line_name].plot(ax = ax0,cmp = 'YlOrRd',linewidth = width[i-1],alpha=alphas[i-1])
        ax2 = locals()[gdp_line_name].plot(ax = ax0, color = colors[i-1],linewidth = width[i-1],alpha=alphas[5-i])
    
    cities = set(np.append(city_network[city_network['总流量'] >= breaks[2]]['城市1'].values,city_network[city_network['总流量'] >= breaks[2]]['城市2'].values))
    # 只选择自然间断点第三级别以上联系的城市在图中显示
    cities_centroid = df_migra_data[df_migra_data['城市1'].isin(cities)].drop_duplicates('城市1')[['城市1','startx','starty']]
    cities_pt_shp = gpd.GeoDataFrame(cities_centroid, geometry=gpd.points_from_xy(cities_centroid['startx'],cities_centroid['starty']), crs='EPSG:4326')
    ax3 = cities_pt_shp.plot(ax = ax0, color = '#19232D', legend = True, markersize = 1, marker = 'o', label = '城市1')
    # 用圆点显示联系城市的位置
    for i in cities_centroid.index:
        text_lon = cities_centroid.loc[i,'startx']+0.1
        text_lat = cities_centroid.loc[i,'starty']
        text = cities_centroid.loc[i,'城市1']
        plt.text(text_lon,text_lat,text,fontsize=6)
        # 添加城市的名称
    # plt.axis('off')   
    plt.savefig(r'C:\Users\Administrator\Desktop' + '\\' + '_'.join(target_city) + '.png',dpi = 300)
    plt.show()
    

def fill_line_list(df):
    line_list = []
    for i in df.index:
        O_lon = df.loc[i,'startx']
        O_lat = df.loc[i,'starty']
        D_lon = df.loc[i,'endx']
        D_lat = df.loc[i,'endy']
        line_shape = LineString([[O_lon,O_lat],[D_lon,D_lat]])
        line_list.append(line_shape)
    return line_list

if __name__ == '__main__':
    CN_city = pd.read_excel(r'E:\1 - git\migration-link\1 - 城市中心点.xlsx')
    # 中国城市名单
    CN_city_shp = gpd.read_file(r'E:\1 - git\migration-link\市.shp').to_crs("EPSG:4326")
    # 中国城市的行政边界
    df_migra_data = pd.read_excel(r'E:\1 - git\migration-link\0 - immigration all.xlsx', sheet_name='sheet1')
    # 中国两两城市之间的人口迁徙量
    while True:
        print('\n')
        print(set(df_migra_data['城市1'].values))
        target_city = input('请从以上城市中输入需要考察人流联系的城市范围，用中文逗号隔开，或者输入“全国”' + '\n').split('，')
        # n = input('请输入自然断点法分级的级数，图中将只显示联系强度前三级的城市（默认为5级）' + '\n')
        network_analysis(df_migra_data, target_city, CN_city_shp)



    
    
    

    




