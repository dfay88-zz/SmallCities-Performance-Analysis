import pandas as pd
import geopandas as gpd

census_tracts = gpd.read_file('../Data/processed/shapefiles/CT_Demo_CH.shp')
foreclosures = gpd.read_file('../Data/processed/shapefiles/FC_count.shp')
police_dispatch = gpd.read_file('../Data/processed/shapefiles/PD_count.shp')
complaints = gpd.read_file('../Data/processed/shapefiles/complaint_count.shp')
property_info = gpd.read_file('../Data/processed/shapefiles/featureSpace.shp')

census_tracts = census_tracts[['Median_Inc', '65_Over_Pe', 'Under_16_P', 'White_Perc', 'Black_Perc',
                               'Other_Perc', 'DP0010001', 'GEOID10', 'NAMELSAD10', 'geometry']]

census_tracts = census_tracts.to_crs({'init': 'epsg:4326'})


# Calculate Count of Properties
trees = property_info[['Tree_Score', 'geometry']]
permits = property_info[['perm_num', 'geometry']]

property_info = property_info[['parcel_add', 'land_tax', 'vacant', 'own_occup', 'NegAct_cou', 'geometry']]
property_info.drop_duplicates(['parcel_add', 'land_tax', 'vacant'], inplace=True)
property_ct = gpd.sjoin(census_tracts, property_info, how='inner', op='intersects')
property_ct.drop_duplicates(['parcel_add', 'land_tax', 'vacant'], inplace=True)
property_ct_count = property_ct.groupby('NAMELSAD10').count()
property_ct_count = property_ct_count[['Median_Inc']]
property_ct_count.reset_index(inplace=True)
property_ct_count.columns = ['NAMELSAD10', 'Res_Count']
census_tracts = pd.merge(census_tracts, property_ct_count, how='inner')


# Calculate foreclosures
foreclosure_ct = gpd.sjoin(census_tracts, foreclosures, how='left', op='intersects')
foreclosure_count = foreclosure_ct.groupby('NAMELSAD10').sum()
foreclosure_count = foreclosure_count[['Count']]
foreclosure_count.reset_index(inplace=True)
featureSpace = pd.merge(census_tracts, foreclosure_count, how='inner')
featureSpace.columns = ['Median_Inc', 'Per_Over65', 'Per_Under16', 'Per_White', 'Per_Black', 'Per_Other',
                        'Population', 'GEOID', 'NAMELSAD10', 'geometry', 'Prop_Count', 'FC_Per']
featureSpace['FC_Per'] = featureSpace.FC_Per/featureSpace.Prop_Count


# Calculate police dispatches
police_dispatch_ct = gpd.sjoin(census_tracts, police_dispatch, how='left', op='intersects')
police_dispatch_count = police_dispatch_ct.groupby('NAMELSAD10').sum()
police_dispatch_count = police_dispatch_count[['PD_Count']]
police_dispatch_count.reset_index(inplace=True)
featureSpace = pd.merge(featureSpace, police_dispatch_count, how='inner')
featureSpace['PD_Count'] = featureSpace['PD_Count']/featureSpace.Population


# Calculate complaints
complaints.columns = ['Address', 'comp_count', 'geometry']
complaints_ct = gpd.sjoin(census_tracts, complaints, how='left', op='intersects')
complaints_count = complaints_ct.groupby('NAMELSAD10').sum()
complaints_count = complaints_count[['comp_count']]
complaints_count.reset_index(inplace=True)
featureSpace = pd.merge(featureSpace, complaints_count, how='inner')
featureSpace['comp_count'] = featureSpace['comp_count']/featureSpace.Population


# Calculate median land tax value
property_info_ct = gpd.sjoin(census_tracts, property_info, how='left', op='intersects')
property_info_count = property_info_ct.groupby('NAMELSAD10').median()
property_info_count = property_info_count[['land_tax']]
property_info_count.reset_index(inplace=True)
featureSpace = pd.merge(featureSpace, property_info_count, how='inner')


# Calculate vacant lots
property_info_count = property_info_ct.groupby('NAMELSAD10').sum()
property_info_count = property_info_count[['vacant']]
property_info_count.reset_index(inplace=True)
featureSpace = pd.merge(featureSpace, property_info_count, how='inner')
featureSpace['vacant'] = featureSpace['vacant']/featureSpace['Prop_Count']


# Calculate homeownership
property_info_count = property_info_ct.groupby('NAMELSAD10').sum()
property_info_count = property_info_count[['own_occup']]
property_info_count.reset_index(inplace=True)
featureSpace = pd.merge(featureSpace, property_info_count, how='inner')
featureSpace['own_occup'] = featureSpace['own_occup']/featureSpace['Prop_Count']


# Calculate Negative Actions
property_info_count = property_info_ct.groupby('NAMELSAD10').sum()
property_info_count = property_info_count[['NegAct_cou']]
property_info_count.reset_index(inplace=True)
featureSpace = pd.merge(featureSpace, property_info_count, how='inner')
featureSpace['NegAct_cou'] = featureSpace['NegAct_cou']/featureSpace['Prop_Count']


# Calculate Tree Scores
trees_ct = gpd.sjoin(census_tracts, trees, how='left', op='intersects')
trees_count = trees_ct.groupby('NAMELSAD10').mean()
trees_count = trees_count[['Tree_Score']]
trees_count.reset_index(inplace=True)
featureSpace = pd.merge(featureSpace, trees_count, how='inner')


# Calculate Building Permits
permits_ct = gpd.sjoin(census_tracts, permits, how='left', op='intersects')
permits_count = permits_ct.groupby('NAMELSAD10').sum()
permits_count = permits_count[['perm_num']]
permits_count.reset_index(inplace=True)
featureSpace = pd.merge(featureSpace, permits_count, how='inner')
featureSpace['perm_num'] = featureSpace['perm_num']/featureSpace['Prop_Count']


# Clean feature space and output file
featureSpace.rename(columns={'comp_count': 'Comp_Per', 'land_tax': 'Median_Val',
                             'vacant': 'Vacant_Per', 'PD_Count': 'PD_Per', 'own_occup': 'Own_Occup',
                             'NegAct_cou': 'Act_Count', 'perm_num': 'Perm_Count'}, inplace=True)
featureSpace.fillna(0, inplace=True)
featureSpace.to_file('../Data/processed/shapefiles/featureSpace_CT.shp')
