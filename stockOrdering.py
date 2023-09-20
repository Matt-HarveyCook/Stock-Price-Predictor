import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from sklearn.metrics import precision_score
import csv
import os
import matplotlib.pyplot as plt

# Block for importing the stocks from yfinance or CSV

msft = yf.Ticker("MSFT")
# msftHist = msft.history(period="max")
# msftHist.to_json("msftStockData.json")
# msftHist = pd.read_json('msftStockData.json') 

otherStock = yf.Ticker('AAPL')
# otherHist = otherStock.history(period="max")
# otherHist.to_json("otherHist.json")
# otherHist = pd.read_json('otherHist.json')


# Loads a given csv into a dataframe with correct columns
def csvConversion(filePath):
    otherHist = pd.read_csv('fiveYearData/'+ filePath)
    newDF = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
    newDF.High = otherHist.high
    newDF.Open = otherHist.open
    newDF.Low = otherHist.low
    newDF.Close = otherHist.close
    newDF.Volume = otherHist.volume
    newDF.index = otherHist.date
    return newDF

# Loads a csv using columns based on file name
def topTenConversion(filePath):
    otherHist = pd.read_csv('fiveYearData/'+ filePath)
    addOn = filePath.split("_")[0]
    newDF = pd.DataFrame(columns=['Open'+addOn, 'High'+addOn, 'Low'+addOn, 'Close'+addOn, 'Volume'+addOn])
    newDF.iloc[:,0] = otherHist.open
    newDF.iloc[:,1] = otherHist.high
    newDF.iloc[:,2] = otherHist.low
    newDF.iloc[:,3] = otherHist.close
    newDF.iloc[:,4] = otherHist.volume
    newDF.index = otherHist.date
    return newDF

msftHist = csvConversion('MSFT_data.csv')

def calculatePrecisionScore(otherHistPath):
    otherHist = csvConversion(otherHistPath)

    temp = msftHist.copy()
    temp["Target"] = None

    # Calculates daily change
    for i in range(0, len(temp)):
        if(temp.iloc[i].Close > temp.iloc[i].Open):
            temp.iloc[i, 5] = 1.0
        else:
            temp.iloc[i, 5] = 0.0

    # Appends and moves daily change
    otherHist = otherHist[otherHist.index >= msftHist.index[0]]
    otherHist['Target'] = temp['Target']
    otherHist['Target'] = otherHist['Target'].shift(-1)

    # Trains a model for prediction using predictCols
    predictCols = ['Open', 'High', 'Low', 'Close', 'Volume']
    model = RandomForestClassifier(n_estimators=100, min_samples_split=200, random_state=1)
    train = otherHist.iloc[:-100]
    test = otherHist.iloc[-100:]
    model.fit(train[predictCols], train["Target"].astype('int'))

    # Uses model to make predictions and return accuracy
    predictions = model.predict(test[predictCols])
    preds = pd.Series(predictions, index = test.index)
    precScore = precision_score(test["Target"].iloc[:-1].astype('int'), preds.iloc[:-1])
    return precScore

stockList = []

# Places every file name into a single array
for file in os.listdir('fiveYearData'):
    filename = os.fsdecode(file)
    if(filename.endswith(".csv")):
        stockList.append(file)
    
# Incomplete datasets
removeList = ['REGN_data.csv', 'VRTX_data.csv']

# Validates the remaining stocks based on length
for stock in stockList:
    path = 'fiveYearData/'+stock
    with open(path, 'r') as f:
        row_count = sum(1 for row in f)
        if(row_count != 1260):
            removeList.append(stock)


# Used for testing
stockList = ['PKI_data.csv', 'DRE_data.csv', 'CNC_data.csv', 'ANSS_data.csv', 'MET_data.csv', 'MAA_data.csv', 'NEM_data.csv', 'TMK_data.csv', 'FTI_data.csv', 'HSIC_data.csv', 'PCG_data.csv', 'BA_data.csv', 'NOV_data.csv', 'MGM_data.csv', 'CTSH_data.csv', 'MAS_data.csv', 'MDLZ_data.csv', 'WEC_data.csv']

# Calculates the accuracy of each stock and stores it in a CSV
# open(r'exampleScore.csv', 'w').close()
# for stock in stockList[:5]:
#     if(stock not in removeList):
#         score = calculatePrecisionScore(stock) 
#         fields=['Name','Score']
#         with open(r'exampleScore.csv', 'a') as f:
#             writer = csv.writer(f)
#             writer.writerow([stock.split('_')[0], score])



def calcCombinedFinal():
    fields=['Name','Score']
    df = pd.read_csv('precisionScore.csv', names=fields)

    # Gets the 10 best stocks from the csv 
    bestTen = df.sort_values('Score').tail(12)[:-2]
    combinedDF = pd.DataFrame()

    # Apply conversion method to each and append
    for i in bestTen['Name']:
        temp = topTenConversion(i+'_data.csv')
        combinedDF = pd.concat([combinedDF, temp], axis=1)

    otherHist = combinedDF
    otherHist['Target'] = 0
    predictCols = otherHist.columns[:-1]
    temp = msftHist.copy()
    temp["Target"] = None

    # Generate a target for each
    for i in range(0, len(temp)):
        if(temp.iloc[i].Close > temp.iloc[i].Open):
            temp.iloc[i, 5] = 1.0
        else:
            temp.iloc[i, 5] = 0.0

    otherHist['Target'] = temp['Target']
    otherHist['Target'] = otherHist['Target'].shift(-1)

    # Make and train a model
    model = RandomForestClassifier(n_estimators=1000, random_state=1)
    train = otherHist.iloc[:-100]
    test = otherHist.iloc[-100:]
    model.fit(train[predictCols], train["Target"].astype('int'))
    
    # Use the model to make predictions
    predictions = model.predict(test[predictCols])
    preds = pd.Series(predictions, index = test.index)
    precScore = precision_score(test["Target"].iloc[:-1].astype('int'), preds.iloc[:-1])

    return precScore

