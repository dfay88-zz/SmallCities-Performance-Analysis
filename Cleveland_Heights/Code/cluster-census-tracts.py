import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn import preprocessing

featureSpace = gpd.read_file('../Data/processed/shapefiles/featureSpace_CT.shp')

X = featureSpace[[u'FC_Per', u'Median_Val',  u'Own_Occup',
                  u'PD_Per', u'Perm_Count', u'Tree_Score', u'Vacant_Per']].as_matrix()

scaler = preprocessing.StandardScaler().fit(X)
X_scaled = scaler.transform(X)

n = 4
km = KMeans(random_state=123, n_clusters=n)
res = km.fit(X)

featureSpace['km_labels'] = res.labels_

clusters = featureSpace[[u'FC_Per', u'Median_Val',  u'Own_Occup',
                         u'PD_Per', u'Perm_Count', u'Tree_Score', u'Vacant_Per', 'km_labels']]

featureSpace.to_file('../Data/processed/shapefiles/featureSpace_CT.shp')
