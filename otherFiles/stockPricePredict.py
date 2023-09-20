import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from sklearn.metrics import precision_score

msft = yf.Ticker("MSFT")
msftHist = msft.history(period="max")
msftHist.to_json("msftStockData.json")


data = msftHist[["Close"]]
data = data.rename(columns = {'Close':'Actual_Close'})
data["Target"] = 'NaN'

for i in range(1, len(data)):
    todayPrice = (data.iloc[i]["Actual_Close"])
    tomoPrice = (data.iloc[i-1]["Actual_Close"])
    if(todayPrice>tomoPrice):
        data["Target"][i] = 1.0
    else:
        data["Target"][i] = 0.0

msftPrev = msftHist.copy()
msftPrev = msftPrev.shift(1)
predictors = ["Close", "Volume", "Open", "High", "Low"]
data = data.join(msftPrev[predictors]).iloc[1:]

model = RandomForestClassifier(n_estimators=100, min_samples_split=200, random_state=1)
train = data.iloc[:-100]
test = data.iloc[-100:]
model.fit(train[predictors], train["Target"].astype('int'))

preds = model.predict(test[predictors])
preds = pd.Series(preds, index = test.index)
print(precision_score(test["Target"].astype('int'), preds))