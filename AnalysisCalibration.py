# -*- coding: utf-8 -*-
"""
@author: FW

Analysis on the calibration of probabilities and anticipated goals
"""

import numpy as np
import pandas as pd
import os
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt
from bettingCalculationTools.ProbabilityCalculation import BasicNormalisation, ShinModel
from bettingCalculationTools.AnticipatedGoalsCalculation import Regression, InvertedPoisson
from bettingCalculationTools.DataImport import DataImporter
from scipy.stats import binned_statistic
from bettingCalculationTools.Metrics import MetricsCalculation
from AverageCalculation import AverageCalculation



#loads, prepares and saves all data
def prepareData():
    root = os.path.join(os.path.dirname(__file__), "input")
    mapping = os.path.join(os.path.dirname(__file__), "inputMappings\inputMappingMatchDataAverageOdds.csv")
    data = DataImporter.inputAllFiles(root, mapping, missingDataAllowed = ['shotsHome', 'shotsAway', 'shotsTargetHome', 'shotsTargetAway'])
    
    #add average points and goals to data
    data = AverageCalculation.calculateAverages(data)
    
    #add data for two different methods of probability calculation
    Calculator = BasicNormalisation()
    dataBasicNormalisation = Calculator.addProbabilities(data)
    dataBasicNormalisation.to_csv(os.path.join(os.path.dirname(__file__), "data\dataBasicNormalisation.csv"))

    Calculator = ShinModel()
    dataShin = Calculator.addProbabilities(data)
    dataShin.to_csv(os.path.join(os.path.dirname(__file__), "data\dataShin.csv"))

    #add data for two different methods of anticipated goals calculation based on the Shin probabilities
    Calculator = Regression("linear")
    dataRegression = Calculator.addAnticipatedGoals(dataShin)
    dataRegression.to_csv(os.path.join(os.path.dirname(__file__), "data\dataRegression.csv"))
    
    Calculator = InvertedPoisson()
    dataInvertedPoisson = Calculator.addAnticipatedGoals(dataShin, os.path.join(os.path.dirname(__file__), "data\Table.csv"))
    dataInvertedPoisson.to_csv(os.path.join(os.path.dirname(__file__), "data\dataInvertedPoisson.csv"))
    

    
    
    
#calculates the mean squared error between anticipated and actual goals for various methods  
def analysisMeanSquaredErrors():
    #read data
    dataShin = pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataShin.csv"), sep = ",")   
    dataRegression = pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataRegression.csv"), sep = ",")   
    dataInvertedPoisson = pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataInvertedPoisson.csv"), sep = ",")     
    

    #print results    
    print('----- All Matches -----')
    print('MSE Average Home Advantage')
    print(MetricsCalculation.calculateSquaredErrorAverageHA(dataShin))
    print('MSE Average Goals')
    print(MetricsCalculation.calculateSquaredErrorAverageGoals(dataShin))
    print('MSE Inverse Poisson')
    print(MetricsCalculation.calculateSquaredErrorAnticipatedGoals(dataInvertedPoisson))
    print('MSE Regression')
    print(MetricsCalculation.calculateSquaredErrorAnticipatedGoals(dataRegression))
        
    dataShin = dataShin[dataShin['round']=='second']
    dataRegression = dataRegression[dataRegression['round']=='second']
    dataInvertedPoisson = dataInvertedPoisson[dataInvertedPoisson['round']=='second']
        
    print('----- Only Second round -----')
    print('MSE Average Home Advantage')
    print(MetricsCalculation.calculateSquaredErrorAverageHA(dataShin))
    print('MSE Average Goals')
    print(MetricsCalculation.calculateSquaredErrorAverageGoals(dataShin))
    print('MSE Inverse Poisson')
    print(MetricsCalculation.calculateSquaredErrorAnticipatedGoals(dataInvertedPoisson))
    print('MSE Regression')
    print(MetricsCalculation.calculateSquaredErrorAnticipatedGoals(dataRegression))
    
    
    
#plots calibration curves for home win probabilities for two methods (Basic Normalisation and Shin Formula)
def plotCalibrationProbabilityHome():
    #read data
    dataShin = pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataShin.csv"), sep = ",")   
    dataBasicNormalisation = pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataBasicNormalisation.csv"), sep = ",")   

         
    # plot baseline
    x=np.linspace(0,1,1000)
    y=x
    
    
    #plot figure only for home matches
    fig, ((ax1, ax2)) = plt.subplots(1,2,figsize = (10.5, 6))
    fig.tight_layout(h_pad=0.2, w_pad=3.0, rect=[0, 0.2, 1, 0.95])
    fig.dpi = 500
    
    for ax in [ax1, ax2]:
        ax.grid()
        ax.set_xlim([0.1, 0.9])
        ax.set_ylim([0.1, 0.9])
        ax.tick_params(axis='both', which='major', labelsize=5)
        ax.plot(x,y, linewidth = 1)
        ax.set_xlabel('Predicted Probability')
        ax.set_ylabel('Observed Probability')
   
    ax1.title.set_text('Basic Normalisation')
    ax1.title.set_size(18)
    ax2.title.set_text('Shin Model')
    ax2.title.set_size(18)


    #plot calibration curves
    #home
    y_true = dataBasicNormalisation['goalsHome']>dataBasicNormalisation['goalsAway']
    y_pred = dataBasicNormalisation['probHome']
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy = 'quantile')
    ax1.plot(prob_pred, prob_true, marker='o', linewidth=1, color = 'firebrick', markersize=4, label='basic normalisation')

    

    y_true = dataShin['goalsHome']>dataShin['goalsAway']
    y_pred = dataShin['probHome']
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy = 'quantile')
    ax2.plot(prob_pred, prob_true, marker='o', linewidth=1, color = 'firebrick', markersize=4, label='Shin')
  
        

    
 #plots calibration curves for two methods (Basic Normalisation and Shin Formula) and all match outcomes
