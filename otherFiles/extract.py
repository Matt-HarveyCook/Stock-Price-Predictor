import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import os
import datetime

directory = os.fsencode(".")
    
# columns=["Ticker", "Stock Price", "Market Cap", "Number of Shares To Buy"]
# final_frame = pd.DataFrame(columns=columns)
# for file in os.listdir(directory):
#     filename = os.fsdecode(file)
#     if(filename.endswith(".csv")):
#         data = pd.read_csv(filename)
#         tail = (data.tail())
#         row = (data.tail()).iloc[0]
#         final_frame = pd.concat([final_frame, pd.DataFrame.from_records([{"Ticker":row.Name, "Stock Price":row.close, "Market Cap":(row.close*row.volume)/10000000, "Number of Shares To Buy":"N/A"}])])

# calculate the percentage change for each of the stocks for a year 
columns=["Ticker", "Stock Price", "Yearly Percentage Change", "Number of Shares To Buy"]
final_frame = pd.DataFrame(columns=columns)

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if(filename.endswith(".csv")):
        data = pd.read_csv(filename)
        if(len(data)>500):

            row = (data.tail()).iloc[0]
            date = row["date"]
            year = int(date[0:4])
            month = int(date[5:7])
            day = int(date[8:10])
            date = datetime.date(year, month, day)
            dateMinusYear = date - datetime.timedelta(days=365)
            if(dateMinusYear.weekday()==6 or dateMinusYear.weekday()==7):
                dateMinusYear = dateMinusYear +datetime.timedelta(days=2) 
            dateMinusYear = (dateMinusYear.strftime("%Y-%m-%d"))
            pastPrice = float(data[data.eq(dateMinusYear).any(1)]["close"])
            currentPrice = float(row["close"])
            percentChange = ((currentPrice/pastPrice)-1)*100
            # print("this is the last yuear "+str(pastPrice))
            # print("this ithe current "+str(currentPrice))
            # print("this is the percet change "+str(percentChange))
            # print(row)
            final_frame = pd.concat([final_frame, pd.DataFrame.from_records([{"Ticker":row.Name, "Stock Price":row.close, "Yearly Percentage Change":percentChange, "Number of Shares To Buy":"N/A"}])])

print(final_frame.sort_values("Ticker"))
final_frame.to_csv("SPpercentChange2018-02-01.csv", sep="\t")
