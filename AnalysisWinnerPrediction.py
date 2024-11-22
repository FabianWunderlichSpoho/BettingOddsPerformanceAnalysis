# -*- coding: utf-8 -*-
"""
@author: FW

Analysis on the accuracy of betting odds in picking the winner of a match compared to several other methods
"""

import pandas as pd
from bettingCalculationTools.DataImport import DataImporter
from AverageCalculation import AverageCalculation
import os
from EloModel import EloRating
from statsmodels.stats.proportion import proportion_confint
import matplotlib.pyplot as plt 

#best performing Elo specification in the present experiment
ha = 80
k = 25

#loads, prepares and saves all data
def prepareData():
    root = os.path.join(os.path.dirname(__file__), "input")
    mapping = os.path.join(os.path.dirname(__file__), "inputMappings\inputMappingMatchDataAverageOdds.csv")
    data = DataImporter.inputAllFiles(root, mapping, missingDataAllowed = ['shotsHome', 'shotsAway', 'shotsTargetHome', 'shotsTargetAway'])
    data = AverageCalculation.calculateAverages(data)
    
    Rating = EloRating()
    data = Rating.calculateRating(data, k, ha)
    
    data.to_csv(os.path.join(os.path.dirname(__file__), "data\dataWinnerPrediction.csv"))


#analyses and prints the accuracy of betting odds and further method to correctly predict the winner of a match 
def calculateAccuracyWinnerPrediction(data, excludeSeason = 'NAN'):
    
    #exclude draws, set favourites and check winners
    data.insert(len(data.columns),'winner',0)
    data.loc[data['goalsHome'] > data['goalsAway'], 'winner'] = 1
    data.loc[data['goalsHome'] < data['goalsAway'], 'winner'] = 2
    
    #exclude first season to allow fair comparison to Elo ratings
    print('Number of total matches: '+str(len(data.index)))
    data = data[data['season'] != excludeSeason]
    print('Number of total matches wo season '+excludeSeason+': '+str(len(data.index)))
    print('Number of draw matches: '+str(len(data[data['winner'] == 0].index)))
    print('Percentage of draw matches: '+str(len(data[data['winner'] == 0].index)/len(data.index)))
    data = data[data['winner'] != 0]
    print('Number of matches without draw: ' + str(len(data.index)))
        
    data.insert(len(data.columns),'location',1)
        
    data.insert(len(data.columns),'odds',0)
    data.loc[data['oddsHome'] < data['oddsAway'], 'odds'] = 1
    data.loc[data['oddsHome'] > data['oddsAway'], 'odds'] = 2

    data.insert(len(data.columns),'points',0)
    data.loc[data['avgPointsHome'] > data['avgPointsAway'], 'points'] = 1
    data.loc[data['avgPointsHome'] < data['avgPointsAway'], 'points'] = 2
    
    data.insert(len(data.columns),'elo',0)
    data.loc[data['eloHome']+ha > data['eloAway'], 'elo'] = 1
    data.loc[data['eloHome']+ha < data['eloAway'], 'elo'] = 2
        
    data.insert(len(data.columns),'goals',0)
    data.loc[data['avgGoalsHome'] - data['avgGoalsAgainstHome'] > data['avgGoalsAway'] - data['avgGoalsAgainstAway'], 'goals'] = 1
    data.loc[data['avgGoalsHome'] - data['avgGoalsAgainstHome'] < data['avgGoalsAway'] - data['avgGoalsAgainstAway'], 'goals'] = 2    

    #print results for each of the methods
    dataBySeason = pd.DataFrame()
    for variable in ['location', 'odds', 'points', 'goals', 'elo']:
        dataEval = data[data[variable] != 0]
        
        n = len(dataEval.index)
        favouriteWins = len(dataEval[dataEval['winner'] == dataEval[variable]].index)
        print('------------ '+variable+' -----------------')
        print('Total matches '+ str(n))
        print('Number of favourite wins '+str(favouriteWins))
        print('Percentage of favourite wins '+str(favouriteWins/n))
        print('Confidence Interval Lower '+str(proportion_confint(favouriteWins, n, method = 'binom_test')[0]))
        print('Confidence Interval Upper '+str(proportion_confint(favouriteWins, n, method = 'binom_test')[1]))
        
        #clculate accuracies by half seasons to be used in the plot
        nSeason = dataEval.groupby(['season', 'round'])['season'].count()
        favoriteWinsSeason = dataEval[dataEval['winner'] == dataEval[variable]].groupby(['season', 'round'])['season'].count()
        accuracySeason = favoriteWinsSeason / nSeason * 100
        dataBySeason[variable]=accuracySeason
        
        dataEval = dataEval[dataEval['round']=='second']
        n = len(dataEval.index)
        favouriteWins = len(dataEval[dataEval['winner'] == dataEval[variable]].index)
        print('------------ Only second -----------------')
        print('Total matches '+ str(n))
        print('Number of favourite wins '+str(favouriteWins))
        print('Percentage of favourite wins '+str(favouriteWins/n))
        print('Confidence Interval Lower '+str(proportion_confint(favouriteWins, n, method = 'binom_test')[0]))
        print('Confidence Interval Upper '+str(proportion_confint(favouriteWins, n, method = 'binom_test')[1]))

    
    #plot accuracies by half season
    plt.rcParams['figure.dpi'] = 300
    dataBySeason['timeInterval'] = dataBySeason.index.get_level_values(0).astype(str).values + ' ' + dataBySeason.index.get_level_values(1).astype(str).values
    dataBySeason['timeInterval'] = dataBySeason['timeInterval'].str.replace("202", "2")
    dataBySeason['timeInterval'] = dataBySeason['timeInterval'].str.replace("201", "1")
    dataBySeason['timeInterval'] = dataBySeason['timeInterval'].str.replace("200", "0")
    dataBySeason['timeInterval'] = dataBySeason['timeInterval'].str.replace("first", "1")
    dataBySeason['timeInterval'] = dataBySeason['timeInterval'].str.replace("second", "2")
    plt.plot(dataBySeason['timeInterval'], dataBySeason['elo'], marker='o', color = "black")
    plt.plot(dataBySeason['timeInterval'], dataBySeason['odds'], marker='o', color = "cornflowerblue")
    plt.plot(dataBySeason['timeInterval'], dataBySeason['location'], marker='o', color = "forestgreen")
    plt.plot(dataBySeason['timeInterval'], dataBySeason['goals'], marker='o', color = "indianred")
    plt.xlabel('Time Interval')
    plt.ylabel('Matches won by favorite in %')
    plt.axhline(y = 50, linestyle = 'dashed', color = "black")
    #plt.axvline(x = "19/20 1", ymin = 0.1, ymax = 0.95, linestyle = 'dotted', color = "black")
    plt.xticks(rotation=30)
    #plt.text("07/08 1", 66, "Elo Rating")
    #plt.text("07/08 1", 71.5, "Betting Odds")
    #plt.text("18/19 1", 54, "Match Location")
    #plt.text("18/19 1", 62, "Average Goals")
    #only show every fifth label on the x-axis
    labels = plt.gca().get_xticklabels()
    for i in range(0, len(labels)):
        if (i%5 != 0):
            labels[i].set_visible(False)
            
    plt.show()
    
prepareData()
#calculateAccuracyWinnerPrediction(pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataWinnerPrediction.csv")), '2005/2006')
calculateAccuracyWinnerPrediction(pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataWinnerPrediction.csv")))
   