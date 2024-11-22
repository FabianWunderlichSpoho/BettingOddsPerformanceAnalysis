# -*- coding: utf-8 -*-
"""
@author: FW

Analysis on the relationship between performance indicators (shots, shots on target), team strength and success
"""

import os
import numpy as np
import pandas as pd
from bettingCalculationTools.DataImport import DataImporter
from bettingCalculationTools.ProbabilityCalculation import ShinModel
from bettingCalculationTools.AnticipatedGoalsCalculation import InvertedPoisson
import matplotlib.pyplot as plt



#loads and saves all data
def saveData():
    root = os.path.join(os.path.dirname(__file__), "input")
    mapping = os.path.join(os.path.dirname(__file__), "inputMappings\inputMappingMatchDataAverageOdds.csv")
    DataImporter.inputAllFiles(root, mapping, missingDataAllowed = ['shotsHome', 'shotsAway', 'shotsTargetHome', 'shotsTargetAway'])

#prepares and saves data to be used for the visualisations
def prepareData():
    data = pd.read_csv(os.path.join(os.path.dirname(__file__), "data\data.csv"), sep = ",")   

    #add favourite information, probabilities and anticipated number of goals
    Calculator = ShinModel()
    data = Calculator.addProbabilities(data)
    data = InvertedPoisson().addAnticipatedGoals(data, os.path.join(os.path.dirname(__file__), "data\Table.csv"))

    dataHome = data[['league','date','teamHome','result','goalsHome','shotsHome','shotsAway','shotsTargetHome','shotsTargetAway','season','oddsHome','oddsDraw', 'oddsAway', 'probHome','probDraw','anticipatedGoalsHome']].copy()
    dataAway = data[['league','date','teamAway','result','goalsAway','shotsAway','shotsHome','shotsTargetAway','shotsTargetHome','season','oddsAway','oddsDraw','oddsHome', 'probAway','probDraw','anticipatedGoalsAway']].copy()
    dataHome.columns = ['league','date','team','result','goals','shots','shotsOpponent','shotsTarget','shotsTargetOpponent','season','odds','oddsDraw','oddsOpponent', 'prob','probDraw','anticipatedGoals']
    dataAway.columns = ['league','date','team','result','goals','shots','shotsOpponent','shotsTarget','shotsTargetOpponent','season','odds','oddsDraw','oddsOpponent','prob','probDraw','anticipatedGoals']
    dataHome.insert(len(dataHome.columns), 'home', 1)
    dataAway.insert(len(dataAway.columns), 'home', 0)
    
    dataHome['result'] = dataHome['result'].map({'H': 'W', 'A': 'L'})
    dataAway['result'] = dataAway['result'].map({'A': 'W', 'H': 'L'})
    
    data = pd.concat([dataHome, dataAway])
    
    data['fav'] = data.apply (lambda row: DataImporter.favOut(row), axis=1)
        
    data.to_csv(os.path.join(os.path.dirname(__file__), "data\dataPrepared.csv"))
    return data
        

#visualises the influence of favorite and outsider on winning with more shots / shots on target
#expects the variable and the prepared dataset as inputs
def visualiseDataFavoriteOutsider(variable, data):
    categories=['Favorite', 'Outsider']

    matchesWon = [len(data[(data.fav == 'fav') & (data[variable] > data[variable+'Opponent']) & (data.result == 'W')]),
                  len(data[(data.fav == 'out') & (data[variable] > data[variable+'Opponent']) & (data.result == 'W')])]
    matchesLost = [len(data[(data.fav == 'fav') & (data[variable] > data[variable+'Opponent']) & (data.result == 'L')]),
                  len(data[(data.fav == 'out') & (data[variable] > data[variable+'Opponent']) & (data.result == 'L')])]

    width = 0.35
    x = np.arange(len(categories))
    
    if(variable == 'shotsTarget'):
        variable = 'shots on target'
    plt.bar(x-width/2, matchesWon, width, label = 'Matches won with more ' + variable)
    plt.bar(x+width/2, matchesLost, width, label = 'Matches lost with more '+ variable)
    
    plt.ylabel('Number of matches')
    plt.xticks(x, categories)
    plt.legend()
    plt.show() 
        
    
