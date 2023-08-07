import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors
from matplotlib.colors import ListedColormap
from matplotlib.widgets import CheckButtons
from PandasModel import PandasModel
from DBSCAN import dbscanGrupowanie
from Hierarchiczna import hierarchicznaGrupowanie
from k_means import kmeansGrupowanie
import k_means
import Hierarchiczna
import DBSCAN
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QMainWindow
from PyQt5.uic import loadUi
import json

class MainWindow(QMainWindow):

    pathToFile =""
    pathsToFiles_comparing = ""
    allFiles_json = []
    dataset = pd.DataFrame({})
    dbscan_run_with_no_params_tries, kmeans_run_with_no_params_tries, hierarchiczna_run_with_no_params_tries = 0, 0, 0
    dbscan_featuresString, hierarchiczna_featuresString, kmeans_featuresString = "", "", ""
    dbscan_epsString, kmeans_ninitString = "", ""
    dbscan_minSamplesString, hierarchiczna_clustersString, kmeans_maxiterString = "", "", ""
    dbscan_metricString, hierarchiczna_metricString = "", ""
    dbscan_ilosc_klastrow, kmeans_ilosc_klastrow, hierarchiczna_ilosc_klastrow = "", "", ""  
    dbscan_ilosc_szumu  = ""
    dbscan_objectsInClustersDict, hierarchiczna_objectsInClustersDict, kmeans_objectsInClustersDict = "", "", ""
    dbscan_klastry, hierarchiczna_klastry, kmeans_klastry = "", "", ""
    dbscan_processingTime, hierarchiczna_processingTime, kmeans_processingTime = "", "", ""
    dbscan_ilosc_wierszy, hierarchiczna_ilosc_wierszy, kmeans_ilosc_wierszy = "", "", ""
    hierarchiczna_linkageString = ""
    hierarchiczna_treshold = ""
    dbscan_arrayOfFeatures_names, hierarchiczna_arrayOfFeatures_names, kmeans_arrayOfFeatures_names = [], [], []
    dbscan_arrayOfFeatures, hierarchiczna_arrayOfFeatures, kmeans_arrayOfFeatures = [], [], []
    dbscan_features, hierarchiczna_features, kmeans_features = [],[],[]
    kmeansCentroids = []
    hierarchiczna_model, lastFeaturesInUse = [], []
    kmeansLabels, hierarchicznaLabels, dbscanLabels = [], [], []
    listOfCommonObjects = []
    listOfDiffrent_in_first, listOfDiffrent_in_second, listOfDiffrent_in_third = [], [], []
    #listOfComonObjectClusterNames = []
    CommonObjectsTemp, Diffrent_in_firstTemp, Diffrent_in_secondTemp, Diffrent_in_thirdTemp, CommolnClusterNamesTemp = [], [], [], [], []
    used_methods_in_comparing, used_methods_in_comparingTemp  = [], []
    UsedMethodsInComparing_StringListTemp, UsedMethodsInComparing_StringList, UsedClustersInComparing_StringListTemp, UsedClustersInComparing_StringList = [],[],[],[]
    checkbox = None
    choices = []
    scatters = []

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("./gui.ui", self)
        self.browse.clicked.connect(self.browseFiles)
        self.pushButton_MetodaGestosciowa.clicked.connect(self.grupowanie_MetodaGestosciowa)
        self.pushButton_MetodaHierarchiczna.clicked.connect(self.grupowanie_MetodaHierarchiczna)
        self.pushButton_MetodaKMeans.clicked.connect(self.grupowanie_MetodaKMeans)
        self.pushButton_MetodaGestosciowa_zapisz.clicked.connect(self.eksportDoPliku_MetodaGestosciowa)
        self.pushButton_MetodaHierarchiczna_zapisz.clicked.connect(self.eksportDoPliku_MetodaHierarchiczna)
        self.pushButton_MetodaKMeans_zapisz.clicked.connect(self.eksportDoPliku_MetodaKMeans)
        self.pushButton_showGraphKMeans.clicked.connect(self.showGraphKmenas)
        self.pushButton_showGraphHierarchiczna.clicked.connect(self.showGraphHierarchiczna)
        self.pushButton_showGraphDbscan.clicked.connect(self.showGraphDBSCAN)
        self.pushButton_showGraphHierarchiczna2.clicked.connect(self.showGraphHierarchicznaDendrogram)
        self.pushButton_Porownanie_zapisz.clicked.connect(self.eksportDoPliku_Wszystko)
        self.pushButton_Porownanie_zapisz.setEnabled(False)
        self.pushButton_MetodaGestosciowa_zapisz.setEnabled(False)
        self.pushButton_MetodaHierarchiczna_zapisz.setEnabled(False)
        self.pushButton_MetodaKMeans_zapisz.setEnabled(False)
        self.pushButton_showGraphKMeans.setEnabled(False)
        self.pushButton_showGraphHierarchiczna.setEnabled(False)
        self.pushButton_showGraphDbscan.setEnabled(False)
        self.pushButton_showGraphHierarchiczna2.setEnabled(False)
        self.tableWidget_wyniki.setEnabled(False)
        self.tableWidget_wyniki2.setEnabled(False)
        self.fillComboBox_MetodaGestosciowa()
        self.fillComboBox_MetodaHierarchiczna()
        self.setTableWidget_wyniki()

        self.checkBox_compare_kmeans.clicked.connect(self.checkIfComboAllowed)
        self.checkBox_compare_hierarchiczna.clicked.connect(self.checkIfComboAllowed)
        self.checkBox_compare_dbscan.clicked.connect(self.checkIfComboAllowed)
        self.checkBox_compare_kmeans.setEnabled(False)
        self.checkBox_compare_hierarchiczna.setEnabled(False)
        self.checkBox_compare_dbscan.setEnabled(False)
        self.comboBox_compare_kmeans.setEnabled(False)
        self.comboBox_compare_hierarchiczna.setEnabled(False)
        self.comboBox_compare_dbscan.setEnabled(False)
        self.pushButton_compare.setEnabled(False)
        self.pushButton_compare.clicked.connect(self.compareClusters)
        self.tableWidget_compare.setEnabled(False)
        self.pushButton_compare_save.setEnabled(False)
        self.pushButton_compare_save.clicked.connect(self.addCompareResultToSave)
        self.pushButton_compare_remove.setEnabled(False)
        self.pushButton_compare_remove.clicked.connect(self.removeSelectedRowFromCompareSaveTable)
        self.comboBox_MetodaHierarchiczna.currentTextChanged.connect(self.onHierarchicznaComboBoxChanged)
        self.clusters_MetodaHierarchiczna.editingFinished.connect(self.onHierarchicznaClustersChanged)
        self.pushButton_compare_graph.setEnabled(False)
        self.pushButton_compare_graph.clicked.connect(self.compareGraph)
        self.pushButton_wczytajPlikiPorownanie.clicked.connect(self.browseFiles_many)
        self.pushButton_wczytajPlikiPorownanie.setEnabled(True)
        self.pushButton_allFilesGenerateGraph1.setEnabled(False)
        self.pushButton_allFilesGenerateGraph1.clicked.connect(self.allFilesGeneratePerformanceGraph)


    def onHierarchicznaClustersChanged(self):
        if(self.clusters_MetodaHierarchiczna.text() == ""):
            self.treshold_MetodaHierarchiczna.setEnabled(True) 
        else:
            self.treshold_MetodaHierarchiczna.setText("")
            self.treshold_MetodaHierarchiczna.setEnabled(False)



    def checkIfComboAllowed(self):
        self.comboBox_compare_kmeans.clear()
        self.comboBox_compare_hierarchiczna.clear()
        self.comboBox_compare_dbscan.clear()
        wybraneKlastry = 0
        if(self.checkBox_compare_kmeans.isChecked()):
            self.comboBox_compare_kmeans.setEnabled(True)
            wybraneKlastry = wybraneKlastry + 1
            for i in range(self.kmeans_ilosc_klastrow):
                self.comboBox_compare_kmeans.addItem(str(i))
        else:
            self.comboBox_compare_kmeans.setEnabled(False)
        if(self.checkBox_compare_hierarchiczna.isChecked()):
            self.comboBox_compare_hierarchiczna.setEnabled(True)
            wybraneKlastry = wybraneKlastry + 1
            for i in range(self.hierarchiczna_ilosc_klastrow):
                self.comboBox_compare_hierarchiczna.addItem(str(i))
        else:
            self.comboBox_compare_hierarchiczna.setEnabled(False)
        if(self.checkBox_compare_dbscan.isChecked()):
            self.comboBox_compare_dbscan.setEnabled(True)
            wybraneKlastry = wybraneKlastry + 1
            for i in range(self.dbscan_ilosc_klastrow):
                self.comboBox_compare_dbscan.addItem(str(i))
        else:
            self.comboBox_compare_dbscan.setEnabled(False)

        if(wybraneKlastry >=2):
            self.pushButton_compare.setEnabled(True)
        else:
            self.pushButton_compare.setEnabled(False)


    def compareClusters(self):
        cluster_kmeans = []
        cluster_hierarchiczna = []
        cluster_dbscan = []
        commonObjects = []
        self.Diffrent_in_firstTemp, self.Diffrent_in_secondTemp, self.Diffrent_in_thirdTemp = [], [], [] 
        diffrent_in_first = []
        diffrent_in_second = []
        diffrent_in_third = []
        usedClusters = []
        usedMethods = []
        self.used_methods_in_comparingTemp = [self.checkBox_compare_kmeans.isChecked(), self.checkBox_compare_hierarchiczna.isChecked(), self.checkBox_compare_dbscan.isChecked()]
        #differentObjects = []
        if(self.checkBox_compare_kmeans.isChecked()):
            usedClusters.append(self.comboBox_compare_kmeans.currentText())
            usedMethods.append("KMeans")
            for i in range(len(self.kmeansLabels)):
                if(str(self.kmeansLabels[i]) == self.comboBox_compare_kmeans.currentText()):
                    cluster_kmeans.append(i+1)

        if(self.checkBox_compare_hierarchiczna.isChecked()):
            usedClusters.append(self.comboBox_compare_hierarchiczna.currentText())
            usedMethods.append("Hierarchiczna")
            for i in range(len(self.hierarchicznaLabels)):
                if(str(self.hierarchicznaLabels[i]) == self.comboBox_compare_hierarchiczna.currentText()):
                    cluster_hierarchiczna.append(i+1)

        if(self.checkBox_compare_dbscan.isChecked()):
            usedClusters.append(self.comboBox_compare_dbscan.currentText())
            usedMethods.append("DBSCAN")
            for i in range(len(self.dbscanLabels)):
                if(str(self.dbscanLabels[i]) == self.comboBox_compare_dbscan.currentText()):
                    cluster_dbscan.append(i+1)

        if(len(cluster_kmeans) > 0 and len(cluster_hierarchiczna) > 0 and len(cluster_dbscan) > 0):
            commonObjects = [i for i in cluster_kmeans if(i in cluster_hierarchiczna and i in cluster_dbscan)]
            diffrent_in_first = list(set(cluster_kmeans).difference(commonObjects))
            diffrent_in_second = list(set(cluster_hierarchiczna).difference(commonObjects))
            diffrent_in_third = list(set(cluster_dbscan).difference(commonObjects))

            #differentObjects = [i for i in cluster_kmeans if(i not in cluster_hierarchiczna and i not in cluster_dbscan)]
        else:
            if(len(cluster_kmeans) > 0 and len(cluster_hierarchiczna) > 0):
                commonObjects = [i for i in cluster_kmeans if i in cluster_hierarchiczna]
                diffrent_in_first = list(set(cluster_kmeans).difference(commonObjects))
                diffrent_in_second = list(set(cluster_hierarchiczna).difference(commonObjects))
            elif(len(cluster_kmeans) > 0 and len(cluster_dbscan) > 0):
                commonObjects = [i for i in cluster_kmeans if i in cluster_dbscan]
                diffrent_in_first = list(set(cluster_kmeans).difference(commonObjects))
                diffrent_in_third = list(set(cluster_dbscan).difference(commonObjects))
            elif(len(cluster_hierarchiczna) > 0 and len(cluster_dbscan) > 0):
                commonObjects = [i for i in cluster_hierarchiczna if i in cluster_dbscan]
                diffrent_in_second = list(set(cluster_hierarchiczna).difference(commonObjects))
                diffrent_in_third = list(set(cluster_dbscan).difference(commonObjects))

        self.textEdit_compare.setText("")
        self.textEdit_compare.append("Wspólne obiekty to ("+str(len(commonObjects))+") : "+str(commonObjects))
        if(self.checkBox_compare_kmeans.isChecked()):
            self.textEdit_compare.append("\nKMeans - różne obiekty to ("+str(len(diffrent_in_first))+") : "+str(diffrent_in_first))
        if(self.checkBox_compare_hierarchiczna.isChecked()):
            self.textEdit_compare.append("\nHierarchiczna - różne obiekty to ("+str(len(diffrent_in_second))+") : "+str(diffrent_in_second))
        if(self.checkBox_compare_dbscan.isChecked()):
            self.textEdit_compare.append("\nDbscan - różne obiekty to ("+str(len(diffrent_in_third))+") : "+str(diffrent_in_third))
        self.textEdit_compare.setEnabled(True)
        self.pushButton_compare_save.setEnabled(True)
        if(len(self.lastFeaturesInUse.columns) == 2 or len(self.lastFeaturesInUse.columns) == 3):
            self.pushButton_compare_graph.setEnabled(True)
        else:
            self.pushButton_compare_graph.setEnabled(False)
        self.CommonObjectsTemp = commonObjects
        # self.CommolnClusterNamesTemp = usedMethods usedClusters
        self.Diffrent_in_firstTemp = diffrent_in_first
        self.Diffrent_in_secondTemp = diffrent_in_second
        self.Diffrent_in_thirdTemp = diffrent_in_third
        self.UsedMethodsInComparing_StringListTemp = usedMethods
        self.UsedClustersInComparing_StringListTemp = usedClusters
        #self.listOfCommonObjects.append(commonObjects)
        #self.listOfComonObjectClusterNames.append(usedClusters)
        # CommonObjectsTemp, CommolnClusterNamesTemp = [], []
        #print(self.listOfCommonObjects)
        #print(str(differentObjects))
        #print(str(commonObjects))
        #return commonObjects
    
    def addCompareResultToSave(self):
        self.listOfCommonObjects.append(self.CommonObjectsTemp)
        self.listOfDiffrent_in_first.append(self.Diffrent_in_firstTemp)
        self.listOfDiffrent_in_second.append(self.Diffrent_in_secondTemp)
        self.listOfDiffrent_in_third.append(self.Diffrent_in_thirdTemp)
        #self.listOfComonObjectClusterNames.append(self.CommolnClusterNamesTemp)
        self.used_methods_in_comparing.append(self.used_methods_in_comparingTemp)
        #    UsedMethodsInComparing_StringListTemp, UsedMethodsInComparing_StringList, UsedClustersInComparing_StringListTemp, UsedClustersInComparing_StringList = [],[],[],[]
        self.UsedMethodsInComparing_StringList.append(self.UsedMethodsInComparing_StringListTemp)
        self.UsedClustersInComparing_StringList.append(self.UsedClustersInComparing_StringListTemp)

        self.tableWidget_compare.setEnabled(True)
        self.pushButton_compare_remove.setEnabled(True)
        self.tableWidget_compare.setRowCount(len(self.listOfCommonObjects))
        self.pushButton_compare_save.setEnabled(False)
        for i in range(len(self.listOfCommonObjects)):
            parsedClusterNames = ""
            for j in range(len(self.UsedMethodsInComparing_StringList[i])):
                parsedClusterNames = parsedClusterNames + self.UsedMethodsInComparing_StringList[i][j]+"_"+self.UsedClustersInComparing_StringList[i][j] + "\n"
            print("wartosc i: "+str(i))
            self.tableWidget_compare.setItem(i,0,QtWidgets.QTableWidgetItem(parsedClusterNames))
            self.tableWidget_compare.setItem(i,1,QtWidgets.QTableWidgetItem(str(len(self.listOfCommonObjects[i]))+" obiektów: "+str(self.listOfCommonObjects[i])) )
            if(self.used_methods_in_comparing[i][0]):
                self.tableWidget_compare.setItem(i,2,QtWidgets.QTableWidgetItem(str(len(self.listOfDiffrent_in_first[i]))+" obiektów: "+str(self.listOfDiffrent_in_first[i])) )
            if(self.used_methods_in_comparing[i][1]):
                self.tableWidget_compare.setItem(i,3,QtWidgets.QTableWidgetItem(str(len(self.listOfDiffrent_in_second[i]))+" obiektów: "+str(self.listOfDiffrent_in_second[i])) )
            if(self.used_methods_in_comparing[i][2]):
                self.tableWidget_compare.setItem(i,4,QtWidgets.QTableWidgetItem(str(len(self.listOfDiffrent_in_third[i]))+" obiektów: "+str(self.listOfDiffrent_in_third[i])) )

    def removeSelectedRowFromCompareSaveTable(self):
        if(self.tableWidget_compare.rowCount() > 0):
            currentRow = self.tableWidget_compare.currentRow()
            self.tableWidget_compare.removeRow(currentRow)
            self.listOfCommonObjects.pop(currentRow)
            #self.listOfComonObjectClusterNames.pop(currentRow)
            self.listOfDiffrent_in_first.pop(currentRow)
            self.listOfDiffrent_in_second.pop(currentRow)
            self.listOfDiffrent_in_third.pop(currentRow)
            self.used_methods_in_comparing.pop(currentRow)
            self.UsedMethodsInComparing_StringList.pop(currentRow)
            self.UsedClustersInComparing_StringList.pop(currentRow)

        if(self.tableWidget_compare.rowCount() == 0):
            self.pushButton_compare_remove.setEnabled(False)


    def allFilesGeneratePerformanceGraph(self):
        y_time_kmeans, y_time_hierarchiczna, y_time_dbscan = [],[],[]
        x_number_of_objects_kmeans, x_number_of_objects_hierarchiczna, x_number_of_objects_dbscan = [],[],[]

        for i in self.allFiles_json:
            y_time_dbscan.append(float(i["metoda_dbscan"]["Wynik_grupowania"]["czas_grupowania"]))
            x_number_of_objects_dbscan.append(int(i["metoda_dbscan"]["Wynik_grupowania"]["ilosc_obiektow"]))
            y_time_hierarchiczna.append(float(i["metoda_hierarchiczna"]["Wynik_grupowania"]["czas_grupowania"]))
            x_number_of_objects_hierarchiczna.append(int(i["metoda_hierarchiczna"]["Wynik_grupowania"]["ilosc_obiektow"]))
            y_time_kmeans.append(float(i["metoda_kmeans"]["Wynik_grupowania"]["czas_grupowania"]))
            x_number_of_objects_kmeans.append(int(i["metoda_kmeans"]["Wynik_grupowania"]["ilosc_obiektow"]))

        yMax = 10
        if(max(y_time_hierarchiczna) > 10):
            yMax = max(y_time_hierarchiczna)

        sns.regplot(x=x_number_of_objects_kmeans, y=y_time_kmeans, label="KMeans", order=2)
        sns.regplot(x=x_number_of_objects_hierarchiczna, y=y_time_hierarchiczna, label="Hierarchiczna", order=2)
        sns.regplot(x=x_number_of_objects_dbscan, y=y_time_dbscan, label="DBSCAN", order=2)
        plt.gca().axis([min(x_number_of_objects_kmeans), max(x_number_of_objects_kmeans), 0, yMax])
        plt.gca().set_xlabel('Ilość obiektów w zbiorze')
        plt.gca().set_ylabel('Czas grupowania (s)')
        plt.title('Czas grupowania metod dla zwiększającej się ilości obiektów')
        plt.legend()
        plt.show()
       

    def browseFiles_many(self):
        self.textEdit_wczytanePliki.setText("")
        self.allFiles_json = []
        fnames = QFileDialog.getOpenFileNames(self, 'Open file', "", 'JSON files (*.JSON)')
        for i in fnames[0]:
            self.textEdit_wczytanePliki.append(i)
            f = open(i)
            self.allFiles_json.append(json.load(f))

        self.pathsToFiles_comparing = fnames[0]
        self.pushButton_allFilesGenerateGraph1.setEnabled(True)


    def browseFiles(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', "", 'CSV files (*.csv)')
        self.filename.setText(fname[0])
        self.pathToFile = fname[0]
        #self.testFileName()
        if(self.pathToFile != ""):
            self.activateTabSection()
            self.fillPreviewTableTab()

    #def testFileName(self):
        #print(self.pathToFile)
    
    def activateTabSection(self):
        self.tabWidget.setEnabled(True)

    def fillPreviewTableTab(self):
        self.dataset = pd.read_csv(self.pathToFile)
        model = PandasModel(self.dataset)
        
        self.tableView.setModel(model)
       # self.tableView.setRowCount(len(self.dataset.shape[0]))
    
    def fillComboBox_MetodaGestosciowa(self):
        self.comboBox_MetodaGestosciowa.addItem('cityblock')
        self.comboBox_MetodaGestosciowa.addItem('euclidean')
        self.comboBox_MetodaGestosciowa.addItem('l1')
        self.comboBox_MetodaGestosciowa.addItem('l2')
        self.comboBox_MetodaGestosciowa.addItem('manhattan')
        self.comboBox_MetodaGestosciowa.setCurrentText('euclidean')
    
    def fillComboBox_MetodaHierarchiczna(self):
        self.comboBox_MetodaHierarchiczna.addItem('cityblock')
        self.comboBox_MetodaHierarchiczna.addItem('euclidean')
        self.comboBox_MetodaHierarchiczna.addItem('l1')
        self.comboBox_MetodaHierarchiczna.addItem('l2')
        self.comboBox_MetodaHierarchiczna.addItem('manhattan')
        self.comboBox_MetodaHierarchiczna.setCurrentText('euclidean')
        self.comboBox_MetodaHierarchiczna_linkage.addItem("ward")
        self.comboBox_MetodaHierarchiczna_linkage.addItem("complete")
        self.comboBox_MetodaHierarchiczna_linkage.addItem("average")
        self.comboBox_MetodaHierarchiczna_linkage.addItem("single")
        self.comboBox_MetodaHierarchiczna_linkage.setCurrentText("complete")

    def onHierarchicznaComboBoxChanged(self, value):
        if(not value == "euclidean"):
            self.comboBox_MetodaHierarchiczna_linkage.clear()
            self.comboBox_MetodaHierarchiczna_linkage.addItem("complete")
            self.comboBox_MetodaHierarchiczna_linkage.addItem("average")
            self.comboBox_MetodaHierarchiczna_linkage.addItem("single")
            self.comboBox_MetodaHierarchiczna_linkage.setCurrentText("complete")
        else:
            self.comboBox_MetodaHierarchiczna_linkage.clear()
            self.comboBox_MetodaHierarchiczna_linkage.addItem("ward")
            self.comboBox_MetodaHierarchiczna_linkage.addItem("complete")
            self.comboBox_MetodaHierarchiczna_linkage.addItem("average")
            self.comboBox_MetodaHierarchiczna_linkage.addItem("single")
            self.comboBox_MetodaHierarchiczna_linkage.setCurrentText("complete")


    def grupowanie_MetodaGestosciowa(self):

        if(self.features_MetodaGestosciowa.text() == ""):
            self.features_MetodaGestosciowa.setText("1,2")
        if(self.eps_MetodaGestosciowa.text() == ""):
            self.eps_MetodaGestosciowa.setText("3")
        if(self.minSamples_MetodaGestosciowa.text() == ""):
            self.minSamples_MetodaGestosciowa.setText("5")

        self.textEdit_MetodaGestosciowa.clear()
        self.dbscan_featuresString = self.features_MetodaGestosciowa.text()
        self.dbscan_epsString = self.eps_MetodaGestosciowa.text()
        self.dbscan_minSamplesString = self.minSamples_MetodaGestosciowa.text()
        self.dbscan_metricString = self.comboBox_MetodaGestosciowa.currentText()

        self.dbscan_arrayOfFeatures = self.dbscan_featuresString.split(",")
      

        #walidacja
        error = False
        if(len(self.dbscan_arrayOfFeatures) < 2):
                self.textEdit_MetodaGestosciowa.append('Błąd: Wprowadzone dane w PIERWSZYM polu są niepoprawne')
                error = True

        for i in self.dbscan_arrayOfFeatures:
            if(not i.isnumeric() or int(i) <= 0 or not float(i).is_integer()):
                if(not error):
                    self.textEdit_MetodaGestosciowa.append('Błąd: Wprowadzone dane w PIERWSZYM polu są niepoprawne')
                error = True
                break
        
        if(not self.dbscan_epsString.replace('.','',1).isdigit() or float(self.dbscan_epsString) <= 0):
             self.textEdit_MetodaGestosciowa.append('Błąd: Wprowadzone dane w DRUGIM polu są niepoprawne')
             error = True

        if(not self.dbscan_minSamplesString.isnumeric() or int(self.dbscan_minSamplesString) <= 0):
             self.textEdit_MetodaGestosciowa.append('Błąd: Wprowadzone dane w TRZECIM polu są niepoprawne')
             error = True

        if(error):
            return   


        arrayOfFeatures_int = [int(x)-1 for x in self.dbscan_arrayOfFeatures]
       
        if(max(arrayOfFeatures_int)+1 >= self.dataset.shape[1] and not error):
            self.textEdit_MetodaGestosciowa.append('Błąd: Wprowadzone dane w PIERWSZYM polu są niepoprawne, podana kolumna nie istnieje')
            error = True

        if(error):
            return   

        self.dbscan_arrayOfFeatures_names = [self.dataset.columns[x] for x in arrayOfFeatures_int]
        self.dbscan_features = self.dataset.iloc[:,arrayOfFeatures_int]
        self.lastFeaturesInUse = self.dbscan_features
        
        self.textEdit_MetodaGestosciowa.append('Wczytane parametry: ')
        self.textEdit_MetodaGestosciowa.append('Kolumny brane pod uwagę - indeksy: '+ str(self.dbscan_arrayOfFeatures))
        self.textEdit_MetodaGestosciowa.append('Kolumny brane pod uwagę - nazwy: '+ str(self.dbscan_arrayOfFeatures_names))
        self.textEdit_MetodaGestosciowa.append('Wartość parametru eps: '+ self.dbscan_epsString)
        self.textEdit_MetodaGestosciowa.append('Wartość parametru min-samples: '+ self.dbscan_minSamplesString)
        self.textEdit_MetodaGestosciowa.append('Wybrana metryka: '+ self.dbscan_metricString)
        self.textEdit_MetodaGestosciowa.append('...')

        self.dbscan_ilosc_klastrow, self.dbscan_ilosc_szumu, self.dbscan_objectsInClustersDict, self.dbscan_klastry, self.dbscan_processingTime, self.dbscan_ilosc_wierszy = dbscanGrupowanie(self.dbscan_features, float(self.dbscan_epsString), int(self.dbscan_minSamplesString), self.dbscan_metricString,  self.dbscan_arrayOfFeatures_names)

        self.textEdit_MetodaGestosciowa.append('Wyniki grupowania: ')
        self.textEdit_MetodaGestosciowa.append('Ilość klastrów: '+ str(self.dbscan_ilosc_klastrow))
        self.textEdit_MetodaGestosciowa.append('Ilość wszystkich obiektów: '+ str(self.dbscan_ilosc_wierszy))
        self.textEdit_MetodaGestosciowa.append('Ilość obiektów sklasyfikowanych jako szum: '+ str(self.dbscan_ilosc_szumu))
        self.textEdit_MetodaGestosciowa.append('Utworzone klastry: '+ str(self.dbscan_objectsInClustersDict))
        self.textEdit_MetodaGestosciowa.append('Czas grupowania: '+ str(self.dbscan_processingTime))
        
        self.dbscanLabels = self.dbscan_klastry
        self.fillTableWidget_wyniki()
        self.pushButton_MetodaGestosciowa_zapisz.setEnabled(True)
        self.tableWidget_wyniki.setEnabled(True)
        self.tableWidget_wyniki2.setEnabled(True)
        self.pushButton_Porownanie_zapisz.setEnabled(True)
        self.checkBox_compare_dbscan.setEnabled(True)
        if(len(self.dbscan_features.columns) == 2 or len(self.dbscan_features.columns) == 3):
            self.pushButton_showGraphDbscan.setEnabled(True)
        else:
            self.pushButton_showGraphDbscan.setEnabled(False)


    def grupowanie_MetodaHierarchiczna(self):

        if(self.features_MetodaHierarchiczna.text() == ""):
            self.features_MetodaHierarchiczna.setText("1,2")
        
        #if(self.clusters_MetodaHierarchiczna.text() == ""):
            #self.clusters_MetodaHierarchiczna.setText("4")

        self.textEdit_MetodaHierarchiczna.clear()
        self.hierarchiczna_featuresString = self.features_MetodaHierarchiczna.text()
        self.hierarchiczna_clustersString = self.clusters_MetodaHierarchiczna.text()
        self.hierarchiczna_metricString = self.comboBox_MetodaHierarchiczna.currentText()
        self.hierarchiczna_linkageString = self.comboBox_MetodaHierarchiczna_linkage.currentText()
        self.hierarchiczna_treshold = self.treshold_MetodaHierarchiczna.text()

        self.hierarchiczna_arrayOfFeatures = self.hierarchiczna_featuresString.split(",")
      
        #walidacja
        error = False
        if(len(self.hierarchiczna_arrayOfFeatures) < 2):
                self.textEdit_MetodaHierarchiczna.append('Błąd: Wprowadzone dane w PIERWSZYM polu są niepoprawne')
                error = True

        for i in self.hierarchiczna_arrayOfFeatures:
            if(not i.isnumeric() or int(i) <= 0 or not float(i).is_integer()):
                if(not error):
                    self.textEdit_MetodaHierarchiczna.append('Błąd: Wprowadzone dane w PIERWSZYM polu są niepoprawne')
                error = True
                break
        
        if(self.hierarchiczna_clustersString != ""):
            if(not self.hierarchiczna_clustersString.isnumeric() or int(self.hierarchiczna_clustersString) < 0):
                self.textEdit_MetodaHierarchiczna.append('Błąd: Wprowadzone dane w DRUGIM polu są niepoprawne')
                error = True

        if(self.hierarchiczna_treshold != ""):
            if(not self.hierarchiczna_treshold.replace('.','',1).isdigit() or float(self.hierarchiczna_treshold) <= 0):
                self.textEdit_MetodaHierarchiczna.append('Błąd: Wprowadzone dane w TRZECIM polu są niepoprawne')
                error = True

        if(error):
            return

        arrayOfFeatures_int = [int(x)-1 for x in self.hierarchiczna_arrayOfFeatures]
       

        if(max(arrayOfFeatures_int)+1 > self.dataset.shape[1] and not error):
            self.textEdit_MetodaHierarchiczna.append('Błąd: Wprowadzone dane w PIERWSZYM polu są niepoprawne, podana kolumna nie istnieje')
            error = True

        if(error):
            return   

        self.hierarchiczna_arrayOfFeatures_names = [self.dataset.columns[x] for x in arrayOfFeatures_int]
        self.hierarchiczna_features = self.dataset.iloc[:,arrayOfFeatures_int]
        self.lastFeaturesInUse = self.hierarchiczna_features

        self.textEdit_MetodaHierarchiczna.append('Wczytane parametry: ')
        self.textEdit_MetodaHierarchiczna.append('Kolumny brane pod uwagę - indeksy: '+ str(self.hierarchiczna_arrayOfFeatures))
        self.textEdit_MetodaHierarchiczna.append('Kolumny brane pod uwagę - nazwy: '+ str(self.hierarchiczna_arrayOfFeatures_names))
        if(self.hierarchiczna_clustersString == ""):
            self.textEdit_MetodaHierarchiczna.append('Ilość grup do wygenerowania: '+ "nie określono")
        else:
            self.textEdit_MetodaHierarchiczna.append('Ilość grup do wygenerowania: '+ self.hierarchiczna_clustersString)
        if(self.hierarchiczna_treshold == ""):   
            self.textEdit_MetodaHierarchiczna.append('Próg odległości powiązania: '+ "nie określono")
        else:
            self.textEdit_MetodaHierarchiczna.append('Próg odległości powiązania: '+ self.hierarchiczna_treshold)
        

        self.textEdit_MetodaHierarchiczna.append('Wybrana metryka: '+ self.hierarchiczna_metricString)
        self.textEdit_MetodaHierarchiczna.append('Wybrany rodzaj powiązania: '+ self.hierarchiczna_linkageString)
        self.textEdit_MetodaHierarchiczna.append('...')

        self.hierarchiczna_ilosc_klastrow, self.hierarchiczna_objectsInClustersDict, self.hierarchiczna_klastry, self.hierarchiczna_processingTime, self.hierarchiczna_ilosc_wierszy, self.hierarchiczna_model = hierarchicznaGrupowanie(self.hierarchiczna_features, self.hierarchiczna_clustersString, self.hierarchiczna_metricString, self.hierarchiczna_linkageString, self.hierarchiczna_treshold,  self.hierarchiczna_arrayOfFeatures_names)

        self.textEdit_MetodaHierarchiczna.append('Wyniki grupowania: ')
        self.textEdit_MetodaHierarchiczna.append('Ilość klastrów: '+ str(self.hierarchiczna_ilosc_klastrow))
        self.textEdit_MetodaHierarchiczna.append('Ilość wszystkich obiektów: '+ str(self.hierarchiczna_ilosc_wierszy))
        self.textEdit_MetodaHierarchiczna.append('Utworzone klastry: '+ str(self.hierarchiczna_objectsInClustersDict))
        self.textEdit_MetodaHierarchiczna.append('Czas grupowania: '+ str(self.hierarchiczna_processingTime))
        
        self.hierarchicznaLabels = self.hierarchiczna_klastry
        self.fillTableWidget_wyniki()
        self.pushButton_MetodaHierarchiczna_zapisz.setEnabled(True)
        self.pushButton_Porownanie_zapisz.setEnabled(True)
        self.tableWidget_wyniki.setEnabled(True)
        self.tableWidget_wyniki2.setEnabled(True)
        self.checkBox_compare_hierarchiczna.setEnabled(True)
        if(len(self.hierarchiczna_features.columns) == 2 or len(self.hierarchiczna_features.columns) == 3):
            self.pushButton_showGraphHierarchiczna.setEnabled(True)
        else:
            self.pushButton_showGraphHierarchiczna.setEnabled(False)
        if(len(self.hierarchiczna_features.columns) == 2):
            self.pushButton_showGraphHierarchiczna2.setEnabled(True)
        else:
            self.pushButton_showGraphHierarchiczna2.setEnabled(False)

    def grupowanie_MetodaKMeans(self):

        if(self.features_MetodaKMeans.text() == ""):
            self.features_MetodaKMeans.setText("1,2")
        if(self.clusters_MetodaKMeans.text() == ""):
            self.clusters_MetodaKMeans.setText("4")
        if(self.ninit_MetodaKMeans.text() == ""):
            self.ninit_MetodaKMeans.setText("10")
        if(self.maxiter_MetodaKMeans.text() == ""):
            self.maxiter_MetodaKMeans.setText("300")

        self.textEdit_MetodaKMeans.clear()
        self.kmeans_featuresString = self.features_MetodaKMeans.text()
        self.kmeans_ilosc_klastrow = self.clusters_MetodaKMeans.text()
        self.kmeans_ninitString = self.ninit_MetodaKMeans.text()
        self.kmeans_maxiterString = self.maxiter_MetodaKMeans.text()
        self.kmeans_arrayOfFeatures = self.kmeans_featuresString.split(",")
      

        #walidacja
        error = False
        if(len(self.kmeans_arrayOfFeatures) < 2):
                self.textEdit_MetodaKMeans.append('Błąd: Wprowadzone dane w PIERWSZYM polu są niepoprawne')
                error = True

        for i in self.kmeans_arrayOfFeatures:
            if(not i.isnumeric() or int(i) <= 0 or not float(i).is_integer()):
                if(not error):
                    self.textEdit_MetodaKMeans.append('Błąd: Wprowadzone dane w PIERWSZYM polu są niepoprawne')
                error = True
                break

        if(not self.kmeans_ninitString.isnumeric() or int(self.kmeans_ninitString) <= 0):
             self.textEdit_MetodaKMeans.append('Błąd: Wprowadzone dane w DRUGIM polu są niepoprawne')
             error = True

        if(not self.kmeans_maxiterString.isnumeric() or int(self.kmeans_maxiterString) <= 0):
             self.textEdit_MetodaKMeans.append('Błąd: Wprowadzone dane w TRZECIM polu są niepoprawne')
             error = True

        if(error):
            return

        arrayOfFeatures_int = [int(x)-1 for x in self.kmeans_arrayOfFeatures]
       
        if(max(arrayOfFeatures_int)+1 > self.dataset.shape[1] and not error):
            self.textEdit_MetodaKMeans.append('Błąd: Wprowadzone dane w PIERWSZYM polu są niepoprawne, podana kolumna nie istnieje')
            error = True

        if(error):
            return   

        self.kmeans_arrayOfFeatures_names = [self.dataset.columns[x] for x in arrayOfFeatures_int]

        self.kmeans_features = self.dataset.iloc[:,arrayOfFeatures_int]
        self.lastFeaturesInUse = self.kmeans_features

        self.textEdit_MetodaKMeans.append('Wczytane parametry: ')
        self.textEdit_MetodaKMeans.append('Kolumny brane pod uwagę - indeksy: '+ str(self.kmeans_arrayOfFeatures))
        self.textEdit_MetodaKMeans.append('Kolumny brane pod uwagę - nazwy: '+ str(self.kmeans_arrayOfFeatures_names))
        self.textEdit_MetodaKMeans.append('Ilość grup do wygenerowania: '+ self.kmeans_ilosc_klastrow)
        self.textEdit_MetodaKMeans.append('Wartość parametru n-init: '+ self.kmeans_ninitString)
        self.textEdit_MetodaKMeans.append('Wartość parametru max-iter: '+ self.kmeans_maxiterString)
        self.textEdit_MetodaKMeans.append('...')

        self.kmeans_ilosc_klastrow, self.kmeans_objectsInClustersDict, self.kmeans_klastry, self.kmeans_processingTime, self.kmeans_ilosc_wierszy, self.kmeansCentroids = kmeansGrupowanie(self.kmeans_features, int(self.kmeans_ilosc_klastrow), int(self.kmeans_ninitString), int(self.kmeans_maxiterString), self.kmeans_arrayOfFeatures_names)

        self.textEdit_MetodaKMeans.append('Wyniki grupowania: ')
        self.textEdit_MetodaKMeans.append('Ilość klastrów: '+ str(self.kmeans_ilosc_klastrow))
        self.textEdit_MetodaKMeans.append('Ilość wszystkich obiektów: '+ str(self.kmeans_ilosc_wierszy))
        self.textEdit_MetodaKMeans.append('Utworzone klastry: '+ str(self.kmeans_objectsInClustersDict))
        self.textEdit_MetodaKMeans.append('Czas grupowania: '+ str(self.kmeans_processingTime))
        
        self.kmeansLabels = self.kmeans_klastry
        self.fillTableWidget_wyniki()
        self.pushButton_MetodaKMeans_zapisz.setEnabled(True)
        self.pushButton_Porownanie_zapisz.setEnabled(True)
        self.tableWidget_wyniki.setEnabled(True)
        self.tableWidget_wyniki2.setEnabled(True)
        self.checkBox_compare_kmeans.setEnabled(True)
        if(len(self.kmeans_features.columns) == 2 or len(self.kmeans_features.columns) == 3):
            self.pushButton_showGraphKMeans.setEnabled(True)
        else:
            self.pushButton_showGraphKMeans.setEnabled(False)

    def eksportDoPliku_MetodaGestosciowa(self):
        jsonContent = {
            "Wczytane_parametry" : {
                "kolumny_indeksy" : str(self.dbscan_arrayOfFeatures),
                "kolumny_nazwy" : str(self.dbscan_arrayOfFeatures_names),
                "metryka" : self.dbscan_metricString,
                "eps" : self.dbscan_epsString,
                "min-samples" : self.dbscan_minSamplesString
            },
            "Wynik_grupowania" : {
                "ilosc_klastrow" : str(self.dbscan_ilosc_klastrow),
                "ilosc_obiektow" : str(self.dbscan_ilosc_wierszy),
                "szum" : str(self.dbscan_ilosc_szumu),
                "klastry" : self.dbscan_objectsInClustersDict,
                "czas_grupowania" : str(self.dbscan_processingTime),
                "obiekty_w_grupach" : dict(enumerate(map(str, self.dbscanLabels), start=1))
            }
        }

        jsonVar = json.dumps(jsonContent, indent=4, sort_keys=True)
        self.SaveFileToJson(jsonVar, 'Wynik_grupowania_metoda_dbscan')

    def eksportDoPliku_MetodaHierarchiczna(self):
        jsonContent = {
            "Wczytane_parametry" : {
                "kolumny_indeksy" : str(self.hierarchiczna_arrayOfFeatures),
                "kolumny_nazwy" : str(self.hierarchiczna_arrayOfFeatures_names),
                "ilosc_klastrow" : self.hierarchiczna_clustersString,
                "prog_odleglosci_powiazania" : self.hierarchiczna_treshold,
                "metryka" : self.hierarchiczna_metricString
            },
            "Wynik_grupowania" : {
                "ilosc_klastrow" : str(self.hierarchiczna_ilosc_klastrow),
                "ilosc_obiektow" : str(self.hierarchiczna_ilosc_wierszy),
                "klastry" : self.hierarchiczna_objectsInClustersDict,
                "czas_grupowania" : str(self.hierarchiczna_processingTime),
                "obiekty_w_grupach" : dict(enumerate(map(str, self.hierarchicznaLabels), start=1))
            }
        }

        jsonVar = json.dumps(jsonContent, indent=4, sort_keys=True)
        self.SaveFileToJson(jsonVar, 'Wynik_grupowania_metoda_hierarchiczna')


    def eksportDoPliku_MetodaKMeans(self):
        jsonContent = {
            "Wczytane_parametry" : {
                "kolumny_indeksy" : str(self.kmeans_arrayOfFeatures),
                "kolumny_nazwy" : str(self.kmeans_arrayOfFeatures_names),
                "ilosc_klastrow" : self.kmeans_ilosc_klastrow,
                "metryka" : "euclidean",
                "n-init" : self.kmeans_ninitString,
                "max-iter" : self.kmeans_maxiterString
               
            },
            "Wynik_grupowania" : {
                "ilosc_klastrow" : str(self.kmeans_ilosc_klastrow),
                "ilosc_obiektow" : str(self.kmeans_ilosc_wierszy),
                "klastry" : self.kmeans_objectsInClustersDict,
                "czas_grupowania" : str(self.kmeans_processingTime),
                "obiekty_w_grupach" : dict(enumerate(map(str, self.kmeansLabels), start=1))
            }
        }

        jsonVar = json.dumps(jsonContent, indent=4, sort_keys=True)
        self.SaveFileToJson(jsonVar, 'Wynik_grupowania_metoda_kmeans')

    def eksportDoPliku_Wszystko(self):
       
        #listOfCommonObjects = []
    #listOfComonObjectClusterNames = []
    #"nazwa_metoda":"zbiór"...
        #print(str(porownanieInDict))
        compare_FullDict = {}
        for i in range(len(self.listOfCommonObjects)):
            compare_FullDict[i+1] = {
                "metody": str(self.UsedMethodsInComparing_StringList[i]),
                "klastry": str(self.UsedClustersInComparing_StringList[i]),
                "obiekty_wspolne": str(self.listOfCommonObjects[i]),
                "obiekty_rozne_kmeans": str(self.listOfDiffrent_in_first[i]),
                "obiekty_rozne_hierarchiczna": str(self.listOfDiffrent_in_second[i]),
                "obiekty_rozne_dbscan": str(self.listOfDiffrent_in_third[i])
            }

        jsonContent = {
            "Porownania_klastrow": compare_FullDict,
            "metoda_kmeans" : {
                "Wczytane_parametry" : {
                    "kolumny_indeksy" : str(self.kmeans_arrayOfFeatures),
                    "kolumny_nazwy" : str(self.kmeans_arrayOfFeatures_names),
                    "ilosc_klastrow" : self.kmeans_ilosc_klastrow,
                    "metryka" : "euclidean",
                    "n-init" : self.kmeans_ninitString,
                    "max-iter" : self.kmeans_maxiterString
                
                },
                "Wynik_grupowania" : {
                    "ilosc_klastrow" : str(self.kmeans_ilosc_klastrow),
                    "ilosc_obiektow" : str(self.kmeans_ilosc_wierszy),
                    "klastry" : self.kmeans_objectsInClustersDict,
                    "czas_grupowania" : str(self.kmeans_processingTime),
                    "obiekty_w_grupach" : dict(enumerate(map(str, self.kmeansLabels), start=1))
                }
            },
            "metoda_hierarchiczna" : { 
                "Wczytane_parametry" : {
                    "kolumny_indeksy" : str(self.hierarchiczna_arrayOfFeatures),
                    "kolumny_nazwy" : str(self.hierarchiczna_arrayOfFeatures_names),
                    "ilosc_klastrow" : self.hierarchiczna_clustersString,
                    "prog_odleglosci_powiazania" : self.hierarchiczna_treshold,
                    "metryka" : self.hierarchiczna_metricString
                },
                "Wynik_grupowania" : {
                    "ilosc_klastrow" : str(self.hierarchiczna_ilosc_klastrow),
                    "ilosc_obiektow" : str(self.hierarchiczna_ilosc_wierszy),
                    "klastry" : self.hierarchiczna_objectsInClustersDict,
                    "czas_grupowania" : str(self.hierarchiczna_processingTime),
                    "obiekty_w_grupach" : dict(enumerate(map(str, self.hierarchicznaLabels), start=1))
                },
            },
            "metoda_dbscan" : {
                "Wczytane_parametry" : {
                    "kolumny_indeksy" : str(self.dbscan_arrayOfFeatures),
                    "kolumny_nazwy" : str(self.dbscan_arrayOfFeatures_names),
                    "metryka" : self.dbscan_metricString,
                    "eps" : self.dbscan_epsString,
                    "min-samples" : self.dbscan_minSamplesString
                    
                },
                "Wynik_grupowania" : {
                    "ilosc_klastrow" : str(self.dbscan_ilosc_klastrow),
                    "ilosc_obiektow" : str(self.dbscan_ilosc_wierszy),
                    "klastry" : self.dbscan_objectsInClustersDict,
                    "szum" : str(self.dbscan_ilosc_szumu),
                    "czas_grupowania" : str(self.dbscan_processingTime),
                    "obiekty_w_grupach" : dict(enumerate(map(str, self.dbscanLabels), start=1))
                }
            }
        }

        jsonVar = json.dumps(jsonContent, indent=4, sort_keys=True)
        self.SaveFileToJson(jsonVar, 'Wynik_grupowania_porownanie')

    def SaveFileToJson(self, jsonVar, domyslnaNazwaPliku):
        file_filter = "Data File (*.json)"
        response = QFileDialog.getSaveFileName(
            parent=self,
            caption = "Select a data file",
            directory = domyslnaNazwaPliku,
            filter = file_filter
        )
        if(response[0] != ""):
            jsonFile = open(response[0], "w")
            jsonFile.write(jsonVar)
            jsonFile.close()

    def setTableWidget_wyniki(self):
        self.tableWidget_wyniki.setColumnWidth(0,100)
        self.tableWidget_wyniki.setColumnWidth(1,100)
        self.tableWidget_wyniki.setColumnWidth(2,100)
        self.tableWidget_wyniki2.setColumnWidth(0,100)
        self.tableWidget_wyniki2.setColumnWidth(1,100)
        self.tableWidget_wyniki2.setColumnWidth(2,100)
        self.tableWidget_compare.setColumnWidth(0,80)
        self.tableWidget_compare.setColumnWidth(1,150)


    def fillTableWidget_wyniki(self):
        self.tableWidget_wyniki.setRowCount(0);
        self.tableWidget_wyniki.setRowCount(max(len(self.kmeansLabels), len(self.hierarchicznaLabels), len(self.dbscanLabels)))

        row = 0
        for object in self.kmeansLabels:
            self.tableWidget_wyniki.setItem(row, 0, QtWidgets.QTableWidgetItem(str(object)))
            row = row + 1
        
        row = 0
        for object in self.hierarchicznaLabels:
            self.tableWidget_wyniki.setItem(row, 1, QtWidgets.QTableWidgetItem(str(object)))
            row = row + 1
        
        row = 0
        for object in self.dbscanLabels:
            if(object == -1):
                object = "szum"
            self.tableWidget_wyniki.setItem(row, 2, QtWidgets.QTableWidgetItem(str(object)))
            row = row + 1
        #proessing time rounded
        kmeansPT = ""
        hierarchicznaPT = ""
        dbscanPT = ""
        if self.kmeans_processingTime != "":    
             kmeansPT = round(float(self.kmeans_processingTime), 5)
        if self.hierarchiczna_processingTime != "":    
             hierarchicznaPT = round(float(self.hierarchiczna_processingTime), 5)
        if self.dbscan_processingTime != "":    
             dbscanPT =round(float(self.dbscan_processingTime), 5)
       
        

        #kmeans parameters:
        self.tableWidget_wyniki2.setItem(0, 0, QtWidgets.QTableWidgetItem(str(kmeansPT)))
        self.tableWidget_wyniki2.setItem(1, 0, QtWidgets.QTableWidgetItem(str(self.kmeans_ilosc_klastrow)))
        if(self.kmeans_ilosc_klastrow == ""):
            self.tableWidget_wyniki2.setItem(2, 0, QtWidgets.QTableWidgetItem(""))
        else:
            self.tableWidget_wyniki2.setItem(2, 0, QtWidgets.QTableWidgetItem("euclidean"))
        self.tableWidget_wyniki2.setItem(3, 0, QtWidgets.QTableWidgetItem(str(self.kmeans_featuresString)))
        #hierarchiczna parameters:
        self.tableWidget_wyniki2.setItem(0, 1, QtWidgets.QTableWidgetItem(str(hierarchicznaPT)))
        self.tableWidget_wyniki2.setItem(1, 1, QtWidgets.QTableWidgetItem(str(self.hierarchiczna_ilosc_klastrow)))
        self.tableWidget_wyniki2.setItem(2, 1, QtWidgets.QTableWidgetItem(str(self.hierarchiczna_metricString)))
        self.tableWidget_wyniki2.setItem(3, 1, QtWidgets.QTableWidgetItem(str(self.hierarchiczna_featuresString)))
        #dbscan parameters:
        self.tableWidget_wyniki2.setItem(0, 2, QtWidgets.QTableWidgetItem(str(dbscanPT)))
        self.tableWidget_wyniki2.setItem(1, 2, QtWidgets.QTableWidgetItem(str(self.dbscan_ilosc_klastrow)))
        self.tableWidget_wyniki2.setItem(2, 2, QtWidgets.QTableWidgetItem(str(self.dbscan_metricString)))
        self.tableWidget_wyniki2.setItem(3, 2, QtWidgets.QTableWidgetItem(str(self.dbscan_featuresString)))

    def showGraphKmenas(self):
        if(len(self.kmeans_features.columns) == 3):
            k_means.kmeansGraph3D(self.kmeans_features, self.kmeans_klastry, self.kmeans_arrayOfFeatures_names, self.kmeansCentroids, self.checkBox_obiectIdOnChart_Kmeans.isChecked())
        elif(len(self.kmeans_features.columns) == 2):
            k_means.kmeansGraph2D(self.kmeans_features, self.kmeans_klastry, self.kmeans_arrayOfFeatures_names, self.kmeansCentroids, self.checkBox_obiectIdOnChart_Kmeans.isChecked())

    def showGraphHierarchiczna(self):
        if(len(self.hierarchiczna_features.columns) == 3):
            Hierarchiczna.hierarhicznaGraph3D(self.hierarchiczna_features, self.hierarchiczna_klastry, self.hierarchiczna_arrayOfFeatures_names, self.checkBox_obiectIdOnChart_Hierarchiczna.isChecked())
        elif(len(self.hierarchiczna_features.columns) == 2):
            Hierarchiczna.hierarhicznaGraph2D(self.hierarchiczna_features, self.hierarchiczna_klastry, self.hierarchiczna_arrayOfFeatures_names, self.checkBox_obiectIdOnChart_Hierarchiczna.isChecked())

    def showGraphDBSCAN(self):
        if(len(self.dbscan_features.columns) == 3):
            DBSCAN.dbscanGraph3D(self.dbscan_features, self.dbscan_klastry, self.dbscan_arrayOfFeatures_names, self.checkBox_obiectIdOnChart_Dbscan.isChecked())
        elif(len(self.dbscan_features.columns) == 2):
            DBSCAN.dbscanGraph2D(self.dbscan_features, self.dbscan_klastry, self.dbscan_arrayOfFeatures_names, self.checkBox_obiectIdOnChart_Dbscan.isChecked())

    def showGraphHierarchicznaDendrogram(self):
        if(len(self.hierarchiczna_features.columns) == 2):
            Hierarchiczna.hierarhicznaGraphDendrogram(self.hierarchiczna_model, self.hierarchiczna_treshold)
   
    """ listOfCommonObjects = []
    listOfDiffrent_in_first, listOfDiffrent_in_second, listOfDiffrent_in_third = [], [], []
    #listOfComonObjectClusterNames = []
    CommonObjectsTemp, Diffrent_in_firstTemp, Diffrent_in_secondTemp, Diffrent_in_thirdTemp, CommolnClusterNamesTemp = [], [], [], [], []
    used_methods_in_comparing, used_methods_in_comparingTemp  = [], []
    UsedMethodsInComparing_StringListTemp, UsedMethodsInComparing_StringList, UsedClustersInComparing_StringListTemp, UsedClustersInComparing_StringList = [],[],[],[]"""

    def compareGraph(self):
        if(self.used_methods_in_comparingTemp[0] and self.used_methods_in_comparingTemp[1] and self.used_methods_in_comparingTemp[2]):
            if(len(self.lastFeaturesInUse.columns) == 2):
                self.compareGraph2D_3methods()
            elif(len(self.lastFeaturesInUse.columns) == 3):
                self.compareGraph3D_3methods()
        else:
            if(len(self.lastFeaturesInUse.columns) == 2):
                self.compareGraph2D_2methods()
            elif(len(self.lastFeaturesInUse.columns) == 3):
                self.compareGraph3D_2methods()


    def compareGraph2D_2methods(self):
        x_caly_zbior, y_caly_zbior = self.lastFeaturesInUse.iloc[:,[0]], self.lastFeaturesInUse.iloc[:,[1]]
        x_cz_wspolna, y_cz_wspolna,featuresNames = [],[],[]
        x_cz_rozna_kmeans, y_cz_rozna_kmeans = [],[]
        x_cz_rozna_hierarchiczna, y_cz_rozna_hierarchiczna = [],[]
        x_cz_rozna_dbscan, y_cz_rozna_dbscan = [],[]

        for i in self.CommonObjectsTemp:
            x_cz_wspolna.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_wspolna.append(self.lastFeaturesInUse.iloc[[i-1],[1]])

        for i in self.Diffrent_in_firstTemp:
            x_cz_rozna_kmeans.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_rozna_kmeans.append(self.lastFeaturesInUse.iloc[[i-1],[1]])

        for i in self.Diffrent_in_secondTemp:
            x_cz_rozna_hierarchiczna.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_rozna_hierarchiczna.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
        
        for i in self.Diffrent_in_thirdTemp:
            x_cz_rozna_dbscan.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_rozna_dbscan.append(self.lastFeaturesInUse.iloc[[i-1],[1]])

        wszystko_w_klastrach = set(self.Diffrent_in_firstTemp + self.Diffrent_in_secondTemp + self.Diffrent_in_thirdTemp + self.CommonObjectsTemp)

        wszystko = list(range(1,len(x_caly_zbior),1))
        x_poza_klastrami, y_poza_klastrami = [], []
        wszystko_poza_klastrami = set(wszystko).difference(wszystko_w_klastrach)
        for i in wszystko_poza_klastrami:
            x_poza_klastrami.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_poza_klastrami.append(self.lastFeaturesInUse.iloc[[i-1],[1]])

        #plt.figure(figsize=(12, 8))
        fig, ax = plt.subplots(figsize=(9,6)) #plt.axes()
        plt.title('Porownanie klastrów (dwie metody)')
        self.scatters = []
        self.choices = []
        check_state = []
        if(len(x_poza_klastrami) > 0):
            scatter_caly_zbior = ax.scatter(x_poza_klastrami, y_poza_klastrami, color='black', label="obiekty_poza_klastrami")
            self.scatters.append(scatter_caly_zbior)
            self.choices.append("obiekty_poza_klastrami")
            check_state.append(True)
        if(len(x_cz_wspolna) > 0):
            scatter_cz_wspolna = ax.scatter(x_cz_wspolna, y_cz_wspolna, color='green', label="cz_wspolna")
            self.scatters.append(scatter_cz_wspolna)
            self.choices.append("cz_wspolna")
            check_state.append(True)
        if(len(x_cz_rozna_kmeans) > 0):
            scatter_cz_rozna_kmeans = ax.scatter(x_cz_rozna_kmeans, y_cz_rozna_kmeans, color='blue', label="cz_rozna_kmeans")
            self.scatters.append(scatter_cz_rozna_kmeans)
            self.choices.append("cz_rozna_kmeans")
            check_state.append(True)
        if(len(x_cz_rozna_hierarchiczna) > 0):
            scatter_cz_rozna_hierarchiczna = ax.scatter(x_cz_rozna_hierarchiczna, y_cz_rozna_hierarchiczna, color='cyan', label="cz_rozna_hierarchiczna")
            self.scatters.append(scatter_cz_rozna_hierarchiczna)
            self.choices.append("cz_rozna_hierarchiczna")
            check_state.append(True)
        if(len(x_cz_rozna_dbscan) > 0):
            scatter_cz_rozna_dbscan = ax.scatter(x_cz_rozna_dbscan, y_cz_rozna_dbscan, color='red', label="cz_rozna_dbscan")
            self.scatters.append(scatter_cz_rozna_dbscan)
            self.choices.append("cz_rozna_dbscan")
            check_state.append(True)

        ax.legend()
        plt.subplots_adjust(left=0.35)
        ax_checkbox = plt.axes([0.02, 0.73, 0.25, 0.15])
        #check_state = (True, True, True, True, True)

        for i, scatter in enumerate(self.scatters):
            scatter.set_visible(check_state[i])

        self.checkbox = CheckButtons(ax_checkbox, self.choices, check_state)
        self.checkbox.on_clicked(self.SetScatterVisable)
        
        plt.show()

    def SetScatterVisable(self, label_name):
        #print(label_name)
        option_index = self.choices.index(label_name)
        scatter = self.scatters[option_index]
        scatter.set_visible(not scatter.get_visible())
        plt.draw()

    def compareGraph2D_3methods(self):
        x_caly_zbior, y_caly_zbior = self.lastFeaturesInUse.iloc[:,[0]], self.lastFeaturesInUse.iloc[:,[1]]
        x_cz_wspolna, y_cz_wspolna,featuresNames = [],[],[]
        x_cz_rozna_kmeans, y_cz_rozna_kmeans = [],[]
        x_cz_rozna_hierarchiczna, y_cz_rozna_hierarchiczna = [],[]
        x_cz_rozna_dbscan, y_cz_rozna_dbscan = [],[]
        
        rozne_kmeans_not_in_hierarchiczna_and_dbscan = set(set(self.Diffrent_in_firstTemp).difference(set(self.Diffrent_in_secondTemp))).difference(set(self.Diffrent_in_thirdTemp))
        rozne_hierarchiczna_not_in_kmeans_and_dbscan = set(set(self.Diffrent_in_secondTemp).difference(set(self.Diffrent_in_firstTemp))).difference(set(self.Diffrent_in_thirdTemp))
        rozne_dbscan_not_in_hierarchiczna_and_kmeans = set(set(self.Diffrent_in_thirdTemp).difference(set(self.Diffrent_in_secondTemp))).difference(set(self.Diffrent_in_firstTemp))


        for i in self.CommonObjectsTemp:
            x_cz_wspolna.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_wspolna.append(self.lastFeaturesInUse.iloc[[i-1],[1]])

        for i in rozne_kmeans_not_in_hierarchiczna_and_dbscan:
            x_cz_rozna_kmeans.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_rozna_kmeans.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
        
        for i in rozne_hierarchiczna_not_in_kmeans_and_dbscan:
            x_cz_rozna_hierarchiczna.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_rozna_hierarchiczna.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
        
        for i in rozne_dbscan_not_in_hierarchiczna_and_kmeans:
            x_cz_rozna_dbscan.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_rozna_dbscan.append(self.lastFeaturesInUse.iloc[[i-1],[1]])

        rozne_cz_wspolna_kmeans_hierarchiczna,  rozne_cz_wspolna_kmeans_dbscan,  rozne_cz_wspolna_dbscan_hierarchiczna = [],[],[]
        x_1_2, x_1_3, x_2_3, y_1_2, y_1_3, y_2_3=[],[],[],[],[],[] 
        rozne_cz_wspolna_kmeans_hierarchiczna = set(self.Diffrent_in_firstTemp).intersection(self.Diffrent_in_secondTemp)
        rozne_cz_wspolna_kmeans_dbscan = set(self.Diffrent_in_firstTemp).intersection(self.Diffrent_in_thirdTemp)
        rozne_cz_wspolna_dbscan_hierarchiczna = set(self.Diffrent_in_thirdTemp).intersection(self.Diffrent_in_secondTemp)
        for i in rozne_cz_wspolna_kmeans_hierarchiczna:
            x_1_2.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_1_2.append(self.lastFeaturesInUse.iloc[[i-1],[1]])

        for i in rozne_cz_wspolna_kmeans_dbscan:
            x_1_3.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_1_3.append(self.lastFeaturesInUse.iloc[[i-1],[1]])

        for i in rozne_cz_wspolna_dbscan_hierarchiczna:
            x_2_3.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_2_3.append(self.lastFeaturesInUse.iloc[[i-1],[1]])

        wszystko_w_klastrach = set(list(rozne_kmeans_not_in_hierarchiczna_and_dbscan) + list(rozne_hierarchiczna_not_in_kmeans_and_dbscan) + list(rozne_dbscan_not_in_hierarchiczna_and_kmeans) + list(rozne_cz_wspolna_kmeans_hierarchiczna) + list(rozne_cz_wspolna_kmeans_dbscan) + list(rozne_cz_wspolna_dbscan_hierarchiczna) + self.CommonObjectsTemp)

        wszystko = list(range(1,len(x_caly_zbior),1))
        x_poza_klastrami, y_poza_klastrami = [], []
        wszystko_poza_klastrami = set(wszystko).difference(wszystko_w_klastrach)
        for i in wszystko_poza_klastrami:
            x_poza_klastrami.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_poza_klastrami.append(self.lastFeaturesInUse.iloc[[i-1],[1]])

        #plt.figure(figsize=(12, 8))
        fig, ax = plt.subplots(figsize=(9,6)) #plt.axes()
        plt.title('Porownanie klastrów (trzy metody)')
        self.scatters = []
        self.choices = []
        check_state = []
        if(len(x_poza_klastrami) > 0):
            scatter_caly_zbior = ax.scatter(x_poza_klastrami, y_poza_klastrami, color='black', label="obiekty_poza_klastrami")
            self.scatters.append(scatter_caly_zbior)
            self.choices.append("obiekty_poza_klastrami")
            check_state.append(True)
        if(len(x_cz_wspolna) > 0):
            scatter_cz_wspolna = ax.scatter(x_cz_wspolna, y_cz_wspolna, color='green', label="cz_wspolna")
            self.scatters.append(scatter_cz_wspolna)
            self.choices.append("cz_wspolna")
            check_state.append(True)
        if(len(x_cz_rozna_kmeans) > 0):
            scatter_cz_rozna_kmeans = ax.scatter(x_cz_rozna_kmeans, y_cz_rozna_kmeans, color='blue', label="ob_rozne_tylko_kmeans")
            self.scatters.append(scatter_cz_rozna_kmeans)
            self.choices.append("ob_rozne_tylko_kmeans")
            check_state.append(True)
        if(len(x_cz_rozna_hierarchiczna) > 0):
            scatter_cz_rozna_hierarchiczna = ax.scatter(x_cz_rozna_hierarchiczna, y_cz_rozna_hierarchiczna, color='cyan', label="ob_rozne_tylko_hierarchiczna")
            self.scatters.append(scatter_cz_rozna_hierarchiczna)
            self.choices.append("ob_rozne_tylko_hierarchiczna")
            check_state.append(True)
        if(len(x_cz_rozna_dbscan) > 0):
            scatter_cz_rozna_dbscan = ax.scatter(x_cz_rozna_dbscan, y_cz_rozna_dbscan, color='red', label="ob_rozne_tylko_dbscan")
            self.scatters.append(scatter_cz_rozna_dbscan)
            self.choices.append("ob_rozne_tylko_dbscan")
            check_state.append(True)
        if(len(x_1_2) > 0):
            scatter_cz_rozna_wspolna_1_2 = ax.scatter (x_1_2, y_1_2, color='blue',  linewidths=2, edgecolors='cyan', label="ob_rozne_kmeans_i_hierarchiczna")
            self.scatters.append(scatter_cz_rozna_wspolna_1_2)
            self.choices.append("ob_rozne_kmeans_i_hierarchiczna")
            check_state.append(True)
        if(len(x_1_3) > 0):
            scatter_cz_rozna_wspolna_1_3 = ax.scatter (x_1_3, y_1_3, color='blue',  linewidths=2, edgecolors='red', label="ob_rozne_kmeans_i_dbscan")
            self.scatters.append(scatter_cz_rozna_wspolna_1_3)
            self.choices.append("ob_rozne_kmeans_i_dbscan")
            check_state.append(True)
        if(len(x_2_3) > 0):
            scatter_cz_rozna_wspolna_2_3 = ax.scatter (x_2_3, y_2_3, color='red',  linewidths=2, edgecolors='cyan', label="ob_rozne_dbscan_i_hierarchiczna")
            self.scatters.append(scatter_cz_rozna_wspolna_2_3)
            self.choices.append("ob_rozne_dbscan_i_hierarchiczna")
            check_state.append(True)

        ax.legend()
        plt.subplots_adjust(left=0.35)
        ax_checkbox = plt.axes([0.02, 0.73, 0.25, 0.15])
        #check_state = (True, True, True, True, True)

        for i, scatter in enumerate(self.scatters):
            scatter.set_visible(check_state[i])

        self.checkbox = CheckButtons(ax_checkbox, self.choices, check_state)
        self.checkbox.on_clicked(self.SetScatterVisable)
        
        plt.show()

    def compareGraph3D_2methods(self):
        x_caly_zbior, y_caly_zbior, z_caly_zbior = self.lastFeaturesInUse.iloc[:,[0]], self.lastFeaturesInUse.iloc[:,[1]], self.lastFeaturesInUse.iloc[:,[2]]
        x_cz_wspolna, y_cz_wspolna, z_cz_wspolna, featuresNames = [],[],[],[]
        x_cz_rozna_kmeans, y_cz_rozna_kmeans, z_cz_rozna_kmeans = [],[],[]
        x_cz_rozna_hierarchiczna, y_cz_rozna_hierarchiczna, z_cz_rozna_hierarchiczna = [],[],[]
        x_cz_rozna_dbscan, y_cz_rozna_dbscan, z_cz_rozna_dbscan = [],[],[]

        for i in self.CommonObjectsTemp:
            x_cz_wspolna.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_wspolna.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
            z_cz_wspolna.append(self.lastFeaturesInUse.iloc[[i-1],[2]])

        for i in self.Diffrent_in_firstTemp:
            x_cz_rozna_kmeans.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_rozna_kmeans.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
            z_cz_rozna_kmeans.append(self.lastFeaturesInUse.iloc[[i-1],[2]])

        for i in self.Diffrent_in_secondTemp:
            x_cz_rozna_hierarchiczna.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_rozna_hierarchiczna.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
            z_cz_rozna_hierarchiczna.append(self.lastFeaturesInUse.iloc[[i-1],[2]])

        for i in self.Diffrent_in_thirdTemp:
            x_cz_rozna_dbscan.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_rozna_dbscan.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
            z_cz_rozna_dbscan.append(self.lastFeaturesInUse.iloc[[i-1],[2]])

        wszystko_w_klastrach = set(self.Diffrent_in_firstTemp + self.Diffrent_in_secondTemp + self.Diffrent_in_thirdTemp + self.CommonObjectsTemp)

        wszystko = list(range(1,len(x_caly_zbior),1))
        x_poza_klastrami, y_poza_klastrami, z_poza_klastrami = [], [], []
        wszystko_poza_klastrami = set(wszystko).difference(wszystko_w_klastrach)
        for i in wszystko_poza_klastrami:
            x_poza_klastrami.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_poza_klastrami.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
            z_poza_klastrami.append(self.lastFeaturesInUse.iloc[[i-1],[2]])

         #plt.figure(figsize=(12, 8))
        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection='3d')

        #fig, ax = plt.subplots(figsize=(9,6)) #plt.axes()
        self.scatters = []
        self.choices = []
        check_state = []
        plt.title('Porownanie klastrów (dwie metody)')
        if(len(x_poza_klastrami) > 0):
            scatter_caly_zbior = ax.scatter3D(x_poza_klastrami, y_poza_klastrami, z_poza_klastrami, color='black', label="obiekty_poza_klastrami")
            self.scatters.append(scatter_caly_zbior)
            self.choices.append("obiekty_poza_klastrami")
            check_state.append(True)
        if(len(x_cz_wspolna) > 0):
            scatter_cz_wspolna = ax.scatter3D(x_cz_wspolna, y_cz_wspolna, z_cz_wspolna, color='green', label="cz_wspolna")
            self.scatters.append(scatter_cz_wspolna)
            self.choices.append("cz_wspolna")
            check_state.append(True)
        if(len(x_cz_rozna_kmeans) > 0):
            scatter_cz_rozna_kmeans = ax.scatter3D(x_cz_rozna_kmeans, y_cz_rozna_kmeans, z_cz_rozna_kmeans, color='blue', label="ob_rozne_kmeans")
            self.scatters.append(scatter_cz_rozna_kmeans)
            self.choices.append("ob_rozne_kmeans")
            check_state.append(True)
        if(len(x_cz_rozna_hierarchiczna) > 0):
            scatter_cz_rozna_hierarchiczna = ax.scatter3D(x_cz_rozna_hierarchiczna, y_cz_rozna_hierarchiczna, z_cz_rozna_hierarchiczna, color='cyan', label="ob_rozne_hierarchiczna")
            self.scatters.append(scatter_cz_rozna_hierarchiczna)
            self.choices.append("ob_rozne_hierarchiczna")
            check_state.append(True)
        if(len(x_cz_rozna_dbscan) > 0):
            scatter_cz_rozna_dbscan = ax.scatter3D(x_cz_rozna_dbscan, y_cz_rozna_dbscan, z_cz_rozna_dbscan, color='red', label="ob_rozne_dbscan")
            self.scatters.append(scatter_cz_rozna_dbscan)
            self.choices.append("ob_rozne_dbscan")
            check_state.append(True)

        ax.legend()
        plt.subplots_adjust(left=0.35)
        ax_checkbox = plt.axes([0.02, 0.73, 0.25, 0.15])
        #check_state = (True, True, True, True, True)

        for i, scatter in enumerate(self.scatters):
            scatter.set_visible(check_state[i])

        self.checkbox = CheckButtons(ax_checkbox, self.choices, check_state)
        self.checkbox.on_clicked(self.SetScatterVisable)
        
        plt.show()


    def compareGraph3D_3methods(self):
        x_caly_zbior, y_caly_zbior, z_caly_zbior = self.lastFeaturesInUse.iloc[:,[0]], self.lastFeaturesInUse.iloc[:,[1]], self.lastFeaturesInUse.iloc[:,[2]]
        x_cz_wspolna, y_cz_wspolna, z_cz_wspolna, featuresNames = [],[],[],[]
        x_cz_rozna_kmeans, y_cz_rozna_kmeans, z_cz_rozna_kmeans = [],[],[]
        x_cz_rozna_hierarchiczna, y_cz_rozna_hierarchiczna, z_cz_rozna_hierarchiczna = [],[],[]
        x_cz_rozna_dbscan, y_cz_rozna_dbscan, z_cz_rozna_dbscan = [],[],[]
        
        rozne_kmeans_not_in_hierarchiczna_and_dbscan = set(set(self.Diffrent_in_firstTemp).difference(set(self.Diffrent_in_secondTemp))).difference(set(self.Diffrent_in_thirdTemp))
        rozne_hierarchiczna_not_in_kmeans_and_dbscan = set(set(self.Diffrent_in_secondTemp).difference(set(self.Diffrent_in_firstTemp))).difference(set(self.Diffrent_in_thirdTemp))
        rozne_dbscan_not_in_hierarchiczna_and_kmeans = set(set(self.Diffrent_in_thirdTemp).difference(set(self.Diffrent_in_secondTemp))).difference(set(self.Diffrent_in_firstTemp))

        for i in self.CommonObjectsTemp:
            x_cz_wspolna.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_wspolna.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
            z_cz_wspolna.append(self.lastFeaturesInUse.iloc[[i-1],[2]])

        for i in rozne_kmeans_not_in_hierarchiczna_and_dbscan:
            x_cz_rozna_kmeans.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_rozna_kmeans.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
            z_cz_rozna_kmeans.append(self.lastFeaturesInUse.iloc[[i-1],[2]])

        for i in rozne_hierarchiczna_not_in_kmeans_and_dbscan:
            x_cz_rozna_hierarchiczna.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_rozna_hierarchiczna.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
            z_cz_rozna_hierarchiczna.append(self.lastFeaturesInUse.iloc[[i-1],[2]])

        for i in rozne_dbscan_not_in_hierarchiczna_and_kmeans:
            x_cz_rozna_dbscan.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_cz_rozna_dbscan.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
            z_cz_rozna_dbscan.append(self.lastFeaturesInUse.iloc[[i-1],[2]])

        rozne_cz_wspolna_kmeans_hierarchiczna,  rozne_cz_wspolna_kmeans_dbscan,  rozne_cz_wspolna_dbscan_hierarchiczna = [],[],[]
        x_1_2, x_1_3, x_2_3, y_1_2, y_1_3, y_2_3, z_1_2, z_1_3, z_2_3=[],[],[],[],[],[],[],[],[] 
        rozne_cz_wspolna_kmeans_hierarchiczna = set(self.Diffrent_in_firstTemp).intersection(self.Diffrent_in_secondTemp)
        rozne_cz_wspolna_kmeans_dbscan = set(self.Diffrent_in_firstTemp).intersection(self.Diffrent_in_thirdTemp)
        rozne_cz_wspolna_dbscan_hierarchiczna = set(self.Diffrent_in_thirdTemp).intersection(self.Diffrent_in_secondTemp)
        for i in rozne_cz_wspolna_kmeans_hierarchiczna:
            x_1_2.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_1_2.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
            z_1_2.append(self.lastFeaturesInUse.iloc[[i-1],[2]])

        for i in rozne_cz_wspolna_kmeans_dbscan:
            x_1_3.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_1_3.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
            z_1_3.append(self.lastFeaturesInUse.iloc[[i-1],[2]])
        
        for i in rozne_cz_wspolna_dbscan_hierarchiczna:
            x_2_3.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_2_3.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
            z_2_3.append(self.lastFeaturesInUse.iloc[[i-1],[2]])
       
        wszystko_w_klastrach = set(list(rozne_kmeans_not_in_hierarchiczna_and_dbscan) + list(rozne_hierarchiczna_not_in_kmeans_and_dbscan) + list(rozne_dbscan_not_in_hierarchiczna_and_kmeans) + list(rozne_cz_wspolna_kmeans_hierarchiczna) + list(rozne_cz_wspolna_kmeans_dbscan) + list(rozne_cz_wspolna_dbscan_hierarchiczna) + self.CommonObjectsTemp)

        wszystko = list(range(1,len(x_caly_zbior),1))
        x_poza_klastrami, y_poza_klastrami, z_poza_klastrami = [], [], []
        wszystko_poza_klastrami = set(wszystko).difference(wszystko_w_klastrach)
        for i in wszystko_poza_klastrami:
            x_poza_klastrami.append(self.lastFeaturesInUse.iloc[[i-1],[0]])
            y_poza_klastrami.append(self.lastFeaturesInUse.iloc[[i-1],[1]])
            z_poza_klastrami.append(self.lastFeaturesInUse.iloc[[i-1],[2]])

        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection='3d')
        plt.title('Porownanie klastrów (trzy metody)')
        self.scatters = []
        self.choices = []
        check_state = []
        if(len(x_poza_klastrami) > 0):
            scatter_caly_zbior = ax.scatter3D(x_poza_klastrami, y_poza_klastrami, z_poza_klastrami, color='black', label="obiekty_poza_klastrami")
            self.scatters.append(scatter_caly_zbior)
            self.choices.append("obiekty_poza_klastrami")
            check_state.append(True)
        if(len(x_cz_wspolna) > 0):
            scatter_cz_wspolna = ax.scatter3D(x_cz_wspolna, y_cz_wspolna, z_cz_wspolna, color='green', label="cz_wspolna")
            self.scatters.append(scatter_cz_wspolna)
            self.choices.append("cz_wspolna")
            check_state.append(True)
        if(len(x_cz_rozna_kmeans) > 0):
            scatter_cz_rozna_kmeans = ax.scatter3D(x_cz_rozna_kmeans, y_cz_rozna_kmeans, z_cz_rozna_kmeans, color='blue', label="ob_rozne_tylko_kmeans")
            self.scatters.append(scatter_cz_rozna_kmeans)
            self.choices.append("ob_rozne_tylko_kmeans")
            check_state.append(True)
        if(len(x_cz_rozna_hierarchiczna) > 0):
            scatter_cz_rozna_hierarchiczna = ax.scatter3D(x_cz_rozna_hierarchiczna, y_cz_rozna_hierarchiczna, z_cz_rozna_hierarchiczna, color='cyan', label="ob_rozne_tylko_hierarchiczna")
            self.scatters.append(scatter_cz_rozna_hierarchiczna)
            self.choices.append("ob_rozne_tylko_hierarchiczna")
            check_state.append(True)
        if(len(x_cz_rozna_dbscan) > 0):
            scatter_cz_rozna_dbscan = ax.scatter3D(x_cz_rozna_dbscan, y_cz_rozna_dbscan, z_cz_rozna_dbscan, color='red', label="ob_rozne_tylko_dbscan")
            self.scatters.append(scatter_cz_rozna_dbscan)
            self.choices.append("ob_rozne_tylko_dbscan")
            check_state.append(True)
        if(len(x_1_2) > 0):
            scatter_cz_rozna_wspolna_1_2 = ax.scatter3D(x_1_2, y_1_2, z_1_2, color='blue',  linewidths=2, edgecolors='cyan', label="ob_rozne_kmeans_i_hierarchiczna")
            self.scatters.append(scatter_cz_rozna_wspolna_1_2)
            self.choices.append("ob_rozne_kmeans_i_hierarchiczna")
            check_state.append(True)
        if(len(x_1_3) > 0):
            scatter_cz_rozna_wspolna_1_3 = ax.scatter3D(x_1_3, y_1_3, z_1_3, color='blue',  linewidths=2, edgecolors='red', label="ob_rozne_kmeans_i_dbscan")
            self.scatters.append(scatter_cz_rozna_wspolna_1_3)
            self.choices.append("ob_rozne_kmeans_i_dbscan")
            check_state.append(True)
        if(len(x_2_3) > 0):
            scatter_cz_rozna_wspolna_2_3 = ax.scatter3D(x_2_3, y_2_3, z_2_3, color='red',  linewidths=2, edgecolors='cyan', label="ob_rozne_dbscan_i_hierarchiczna")
            self.scatters.append(scatter_cz_rozna_wspolna_2_3)
            self.choices.append("ob_rozne_dbscan_i_hierarchiczna")
            check_state.append(True)

        ax.legend()
        plt.subplots_adjust(left=0.35)
        ax_checkbox = plt.axes([0.02, 0.73, 0.25, 0.15])
        

        for i, scatter in enumerate(self.scatters):
            scatter.set_visible(check_state[i])

        self.checkbox = CheckButtons(ax_checkbox, self.choices, check_state)
        self.checkbox.on_clicked(self.SetScatterVisable)
        
        plt.show()

