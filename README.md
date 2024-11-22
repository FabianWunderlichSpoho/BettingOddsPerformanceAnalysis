# BettingOddsPerformanceAnalysis
including tools for performance analysts to extract information enclosed in betting odds

## 1) Scope
This repository is related to the paper:

Wunderlich, F. (2024). Using the wisdom of crowds in sports: How performance analysis in football can benefit from the information enclosed in betting odds. International Journal of Performance Analysis in Sport (in revision)

It is intended to provide tools to extract and use information enclosed in betting odds for further analysis to anybody interested in performance analysis in football. Please refer to the paper for any questions on the background of the models used and explanation on example use cases. 


## 2) License & Usage
The code is open and can be used freely. If you use it for scientific purposes, please make sure to always cite the paper referenced above.


## 3) Content & Folder Structure
### Tools
The repository includes tools intended to be used to extract information from betting odds:
* **AnticipatedGoalsCalculation.py** (calculates anticipated goals from betting odds)
* **DataImport.py** (imports data from the input folder to the system using the customised input mappings)
* **Metrics.py** (calculates metrics like rank probability score or squared errors)
* **ProbabilityCalculation.py** (obtains outcome probabilities from betting odds)
* **ProbabilityModelling.py** (translates anticipated goal numbers to outcome probabilities and can be reversely used for calculation of anticipated goals)

### Code used for the paper
The repository further includes the code used to infer the results shown in the paper. These are not originally intended to be used as tools, but to enable replicability of the paper and to show example usage of the tools. 
* **AnalysisCalibration.py** (analyses and illustrates calibration of the models)
* **AnalysisShotSuccess.py** (analyses and illustrates the relationship between team strength, shot numbers and success)
* **AnalysisWinnerPrediction.py** (analyses and illustrates the accuracy of several models in predicting the winner of a match)
* **AverageCalculation.py** (calculates average number of goals or points to be used in further analysis)
* **EloModel.py** (used to calculate Elo ratings for the teams in the data for further analysis)

### Example data
Finally, the repository includes example data with a very limited amount of matches with no reference to real teams. It does not republish any real-world datasets, however, sources for real-world datasets can be found in the paper. Moreover, it includes the possibility to define inputMappings, that help to import data from varying data sources. 

    .
    ├── bettingCalculationTools                    # Tools to extract information from betting odds
    ├── data                                       # Folder used to store intermediate results for debugging and further usage
    ├── input                                      # Input data to be used by the tools (by default including very basic example data)
    ├── inputMappings                              # Standard input mappings and possibility to design additional ones
    └── Code used for the Paper / README.md        # The code used for the analyses shown in the paper


## 4) Limitations
This is an repository open to public, but does not constitute a python package. The code is provided as is and may not fulfil highest standards for documentation and error handling. Code might be in need to be sligthly adjusted depending on python version and operating system used. There is no guarantee for the functionality of the code or the absence of any undesired effects.


## 5) Contact
If you have any questions, please contact f.wunderlich@dshs-koeln.de
