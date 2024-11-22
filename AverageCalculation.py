# -*- coding: utf-8 -*-
"""
@author: FW
"""

import os
import numpy as np
import pandas as pd


#class ised to calculate the average number of points or goals to be used in further analysis
class AverageCalculation:

    #expects dataframe and calculates average number of points and goals for each team in each match 
    def calculateAverages(data):
        #reset to use right order
        data['date'] = pd.to_datetime(data['date'], format = '%d/%m/%y')
        data.sort_values(by=['date','teamHome','teamAway'], ascending = [True, True, True], inplace=True)
        data.reset_index(drop = True, inplace=True)
        
        #set season and flag for first/second round
        data['round'] = np.nan
        data.loc[data['date'].dt.month >= 7, 'round'] = 'first'
        data.loc[data['date'].dt.month < 7, 'round'] = 'second'
        
        #add points to data
        conditions = [data['goalsHome'] > data['goalsAway'],
                      data['goalsHome'] == data['goalsAway']]
        choices = [3,1]
        data['pointsHome'] = np.select(conditions, choices, default=0)
        
        choices = [0,1]
        data['pointsAway'] = np.select(conditions, choices, default=3)
        

        #calculation of average goals and points for each team as well as averages across teams and anticipated goals based on these
        data.insert(len(data.columns),'avgGoalsHome',np.nan)
        data.insert(len(data.columns),'avgGoalsAway',np.nan)
        data.insert(len(data.columns),'avgGoalsAgainstHome',np.nan)
        data.insert(len(data.columns),'avgGoalsAgainstAway',np.nan)
        data.insert(len(data.columns),'avgPointsHome',np.nan)
        data.insert(len(data.columns),'avgPointsAway',np.nan)
        data.insert(len(data.columns),'avgGoalsHomeAllTeams',np.nan)
        data.insert(len(data.columns),'avgGoalsAwayAllTeams',np.nan)
        avgGoalsHomeAllTeams = 0
        avgGoalsAwayAllTeams = 0
        data.insert(len(data.columns),'anticipatedGoalsHomeAverage',np.nan)
        data.insert(len(data.columns),'anticipatedGoalsAwayAverage',np.nan)
        
        
        teamInformation = dict.fromkeys(np.unique(np.concatenate([data['teamHome'], data['teamAway']])))
        for key in teamInformation:
            teamInformation[key] = {'season': 'None', 'goals': 0, 'goalsAgainst':0, 'points': 0, 'matches': 0}
            
        #iterate over all matches
        for i in range(0,len(data.index)):
            teamHome = data['teamHome'][i]
            teamAway = data['teamAway'][i]
            season = data['season'][i]
            goalsHome = data['goalsHome'][i]
            goalsAway = data['goalsAway'][i]
            pointsHome = data['pointsHome'][i]
            pointsAway = data['pointsAway'][i]

                
            #reset data in case of new season
            if(season != teamInformation[teamHome]['season']):
                teamInformation[teamHome] = {'season': 'None', 'goals': 0, 'goalsAgainst': 0, 'points': 0, 'match': 0}
            if(season != teamInformation[teamAway]['season']):
                teamInformation[teamAway] = {'season': 'None', 'goals': 0, 'goalsAgainst': 0, 'points': 0, 'match': 0}                
            
            #set average goals and points for both teams as well as averages across all teams and anticipated goals based on these
            data.iloc[i, data.columns.get_loc('avgPointsHome')] = teamInformation[teamHome]['points']
            data.iloc[i, data.columns.get_loc('avgGoalsHome')] = teamInformation[teamHome]['goals']
            data.iloc[i, data.columns.get_loc('avgGoalsAgainstHome')] = teamInformation[teamHome]['goalsAgainst']
            data.iloc[i, data.columns.get_loc('avgPointsAway')] = teamInformation[teamAway]['points']
            data.iloc[i, data.columns.get_loc('avgGoalsAway')] = teamInformation[teamAway]['goals']
            data.iloc[i, data.columns.get_loc('avgGoalsAgainstAway')] = teamInformation[teamAway]['goalsAgainst']
            data.iloc[i, data.columns.get_loc('avgGoalsHomeAllTeams')] = avgGoalsHomeAllTeams
            data.iloc[i, data.columns.get_loc('avgGoalsAwayAllTeams')] = avgGoalsAwayAllTeams
            anticipatedGoalDiffAverage = 1/2*((data['avgGoalsHome'][i] - data['avgGoalsAgainstHome'][i]) - (data['avgGoalsAway'][i] - data['avgGoalsAgainstAway'][i]))
            data.iloc[i, data.columns.get_loc('anticipatedGoalsHomeAverage')] = data['avgGoalsHomeAllTeams'][i] + 1/2 * anticipatedGoalDiffAverage
            data.iloc[i, data.columns.get_loc('anticipatedGoalsAwayAverage')] = data['avgGoalsAwayAllTeams'][i] - 1/2 * anticipatedGoalDiffAverage
            
            
            
            #update team information, particularly average goals and points
            match = teamInformation[teamHome]['match']
            teamInformation[teamHome]['points'] = (teamInformation[teamHome]['points']*match + pointsHome)/(match + 1)
            teamInformation[teamHome]['goals'] = (teamInformation[teamHome]['goals']*match + goalsHome)/(match + 1)
            teamInformation[teamHome]['goalsAgainst'] = (teamInformation[teamHome]['goalsAgainst']*match + goalsAway)/(match + 1)
            teamInformation[teamHome]['season'] = season
            teamInformation[teamHome]['match'] = match + 1
            
            match = teamInformation[teamAway]['match']
            teamInformation[teamAway]['points'] = (teamInformation[teamAway]['points']*match + pointsAway)/(match + 1)
            teamInformation[teamAway]['goals'] = (teamInformation[teamAway]['goals']*match + goalsAway)/(match + 1)
            teamInformation[teamAway]['goalsAgainst'] = (teamInformation[teamAway]['goalsAgainst']*match + goalsHome)/(match + 1)
            teamInformation[teamAway]['season'] = season
            teamInformation[teamAway]['match'] = match + 1
            
            #update average number of home/away goals across all teams
            avgGoalsHomeAllTeams = (avgGoalsHomeAllTeams*(i)+goalsHome)/(i+1)
            avgGoalsAwayAllTeams = (avgGoalsAwayAllTeams*(i)+goalsAway)/(i+1)            
       
        data.to_csv(os.path.join(os.path.dirname(__file__), "data\dataAverages.csv"))          
        return data
            
    
