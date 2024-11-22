# -*- coding: utf-8 -*-
"""
@author: FW

#In this class, several options are provided to obtain outcome probabilities from betting odds
"""

import pandas as pd
from abc import ABC
import shin
from statsmodels.miscmodels.ordinal_model import OrderedModel
import statsmodels.api as sm
import math as m

#defining the interface of objects that calculate outcome probabilities from betting odds.
class ProbabilityCalculator(ABC):

    def __init__(self, calculatorType):
        self.type = calculatorType

    #calculates probabilities for a range of outcomes from the given betting odds
    def calculateProbabilities(self, outcomes):
        pass
    
    #expects a dataframe with data and adds probabilities 
    def addProbabilities(self, dataInput):
        data = dataInput.copy()
        #data.reset_index()
        probabilitiesHDA = self.calculateProbabilities(data['oddsHome'], data['oddsDraw'], data['oddsAway'])
        probabilitiesOU = self.calculateProbabilities(data['oddsOver25'], data['oddsUnder25'])
        
        data['probHome']=probabilitiesHDA[0]
        data['probDraw']=probabilitiesHDA[1]
        data['probAway']=probabilitiesHDA[2]
        data['probOver25']=probabilitiesOU[0]
        data['probUnder25']=probabilitiesOU[1]

        return data
    

#uses basic normalisation to convert odds into probabilities 
#(see Štrumbelj, E. (2014). On determining probability forecasts from betting odds. International journal of forecasting, 30(4), 934-943.)
class BasicNormalisation(ProbabilityCalculator):
    
    def __init__(self):
        super().__init__('basicNormalisation')
    
    def calculateProbabilities(self, *outcomes):
        #calculate overround
        overround = 0 
        for outcome in outcomes:
            overround = overround + 1/outcome
        #calculate probabilities  
        results = []
        for outcome in outcomes:
            results.append(1/outcome/overround)
            
        return results
    

    
    
#uses a model proposed by Shin to convert odds into probabilities (see Shin, H.S., 1993. Measuring the incidence of insider trading in a market for state-contingent claims. Economic Journal 103, 1141–53.)
#Also see Štrumbelj, E. (2014). On determining probability forecasts from betting odds. International journal of forecasting, 30(4), 934-943.
class ShinModel(ProbabilityCalculator):
    
    def __init__(self):
        super().__init__('basicNormalisation')
    
    def calculateProbabilities(self, *outcomes):
        results = pd.DataFrame()
        for row in range(0,len(outcomes[0])):
            list = []
            for outcome in outcomes:
                outcome = outcome.tolist()
                list.append(outcome[row])
            results = pd.concat([results, pd.DataFrame([shin.calculate_implied_probabilities(list, full_output=False)])], ignore_index=True, axis=0)
    
            if(row % 10000 == 0):
                print("Calculating Shin probabilities for row "+str(row)+ " of "+str(len(outcomes[0])))
        return results
    
    
#uses a logistic regression or an ordered logistic regression in case of three outcomes
#See Hvattum, L. M., & Arntzen, H. (2010). Using ELO ratings for match result prediction in association football. International Journal of forecasting, 26(3), 460-470.
class LogisticRegression(ProbabilityCalculator):   
    def __init__(self):
        super().__init__('logisticRegression')
        
        
    def addProbabilities(self, dataInput):
        data = dataInput.copy()
        
        #calculate output variables for fitting
        data.insert(len(data.columns),'winner',0)
        data.loc[data['goalsHome'] > data['goalsAway'],'winner'] = 2
        data.loc[data['goalsHome'] == data['goalsAway'],'winner'] = 1
        data.insert(len(data.columns),'over25',0)
        data.loc[data['goalsHome'] + data['goalsAway'] > 2, 'over25'] = 1
        
        #split dataset by half
        data1 = data.iloc[:m.floor(len(data)/2),:]
        data2 = data.iloc[m.floor(len(data)/2):,:]

        
        #calculate models
        orderedModel1 = OrderedModel(data2['winner'], data2[['oddsHome', 'oddsDraw', 'oddsAway']])
        regression1 = orderedModel1.fit(method='bfgs')
        probabilitiesHDA1 = regression1.predict(data1[['oddsHome', 'oddsDraw', 'oddsAway']])
        
        orderedModel2 = OrderedModel(data1['winner'], data1[['oddsHome', 'oddsDraw', 'oddsAway']])
        regression2 = orderedModel2.fit(method='bfgs')
        probabilitiesHDA2 = regression2.predict(data2[['oddsHome', 'oddsDraw', 'oddsAway']])
        
        probabilitiesHDA = pd.concat([probabilitiesHDA1, probabilitiesHDA2])

        logModel1 = sm.Logit(data2['over25'], data2[['oddsOver25', 'oddsUnder25']])
        regressionOU1 = logModel1.fit()
        probabilitiesOU1 = regressionOU1.predict(data1[['oddsOver25', 'oddsUnder25']])
        
        logModel2 = sm.Logit(data1['over25'], data1[['oddsOver25', 'oddsUnder25']])
        regressionOU2 = logModel2.fit()
        probabilitiesOU2 = regressionOU2.predict(data2[['oddsOver25', 'oddsUnder25']])
                                                  
        probabilitiesOU = pd.concat([probabilitiesOU1, probabilitiesOU2])
        
        data['probHome']=probabilitiesHDA[2]
        data['probDraw']=probabilitiesHDA[1]
        data['probAway']=probabilitiesHDA[0]
        data['probOver25']=probabilitiesOU
        data['probUnder25']=1-probabilitiesOU
        
        return data

