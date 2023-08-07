import pandas as pd
import numpy as np
from sklearn import metrics
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as shc
from sklearn.preprocessing import StandardScaler
import time


def hierarchicznaGrupowanie(features, n_clusters, metric, linkage, treshold, features_column_names):
    startTime = time.time()
    ac = []
    print("klastry: "+n_clusters)
    print("treshold: "+treshold)
    if(n_clusters=="" and treshold ==""):
        ac = AgglomerativeClustering(affinity=metric, linkage=linkage, compute_distances=True)
    elif(n_clusters != ""):
        ac = AgglomerativeClustering(n_clusters=int(n_clusters), affinity=metric, linkage=linkage, compute_distances=True)
    else:
        ac = AgglomerativeClustering(n_clusters = None, affinity=metric, linkage=linkage, distance_threshold = float(treshold), compute_distances=True)
     

    ac.fit(features)
    clusters = ac.fit_predict(features)

    rows = features.shape[0]

    uniqueValuesFromLabels  = np.unique(clusters)
    objectsInClustersDict ={}
    for i in range(0, len(uniqueValuesFromLabels)):
        objectsInClustersDict[str(uniqueValuesFromLabels[i])] = np.count_nonzero(clusters == uniqueValuesFromLabels[i])

    endTime = time.time()
    processingTime = endTime - startTime

    return len(uniqueValuesFromLabels), objectsInClustersDict, clusters, processingTime, rows, ac


def hierarhicznaGraph2D(features, clusters, features_column_names, isIdOfObjects):
    x = np.ravel(features.iloc[:,[0]])
    y = np.ravel(features.iloc[:,[1]])
    n = range(1, len(clusters)+1)

    plt.figure(figsize=(12, 8))
    ax = plt.axes()
    plt.title('Wynik grupowania metodą hierarchiczną')
    scatter = ax.scatter (x, y, c = clusters, cmap='rainbow')
    ax.legend(*scatter.legend_elements(), loc="lower left", title="Clusters")
    ax.set_xlabel(features_column_names[0])
    ax.set_ylabel(features_column_names[1])
    if(isIdOfObjects):
        for i, txt in enumerate(n):
            ax.annotate(txt, (x[i], y[i]))

    plt.show()
    #hierarhicznaGraphDendrogram(features, 'complete')

def hierarhicznaGraph3D(features, clusters, features_column_names, isIdOfObjects):
    x = np.ravel(features.iloc[:,[0]])
    y = np.ravel(features.iloc[:,[1]])
    z = np.ravel(features.iloc[:,[2]])
    n = range(len(clusters))
    
    plt.figure(figsize=(12, 8))
    ax = plt.axes(projection='3d')
    plt.title('Wynik grupowania metodą hierarchiczną')
    scatter = ax.scatter3D(x, y, z, c= clusters, cmap='rainbow')
    if(isIdOfObjects):
        for i in n:
             ax.text(x[i], y[i], z[i], '%s' % (str(i+1)), size=10, zorder=1, color='k') 

    ax.legend(*scatter.legend_elements(), loc="lower left", title="Clusters")
    ax.set_xlabel(features_column_names[0])
    ax.set_ylabel(features_column_names[1])
    ax.set_zlabel(features_column_names[2])
    plt.show()



def hierarhicznaGraphDendrogram(model, treshold):
    plotDendrogram(model, truncate_mode="level", p=4)
    plt.title("Grupowanie hierarchiczne - dendrogram")
    plt.xlabel("Number of points in node (or index of point if no parenthesis).")
    if(treshold != ""):
        plt.axhline(y=float(treshold), color='r', linestyle='-')
    plt.show()



def plotDendrogram(model, **kwargs):
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    dendrogram(linkage_matrix, **kwargs)

#dataset = pd.read_csv('./dane/serce.csv')
#features = dataset.iloc[:,[0,3]]   #Wiek i cisnienie krwi (tylko dwa atrybuty do grupowania)          

#il_klastrow, objectsInClustersDict, clusters, processingTime, rows = dbscanClusters(dataset, features, 4, 'euclidean', ['tak', 'nie'])

#print(il_klastrow)

#print(str(objectsInClustersDict))

#print(clusters)

#print(processingTime)

#print(rows)
"""  plot_dendrogram(model, truncate_mode="level", p=3)
    f1 = plt.figure(figsize=(12, 8))
    ax2 = f1.add_subplot(111)

    clusters = shc.linkage(features, 
            method=method, 
            metric=metric)
    ax2 = shc.dendrogram(Z=clusters)
    
    plt.title("Dendrogram dla grupowanych danych")   
    plt.show()"""