def plotCalibrationProbabilities():
    #read data
    dataShin = pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataShin.csv"), sep = ",")   
    dataBasicNormalisation = pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataBasicNormalisation.csv"), sep = ",")   
    
        
    #plot calibration for two methods and all match outcomes
    fig, ((fig1Home, fig2Home), (fig1Draw, fig2Draw), (fig1Away, fig2Away), (fig1Over, fig2Over), (fig1Under, fig2Under)) = plt.subplots(5,2,figsize = (6, 8))
    fig.tight_layout(h_pad=2.0, w_pad=2.0, rect=[0, 0.03, 1, 0.95])
    fig.suptitle('Basic Normalisation                                           Shin model    ', fontsize = 10)
    fig.dpi = 500
    
    #baseline
    x=np.linspace(0,1,1000)
    y=x

    for fig in [fig1Home,fig1Draw,fig1Away,fig1Over,fig1Under,fig2Home,fig2Draw,fig2Away,fig2Over,fig2Under]:

        fig.grid()
        fig.set_xlabel('Predicted Probability', fontsize = 7)
        fig.set_ylabel('Observed Probability', fontsize = 7)
        fig.tick_params(axis='both', which='major', labelsize=5)
        fig.plot(x,y, linewidth = 1)

            
    fig1Home.set_title('Home', fontsize = 7)
    fig1Draw.set_title('Draw', fontsize = 7)
    fig1Away.set_title('Away', fontsize = 7)
    fig1Over.set_title('Over25', fontsize = 7)
    fig1Under.set_title('Under25', fontsize = 7)
    fig2Home.set_title('Home', fontsize = 7)
    fig2Draw.set_title('Draw', fontsize = 7)
    fig2Away.set_title('Away', fontsize = 7)
    fig2Over.set_title('Over25', fontsize = 7)
    fig2Under.set_title('Under25', fontsize = 7)
        
    fig1Home.set_xlim([0.1, 0.9])
    fig1Draw.set_xlim([0.1, 0.4])
    fig1Away.set_xlim([0, 0.7])
    fig1Over.set_xlim([0.3, 0.7])
    fig1Under.set_xlim([0.25, 0.65])
    fig2Home.set_xlim([0.1, 0.9])
    fig2Draw.set_xlim([0.1, 0.4])
    fig2Away.set_xlim([0, 0.7])
    fig2Over.set_xlim([0.3, 0.7])
    fig2Under.set_xlim([0.25, 0.65])
        
    fig1Home.set_ylim([0.1, 0.9])
    fig1Draw.set_ylim([0.1, 0.4])
    fig1Away.set_ylim([0, 0.7])
    fig1Over.set_ylim([0.3, 0.7])
    fig1Under.set_ylim([0.30, 0.70])
    fig2Home.set_ylim([0.1, 0.9])
    fig2Draw.set_ylim([0.1, 0.4])
    fig2Away.set_ylim([0, 0.7])
    fig2Over.set_ylim([0.3, 0.7])
    fig2Under.set_ylim([0.30, 0.70])
    


    #plot calibration curves
    #home
    y_true = dataBasicNormalisation['goalsHome']>dataBasicNormalisation['goalsAway']
    y_pred = dataBasicNormalisation['probHome']
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy = 'quantile')
    fig1Home.plot(prob_pred, prob_true, marker='o', linewidth=1, color = 'firebrick', markersize=4, label='basic normalisation')
    #draw
    y_true = dataBasicNormalisation['goalsHome']==dataBasicNormalisation['goalsAway']
    y_pred = dataBasicNormalisation['probDraw']
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy = 'quantile')
    fig1Draw.plot(prob_pred, prob_true, marker='o', linewidth=1, color = 'firebrick', markersize=4, label='basic normalisation')
    #away
    y_true = dataBasicNormalisation['goalsHome']<dataBasicNormalisation['goalsAway']
    y_pred = dataBasicNormalisation['probAway']
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy = 'quantile')
    fig1Away.plot(prob_pred, prob_true, marker='o', linewidth=1, color = 'firebrick', markersize=4, label='basic normalisation')
    #over25
    y_true = dataBasicNormalisation['goalsHome']+dataBasicNormalisation['goalsAway']>2.5
    y_pred = dataBasicNormalisation['probOver25']
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy = 'quantile')
    fig1Over.plot(prob_pred, prob_true, marker='o', linewidth=1, color = 'firebrick', markersize=4, label='basic normalisation')
    #over25
    y_true = dataBasicNormalisation['goalsHome']+dataBasicNormalisation['goalsAway']<2.5
    y_pred = dataBasicNormalisation['probUnder25']
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy = 'quantile')
    fig1Under.plot(prob_pred, prob_true, marker='o', linewidth=1, color = 'firebrick', markersize=4, label='basic normalisation')

    

    y_true = dataShin['goalsHome']>dataShin['goalsAway']
    y_pred = dataShin['probHome']
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy = 'quantile')
    fig2Home.plot(prob_pred, prob_true, marker='o', linewidth=1, color = 'firebrick', markersize=4, label='Shin')
    #draw
    y_true = dataShin['goalsHome']==dataShin['goalsAway']
    y_pred = dataShin['probDraw']
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy = 'quantile')
    fig2Draw.plot(prob_pred, prob_true, marker='o', linewidth=1, color = 'firebrick', markersize=4, label='Shin')
    #away
    y_true = dataShin['goalsHome']<dataShin['goalsAway']
    y_pred = dataShin['probAway']
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy = 'quantile')
    fig2Away.plot(prob_pred, prob_true, marker='o', linewidth=1, color = 'firebrick', markersize=4, label='Shin')
    #over25
    y_true = dataShin['goalsHome']+dataShin['goalsAway']>2.5
    y_pred = dataShin['probOver25']
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy = 'quantile')
    fig2Over.plot(prob_pred, prob_true, marker='o', linewidth=1, color = 'firebrick', markersize=4, label='Shin')
    #over25
    y_true = dataShin['goalsHome']+dataShin['goalsAway']<2.5
    y_pred = dataShin['probUnder25']
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy = 'quantile')
    fig2Under.plot(prob_pred, prob_true, marker='o', linewidth=1, color = 'firebrick', markersize=4, label='Shin')
         
       
   
