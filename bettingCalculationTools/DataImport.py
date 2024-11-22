# -*- coding: utf-8 -*-
"""
@author: FW
"""

import pandas as pd
import os


#used for the import of data from csv to a DataFrame with the expected format
class DataImporter:
    
    #imports relevant information from a file of any data source using the given mapping
    #New data are added to the existing data. If no data is available, the input for existing data should be an empty dataframe
    def addInputFile(self, existingData, file, mapping, inputFormat = '%d/%m/%y', targetFormat = '%d/%m/%y'):
        input = pd.read_csv(file, encoding = "latin", on_bad_lines='error')
        mapping = pd.read_csv(mapping)        
        newData = pd.DataFrame()
        
        #add newData if it exists in the input and not yet in the newData (i.e. only first apperance in the mapping is considered)
        for row in range(0,len(mapping)):
            if(mapping['nameDataSource'][row] in input and mapping['nameInternal'][row] not in newData):
                newData[mapping['nameInternal'][row]] = input[mapping['nameDataSource'][row]]
                
        #convert date to proper time format and save information on season
        newData['date'] = pd.to_datetime(newData['date'], format=inputFormat)
        seasonStart = str(newData['date'][0].year)
        seasonEnd = str(newData['date'][len(newData.index)-1].year)
        newData['season']=seasonStart+"/"+seasonEnd
        newData['date'] = newData['date'].dt.strftime(targetFormat)

        return pd.concat([existingData, newData], ignore_index=True, axis=0)


    #internal method to add all existing files, for all variables not in missingDataAllowed, missing data leads to deletion of the whole match from the data
    def inputAllFiles(root, mapping, inputFormat = '%d/%m/%y', missingDataAllowed = []):
        
        data = pd.DataFrame()
        importer = DataImporter()
        
        for path, subdirs, files in os.walk(root):
            for name in files:
                filename = os.path.join(path, name)
                if("._" not in filename):
                    print("Inserting data from: "+filename)
                    data = importer.addInputFile(data, filename, mapping, inputFormat)
        
        
        print("Total dataset of "+str(len(data))+" matches")
        
        for column in data.columns:
            if(column not in missingDataAllowed):
                data.dropna(subset=[column], inplace=True)
        data.reset_index(drop=True, inplace=True)
        
        print("Total dataset of "+str(len(data))+" matches")
        
        data.to_csv(os.path.join(os.path.dirname(__file__), "../data\data.csv"))
        
        return data
    
    
    #helper method to add information indicating whether a team has a higher number of a variable (e.g. shots)
    def moreLess(row, variable):
        if row[variable] > row[variable+'Opponent']:
            return 'more'
        elif row[variable] < row[variable+'Opponent']:
            return 'less'
        else:
            return 'same'
    
    #helper method to add information indicating whether a team is favorite or outsider in a match    
    def favOut(row):
        if row['odds'] < row['oddsOpponent']:
            return 'fav'
        elif row['odds'] > row['oddsOpponent']:
            return 'out'
        else:
            return 'none'
        
    #helper method to add information indicating whether a match is close or clear 
    def closeMatch(row):
        if abs(row['oddsHome'] - row['oddsAway'])<0.2:
            return 'close'
        else:
            return 'clear'
        