app = QApplication(sys.argv)
mainWindow = MainWindow()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainWindow)
widget.setFixedWidth(1052)
widget.setFixedHeight(666)
widget.show()
sys.exit(app.exec_())

#dendogram
#add default values
#-1 do indexaxji kolumn
#poprawienie literowki w zakladce "knn" na "kmeans"
#tabela z wynikami obiekt - grupa - porównanie
#indeksacja do tabeli w podglądzie
#zapis wynikow z tabeli do pliku json 
#wykresy z identyfikacją
#na koniec jak bedzei czas wczytywanie inych formatów plików...

# 5 kryteriów porównania w badaniu:
#
# 1.Jakość przeprowadzonego grupowania (czy wynik grupowania nie jest mylący, słabe punkty pogrupowania)
# 2.Intuicyjność parametrów (które są łatwiejsze w dostosowaniu do grupowanych danych jeśli nie jesteśmy dobrze zaznajomieni z badanymi danymi)
# 3.Stabilność grupowania (przy dwukrotnym uruchomieniu algorytmy z podobnymi ustawieniami powinniśmy się spodziewać zbliżonych wyników grupowania, 
#   nie powinno być widocznych radykalnych różnic w grupowaniu)
# 4.Wpływ metryki na proces grupowania????
# 5.Wydajność metody (jak dana metoda radzi sobie ze zwiększającymi się zbiorami danych, ile czasu potrzebuje na grupowanie)