#visualises the average shots / shots on target for winning and losing teams depending on the pre-game winning probability
#expects the variable and the prepared dataset as inputs    
def visualiseDataWinningProbability(variable , data):
    categories=['<10%', '10-20%', '20-30%','30-40%', '40-50%', '50-60%', '60-70%', '>70%']
    
    data['category'] = pd.cut(x=data['prob'], bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 1], 
                     labels = categories) 
    
    winner = []
    loser = []
    for category in categories:
        winner.append(np.mean(data[(data.category == category) & (data.result == "W")][variable]))
        loser.append(np.mean(data[(data.category == category) & (data.result == "W")][variable+'Opponent']))
  
    width = 0.35
    x = np.arange(len(categories))
    plt.bar(x-width/2, winner, width, label = 'Winning team')
    plt.bar(x+width/2, loser, width, label = 'Losing team')
    
    plt.xlabel('Pre-game winning probability of the winning team')
    if(variable == 'shotsTarget'):
        variable = 'shots on target'
    plt.ylabel('Average '+variable)
    plt.xticks(x, categories)
    plt.legend()
    plt.show() 
    

#visualises the performance/overperformance of teams dependent on the difference in shots / shots on target
#expects the variable and the prepared dataset as inputs
def visualiseDataAnticipatedGoals(variable, data):
    averageHome = np.mean(data[data.home == 1].goals, axis = 0)
    averageAway = np.mean(data[data.home == 0].goals, axis = 0)
    data['anticipatedGoalsLocation'] = data['home']
    data['anticipatedGoalsLocation'].replace(1, averageHome, inplace = True)
    data['anticipatedGoalsLocation'].replace(0, averageAway, inplace = True)
    
    data['overperformance'] = data['goals'] - data['anticipatedGoals']
    data['performance'] = data['goals'] - data['anticipatedGoalsLocation']
    data['variableDifference'] = data[variable]-data[variable+'Opponent']
    
    if(variable == 'shotsTarget'):
        categories=['<-5','-5','-4','-3','-2','-1','0','1','2','3','4','5','>5']
        bins = [-100,-5.5,-4.5,-3.5,-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5,5.5,100]
    elif(variable == 'shots'):
        categories=['<-10','-10','-8','-6','-4','-2','0','2','4','6','8','10','>10']
        bins = [-200,-10.5,-8.5,-6.5,-4.5,-2.5,-0.5,0.5,2.5,4.5,6.5,8.5,10.5,100]
    else:
        categories = []
        bins = []
    
    data['category'] = pd.cut(x=data['variableDifference'], bins=bins, 
                     labels = categories) 
    
    performance = []
    overperformance = []
    for category in categories:
        performance.append(np.mean(data[data.category == category].performance))
        overperformance.append(np.mean(data[data.category == category].overperformance))
           
    width = 0.35
    x = np.arange(len(categories))
    plt.bar(x-width/2, performance, width, label = 'Performance relative to global expectation')
    plt.bar(x+width/2, overperformance, width, label = 'Performance relative to team-specific expectation')
    
    if(variable == 'shotsTarget'):
        variable = 'shots on target'
    plt.xlabel('Difference in '+variable)
    plt.ylabel('Relative performance in goals')
    plt.xticks(x, categories)
    plt.yticks(np.arange(-0.75, 1.5, step = 0.25))
    plt.legend()
    plt.show() 
    
    

saveData()     
prepareData() 
visualiseDataFavoriteOutsider('shots', pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataPrepared.csv"), sep = ","))
visualiseDataWinningProbability('shots', pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataPrepared.csv"), sep = ","))
visualiseDataAnticipatedGoals('shots', pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataPrepared.csv"), sep = ","))
visualiseDataFavoriteOutsider('shotsTarget', pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataPrepared.csv"), sep = ","))
visualiseDataWinningProbability('shotsTarget', pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataPrepared.csv"), sep = ","))
visualiseDataAnticipatedGoals('shotsTarget', pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataPrepared.csv"), sep = ","))
