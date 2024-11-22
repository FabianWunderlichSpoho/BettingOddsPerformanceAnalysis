# -*- coding: utf-8 -*-
"""
@author: FW

#At this point, several options are provided to obtain the anticipated number of goals per team from the betting odds
"""


import pandas as pd
from abc import ABC
from bettingCalculationTools.ProbabilityModelling import PoissonModel

from sklearn import linear_model


#defining the interface of objects that calculate anticipated goals.
class AnticipatedGoalsCalculator(ABC):

    def __init__(self, calculatorType):
        self.type = calculatorType

    #calculates probabilities for a range of outcomes from the given betting odds
    def addAnticipatedGoals(self, data, percentageIS = 0.5):
        pass
        
        return data
    

#uses linear or Poisson regression to transfer odds into anticipated goals
class Regression(AnticipatedGoalsCalculator):
    #regressionType=''
    
    def __init__(self, regressionType):
        self.regressionType = regressionType
        super().__init__(regressionType)

    
    def addAnticipatedGoals(self, data):
        #split in-sample and out-of-sample
        data.sort_values(by=['date','teamHome','teamAway'], ascending = [True, True, True], inplace=True)
        row = int(len(data)*0.5)
        data1 = data.iloc[:row,:]
        data2 = data.iloc[row:,:]
        
        if self.regressionType == 'poisson':
            regressionHome = linear_model.PoissonRegressor()
            regressionAway = linear_model.PoissonRegressor()      
        else:
            regressionHome = linear_model.LinearRegression()
            regressionAway = linear_model.LinearRegression()
        
        odds1 = data1[['oddsHome','oddsDraw','oddsAway','oddsUnder25', 'oddsOver25']]
        odds2 = data2[['oddsHome','oddsDraw','oddsAway','oddsUnder25', 'oddsOver25']]

        regressionHome.fit(odds2,data2['goalsHome'])
        regressionAway.fit(odds2,data2['goalsAway'])        
        
        data1 = data1.assign(anticipatedGoalsHome = regressionHome.predict(odds1))
        data1 = data1.assign(anticipatedGoalsAway = regressionAway.predict(odds1))
        
        regressionHome.fit(odds1,data1['goalsHome'])
        regressionAway.fit(odds1,data1['goalsAway'])
        
        data2 = data2.assign(anticipatedGoalsHome = regressionHome.predict(odds2))
        data2 = data2.assign(anticipatedGoalsAway = regressionAway.predict(odds2))
        
        
        return pd.concat([data1, data2], ignore_index=True, axis=0)

        
#uses the combination of two regressions to transfer odds into anticipated goals (only linear regression is possible as difference does not suit Poisson regression)
class DoubleRegression(AnticipatedGoalsCalculator):
    #regressionType=''
    
    def __init__(self):
        super().__init__('regression')

    
    def addAnticipatedGoals(self, data, percentageIS):
        #split in-sample and out-of-sample
        data.sort_values(by=['date','teamHome','teamAway'], ascending = [True, True, True], inplace=True)
        row = int(len(data)*percentageIS)
        inSample = data.iloc[:row,:]
        outOfSample = data.iloc[row+1:,:]
        
        regressionSum = linear_model.LinearRegression()
        regressionDifference = linear_model.LinearRegression()
        
        oddsIS = inSample[['oddsHome','oddsDraw','oddsAway','oddsUnder25', 'oddsOver25']]
        oddsOOS = outOfSample[['oddsHome','oddsDraw','oddsAway','oddsUnder25', 'oddsOver25']]

        
        regressionSum.fit(oddsIS,inSample['goalsHome']+inSample['goalsAway'])
        regressionDifference.fit(oddsIS,inSample['goalsHome']-inSample['goalsAway'])
        
        outOfSample = outOfSample.assign(anticipatedGoalsHome = 0.5*(regressionSum.predict(oddsOOS)+regressionDifference.predict(oddsOOS)))
        outOfSample = outOfSample.assign(anticipatedGoalsAway = 0.5*(regressionSum.predict(oddsOOS)-regressionDifference.predict(oddsOOS)))
        return pd.concat([inSample, outOfSample], ignore_index=True, axis=0)
        

#uses a precalculated Poisson model to inversely obtain anticipated goals from odds
class InvertedPoisson(AnticipatedGoalsCalculator):
    
    def __init__(self):
        super().__init__('invertedPoisson')
   
    def addAnticipatedGoals(self, data, file):
        model = PoissonModel()
        table = model.loadTable(file)
        antHome = []
        antAway = []
        for row in range(0,len(data)):
            probabilities = data[['probHome', 'probDraw', 'probAway', 'probOver25', 'probUnder25']].iloc[row]
            anticipations = model.obtainAnticipatedGoals(table, probabilities)
            antHome.append(anticipations[0])
            antAway.append(anticipations[1])
        
        data = data.assign(anticipatedGoalsHome = antHome)
        data = data.assign(anticipatedGoalsAway = antAway)
   
        return data

        
    