def plotCalibrationAnticipatedGoals():
    #read data
    dataInvertedPoisson = pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataInvertedPoisson.csv"), sep = ",")   
    dataRegression = pd.read_csv(os.path.join(os.path.dirname(__file__), "data\dataRegression.csv"), sep = ",")   
    
    #genrate plot including four figures
    fig, ((ax1, ax3), (ax2, ax4)) = plt.subplots(2,2,figsize = (15, 10))
    fig.tight_layout(h_pad=6.0, w_pad = 6.0)
    fig.dpi = 500
    x=np.linspace(0.0,2.5,1000)
    y=x
    
    for ax in [ax1,ax2,ax3,ax4]:
        ax.plot(x,y, linewidth = 1)
        ax.set_xlim([0.0, 2.5])
        ax.set_ylim([0.0, 2.5])
        ax.grid()
        ax.set_xlabel('Anticipated Goals')
        ax.set_ylabel('Observed Goals')
        
    ax1.title.set_text('Home Goals - Inverted Poisson')
    ax2.title.set_text('Away Goals - Inverted Poisson')
    ax3.title.set_text('Home Goals - Regression')
    ax4.title.set_text('Away Goals - Regression')

    #generate and plot calibration curves
    for method in ['dataInvertedPoisson', 'dataRegression']:
        if(method == 'dataInvertedPoisson'):
            data = dataInvertedPoisson
        if(method == 'dataRegression'):
            data = dataRegression
    

        antHome = data['anticipatedGoalsHome']
        realHome = data['goalsHome']
        antAway = data['anticipatedGoalsAway']
        realAway = data['goalsAway']
     
        binsHome = []
        binsAway = []
        for i in np.linspace(0,1,11):
            binsHome.append(np.quantile(antHome, i))
            binsAway.append(np.quantile(antAway, i))
        xHome = binned_statistic(antHome, antHome, statistic='mean', bins=binsHome).statistic
        yHome = binned_statistic(antHome, realHome, statistic=np.nanmean, bins=binsHome).statistic
        xAway = binned_statistic(antAway, antAway, statistic='mean', bins=binsAway).statistic
        yAway = binned_statistic(antAway, realAway, statistic=np.nanmean, bins=binsAway).statistic
            
        if(method == 'dataInvertedPoisson'):
            ax1.scatter(xHome, yHome)
            ax2.scatter(xAway, yAway)
        if(method == 'dataRegression'):
            ax3.scatter(xHome, yHome)
            ax4.scatter(xAway, yAway)
        
        

prepareData()   
analysisMeanSquaredErrors()
plotCalibrationProbabilityHome()
plotCalibrationProbabilities()
plotCalibrationAnticipatedGoals()

    

    