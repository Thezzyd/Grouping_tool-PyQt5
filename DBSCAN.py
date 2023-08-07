import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn import metrics
import matplotlib.pyplot as plt
import time

#dataset = pd.read_csv('./dane/serce.csv')
#features = dataset.iloc[:,[0,3]]   #Wiek i cisnienie krwi (tylko dwa atrybuty do grupowania) 
#eps = 3
#min_samples = 5
#metric = 'euclidean'

def dbscanGrupowanie(features, eps, min_samples, metric, features_column_names):
    startTime = time.time()
    db = DBSCAN(eps=eps, min_samples=min_samples, metric=metric)
    db.fit(features)
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)
    rows = features.shape[0]

    uniqueValuesFromLabels  = np.unique(labels)
    objectsInClustersDict ={}
    for i in range(0, len(uniqueValuesFromLabels)):
        objectsInClustersDict[str(uniqueValuesFromLabels[i])] = np.count_nonzero(labels == uniqueValuesFromLabels[i])


    #print(objectsInClustersDict)
    clusters = db.fit_predict(features)  
    endTime = time.time()
    processingTime = endTime - startTime

    return n_clusters_, n_noise_, objectsInClustersDict, clusters, processingTime, rows


def dbscanGraph2D(features, clusters, features_column_names, isIdOfObjects):
    x = np.ravel(features.iloc[:,[0]])
    y = np.ravel(features.iloc[:,[1]])
    n = range(1, len(clusters)+1)   

    plt.figure(figsize=(12, 8))
    ax = plt.axes()
    plt.title('Wynik grupowania metodą DBSCAN')
    scatter = ax.scatter (x, y, c = clusters, cmap='rainbow')
    ax.legend(*scatter.legend_elements(), loc="lower left", title="Clusters")
    ax.set_xlabel(features_column_names[0])
    ax.set_ylabel(features_column_names[1])
    if(isIdOfObjects):
        for i, txt in enumerate(n):
            ax.annotate(txt, (x[i], y[i]))

    plt.show()

def dbscanGraph3D(features, clusters, features_column_names, isIdOfObjects):
    x = np.ravel(features.iloc[:,[0]])
    y = np.ravel(features.iloc[:,[1]])
    z = np.ravel(features.iloc[:,[2]])
    n = range(len(clusters))

    plt.figure(figsize=(12, 8))
    ax = plt.axes(projection='3d')
    plt.title('Wynik grupowania metodą DBSCA')
    scatter = ax.scatter3D(x, y, z, c= clusters, cmap='rainbow')
    if(isIdOfObjects):
        for i in n:
             ax.text(x[i], y[i], z[i], '%s' % (str(i+1)), size=10, zorder=1, color='k') 

    ax.legend(*scatter.legend_elements(), loc="lower left", title="Clusters")
    ax.set_xlabel(features_column_names[0])
    ax.set_ylabel(features_column_names[1])
    ax.set_zlabel(features_column_names[2])
    plt.show()

#n_clusters_, n_noise_, objectsInClustersDict, clusters, processingTime = dbscanClusters(dataset, features, eps, min_samples, metric)
#print(processingTime)