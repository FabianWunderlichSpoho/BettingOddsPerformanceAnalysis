# -*- coding: utf-8 -*-
"""
@author: FW
"""


import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import os


pd.options.mode.chained_assignment = None

#Abstract class defining the interface of rating model.
#rating is calculated based on the dataset
class RatingModel(ABC):

    def __init__(self, modelType):
        self.type = modelType

    #calculates rating for the teams based on the dataset
    def calculateRating(self, data):
        pass

        
    #helper method to update information on the initial ratings to be used for promoted or relegated teams
    def updateRelegationPromotionRatings(self, data, i, season, league, columnName, team, currentRatings, relegationRating, promotionRating):
        if(data[columnName][i]==1):
            #reset relegation ratings in case of new seasons
            if(relegationRating[league]['season']!=season):
                relegationRating[league]['rating']=[] 
            relegationRating[league]['season']=season
            relegationRating[league]['rating'].append(currentRatings[team]['calculated'])  
        elif(data[columnName][i]==-1):
            #reset promotion ratings in case of new seasons
            if(promotionRating[league]['season']!=season):
                 promotionRating[league]['rating']=[] 
            promotionRating[league]['season']=season
            promotionRating[league]['rating'].append(currentRatings[team]['calculated'])  
                    
        
    
    #helper method to initialise ratings to be used for promoted or relegated teams          
    def initialiseRating(self, data, i, columnName, league, team, currentRatings, relegationRating, promotionRating):
        if(data[columnName][i]==2):
            currentRatings[team]['calculated']=np.mean(promotionRating[league]['rating'])
        elif(data[columnName][i]==-2):
            currentRatings[team]['calculated']=np.mean(relegationRating[league]['rating'])


    #this method flags promoted or relegated teams, which is important for rating calculation, e.g. in ELO or pi-rating
    def flagPromotedRelegatedTeams(self, data, teamInformation):
        promotedHome = [0]*len(data.index)
        promotedAway = [0]*len(data.index)
        relegatedHome = [0]*len(data.index)
        relegatedAway = [0]*len(data.index)
        
        
        for i in range(0,len(data.index)):
            teamHome = data['teamHome'][i]
            teamAway = data['teamAway'][i]
            season = int(data['season'][i][:2])
            
            #get information on old and new league
            leagueOldHome = teamInformation[teamHome]['league']
            divisionOldHome = int(leagueOldHome[-1])
            leagueOldAway = teamInformation[teamAway]['league']            
            divisionOldAway = int(leagueOldAway[-1])
            leagueNew = data['league'][i]
            divisionNew = int(leagueNew[-1])

            #promoted teams are flagged in current and last match, league is adjusted
            #1 means last match before promotion, 2 means first match after promotion
            #teams who have not been in the dataset for min a season are considered to be promoted
            if(divisionOldHome>divisionNew):# or season - teamInformation[teamHome]['lastMatchSeason'] > 1):
                RatingModel.updateTeamInformation(i, teamHome, teamInformation, leagueNew, promotedHome, promotedAway, home = True)
            if(divisionOldAway>divisionNew):# or season - teamInformation[teamHome]['lastMatchSeason'] > 1):
                RatingModel.updateTeamInformation(i, teamAway, teamInformation, leagueNew, promotedHome, promotedAway, home = False)

            #every team is flagged as relegated in every match. Once the team appears again in the data, still has the same or better league, it is unflagged again
            relegatedHome[i] = 1
            relegatedAway[i] = 1
            if(divisionOldHome >= divisionNew and season - teamInformation[teamHome]['lastMatchSeason'] <= 1):
                if(teamInformation[teamHome]['homeAway']=='home'):
                    if(relegatedHome[teamInformation[teamHome]['lastMatchIndex']] == 1):
                        relegatedHome[teamInformation[teamHome]['lastMatchIndex']] = 0
                else:
                    if(relegatedAway[teamInformation[teamHome]['lastMatchIndex']] == 1):
                        relegatedAway[teamInformation[teamHome]['lastMatchIndex']] = 0
            if(divisionOldAway >= divisionNew and season - teamInformation[teamAway]['lastMatchSeason'] <= 1):
                if(teamInformation[teamAway]['homeAway']=='home'):
                    if(relegatedHome[teamInformation[teamAway]['lastMatchIndex']] == 1):
                        relegatedHome[teamInformation[teamAway]['lastMatchIndex']] = 0
                else:
                    if(relegatedAway[teamInformation[teamAway]['lastMatchIndex']] == 1):
                        relegatedAway[teamInformation[teamAway]['lastMatchIndex']] = 0
                    
            #relegated teams are flagged in current and last match, league is adjusted
            #1 means last match before relegation, 2 means first match after relegation
            if(divisionOldHome<divisionNew):            
                RatingModel.updateTeamInformation(i, teamHome, teamInformation, leagueNew, relegatedHome, relegatedAway, home = True)   
            if(divisionOldAway<divisionNew):
                 RatingModel.updateTeamInformation(i, teamAway, teamInformation, leagueNew, relegatedHome, relegatedAway, home = False) 

            #save the current match information as last match in the team information
            teamInformation[teamHome]['lastMatchIndex']=i
            teamInformation[teamHome]['homeAway']='home'
            teamInformation[teamHome]['lastMatchSeason']=season
            teamInformation[teamAway]['lastMatchIndex']=i
            teamInformation[teamAway]['homeAway']='away'
            teamInformation[teamAway]['lastMatchSeason']=season
             
        data['leagueChangeHome']=np.array(promotedHome) - np.array(relegatedHome)
        data['leagueChangeAway']=np.array(promotedAway) - np.array(relegatedAway)
         
        
        
    #helper method to update information on the promoted or relegated teams
    def updateTeamInformation(i, team, teamInformation, leagueNew, flagHome, flagAway, home = True):
        if(teamInformation[team]['homeAway']=='home'):
            flagHome[teamInformation[team]['lastMatchIndex']]=1
        elif(teamInformation[team]['homeAway']=='away'):
            flagAway[teamInformation[team]['lastMatchIndex']]=1
        if(home == True):
            flagHome[i]=2
        else:
            flagAway[i]=2
        teamInformation[team]['league']=leagueNew
    
    
    
