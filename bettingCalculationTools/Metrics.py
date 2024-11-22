# -*- coding: utf-8 -*-
"""
@author: FW
"""

#this class provides several methods to calculate accuracy metrics like rank probability score or squared errors
class MetricsCalculation():
    
    #expects a dataframe and calculates RPS for over under bets
    def calculateRPSOU(data):
        over25 = data['goalsHome']+data['goalsAway']>2
        scores = (data['probOver25']-over25)**2
        return scores
    
    #expects a dataframe and calculates RPS for home draw away bets
    def calculateRPSAvgOU(data):
        print("RPS OU calculated for "+str(len(data))+" matches")
        return MetricsCalculation.calculateRPSOU(data).mean()
    
    #expects a dataframe and calculates RPS for home draw away bets
    def calculateRPSHDA(data):
        home = data['goalsHome']>data['goalsAway']
        draw = data['goalsHome']==data['goalsAway']
        scores = 0.5*((data['probHome']-home)**2 + (data['probHome']+data['probDraw']-home-draw)**2)
        return scores
    
    #expects a dataframe and calculates RPS for home draw away bets
    def calculateRPSAvgHDA(data):
        print("RPS HDA calculated for "+str(len(data))+" matches")
        return MetricsCalculation.calculateRPSHDA(data).mean()
    
    #expects a dataframe and calculates squared error between anticipated and actual number of goals
    def calculateSquaredErrorAnticipatedGoals(data):
        squaredHome = (data['anticipatedGoalsHome']-data['goalsHome'])**2
        squaredAway = (data['anticipatedGoalsAway']-data['goalsAway'])**2
        print("Squared error home and away calculated for "+str(len(data))+" matches")
        return squaredHome.mean(), squaredAway.mean()
    
    #same as above, but goal prediction is the average goal difference per team plus the average goal difference across all teams (i.e. information on each teams average goals and the match location)
    def calculateSquaredErrorAverageGoals(data):
        squaredHome = (data['anticipatedGoalsHomeAverage']-data['goalsHome'])**2
        squaredAway = (data['anticipatedGoalsAwayAverage']-data['goalsAway'])**2
        print("Squared error home and away calculated for "+str(len(data))+" matches")
        return squaredHome.mean(), squaredAway.mean()
    
    #same as above, but goal prediction is the average number of home and away teams across all teams (i.e. just information on the match location)
    def calculateSquaredErrorAverageHA(data):
        squaredHome = (data['avgGoalsHomeAllTeams']-data['goalsHome'])**2
        squaredAway = (data['avgGoalsAwayAllTeams']-data['goalsAway'])**2
        print("Squared error home and away calculated for "+str(len(data))+" matches")
        return squaredHome.mean(), squaredAway.mean()