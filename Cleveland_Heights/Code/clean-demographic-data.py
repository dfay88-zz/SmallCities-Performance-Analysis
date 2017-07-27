import pandas as pd
import geopandas as gpd

demo_data = gpd.read_file('../Data/Raw/Tract_2010Census_DP1/Tract_2010Census_DP_Cuyahoga.shp')
econ_data = pd.read_table('../Data/Raw/econ_data_tab.txt')

demo_data['Under_16_Percent'] = (demo_data['DP0010001'] - demo_data['DP0030001'])/demo_data['DP0010001']
demo_data['65_Over_Percent'] = demo_data['DP0070001']/demo_data['DP0010001']
demo_data['White_Percent'] = demo_data['DP0080003']/demo_data['DP0080001']
demo_data['Black_Percent'] = demo_data['DP0080004']/demo_data['DP0080001']
demo_data['Other_Percent'] = 1 - (demo_data['White_Percent'] + demo_data['Black_Percent'])
demo_data = demo_data[['Under_16_Percent', '65_Over_Percent', 'White_Percent', 'Black_Percent',
                       'Other_Percent', 'DP0010001', 'geometry', 'GEOID10', 'NAMELSAD10']]

econ_tracts = []
for ix, row in econ_data.iterrows():
    ct = row['Geography'].split(',')[0]
    econ_tracts.append(ct)

econ_data['NAMELSAD10'] = econ_tracts

econ_data = econ_data[['NAMELSAD10', 'Estimate; Median household income in the past 12 months (in 2015 Inflation-adjusted dollars)']]
econ_data.columns = ['NAMELSAD10', 'Median_Income']

demo_ct = pd.merge(demo_data, econ_data, on='NAMELSAD10')

cts = ['Census Tract 1401', 'Census Tract 1403.01', 'Census Tract 1403.02', 'Census Tract 1404', 'Census Tract 1405',
       'Census Tract 1960', 'Census Tract 1407.01', 'Census Tract 1408', 'Census Tract 1410', 'Census Tract 1411',
       'Census Tract 1412', 'Census Tract 1406', 'Census Tract 1407.02', 'Census Tract 1409', 'Census Tract 1413',
       'Census Tract 1414', 'Census Tract 1415', 'Census Tract 1416.02', 'Census Tract 1416.01', 'Census Tract 1417']

demo_ct = demo_ct.loc[demo_ct['NAMELSAD10'].isin(cts)]

demo_ct.to_file('../Data/processed/shapefiles/CT_Demo_CH.shp')

demo_ct.to_csv("../Data/processed/CT_Demo_Data_CH.csv")