#implements ELO rating based on the work of Hvattum&Arntzen (2010)
class EloRating(RatingModel):
    
    def __init__(self):
        super().__init__('ELORating')
        
    def calculateRating(self, data, k, ha):
        teamInformation = dict.fromkeys(np.unique(np.concatenate([data['teamHome'], data['teamAway']])))
        for key in teamInformation:
            teamInformation[key] = {'league': 'Start9', 'lastMatchSeason': -1, 'lastMatchIndex': 0, 'homeAway': 'NaN'}
            
        super().flagPromotedRelegatedTeams(data, teamInformation)
        
        #sort data by date
        data.sort_values(by=['date'], inplace = True)
        data.reset_index(inplace=True, drop = True)
        
        #distinct list of all teams in the dataset, initialised with rating of 1000/ initialised with league, last match and home/away information
        currentRatings = dict.fromkeys(np.unique(np.concatenate([data['teamHome'], data['teamAway']])))
        #if no data is avaiable, the actual rating is not set, but a calculated one exists, the history flag is false until data was available for the first time
        for key in currentRatings:
            currentRatings[key] = {'calculated': 0}        
        #distinct lists of all leagues in the dataset
        promotionRating = dict.fromkeys(np.unique(data['league']))
        for key in promotionRating:
            promotionRating[key] = {'season': 'NaN', 'rating': [1000,1000]}   
        relegationRating = dict.fromkeys(np.unique(data['league']))
        for key in relegationRating:
            relegationRating[key] = {'season': 'NaN', 'rating': [1000,1000]}   

        #Calculation of ELO ratings
        eloRatingsHome=[]
        eloRatingsAway=[]
        
        #iterate over all matches
        for i in range(0,len(data.index)):
            teamHome = data['teamHome'][i]
            teamAway = data['teamAway'][i]
            league = data['league'][i]
            season = data['season'][i]
            
            #update average ratings for promoted or relegated teams
            super().updateRelegationPromotionRatings(data, i, season, league, 'leagueChangeHome', teamHome, currentRatings, relegationRating, promotionRating)
            super().updateRelegationPromotionRatings(data, i, season, league, 'leagueChangeAway', teamAway, currentRatings, relegationRating, promotionRating)

            #initialise rating if needed 
            super().initialiseRating(data, i, 'leagueChangeHome', league, teamHome, currentRatings, relegationRating, promotionRating)
            super().initialiseRating(data, i, 'leagueChangeAway', league, teamAway, currentRatings, relegationRating, promotionRating)


            eloHome = currentRatings[teamHome]['calculated']
            eloAway = currentRatings[teamAway]['calculated']
            eloRatingsHome.append(eloHome)
            eloRatingsAway.append(eloAway)
            
            #calculate expected result (using c = 10 and d=400 and ha as specified)
            expHome = 1/(1+10**((eloAway-eloHome-ha)/400))
            expAway = 1-expHome
            

            
            #obtain actual result
            actHome = 1
            if(data['result'][i] == 'D'):
                actHome = 0.5
            elif(data['result'][i] == 'A'):
                actHome = 0

            actAway = 1 - actHome



            #calculate new elo rating (using k = 20)
            currentRatings[teamHome]['calculated']=eloHome + k * (actHome-expHome)
            currentRatings[teamAway]['calculated']=eloAway + k * (actAway-expAway)



        #set final ratings in dataframe    
        data['eloHome'] = eloRatingsHome
        data['eloAway'] = eloRatingsAway
            
        return data

