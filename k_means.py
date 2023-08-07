import time
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def kmeansGrupowanie(features, clusters, n_init, max_iter, features_column_names):
    startTime = time.time()
    km = KMeans(n_clusters=clusters, n_init=n_init, max_iter = max_iter)
    km.fit(features)

    centroidsKMeans = km.cluster_centers_
   

    labels = km.labels_
    rows = features.shape[0]

    uniqueValuesFromLabels  = np.unique(labels)
    objectsInClustersDict ={}
    for i in range(0, len(uniqueValuesFromLabels)):
        objectsInClustersDict[str(uniqueValuesFromLabels[i])] = np.count_nonzero(labels == uniqueValuesFromLabels[i])

    clusters = km.fit_predict(features)  
    endTime = time.time()
    processingTime = endTime - startTime

    return len(uniqueValuesFromLabels), objectsInClustersDict, clusters, processingTime, rows, centroidsKMeans 


def kmeansGraph2D(features, clusters, features_column_names, centroids, isIdOfObjects):
    x = np.ravel(features.iloc[:,[0]])
    y = np.ravel(features.iloc[:,[1]])
    n = range(1, len(clusters) + 1)

    centroidsKMeansX = centroids[:,0]
    centroidsKMeansY = centroids[:,1]

    plt.figure(figsize=(12, 8))
    ax = plt.axes()
    plt.title('Wynik grupowania metodą KMeans')
    scatter1 = ax.scatter (x, y, c = clusters, cmap='rainbow')
    scatter2 = ax.scatter(centroidsKMeansX, centroidsKMeansY, s=50,  color="black")
    ax.legend(*scatter1.legend_elements(), loc="lower left", title="Clusters")
    ax.set_xlabel(features_column_names[0])
    ax.set_ylabel(features_column_names[1])
    if(isIdOfObjects):
        for i, txt in enumerate(n):
            ax.annotate(txt, (x[i], y[i]))

    plt.show()

def kmeansGraph3D(features, clusters, features_column_names, centroids, isIdOfObjects):
    x = np.ravel(features.iloc[:,[0]])
    y = np.ravel(features.iloc[:,[1]])
    z = np.ravel(features.iloc[:,[2]])
    n = range(len(clusters))

    centroidsKMeansX = centroids[:,0]
    centroidsKMeansY = centroids[:,1]
    centroidsKMeansZ = centroids[:,2]

    plt.figure(figsize=(12, 8))
    ax = plt.axes(projection='3d')
    plt.title('Wynik grupowania metodą KMeans')
    scatter1 = ax.scatter3D(x, y, z, c= clusters, cmap='rainbow')
    scatter2 = ax.scatter(centroidsKMeansX, centroidsKMeansY, centroidsKMeansZ, s=50,  color="blue", alpha=0.9)
    if(isIdOfObjects):
        for i in n:
             ax.text(x[i], y[i], z[i], '%s' % (str(i+1)), size=10, zorder=1, color='k') 

    ax.legend(*scatter1.legend_elements(), loc="lower left", title="Clusters")
    ax.set_xlabel(features_column_names[0])
    ax.set_ylabel(features_column_names[1])
    ax.set_zlabel(features_column_names[2])

    plt.show()
