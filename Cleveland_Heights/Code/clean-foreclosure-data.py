import geopandas as gpd
import pandas as pd

foreclosures = gpd.read_file('../Data/Raw/Foreclosure_Filings_for_Cuyahoga_County.shp')

foreclosures_count = foreclosures.groupby(['PPN']).count()
foreclosures_count = foreclosures_count[['OBJECTID']]
foreclosures_count.reset_index(inplace=True)
foreclosures_count.columns = ['PPN', 'Count']

foreclosures_geo = foreclosures[['PPN', 'geometry']]
foreclosures_count = pd.merge(foreclosures_count, foreclosures_geo, how='left', on='PPN')
foreclosures_count.drop_duplicates('PPN', inplace=True)
foreclosures_count_shape = gpd.GeoDataFrame(foreclosures_count, crs={'init': 'epsg:4326'})

foreclosures_count.to_csv('../Data/processed/FC_count.csv')
foreclosures_count_shape.to_file('../Data/processed/shapefiles/FC_count.shp')
