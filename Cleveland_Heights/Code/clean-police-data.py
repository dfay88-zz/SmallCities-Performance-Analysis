import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

policeData_17 = pd.read_csv('../Data/Interim/police_data/2017clean.csv', index_col=0)

policeData_16 = pd.read_csv('../Data/Interim/police_data/2016clean.csv', index_col=0)

policeData_15 = pd.read_csv('../Data/Interim/police_data/2015clean.csv', index_col=0)

policeData_14 = pd.read_csv('../Data/Interim/police_data/2014clean.csv', index_col=0)

policeData_13 = pd.read_csv('../Data/Interim/police_data/2013clean.csv', index_col=0)

geocode1 = pd.read_csv('../Data/Interim/police_data/geocodes/Cop_geocodes_991.csv', index_col=0)
geocode2 = pd.read_csv('../Data/Interim/police_data/geocodes/Cop_geocodes_991_2000.csv', index_col=0)
geocode3 = pd.read_csv('../Data/Interim/police_data/geocodes/Cop_geocodes_1984_3000.csv', index_col=0)
geocode4 = pd.read_csv('../Data/Interim/police_data/geocodes/Cop_geocodes_2993_4000.csv', index_col=0)
geocode5 = pd.read_csv('../Data/Interim/police_data/geocodes/Cop_geocodes_3988_5000.csv', index_col=0)
geocode6 = pd.read_csv('../Data/Interim/police_data/geocodes/Cop_geocodes_4989_6000.csv', index_col=0)
geocode7 = pd.read_csv('../Data/Interim/police_data/geocodes/Cop_geocodes_5985_7000.csv', index_col=0)
geocode8 = pd.read_csv('../Data/Interim/police_data/geocodes/Cop_geocodes_6971_8000.csv', index_col=0)
geocode9 = pd.read_csv('../Data/Interim/police_data/geocodes/Cop_geocodes_7972_9000.csv', index_col=0)
geocode10 = pd.read_csv('../Data/Interim/police_data/geocodes/Cop_geocodes_8982.csv', index_col=0)
geocode11 = pd.read_csv('../Data/Interim/police_data/geocodes/Cop_geocodes_10504.csv', index_col=0)

geocodes = geocode1.append(geocode2)
geocodes = geocodes.append(geocode3)
geocodes = geocodes.append(geocode4)
geocodes = geocodes.append(geocode5)
geocodes = geocodes.append(geocode6)
geocodes = geocodes.append(geocode7)
geocodes = geocodes.append(geocode8)
geocodes = geocodes.append(geocode9)
geocodes = geocodes.append(geocode10)
geocodes = geocodes.append(geocode11)

policeData = policeData_17.append(policeData_16)
policeData = policeData.append(policeData_15)
policeData = policeData.append(policeData_14)
policeData = policeData.append(policeData_13)

policeData.to_csv('../Data/Interim/police_data/police_data_13_17.csv')

policeData_count = policeData.groupby('address1').count()
policeData_count = policeData_count[['offtext']]
policeData_count.columns = ['PD_Count']

policeData_count.to_csv('../Data/processed/PD_count.csv')

policeData_count.reset_index(inplace=True)
policeData_count_shp = pd.merge(policeData_count, geocodes, how='inner', left_on='address1', right_on='address')
policeData_count_shp.drop('address1', axis=1, inplace=True)
policeData_count_shp['latitude'] = [float(str(row['coordinate']).split(',')[0][1:]) for ix, row in policeData_count_shp.iterrows()]
policeData_count_shp['longitude'] = [float(str(row['coordinate']).split(',')[1][1:-1]) for ix, row in policeData_count_shp.iterrows()]

geometry = gpd.GeoSeries([Point(xy) for xy in zip(policeData_count_shp.longitude, policeData_count_shp.latitude)])
policeData_count_shp = gpd.GeoDataFrame(policeData_count_shp, geometry=geometry)
policeData_count_shp.crs = {'init': 'epsg:4326'}
policeData_count_shp.dropna(subset=['geometry'], inplace=True)
policeData_count_shp.drop(['coordinate', 'latitude', 'longitude'], axis=1, inplace=True)

policeData_count_shp.to_file('../Data/processed/shapefiles/PD_count.shp')
