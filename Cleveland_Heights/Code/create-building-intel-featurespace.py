
import pandas as pd
import geopandas as gpd

foreclosures = gpd.read_file('../Data/processed/shapefiles/FC_count.shp')
police = gpd.read_file('../Data/processed/shapefiles/PD_count.shp')
complaints = gpd.read_file('../Data/processed/shapefiles/complaint_count.shp')
owners = gpd.read_file('../Data/Interim/Master_Building/CH_Only_Clip.shp')
code_enforcement = gpd.read_file('../Data/processed/shapefiles/viol_agg_final_shp.shp')
tree_scores = pd.read_csv('../Data/processed/tree_scores.csv')
building_permits = pd.read_csv('../Data/processed/bldg_permits_agg.csv')

addresses = []
for ix, row in owners.iterrows():
    address = str(row['parcel_add'])[:-7]
    addresses.append(address)

owners['parcel_add'] = addresses


# foreclosures
foreclosures = foreclosures[['PPN', 'Count']]
foreclosures.columns = ['PPN', 'FC_count']
owners.PARCELPIN = owners.PARCELPIN.astype(str)
foreclosures.PPN = foreclosures.PPN.astype(str)
featureSpace = pd.merge(owners, foreclosures, how='left', left_on='PARCELPIN', right_on='PPN')
featureSpace.drop(['PPN'], axis=1, inplace=True)


# Police
police['address'] = map(lambda x: x.upper(), police['address'])
police['address'] = police['address'] + ', CLEVELAND HEIGHTS, OH'
featureSpace = gpd.sjoin(featureSpace, police, how='left', op='intersects')
featureSpace.drop(['address', 'index_right'], axis=1, inplace=True)

counts = featureSpace[['parcel_add', 'PARCELPIN', 'PD_Count']]
counts = counts.groupby(['parcel_add', 'PARCELPIN']).sum()
counts.reset_index(inplace=True)
featureSpace.drop(['PD_Count'], axis=1, inplace=True)
featureSpace.drop_duplicates(['parcel_add', 'PARCELPIN'], inplace=True)
featureSpace['PD_count'] = counts.PD_Count


# Complaints
addresses = []
for ix, row in complaints.iterrows():
    address = row['Address'].split(',')[0] + ', Cleveland Heights, OH'
    addresses.append(address)

complaints.Address = addresses
complaints['Address'] = map(lambda x: x.upper(), complaints['Address'])
featureSpace = gpd.sjoin(featureSpace, complaints, how='left', op='intersects')
featureSpace.drop(['Address', 'index_right'], axis=1, inplace=True)

counts = featureSpace[['parcel_add', 'PARCELPIN', 'Complaint_']]
counts = counts.groupby(['parcel_add', 'PARCELPIN']).sum()
counts.reset_index(inplace=True)
featureSpace.drop(['Complaint_'], axis=1, inplace=True)
featureSpace.drop_duplicates(['parcel_add', 'PARCELPIN'], inplace=True)
featureSpace['Comp_count'] = counts.Complaint_


# Code Enforcement
code_enforcement = code_enforcement[['address', 'negCodecnt', 'last_case', 'own_occup', 'geometry']]
featureSpace = gpd.sjoin(featureSpace, code_enforcement, how='left', op='intersects')
featureSpace.drop(['address', 'index_right'], axis=1, inplace=True)

counts = featureSpace[['parcel_add', 'PARCELPIN', 'negCodecnt']]
counts = counts.groupby(['parcel_add', 'PARCELPIN']).sum()
counts.reset_index(inplace=True)
featureSpace.drop(['negCodecnt'], axis=1, inplace=True)
featureSpace.drop_duplicates(['parcel_add', 'PARCELPIN'], inplace=True)
featureSpace['NegAct_count'] = counts.negCodecnt


# Tree Scores
def fix_address(row):
    num = row['Address'].split(' ')[2]
    st = row['Address'].split(' ')[0] + ' ' + row['Address'].split(' ')[1]
    add = num + ' ' + st + ', CLEVELAND HEIGHTS, OH'
    return add

tree_scores['Address'] = tree_scores.apply(fix_address, axis=1)
tree_scores['Address'] = map(lambda x: x.upper(), tree_scores['Address'])
featureSpace = pd.merge(featureSpace, tree_scores, how='left', left_on='parcel_add', right_on='Address')
featureSpace.drop('Address', axis=1, inplace=True)


# Building Permits
building_permits = building_permits[['parcelID', 'perm_num']]
featureSpace = pd.merge(featureSpace, building_permits, how='left', left_on='PARCEL_ID', right_on='parcelID')
featureSpace.drop('parcelID', axis=1, inplace=True)
featureSpace[['FC_count', 'PD_count', 'own_occup', 'Comp_count', 'NegAct_count', 'perm_num']] = featureSpace[['FC_count', 'PD_count', 'own_occup',
                                                                                                             'Comp_count', 'NegAct_count', 'perm_num']].fillna(value=0)
featureSpace.drop('sold_date', axis=1, inplace=True)
featureSpace_shp = gpd.GeoDataFrame(featureSpace, crs={'init': 'epsg:4326'})
featureSpace_shp.to_file('../Data/processed/shapefiles/featureSpace.shp')
