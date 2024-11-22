# -*- coding: utf-8 -*-
"""
@author: FW

In this class parameters (e.g. anticipated goals) are transferred into winning or O/U probabilities through a statistcal model of matches.
Moreover, a numerical solution to invert such a model and obtain anticipated goals from odds/probabilities is implemented
"""

import os
import numpy as np
import pandas as pd
from abc import ABC
from scipy.stats import poisson


 
#defining the interface of objects that calculate outcome probabilities through statistical models of matches.
class ProbabilityModel(ABC):

    def __init__(self, modelType):
        self.type = modelType

    #calculates probabilities for a range of outcomes from the given parameters
    def calculateProbabilities(self, outcomes):
        pass
    
    #expects probabilities for each result and calculates summarised probabilities
    def summariseProbabilities(self, probabilities):
        probabilityHome = 0
        probabilityDraw = 0
        probabilityAway = 0
        probabilityOver25 = 0
        probabilityUnder25 = 0
        sum = 0
        
        for i in range(0,10):
            for j in range(0,10):
                if (i>j):
                    probabilityHome += probabilities[i][j]
                elif (i==j):
                    probabilityDraw += probabilities[i][j]
                else:
                    probabilityAway += probabilities[i][j]
                if (i+j>2):
                    probabilityOver25 += probabilities[i][j]
                else:
                    probabilityUnder25 += probabilities[i][j]
                sum += probabilities[i][j]
        
        return [probabilityHome/sum, probabilityDraw/sum, probabilityAway/sum, probabilityOver25/sum, probabilityUnder25/sum]
    
    #calculates a table with all combinations of anticipated goals home and away
    def calculateTable(self):
        table = pd.DataFrame()
        for antHome in np.arange(0.0,6.0,0.025):
            print("Calculating model probabilities for anticipated number of home goals: "+str(antHome))
            for antAway in np.arange(0.0,6.0,0.025):
                table = pd.concat([table, pd.DataFrame([[antHome, antAway] + self.summariseProbabilities(self.calculateProbabilities(antHome, antAway))])], ignore_index=True, axis=0)
        table.columns = ['antHome', 'antAway', 'probHome', 'probDraw', 'probAway', 'probOver25', 'probUnder25']
        return table
    
    
    #saves a table in csv format in a given file 
    def saveTable(self, table, file):
        table.to_csv(file, index = False)
    
    #loads an existing table
    def loadTable(self, file):
        return(pd.read_csv(file, encoding = "latin", on_bad_lines='error'))
    
    #given the outcome probabilities, obtain the best-fitting anticipated goals from a precalculated table
    def obtainAnticipatedGoals(self, table, probabilities):
        #calculate difference to input probabilities
        diff = table.iloc[:,2:]-probabilities
        #calculate sum of squared differences
        sumDiffs = diff['probHome']**2 + diff['probDraw']**2 + diff['probAway']**2 + diff['probOver25']**2 + diff['probUnder25']**2 

        minIndex = sumDiffs.idxmin()
        return table['antHome'][minIndex], table['antAway'][minIndex]
    
    
#independent Poisson model
class PoissonModel(ProbabilityModel):
    
    def __init__(self):
        super().__init__('poissonModel')
    
    def calculateProbabilities(self, lambda1, lambda2):
        probabilities=[]
        for i in range(0,10):
            column = []
            for j in range(0,10):
                column.append(poisson.pmf(i, lambda1)*poisson.pmf(j, lambda2))
            probabilities.append(column)
        return probabilities
    



mod = PoissonModel()
table = mod.calculateTable()
mod.saveTable(table, os.path.join(os.path.dirname(__file__), "../data\Table.csv"))