
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from sklearn import preprocessing

trees = pd.read_excel('../Data/Raw/Treetracker Site Table.xlsx')
owners = gpd.read_file('../Data/Interim/Master_Building/CH_Only_Clip.shp')

trees = trees[['Address', 'Diameter', 'Condition Wood', 'Condition Leaves', 'X_Coord', 'Y_Coord']]
trees.dropna(inplace=True)

conditions = {'Dead': 0, 'Poor': 1, 'Fair': 2, 'Good': 3, 'Excellent': 4}
trees['Condition Wood'] = trees['Condition Wood'].map(conditions)
trees['Condition Leaves'] = trees['Condition Leaves'].map(conditions)
min_max_scaler = preprocessing.MinMaxScaler((0, 4))
trees['Diameter'] = min_max_scaler.fit_transform(np.array(trees['Diameter'].astype(float)).reshape(-1, 1))
trees['Tree_Score'] = 2*(trees['Diameter']) + trees['Condition Wood'] + trees['Condition Leaves']

tree_scores = trees[['Address', 'Tree_Score']].groupby('Address').mean()

tree_scores.to_csv('../Data/processed/tree_scores.csv')


def fix_address(row):
    num = row['Address'].split(' ')[2]
    st = row['Address'].split(' ')[0] + ' ' + row['Address'].split(' ')[1]
    add = num + ' ' + st
    return add

tree_scores.reset_index(inplace=True)
tree_scores['Address'] = tree_scores.apply(fix_address, axis=1)
tree_scores['Address'] = map(lambda x: x.upper(), tree_scores['Address'])

owners = owners[['parcel_add', 'geometry']]
owners.dropna(inplace=True)


def fix_owners_add(row):
    return row['parcel_add'].split(',')[0]

owners['parcel_add'] = owners.apply(fix_owners_add, axis=1)


tree_scores_shp = pd.merge(tree_scores, owners, how='inner', left_on='Address', right_on='parcel_add')
tree_scores_shp = gpd.GeoDataFrame(tree_scores_shp, crs={'init': 'epsg:4326'})

tree_scores_shp.to_file('../Data/processed/shapefiles/tree_scores.shp')
