import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import os

complaints = pd.read_excel('../Data/Raw/Access_CH.xlsx')
geocodes = pd.read_excel('../Data/Interim/AccessCH_geocodes.xlsx')

complaints_gc = pd.merge(complaints, geocodes, how='left', left_on='Address', right_on='address')
complaints_gc.drop_duplicates(['Description', 'Address', 'Date Created'], inplace=True)
complaints_gc.drop('address', axis=1, inplace=True)

complaints_count = complaints_gc.groupby('Address').count()
complaints_count = complaints_count[['Description']]
complaints_count.columns = ['Complaint_count']
complaints_count.to_csv('../Data/processed/complaint_count.csv', encoding='utf-8')

complaints_count.reset_index(inplace=True)
complaints_count = pd.merge(complaints_count, geocodes, how='left', left_on='Address', right_on='address')
complaints_count.drop('address', axis=1, inplace=True)
complaints_count.dropna(subset=['coordinate'], inplace=True)
complaints_count['latitude'] = [float(str(row['coordinate']).split(',')[0][1:]) for ix, row in complaints_count.iterrows()]
complaints_count['longitude'] = [float(str(row['coordinate']).split(',')[1][1:-1]) for ix, row in complaints_count.iterrows()]

geometry = gpd.GeoSeries([Point(xy) for xy in zip(complaints_count.longitude, complaints_count.latitude)])
complaints_count_shape = gpd.GeoDataFrame(complaints_count, geometry=geometry)
complaints_count_shape.crs = {'init': 'epsg:4326'}
complaints_count_shape.dropna(subset=['geometry'], inplace=True)
complaints_count_shape.drop(['coordinate', 'latitude', 'longitude'], axis=1, inplace=True)

complaints_count_shape.to_file('../Data/processed/shapefiles/complaint_count.shp')
